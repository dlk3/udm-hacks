#!/bin/sh

#  Add custom cron jobs

DUCKDNS_HOSTNAME=""
DUCKDNS_TOKEN=""

#  Run cron job commands at boot time
curl -o /dev/null -s "https://www.duckdns.org/update?domains=$DUCKDNS_HOSTNAME&token=$DUCKDNS_TOKEN"
/usr/bin/podman exec -it unifi-os /data/dlk-udm-hacks/away-recording -q

#  Create my custom cron.d file
cat <<EOF >/etc/cron.d/udm-hacks-cronjobs
0 * * * * curl -o /dev/null -s "https://www.duckdns.org/update?domains=$DUCKDNS_HOSTNAME&token=$DUCKDNS_TOKEN"
*/10 * * * * /usr/bin/podman exec -it unifi-os /data/dlk-udm-hacks/away-recording -q
EOF

#  Restart the cron daemon to pick up my changes
/etc/init.d/crond restart
