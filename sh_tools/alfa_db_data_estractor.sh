#!/bin/bash

DEF_PORT=6902
nc_dest_ip="$1"
dest_dir_ending="$2"
LISTEN_PORT=${3:-"$DEF_PORT"}

if [ -n "$nc_dest_ip" ]; then

    dirname="db_data$dest_dir_ending"
    fulldirname="/var/lib/postgresql/db_data$dest_dir_ending"

    sudo -u postgres mkdir -p "$fulldirname"

    echo reading...
    sudo -u postgres whoami
    sudo -u postgres psql -d alfakiosk -c "COPY client_alarm TO '$fulldirname/client_alarm.dat'"
    sudo -u postgres psql -d alfakiosk -c "COPY client_dispensationqueue TO '$fulldirname/client_dispensationqueue.dat'"
    sudo -u postgres psql -d alfakiosk -c "COPY client_event TO '$fulldirname/client_event.dat'"

    cd "$fulldirname"/..
    tar czf "/home/admin/db_data.tgz" "$dirname"

    nc 192.168.0.1 6902 < /home/admin/db_data.tgz

    sudo -u postgres rm -rf "$fulldirname"
    rm /home/admin/db_data.tgz
    echo "fatto il misfatto"

else
    echo
    echo "usage: alfa_db_data_estractor.sh <nc_dest_ip> <dest_dir_ending> [<port>]"
fi