#!/bin/bash

# Ric101 - ssh responder - v. 1.0.1
#
# Options: start | stop | scan
#
# start
# This AMAZING script creates a demon which listens
# to nc (NetCat) calls on selected port (default 8069)
#
# it is recommended to run the script in background, i.e.:
#       ssh_responder_demon start [port] &
#
# when called via nc, it responds with a string containing
# - the IP and MAC addresses of ALL found network cards (ethX and wlanX).
# MAC addresses are shown both in full and compact (without colons ':')
# - the content of and INFO_FILE and and a SOFTWARE_VERSION_FILE,
# if present on the machine on which the script runs. This allows
# to add data to better understand/identify the machine, and keep
# track of current version of software currently running on the machine
# (not the linux version, the actual software you use the machine for,
# ie firmware version for an embedded machine)
#
# the INFO_FILE and SOFTWARE_VERSION_FILE are searched in 2 locations,
# specified in the settings, ideally first in the user's home and than
# globally (root). Currently:
#   INFO_FILE="$HOME/.ssh_responder_demon.info"
#   INFO_FILE_ROOT="/etc/ssh_responder_demon.info"
#   SOFTWARE_VERSION_FILE="$HOME/.ssh_responder_demon_system_version.info"
#   SOFTWARE_VERSION_FILE_ROOT="/etc/ssh_responder_demon_system_version.info"
#
# scan
# This AMAZING script using nc (NetCat) calls on selected port (default 8069),
# tries to query ssh responder demon's on all (max 256) devices connected
# in the current LAN of EACH network port (ethX wlanX) present on the
# machine she script from which the script is launched.
#
# For handiness, it redirects all activity output to stderr, and keeps
# the stdout to print the responses from the devices
#
# can be called with 2 optional arguments
# - number of seconds for nc calls timeout
# - port to use to try and and query remote (on same LAN) devices
#

DEF_PORT=6901
INFO_FILE="$HOME/.ssh_responder_demon.info"
INFO_FILE_ROOT="/etc/ssh_responder_demon.info"
SOFTWARE_VERSION_FILE="$HOME/.ssh_responder_demon_system_version.info"
SOFTWARE_VERSION_FILE_ROOT="/etc/ssh_responder_demon_system_version.info"
TMP_FILE="/tmp/ssh_responder_demon.tmp"
ARG1="$1"
ARG2="$2"
ARG3="$3"
ARG4="$4"

function f_scan {
    LOCAL_IPS=(${ARG2:-$(hostname -I)})
    DT=${ARG3:-1}
    LISTEN_PORT=${ARG4:-"$DEF_PORT"}

    RET=""
    for LOCAL_IP in "${LOCAL_IPS[@]}"; do
        IP_X=$(printf "$LOCAL_IP" | cut -d"." -f1-3)
        printf "\n\nUSING $IP_X" 1>&2
        IPS=$(nmap -n -T4 -p "$LISTEN_PORT" "$IP_X".0/24 -oG - | grep "$LISTEN_PORT/open/tcp" | grep -E -o '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
        IPS=($IPS)

        sleep 1
        for IP in "${IPS[@]}"; do
            printf "\ntrying: $IP" 1>&2
            DATA=$(nc -w "$DT" "$IP" "$LISTEN_PORT")
            if [ -n "$DATA" ]; then
                # reread to get updated data!!
                sleep 1
                DATA=$(nc -w "$DT" "$IP" "$LISTEN_PORT")
                RET="$RET\n$DATA"
                printf " ...!" 1>&2
            else
                printf " ...X" 1>&2
            fi
        done
    done

    printf "\n\n$RET\n\n"
}

function f_start {
    LISTEN_PORT=${ARG2:-"$DEF_PORT"}

    if [ -f $TMP_FILE ]; then
        PID=$(head -1 $TMP_FILE)
        kill -9 $PID &> /dev/null
        # removing file is problematic if has been created by root, set it to empty value instead
        : > $TMP_FILE
        printf "\n\nsh_responder_demon_restarted!\n" 1>&2
    else
        touch $TMP_FILE
        chmod 777 $TMP_FILE
    fi
    printf "$BASHPID\n" > $TMP_FILE
    printf "\n\n TMP file used to track the PID of the sh_responder_demon, so it can be easily stopped" >> $TMP_FILE

    LAN_PORTS="$(ifconfig -a | sed 's/[ \t].*//;/^\(lo\|\)$/d' | tr '\n' ' ' )"
    LAN_PORTS=($LAN_PORTS)
    while true
    do
        RET=""

        if [ -f $INFO_FILE ]; then
          INFO="$(cat $INFO_FILE)"
          RET="$RET\nINFO[$USER]:\n$INFO"
        elif [ -f $INFO_FILE_ROOT ]; then
          INFO="$(cat $INFO_FILE_ROOT)"
          RET="$RET\nINFO[root]:\n$INFO"
        else
          INFO=" N/A"
          RET="$RET\nINFO:$INFO"
        fi

        if [ -f $SOFTWARE_VERSION_FILE ]; then
          VERSION=" $(cat $SOFTWARE_VERSION_FILE)"
          RET="$RET\n\nVERSION[$USER]: $VERSION"
        elif [ -f $SOFTWARE_VERSION_FILE_ROOT ]; then
          VERSION=" $(cat $SOFTWARE_VERSION_FILE_ROOT)"
          RET="$RET\n\nVERSION[root]: $VERSION"
        else
          VERSION=" N/A"
          RET="$RET\n\nVERSION: $VERSION"
        fi

        for p in "${LAN_PORTS[@]}"
        do
            MACADDR="$(cat /sys/class/net/$p/address)"
            SIMPLEMACADDR="$(cat /sys/class/net/$p/address | tr -d ':')"
            IP="$(ifconfig $p | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
            RET="$RET\n"
            RET="$RET\nIP_$p=$IP"
            RET="$RET\nMACADDR_$p=$MACADDR=$SIMPLEMACADDR"
        done

        RET="$RET\n\n - - - - - - - - - - - - - - - - -\n\n"

        # flush existing nc if running on same port
        nc -w 1 127.0.0.1 $LISTEN_PORT > /dev/null

        #printf "$RET"
        printf "$RET" | nc -l $LISTEN_PORT
    done
}

function f_stop {
    LISTEN_PORT=${ARG2:-"$DEF_PORT"}

    if [ -f $TMP_FILE ]; then
        PID=$(head -1 $TMP_FILE)
        kill -9 $PID &> /dev/null
        # removing file is problematic if has been created by root, set it to empty value instead
        : > $TMP_FILE
        printf "\n\nsh_responder_demon stopped!\n\n" 1>&2
    else
        printf "\n\nsh_responder_demon was already not running\n\n" 1>&2
    fi
    # flush existing nc if running on same port
    nc -w 1 127.0.0.1 $LISTEN_PORT > /dev/null
}

# launch proper command in a (subshell - works even when sourcing this file)
if [ "$1" == "scan" ]; then
    (f_scan)
elif [  "$1" == "start" ]; then
    (f_start)
elif [ "$1" == "stop" ]; then
    (f_stop)
else
    printf "\n\nSyntax: sh_responder start|stop [port]" 1>&2
    printf "\nSyntax: sh_responder scan [as_ip] [Dt] [port]\n\n" 1>&2
fi

#
# Version 1.0.1 updates
#    - is now subshell-robust (can be called as executable or sourced)
#    - code reformatted for better readability
#    - uses nmap in plce of old arp-scan (both are good actually, changed
#    for debugging purposes)
#    - added (first) argument for scan, to specify (fake) ip to get subnet from
#    (for example if in a nat-ed network, you can access a subnet you do not
#    belong to, such as 192.168.15.00 will try all 192.168.15.XXX
#