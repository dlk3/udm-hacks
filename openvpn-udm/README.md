# Configuring An OpenVPN Server On A Unifi Dream Machine Pro

The Unifi Dream Machine Pro (UDM) comes with OpenVPN software installed on it.  The UDM's administrative UI can configure UDM's OpenVPN to create a point-to-point VPN connection between the UDM and another network.  It does not support configuring OpenVPN as a VPN server that clients on the public internet can use to access my local LAN.  This can be done manually, however, in a manner that will persist through UDM firmware upgrades and reboots.

The steps necessary are:

1)  Install the EasyRSA tool that the OpenVPN development team provides to create and manage the X509 certificates that are used by the OpenVPN server and the clients.
2)  Create the X509 certificates and keys that the OpenVPN server needs to run.
3)  Create the OpenVPN server configuration file.
4)  Install a boot script which will start the OpenVPN server whenever the UDM boots.
5)  Create one or more client configuration files which contain the settings, certificate and key that the client needs to authenticate with the server.
6)  Distribute the client configuration files and test connectivity.

I haven't tested whether OpenVPN cannot be used in server mode at the same time that it is being used in point-to-point mode.  I've never had occasion to use the point-to-point mode so it's never been configured on my UDM.

## Security Warning

This process is all about opening a new hole in the UDM firewall, thereby making the network that the UDM protects less secure.  While I try not to do stupid stuff that exposes my network to harm, I cannot guarantee that there are no security exposures inherent in making the UDM configuration changes I describe below.  Fair warning, ok?  Do not do any of this if your UDM protects a critical network.  I cannot accept any responsibility for any harm that may befall anyone as a result of what I have done and documented here.

## Where To Put The Files

This document uses the `/data` directory as the location for the files that are added to configure the OpenVPN server.  If the secondary hard drive is installed in the UDM then the `/volume1` directory could be used instead.  The advantage is that data stored in `/volume1` is more likely to survive a major UDM firmware update.  For example, with the 2.4.27 firmware update that just came out, all of my customizations in the `/data` directory were deleted.  They had previously survived three years of updates, but this major update deleted them.  Those on the secondary disk, `/volume1`, survived however.  

## Install EasyRSA

EasyRSA is a tool that the OpenVPN development team has created to make the process of creating the PKI (public key infrastructure) associated with OpenVPN simpler.  This PKI is where I create, store and manage all of the certificates, keys and configuration files for my OpenVPN server and clients.  

EasyRSA is available in the OpenVPN GitHub repository at (https://github.com/OpenVPN/easy-rsa/releases/latest).  Get the name of the latest <code>EasyRSA-*.tgz</code> file there and then substitute it into these commands to complete the installation:
```
mkdir -p /data/openvpn/easyrsa
curl -OJL https://github.com/OpenVPN/easy-rsa/releases/download/v3.0.8/EasyRSA-3.0.8.tgz
tar xf EasyRSA-3.0.8.tgz --strip-components=1 -C /data/openvpn/easyrsa
rm EasyRSA-3.0.8.tgz
```
## Creating OpenVPN server certificates and keys

I created all of the certificates and keys that the OpenVPN server needs.  The OpenVPN web site has [instructions](https://openvpn.net/community-resources/how-to/#setting-up-your-own-certificate-authority-ca-and-generating-certificates-and-keys-for-an-openvpn-server-and-multiple-clients) for doing this but they are based on an earlier version of EasyRSA.  The EasyRSA commands and their options have changed a little with the release I am using.  Still, the web site is a useful source of additional information on what I'm doing here and why:
```
mkdir /data/openvpn/server
cd /data/openvpn/server
../easyrsa/easyrsa init-pki
../easyrsa/easyrsa build-ca nopass  
    Note: This command prompts for a name for the certificate authority that's being
          created.  I called mine "OpenVPN CA"
../easyrsa/easyrsa build-server-full server nopass
../easyrsa/easyrsa gen-dh
openvpn --genkey --secret pki/private/ta.key
```
The server certificates I created here and the client certificates I'll create later are good for 825 days.  Once that time expires I'll need to come back and renew all of the certificates I've issued.

## Creating a server configuration file

The [server configuration file](https://github.com/dlk3/udm-hacks/blob/master/openvpn-udm/server.conf) that I use is in this GitHub project.  It references all of the certificate and key files generated in the previous step.  See the [OpenVPN documentation](https://openvpn.net/community-resources/how-to/#creating-configuration-files-for-server-and-clients) for additional information on the server configuration file.

I would direct your attantion to the following lines in the configuration file:
```
local MY-UDM.SOMEDDNS.ORG
```
This line tells OpenVPN the IP address or the hostname of the WAN network interface on the UDM.  This is where OpenVPN will listen for clients that are trying to connect.  I use a hostname from a free DDNS service here.  It always stays the same, even when my cable company changes the IP address that my cable modem assigns to the WAN adapter on my UDM.
```
server 10.8.0.0 255.255.255.0
```
This is the IP subnet in my local network from which my VPN clients are assigned addresses by the server.  It needs to be a subnet that isn't in use elsewhere in my network.
```
push "route 192.168.1.0 255.255.255.0"
```
There needs to be a line like this for every LAN or VLAN in my local network that I want my clients to be able to access.

## The Management Option In The Server Configuration File

The management option is defined in the config file as a way to provide the Nagios network monitoring server that I use with an interface it can use to check the status of the openvpn daemon.  You could remove this option.  If not, be sure to create a pw-file containing a password to authenticate access through the management port.

## Creating a boot script to start the OpenVPN server

I want the OpenVPN server to start automatically every time my UDM boots up.  I previously used John "boostchicken" D's [on-boot-script GitHub repository](https://github.com/boostchicken/udm-utilities/tree/master/on-boot-script) utility for this purpose and that approach would still work.  This time around I prefer to build my own Debian package containing the startup routine and install that from my PPA repository.  That approach keeps things simple while ensuring persistence of my changes.

I wrote the [openvpn-server.sh script](https://github.com/dlk3/udm-hacks/blob/master/openvpn-udm/openvpn-server.sh) in this GitHub repository to start the OpenVPN server whenever the UDM boots.  It also configures the <code>iptables</code> firewall rules necessary to control access via the VPN.  It and the [openvpn-server.service](https://github.com/dlk3/udm-hacks/blob/master/openvpn-udm/openvpn-server.service) systemd file that controls it are included in the Debian package.

Before using this script on a new server the script might need an edit.  Please look at these parts of the script before using it on a new server:
```
WAN_IF='eth8'
OPENVPN_PORT='1194'
```
Confirm that the WAN interface specified here is, indeed, the WAN interface of the UDM.  The OpenVPN port, 1194, specified here needs to match the <code>port</code> directive in the server configuration file.

There is only one <code>iptables</code> firewall rule needed in order to enable OpenVPN on the UDM.  The rule used in my script opens the OpenVPN port on the WAN network interface to any internet device.  Once a device has been authenticated by the OpenVPN server, and has been connected to the VPN subnet, then the UDM's regular access rules will control what parts of the local network it has access to.  By default the UDM allows all devices on all networks to communicate with each other.  That works for me.  If you require additional restrictions, make the necessary changes using the UDM's regular network configuration UI.

### Script command line options

The <code>15-openvpn-server.sh</code> script can also be used to manually control the OpenVPN server and its <code>iptables</code> rule if that's ever necessary:

- Start the OpenVPN server<br /><code>/mnt/data/openvpn/15-openvpn-server</code> 
- Stop the OpenVPN server<br /><code>/mnt/data/openvpn/15-openvpn-server stop</code>
- Delete the <code>iptables</code> rules controlled by this script<br /><code>/mnt/data/openvpn/15-openvpn-server delete_rules</code>

## Creating OpenVPN configuration files for clients

I create, store and manage my OpenVPN client configuration files on the UDM in the same PKI that I created using EasyRSA when I configured the server.  I have created a script that generates a single <code>*.ovpn</code> file that contains the configuration directives plus the certificates and keys that the client needs to connect.

The [mk-ovpn](https://github.com/dlk3/udm-hacks/blob/master/openvpn-udm/mk-ovpn) script I use is in this GitHub repository.  It is in the <code>/data/openvpn</code> directory on my UDM.  Now, when I want to create an OpenVPN configuration file for a client I connect to my UDM via ssh and enter:
```
/data/openvpn/mk-ovpn client-name
```
The output configuration file is written to <code>/data/openvpn/client-name.ovpn</code>.  I move this file to the client machine.

These additional files are generated in the PKI to manage this client's certificate and private key.  They remain on the UDM:
```
/data/openvpn/server/pki/private/client-name.key
/data/openvpn/server/pki/client-name.creds
/data/openvpn/server/pki/reqs/client-name.req
/data/openvpn/server/pki/issued/client-name.crt
```
To use my script with a different OpenVPN server, the <code>OPENVPN_SERVER</code> variable at the top of the script needs to be set to be the hostname or IP address of the WAN interface on that UDM.

There's more information on managing OpenVPN clients, like revoking access by revoking certificates, in the [OpenVPN How To Guide](https://openvpn.net/community-resources/how-to).

## Distributing configuration files to clients and testing

The <code>*.ovpn</code> configuration files need to be treated like they are passwords allowing open access to the network.  The files need to be kept secure as they are distributed to client machines.

Configuring and running an OpenVPN client is beyond the scope of this document, so I'll leave that as an exercise for the reader.  I will point out a few things on the UDM which could help with troubleshooting:

* The OpenVPN server writes its log output into the UDM's <code>/var/log/messages</code> file.  The amount of information it writes can be controlled by setting the <code>verb</code> directive in the <code>/data/openvpn/server/server.conf</code> file.  Setting <code>verb 6</code> is recommended for debugging purposes.  The same change can be made in a client's configuration file to see debugging data at the client end of the connection.
* The OpenVPN server updates <code>/data/openvpn/server/openvpn-status.log</code> once every minute with information about currently connected clients.
* The OpenVPN server uses the <code>/data/openvpn/server/ipp.txt</code> file to remember what clients were assigned which addresses in case the server experiences a quick restart.
