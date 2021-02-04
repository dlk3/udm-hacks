#!/bin/sh

cat <<EOF >/etc/cron.d/duckdns
@reboot root curl -o /dev/null -s 'https://www.duckdns.org/update?domains=<HOSTNAME>&token=<ACCESSTOKEN>'
0 */1 * * * root curl -o /dev/null -s 'https://www.duckdns.org/update?domains=<HOSTNAME>&token=<ACCESSTOKEN>'
EOF
