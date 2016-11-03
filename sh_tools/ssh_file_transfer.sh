#!/bin/bash

DEF_PORT=6902

function f_send {

}

function f_start {

}

function f_stop {

}


if [ "$1" == "send" ]; then
    (f_send)
elif [  "$1" == "start" ]; then
    (f_start)
elif [ "$1" == "stop" ]; then
    (f_stop)
else
    printf "\n\nSyntax: ssh_file_transfer start|stop [port]" 1>&2
    printf "\nSyntax: ssh_file_transfer scan [as_ip] [Dt] [port]\n\n" 1>&2
fi
