#!/bin/sh

echo >>/etc/profile.d/aliases.sh
echo "# Added by /mnt/data/on_boot.d/05-profile.sh" >>/etc/profile.d/aliases.sh
echo "alias ll='ls -l'" >>/etc/profile.d/aliases.sh
