#!/bin/sh

DATADIR="/mnt/data/ntopng"

#  Allow this script to be run as the "ntopng" command
ln -s /mnt/data/on_boot.d/15-start-ntopng.sh /usr/bin/ntopng &>/dev/null

# Start existing container
echo "Trying to start existing container instance ..."
podman start ntopng

#  If that failed, try to start a new container
if [ $? -eq 125 ]; then
    echo "Trying to start a new container instance ..."
    podman run -d --net=host --privileged --restart always --name ntopng \
       -v ${DATADIR}/GeoIP.conf:/etc/GeoIP.conf \
       -v ${DATADIR}/ntopng.conf:/etc/ntopng/ntopng.conf \
       -v ${DATADIR}/redis.conf:/etc/redis/redis.conf \
       -v ${DATADIR}/lib:/var/lib/ntopng \
       -v ${DATADIR}/redis:/var/lib/redis \
       -v /etc/localtime:/etc/localtime:ro \
       -v ${DATADIR}/ssl/ntopng-cert.pem:/usr/share/ntopng/httpdocs/ssl/ntopng-cert.pem \
       ntopng-udm:latest
fi
