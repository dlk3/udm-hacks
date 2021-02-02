#!/bin/sh

#  Allow this script to be run as the "ntopng" command
ln -s $(realpath $0) /usr//bin/ntopng &>/dev/null

# Start existing container
echo "Trying to start existing container instance ..."
podman start ntopng

#  If that failed, try to start a new container
if [ $? -eq 125 ]; then
    echo "Trying to start a new container instance ..."
    podman run -d --net=host --privileged --restart always --name ntopng \
       -v /mnt/data_ext/ntopng/GeoIP.conf:/etc/GeoIP.conf \
       -v /mnt/data_ext/ntopng/ntopng.conf:/etc/ntopng/ntopng.conf \
       -v /mnt/data_ext/ntopng/redis.conf:/etc/redis/redis.conf \
       -v /mnt/data_ext/ntopng/lib:/var/lib/ntopng \
       -v /mnt/data_ext/ntopng/redis:/var/lib/redis \
       ntopng-udm:latest
fi
