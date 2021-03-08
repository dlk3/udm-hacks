#!/bin/sh

WAN_IF='eth8'
OPENVPN_PORT='1194'

#  This function inserts and deletes the iptables rules we need.
#
#  New rules are "inserted" at the top of their respective chains so, if order is important, 
#  rules need to be issued in reverse order (bottom-to-top) inside this function.
function iptables_rules () {
    #  Open the OpenVPN port on the WAN interface
    iptables $1 UBIOS_WAN_LOCAL_USER -i $WAN_IF -p udp --dport $OPENVPN_PORT -m conntrack --ctstate NEW -j RETURN
}

#  This function prevents duplicate iptables rules being put into the chains
function iptables () {
    ACTION=$(echo "$*" | sed 's/.*\(-I\|-D\) .*/\1/')
    TEST=$(echo "$*" | sed 's/\(.*\)-I\|-D \(.*\)/\1-C \2/')
    if [ "$ACTION" == "-D" ]; then
        eval "/usr/sbin/iptables $TEST &>/dev/null" && eval "/usr/sbin/iptables $*"
    else
        eval "/usr/sbin/iptables $TEST &>/dev/null" || eval "/usr/sbin/iptables $*"
    fi
    [ $? -eq 0 ] || echo "\"iptables $*\" command failed"
}

#  Get the PID of any OpenVPN process that's running right now
PID=$(ps -ef | grep "/usr/sbin/[o]penvpn" | awk '{print $1 }')

case "$1" in
    "start"|"")
	[ ! -z "$PID" ] && echo 'OpenVPN is already running' && exit 1
        iptables_rules "-I"
        /usr/sbin/openvpn --daemon --config /mnt/data/openvpn/server/server.conf
        ;;
    "stop")
	[ -z "$PID" ] && echo 'OpenVPN is not running' && exit 1
        iptables_rules "-D"
        kill -sigint $PID
        ;;
    "delete_rules")
        iptables_rules "-D"
        ;;
    *)
        echo "Usage: $0 [start|stop|delete_rules]"
        echo "       If no action is specified, "start" is the default."
        exit 1
        ;;
esac
