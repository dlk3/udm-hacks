#!/bin/sh

cat <<EOF >/etc/cron.d/duckdns
@reboot curl -o /dev/null -s 'https://www.duckdns.org/update?domains=aaaaaaaa&token=xxxxxxxx'
0 * * * * curl -o /dev/null -s 'https://www.duckdns.org/update?domains=aaaaaaaa&token=xxxxxxxx'
EOF
