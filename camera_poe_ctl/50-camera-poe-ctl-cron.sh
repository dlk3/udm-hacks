#!/bin/sh

#  Add custom cron job

#  Run cron job command at boot time
/mnt/data/camera_poe_ctl/camera_poe_ctl

#  Create my custom cron.d file
cat <<EOF >/etc/cron.d/camera-poe-ctl
*/10 * * * * /mnt/data/camera_poe_ctl/camera_poe_ctl
EOF

#  Restart the cron daemon to pick up my changes
/etc/init.d/crond restart
