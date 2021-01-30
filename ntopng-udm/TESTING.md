# Building And Testing The Container Locally

This section outlines the process I use to build and test the contain on my personal workstation, before I build it for the UDM.

## Building the container

A Dockerfile is provided in this project that builds the container.  It can be built on a workstation for testing purposes using one of these commands:

```
sudo podman build -t ntopng-udm:latest .
sudo docker build -t ntopng-udm:latest .
```

## Creating the ntopng persistent data directories

The runtime environment for the container can be established by entering the following commands from the directory where you wish to store the container's data.

```
mkdir -p /tmp/ntopng/redis
mkdir -p /tmp/ntopng/lib
curl -Lo /tmp/ntopng/GeoIP.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm/data/ntopng/GeoIP.conf
curl -Lo /tmp/ntopng/ntopng.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm/data/ntopng/ntopng.conf
curl -Lo /tmp/ntopng/redis.conf https://github.com/dlk3/udm-hacks/blob/master/ntopng-udm/data/ntopng/redis.conf
```

Change the network interface specified in /tmp/data/ntopng.conf to match the local system.

## Enabling GeoIP support

If you want GeoIP support, i.e., you want country flags displayed next to the hosts and IP addresses in the ntopng user interface, then follow [these instructions](https://github.com/ntop/ntopng/blob/dev/doc/README.geolocation.md) on the ntopng web site to create a free account and register for an API key.  These must be placed into the ntopng/GeoIP.conf file in the container's data directory.

## Running the container

Again, this should be run from the directory where you created the container's data directories.
```
sudo podman run -d --net=host --privileged=true --restart always --name ntopng \
   -v /tmp/ntopng/GeoIP.conf:/etc/GeoIP.conf \
   -v /tmp/ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
   -v /tmp/ntopng/redis.conf:/etc/redis/redis.conf \
   -v /tmp/ntopng/lib:/var/lib/ntopng \
   -v /tmp/ntopng/redis:/var/lib/redis \
   ntopng-udm:latest
```

## Accessing ntopng

Point your browser to https://localhost:3001

In this container ntopng is configured with a self-signed SSL certificate for HTTPS security.  Your browser will ask you to accept this certificate each time you run a new build of the ntopng-udm container.

The ntopng documentation can be found [here](https://www.ntop.org/guides/ntopng/).  Note that this container runs the Community Edition of ntopng.

