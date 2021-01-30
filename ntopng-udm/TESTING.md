# Building And Testing The Container Locally

This section outlines the process I use to build and test the contain on my personal workstation, before I build it for the UDM.

## Building the container

A Dockerfile is provided in this project that builds the container.  It can be built on a workstation for testing purposes using one of these commands:

```
podman build -t ntopng-udm:latest .
docker build -t ntopng-udm:latest .
```

## Creating the ntopng persistent data directories

The runtime environment for the container can be established by entering the following commands from the directory where you wish to store the container's data.

```
mkdir -p ntopng/redis
mkdir -p ntopng/lib
curl -Lo ntopng/GeoIP.conf http://...
curl -Lo ntopng/ntopng.conf http://...
curl -Lo ntopng/redis.conf http://...
```

## Enabling GeoIP support

If you want GeoIP support, i.e., you want country flags displayed next to the hosts and IP addresses in the ntopng user interface, then follow [these instructions](https://github.com/ntop/ntopng/blob/dev/doc/README.geolocation.md) on the ntopng web site to create a free account and register for an API key.  These must be placed into the ntopng/GeoIP.conf file in the container's data directory.

## Running the container

Again, this should be run from the directory where you created the container's data directories.
```
podman run -d --net=host --restart always \
   --name ntopng \
   -v ntopng/GeoIP.conf:/etc/GeoIP.conf \
   -v ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
   -v ntopng/redis.conf:/etc/redis/redis.conf \
   -v ntopng/lib:/var/lib/ntopng \
   ntopng-udm:latest
```

## Accessing ntopng

Point your browser to https://localhost:3001

The ntopng documentation can be found [here](https://www.ntop.org/guides/ntopng/).  Note that this container runs the Community Edition of ntopng.
