#!/bin/sh

cat <<EOF >/etc/cron.d/away-recording
@reboot /usr/bin/podman exec -it unifi-os /data/dlk-udm-hacks/away-recording -q -l /data/dlk-udm-hacks/away-recording.log
*/10 * * * * /usr/bin/podman exec -it unifi-os /data/dlk-udm-hacks/away-recording -q -l /data/dlk-udm-hacks/away-recording.log
EOF
