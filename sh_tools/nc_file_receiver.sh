#!/bin/bash

DEF_PORT=6902
out_path="$1"
out_file_name="$2"
out_file_ext="$3"
LISTEN_PORT=${4:-"$DEF_PORT"}

if [ -n "$out_file_ext" ]; then
    mkdir -p "$out_path"
    cd "$out_path"
    echo
    echo "Listening on port $LISTEN_PORT"
    while true; do
        # build incremental file name for new dest file
        i=0
        while [[ -e "$out_file_name"_"$i.$out_file_ext" ]] ; do
            let i++
        done
        out_file="$out_file_name"_"$i"."$out_file_ext"

        # wait for nc call
        printf "\nnext file: $out_file..."
        nc -l "$LISTEN_PORT" > "tmp.tmp"
        mv tmp.tmp "$out_file"
        printf "saved!"
    done

else
    echo
    echo "starts nc-listening on specified port (default 6902) and"
    echo "saves all received files on specified path and filename (adding"
    echo "a sequential number at the end of the name)"
    echo
    echo "usage: nc_file_receiver.sh <dest_path> <dest_file_name> <dest_file_ext> [<port>]"
    echo "    ie: nc_file_receiver.sh /tmp/myFiles recent_data data"
    echo
fi