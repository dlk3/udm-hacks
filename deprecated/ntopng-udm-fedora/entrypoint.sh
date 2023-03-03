#!/bin/bash

echo 'Starting redis-server ...'
/usr/bin/redis-server /etc/redis/redis.conf

echo 'Updating GeoIP data using geoipupdate ...'
/usr/bin/geoipupdate

#  FIXME: Even though these settings are set here, it doesn't prevent
#  oversize packet segementation problems, i.e., "invald packet received"
#  messages in the ntopng log like it's supposed to.
#
#  Parse the interface name(s) out of the ntopng config file and
#  turn off oversize packet handling on each.
LIST=$(grep -e "^\s*-i=" /etc/ntopng/ntopng.conf | cut -d"=" -f2)
for IF in $LIST; do
    ethtool -K $IF gro off gso off tso off
done

echo 'Starting ntopng server ...'
/usr/bin/ntopng /etc/ntopng/ntopng.conf
