#!/bin/bash

echo Starting redis ...
/usr/bin/redis-server /etc/redis/redis.conf

echo 'Running geoipupdate ...'
/usr/bin/geoipupdate

#  FIXME: Even though these settings are set here, it doesn't prevent
#  oversize packet segementation problems, i.e., "invald packet received"
#  messages in the ntopng log.
#
#  Parse the interface name(s) out of the ntopng config file and
#  turn off oversize packet handling on each.
LIST=$(grep -e "^\s*-i=" /etc/ntopng/ntopng.conf | cut -d"=" -f2)
for IF in $LIST; do
    ethtool -K $IF gro off gso off tso off
done

echo Starting ntopng ..
/usr/local/bin/ntopng /etc/ntopng/ntopng.conf
