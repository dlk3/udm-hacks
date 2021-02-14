#!/bin/sh

WAN_IF='eth8'
LAN_IF='br0'

function iptables_rules () {
    [ -z "$1" ] && return 1
    # Allow incoming traffic to the OpenVPN port
    /usr/sbin/iptables $1 INPUT -p udp --dport 1194 -m state --state NEW -s 0.0.0.0/0 -j ACCEPT
    # Allow incoming traffic to the TUN interface
    /usr/sbin/iptables $1 INPUT -i tun0 -j ACCEPT
    # Allow TUN interface traffic to be forwarded to any other interface
    /usr/sbin/iptables $1 FORWARD -i tun0 -j ACCEPT
    # Allow LAN hosts to send traffic back to the TUN interface if they have an established connection
    # Add similar rules for other VLAN interfaces if required
    /usr/sbin/iptables $1 FORWARD -i $LAN_IF -o tun0 -m state --state RELATED,ESTABLISHED -j ACCEPT
    # Allow outbound traffic from the TUN interface
    /usr/sbin/iptables $1 OUTPUT -o tun0 -j ACCEPT
    # Block any traffic between VPN clients 
    # The subnet definition used here must match the that defined in the OpenVPN server.conf
    /usr/sbin/iptables $1 FORWARD -i tun0 -s 10.8.0.0/24 -d 10.8.0.0/24 -j DROP
}

#  Get the PID of any OpenVPN process that's running now
PID=$(ps -ef | grep "/usr/sbin/[o]penvpn" | awk '{print $1 }')

case "$1" in
    "stop")
	[ -z "$PID" ] && echo 'OpenVPN is not running' && exit 1
        kill -sigint $PID
        iptables_rules "-D"
        ;;
    "delete_rules")
        iptables_rules "-D"
        ;;
    "start"|"")
	[ ! -z "$PID" ] && echo 'OpenVPN is already running' && exit 1
        iptables_rules "-I"
	#  When OpenVPN runs as a daemon its output is logged in /var/log/messages
        /usr/sbin/openvpn --daemon --config /mnt/data/openvpn/server/server.conf
        ;;
    *)
        echo "Usage: $0 [start|stop|delete_rules]"
        echo "       If no action is specified, "start" is the default."
        ;;
esac
