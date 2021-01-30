#!/bin/sh

podman run -d --net=host --restart always \
   --name ntopng \
   -v `pwd`/data/ntopng/myGeoIP.conf:/etc/GeoIP.conf \
   -v `pwd`/data/ntopng/myntopng.conf:/etc/ntopng/ntopng.conf \
   -v `pwd`/data/ntopng/redis.conf:/etc/redis/redis.conf \
   -v `pwd`/data/ntopng/lib:/var/lib/ntopng \
   ntopng-udm:20210129
