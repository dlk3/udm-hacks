# Configuring An OpenVPN Server On A Unifi Dream Machine Pro

The Unifi Dream Machine Pro (UDM) comes with OpenVPN software installed on it.  The UDM's administrative UI can configure UDM's OpenVPN to create a point-to-point VPN connection between two machines.  It cannot configure OpenVPN as a VPN server providing access from the public internet into the local LAN.  This can be done manually, however, in a manner that will persist through UDM firmware upgrades and reboots.

The major steps in this process are:

1)  Install the EasyRSA tool that the OpenVPN development team provides to create and manage the X509 certificates that are used by the OpenVPN server and its clients.
2)  Create the X509 certificates and keys that the OpenVPN server needs to run.
3)  Create the OpenVPN server configuration file.
4)  Install a boot script which will start the OpenVPN server whenever the UDM boots.  This script also, very importantly, configures the UDM firewall rules to allow VPN traffic to flow between the server and its clients
5)  Create one or more client configuration files which contain the settings, certificate and key that the client needs to connect to the server.
6)  Distribute the client configuration file and test connectivity.

I haven't tested it, but I assume that OpenVPN cannot be used in server mode at the same time that it is being used in point-to-point mode.  I assume that any point-to-point configuration done through the admin UI would need to be disabled before doing any of what I'll describe below.  But, hey, you never know, I could be totally wrong about this.

## Security Warning

This process requires some additions to the <code>iptables</code> rules that the UDM uses to protect a network behind a firewall.  While I try not to do stupid stuff that exposes my network to harm, I cannot guarantee that there are no security exposures in the iptables rules changes I describe below.  Fair warning, ok?  Do not do any of this if your UDM protects a critical network.  I cannot accept any responsibility for any harm that may befall anyone as a result of what I have done and documented here.

## Install EasyRSA

EasyRSA is a tool that the OpenVPN development team has created to make the process of creating the PKI (public key infrastructure) associated with OpenVPN simpler.  This PKI is where I create, store and manage all of the certificates, keys and configuration files for my OpenVPN server and clients.  

EasyRSA is available in the OpenVPN GitHub repository at (https://github.com/OpenVPN/easy-rsa/releases/latest).  I downloaded and installed the latest <code>EasyRSA-*.tgz</code> file found there into a persistent directory on my UDM.

After connecting to my UDM via ssh, I installed EasyRSA with these commands:
```
mkdir -p /mnt/data/openvpn/easyrsa
curl -OJL https://github.com/OpenVPN/easy-rsa/releases/download/v3.0.8/EasyRSA-3.0.8.tgz
tar xf EasyRSA-3.0.8.tgz --strip-components=1 -C /mnt/data/openvpn/easyrsa
rm EasyRSA-3.0.8.tgz
```
## Creating OpenVPN server certificates and keys

I created all of the certificates and keys that the OpenVPN server will need.  The OpenVPN web site has [instructions](https://openvpn.net/community-resources/how-to/#setting-up-your-own-certificate-authority-ca-and-generating-certificates-and-keys-for-an-openvpn-server-and-multiple-clients) for doing this but they are based on a earlier version of EasyRSA.  The EasyRSA commands and their options have changed a little with the release I am using.  Still, the web site is a useful source of additional information on what I'm doing here and why:
```
mkdir /mnt/data/openvpn/server
cd /mnt/data/openvpn/server
../easyrsa/easyrsa init-pki
../easyrsa/easyrsa build-ca nopass  
    Note: This command prompts for a name for the certificate authority that's being
          created.  I called mine "OpenVPN CA"
../easyrsa/easyrsa build-server-full server nopass
../easyrsa/easyrsa gen-dh
openvpn --genkey --secret pki/private/ta.key
```
The server certificates I created here and the client certificates I'll create later are good for 825 days.  Before that time expires I'll need to come back and renew all of the certificates I've issued.

## Creating a server configuration file

The [server configuration file](https://github.com/dlk3/udm-hacks/blob/master/openvpn-udm/server.conf) that I use is in this GitHub project.  It references all of the certificate and key files generated in the previous step, using the directory structure and naming conventions assumed there.  See the [OpenVPN documentation](https://openvpn.net/community-resources/how-to/#creating-configuration-files-for-server-and-clients) for additional information on the server configuration file.

I would direct your attantion to the following lines in the file:
```
local MY-UDM.SOMEDDNS.ORG
```
This line tells OpenVPN the IP address or the hostname of the WAN network interface on the UDM.  This is where OpenVPN will listen for clients that are trying to connect.  I use a hostname from a DynamicDNS service here.  It always stays the same, even when my cable company changes the IP address that my cable modem assigns to the WAN adapter on my UDM.
```
server 10.8.0.0 255.255.255.0
```
This is the IP subnet from which my VPN clients are assigned addresses by the server.  It needs to be a subnet that isn't in use elsewhere in my network.  This subnet needs to match the one used in the <code>iptables</code> rules that are in the OpenVPN boot script I'll be creating below.
```
push "route 192.168.1.0 255.255.255.0"
```
There needs to be a line like this for every LAN or VLAN in my network that I want my clients to be able to access.  There also needs to be a matching <code>iptables</code> rule in the OpenVPN boot script I'll be creating below.  In my case, my clients only need to access my main LAN.  My other VLANs are off limits to them.

## Creating a boot script to start the OpenVPN server

I want the OpenVPN server to start automatically every time my UDM boots up.  John "boostchicken" D. has made a great little utility that makes this easy.  Go to his [on-boot-script GitHub repository](https://github.com/boostchicken/udm-utilities/tree/master/on-boot-script) and follow the very simple instructions found there to get it installed.

I wrote the [15-openvpn-server.sh script](https://github.com/dlk3/udm-hacks/blob/master/openvpn-udm/15-openvpn-server.sh) in this GitHub repository to start the OpenVPN server whenever the UDM boots.  It also configures the <code>iptables</code> firewall rules necessary to allow VPN traffic to flow to and from my OpenVPN clients.  It lives in the <code>/mnt/data/on_boot.d</code> directory used by boostchicken's tool.

Before using this script on a new server the <code>iptables</code> rules that it contains would need to be modified to match that sever's server.conf file.  Let's look at some of the rules that get set by the <code>iptables_rules</code> function inside the script:
```
#  Allow incoming traffic to the OpenVPN port
/usr/sbin/iptables $1 INPUT -p udp --dport 1194 -m state --state NEW -s 0.0.0.0/0 -j ACCEPT
```
The distination port, 1194, used in this rule needs to match the <code>port</code> directive in the server configuration file.
```
# Allow LAN hosts to send traffic back to the TUN interface if they have an established connection
# Add similar rules for other VLAN interfaces if required
/usr/sbin/iptables $1 FORWARD -i $LAN_IF -o tun0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```
I only need my clients to access my main LAN network, which uses the <code>br0</code> interface on my UDM.  If I want my clients to be able to access other networks I would need to add a line like this for the interfaces used by those VLANs.  I'd also need to add a <code>push</code> directive to the server configuration that would push a route for those VLANs to the clients.
```
# Block any traffic between VPN clients
# The subnet definition used here must match the that defined in the OpenVPN server.conf
/usr/sbin/iptables $1 FORWARD -i tun0 -s 10.8.0.0/24 -d 10.8.0.0/24 -j DROP
```
If the <code>server</code> directive in the server configuration file specifies a subnet other than <code>10.8.0.0 255.255.255.0</code> then I would need to change this rule to match.

### Script command line options

The <code>15-openvpn-server.sh</code> script can also be used to manually control the OpenVPN server and the <code>iptables</code> rules if that's ever necessary:

- Start the OpenVPN server<br /><code>/mnt/data/openvpn/15-openvpn-server</code> 
- Stop the OpenVPN server<br /><code>/mnt/data/openvpn/15-openvpn-server stop</code>
- Delete the iptables rules associated with the OpenVPN server<br /><code>/mnt/data/openvpn/15-openvpn-server delete_rules</code>

## Creating OpenVPN configuration files for clients

I create, store and manage my OpenVPN client configuration files on the UDM using the PKI that I created using EasyRSA when I configured the server.  I have created a script that generates a single <code>*.ovpn</code> file that contains the configuration directives plus the certificates and keys that the client needs to connect.

The [mk-ovpn](https://github.com/dlk3/udm-hacks/blob/master/openvpn-udm/mk-ovpn) script I use is in this GitHub repository.  It is in the <code>/mnt/data/openvpn</code> directory on my UDM.  Now, when I want to create an OpenVPN configuration file for a client I connect to my UDM via ssh and enter:
```
/mnt/data/openvpn/mk-ovpn client-name
```
The output configuration file is written to <code>/mnt/data/openvpn/client-name.ovpn</code>

These additional files are generated in the PKI to manage this client's certificate and private key:
```
/mnt/data/openvpn/server/pki/private/client-name.key
/mnt/data/openvpn/server/pki/client-name.creds
/mnt/data/openvpn/server/pki/reqs/client-name.req
/mnt/data/openvpn/server/pki/issued/client-name.crt
```
To use my script with a different OpenVPN server, the <code>OPENVPN_SERVER</code> variable at the top of the script would need to be set to be the hostname or IP address of the WAN interface on that UDM.

There's more information on managing OpenVPN clients, like revoking access by revoking certificates, in the [OpenVPN documentation](https://openvpn.net/community-resources/how-to).

## Distributing configuration files to clients and testing

The <code>*.ovpn</code> configuration files need to be treated like they are passwords allowing open access to the network.  The files need to be kept secure as they are distributed to client machines.

Confiuring and running an OpenVPN client is beyond the scope of this document, so I'll leave that as an exercise for the reader.  I will point out a few things on the UDM which could help with troubleshooting:

* The OpenVPN server writes its log output into the UDM's <code>/var/log/messages</code> file.  The amount of information it writes can be controlled by setting the <code>verb</code> directive in the <code>/mnt/data/openvpn/server/server.conf</code> file.  Setting <code>verb 6</code> is recommended for debugging purposes.  The same change can be made in a client's configuration file to see debugging data at the client end of the connection.
* The OpenVPN server updates <code>/mnt/data/openvpn/server/openvpn-status.log</code> once every minute with information about currently connected clients.
* The OpenVPN server uses the <code>/mnt/data/openvpn/server/ipp.txt</code> file to remember what clients were assigned which addresses in case the server experiences a quick restart.
