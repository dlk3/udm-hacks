#!/bin/sh

#  Allow this script to be run as the "ntopng" command
ln -s $(realpath $0) /usr//bin/ntopng &>/dev/null

# Start existing container
podman start ntopng

#  If that failed, try to start a new container
if [ $? -eq 125 ]; then
    podman run -d --net=host --privileged=true --restart always --name ntopng \
       -v /mnt/data/ntopng/GeoIP.conf:/etc/GeoIP.conf \
       -v /mnt/data/ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
       -v /mnt/data/ntopng/redis.conf:/etc/redis/redis.conf \
       -v /mnt/data/ntopng/lib:/var/lib/ntopng \
       -v /mnt/data/ntopng/redis:/var/lib/redis \
       ntopng-udm:latest
fi
