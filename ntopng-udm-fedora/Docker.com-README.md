# Running ntopng On The Unifi Dream Machine (UDM)

This container image can be used to run the ntopng network traffic analysis tool on a Unifi Dream Machine router/switch.  

This project was inspired by Carlos Talbot's  [tusc/ntopng-udm project](https://github.com/tusc/ntopng-udm).  This container differs in the following ways:

1. A Fedora container is used, because I like being on the semi-bleeding edge.
2. The unstable development version of ntopng from GitHub is used in this container.  This container is rebuilt weekly, on Monday night.
3. Network Discovery is enabled, i.e., the libcap library is compiled in.
4. An up-to-date version of the geoipupdate tool is used.
5. The start-up process for the container has been modified so that startup will not loop endlessly, blocking startup, when the GeoIP.conf file has errors.
6. An `ethtool` command was added to the startup process to turn off oversized packet handling per the ntopng log.
7. The run command in this documentation has been fixed so that the ntopng configuration data stored in the redis DB is actually persisted through UDM updates and restarts.
8. The run command in this documentation has been updated to include the `--privileged` option.  This gives the commands running inside the container the same access to system devices and files they would have if they were running natively on the UDM, under the root userid.  This fixes a couple of errors seen in the logs.

# Running The Container On The UDM

## Creating the ntopng persistent data directories

Access the UDM as the root user via ssh.  You will be placed into the system's root directory.  The runtime environment for the container can be established by entering the following commands.
```
mkdir -p /mnt/data/ntopng/redis
mkdir -p /mnt/data/ntopng/lib
curl -Lo /mnt/data/ntopng/GeoIP.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm-fedora/data/ntopng/GeoIP.conf
curl -Lo /mnt/data/ntopng/ntopng.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm-fedora/data/ntopng/ntopng.conf
curl -Lo /mnt/data/ntopng/redis.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm-fedora/data/ntopng/redis.conf
```
If the secondary disk is installed in the UDM then `/mnt/data_ext` can be used as the root for these directories to make it so that the application data is stored on the secondary disk.

## Enabling GeoIP support

If you want GeoIP support, i.e., you want geo maps of hosts sending and receiving traffic, then follow [these instructions](https://github.com/ntop/ntopng/blob/dev/doc/README.geolocation.md) on the ntopng web site to create a free account at MaxMind and to register for an API key.  The account and API key values must be placed into the /mnt/data/ntopng/GeoIP.conf file.

## Installing The Container

Run this command to copy the container from the Docker repository onto the UDM:

`podman pull dlk3/ntopng-udm:latest`
 
## Running the container

Run this command to start the container:
```
podman run -d --net=host --privileged --restart always --name ntopng \
   -v /mnt/data/ntopng/GeoIP.conf:/etc/GeoIP.conf \
   -v /mnt/data/ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
   -v /mnt/data/ntopng/redis.conf:/etc/redis/redis.conf \
   -v /mnt/data/ntopng/lib:/var/lib/ntopng \
   -v /mnt/data/ntopng/redis:/var/lib/redis \
   -v /etc/localtime:/etc/localtime:ro \
   ntopng-udm:latest
```
Remember to use `/mnt/data_ext` as the root for the directories if you are keeping the application data on the UDM's secondary disk.

To stop ntopng:

`podman stop ntopng`

To start ntopng:

`podman start ntopng`

You will need to do this start command each time the UDM is rebooted or upgraded.  (The ntopng-udm container and its data will survive a UDM firmward update.)  To perform this task automatically at boot time take a look at John D's [on-boot-script project](https://github.com/boostchicken/udm-utilities/tree/master/on-boot-script) on GitHub for a tool that can help you do that.

## Accessing ntopng

Point your browser to https://YOUR.UDM.IP.ADDRESS:3001, for example: https://192.168.1.1:3001

In this container ntopng is configured with a self-signed SSL certificate for HTTPS security.  Your browser will ask you to accept this certificate the first time you access ntopng.

The ntopng documentation can be found [here](https://www.ntop.org/guides/ntopng/).  Note that this container runs the Community Edition of ntopng.

## Viewing the ntopng log

```
podman logs ntopng
```

This command, when entered at the UDM's command prompt, will display the contents of the podman container's console log.  This will include any messages from the ntopng startup process and can be useful when troublshooting startup problems.

## Upgrading the container

Use these commands to upgrade the ntopng-udm to the latest release:
```
podman stop ntopng
podman rm ntopng
podman rmi ntopng-udm
podman pull dlk3/ntopng-udm:latest
podman run -d --net=host --privileged --restart always --name ntopng \
   -v /mnt/data/ntopng/GeoIP.conf:/etc/GeoIP.conf \
   -v /mnt/data/ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
   -v /mnt/data/ntopng/redis.conf:/etc/redis/redis.conf \
   -v /mnt/data/ntopng/lib:/var/lib/ntopng \
   -v /mnt/data/ntopng/redis:/var/lib/redis \
   -v /etc/localtime:/etc/localtime:ro \
   ntopng-udm:latest
```
Remember to use `/mnt/data_ext` as the root for the directories if you are keeping the application data on the UDM's secondary disk.

## Uninstalling the container and all of its data

Use these commands to completely uninstall the ntopng-udm container and all of its data:
```
podman stop ntopng
podman rm ntopng
podman rmi ntopng-udm
rm -fr /mnt/data/ntopng
```
If you have been keeping the application data on the UDM's secondary disk, then use the command `rm -fr /mnt/data_ext/ntopng` as the final step in this process.

## What to do when you forget your ntopng password

1. Access the command shell inside the ntopng container with this command:<br /><br />`podman exec -it ntopng /bin/sh`

2. Issue this command to delete the admin password from the redis db:<br /><br />`redis-cli del ntopng.user.admin.password`  

3. Exit the ntopng container shell with the `exit` command or by pressing Ctrl-D.

4. Restart the container with this command:<br /><br />`podman restart ntopng`  

5. When you reconnect your browser you will be able to login using the default `admin` userid and `admin` password, which you will promptly be prompted to change.
