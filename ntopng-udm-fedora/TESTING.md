# Building And Testing The Container Locally

This section outlines the process I use to build and test the container on a x86_64 workstation, before I build it for the UDM which is an arm64 system.

## Building the ntopng RPM package

I use the Fedora COPR repository to build and distribute the ntopng RPM file that the Dockerfile installs into the ntopng-udm container.  The files that I use to build that RPM in COPR are in this GitHub repository in the folder called [ntopng-udm-fedora/copr](https://github.com/dlk3/udm-hacks/tree/master/ntopng-udm-fedora/copr)  Both an x86_64 and arm64 (aarch64) version of the RPM need to be built in COPR.

## Building the container

A Dockerfile is provided in this project that builds the container once the RPM is available.  It can be built on a x86_64 workstation for testing purposes using one of the follwing commands, from within the folder which contains the Dockerfile:

```
sudo podman build -t ntopng-udm:latest .
sudo docker build -t ntopng-udm:latest .
```

## Creating the ntopng persistent data directories for local testing

The directories and files needed  for local testing of the container can be created with the following commands:

```
mkdir -p /tmp/ntopng/redis
mkdir -p /tmp/ntopng/lib
curl -Lo /tmp/ntopng/GeoIP.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm-fedora/data/ntopng/GeoIP.conf
curl -Lo /tmp/ntopng/ntopng.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm-fedora/data/ntopng/ntopng.conf
curl -Lo /tmp/ntopng/redis.conf https://github.com/dlk3/udm-hacks/raw/master/ntopng-udm-fedora/data/ntopng/redis.conf
```

You will need to change the network interface specified in /tmp/data/ntopng.conf to match the local system.

## Enabling GeoIP support

If you want GeoIP support, i.e., you want geo maps of hosts sending and receiving traffic, then follow [these instructions](https://github.com/ntop/ntopng/blob/dev/doc/README.geolocation.md) on the ntopng web site to create a free account at MaxMind and to register for an API key.  The account and API key values must be placed into the /tmp/ntopng/GeoIP.conf file.

## Running the container

This command starts ntopng running within its container:
```
sudo podman run -d --net=host --privileged --restart always --name ntopng \
   -v /tmp/ntopng/GeoIP.conf:/etc/GeoIP.conf \
   -v /tmp/ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
   -v /tmp/ntopng/redis.conf:/etc/redis/redis.conf \
   -v /tmp/ntopng/lib:/var/lib/ntopng \
   -v /tmp/ntopng/redis:/var/lib/redis \
   -v /etc/localtime:/etc/localtime:ro \
   ntopng-udm:latest
```

## Accessing ntopng

Point your browser to https://localhost:3001

I have configured ntopng with a self-signed SSL certificate for HTTPS access.  Your browser will ask you to accept this certificate the first time you access a new ntopng container.

The ntopng documentation can be found [here](https://www.ntop.org/guides/ntopng/).  Note that this container runs the Community Edition of ntopng.

