# Running ntopng On The Unifi Ultimate Dream Machine (UDM)

This container image can be used to run the ntopng network traffic flow analysis tool on a Unifi Ultimate Dream Machine.  

This project was inspired by Carlos Talbot's  [tusc/ntopng-udm project](https://github.com/tusc/ntopng-udm).  This container differs in the following ways:

1. A Fedora container is used, providing repository packages that are more up-to-date than those provided by Ubuntu.
2. The current GitHub version of ntopng is used, as it existed when the container was built, not the latest stable branch.
3. The libpcap-supported features of ntopng are enabled.
4. A more up-to-date version of the geoipupdate tool is used.
5. The start-up process for the container has been modified to ignore geoipupdate failures.

# Running The Container On The UDM

## Creating the ntopng persistent data directories

Access the UDM as the root user via ssh.  You will be placed into the system's root directory.  The runtime environment for the container can be established by entering the following commands.

```
mkdir -p /mnt/data/ntopng/redis
mkdir -p /mnt/data/ntopng/lib
curl -Lo /mnt/data/ntopng/GeoIP.conf http://...
curl -Lo /mnt/data/ntopng/ntopng.conf http://...
curl -Lo /mnt/data/ntopng/redis.conf http://...
```

## Enabling GeoIP support

If you want GeoIP support, i.e., you want country flags displayed next to the hosts and IP addresses in the ntopng user interface, then follow [these instructions](https://github.com/ntop/ntopng/blob/dev/doc/README.geolocation.md) on the ntopng web site to create a free account and register for an API key.  These must be placed into the /mnt/data/ntopng/GeoIP.conf file in the container's data directory.

## Installing The Container

Run this command to copy the container onto the UDM:

`podman pull dlk3/ntopng-udm:latest`
 
## Running the container

Run this command to start the container:
```
podman run -d --net=host --restart always \
   --name ntopng \
   -v /mnt/data/ntopng/GeoIP.conf:/etc/GeoIP.conf \
   -v /mnt/data/ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
   -v /mnt/data/ntopng/redis.conf:/etc/redis/redis.conf \
   -v /mnt/data/ntopng/lib:/var/lib/ntopng \
   ntopng-udm:latest
```
## Accessing ntopng

Point your browser to https://YOUR.UDM.IP.ADDRESS:3001, for example: hppts://192.168.1.1:3001

The ntopng documentation can be found [here](https://www.ntop.org/guides/ntopng/).  Note that this container runs the Community Edition of ntopng.
