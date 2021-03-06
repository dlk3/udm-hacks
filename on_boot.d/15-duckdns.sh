#!/bin/sh

cat <<EOF >/etc/cron.d/duckdns
@reboot curl -o /dev/null -s 'https://www.duckdns.org/update?domains=snaggy&token=MY_TOKEN'
0 * * * * curl -o /dev/null -s 'https://www.duckdns.org/update?domains=snaggy&token=MY_TOKEN'
EOF
