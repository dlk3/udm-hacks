#!/bin/sh

echo "search localdomain" >/etc/resolv.conf
echo "nameserver 192.168.1.40" >>/etc/resolv.conf
echo "nameserver 192.168.1.21" >>/etc/resolv.conf
