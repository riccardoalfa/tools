#!/bin/bash

# useful variables obtained from _mount_drives.sh
#   mount_iso   -> path where the ISOs drive is mounted
#   sdx_iso     -> device letter (sdX) for ISOs drive, empty string if missing
#   sdx_flash   -> array of device letters (sdX) of all other usb devices
thisfile=$(readlink -f "$0")
thisfilepath=$(dirname "$thisfile")
source "$thisfilepath"/_mount_drives.sh

source "$thisfilepath"/_list_iso.sh
echo

if [ -n "$sdx_iso" ]; then
    if [ -z "$1" ]; then
        read -p "Which image NUMBER would you like to DELETE? " iso_id
    else
        iso_id="$1"
    fi

    # add initial zeros to reach length of 6 digits
    iso_id=$(printf "%06d\n" "$iso_id")

    iso_file=$(ls -1 "$mount_iso/ISO/$iso_id-"* | head -1)
    # oddly enough  $iso_file here already includes the full path

    if [ -f "$iso_file" ]; then
        read -p "FOREVER remove $iso_file. Are you REALLY sure? [Y/N]" confirm
        if [ "$confirm" = "Y" ] || [ "$confirm" = "YES" ] || [ "$confirm" = "y" ] || [ "$confirm" = "yes" ]; then
            rm -rf "$iso_file"
            echo REMOVED
        else
            echo Canceled, no files were harmed
        fi
    else
        echo "ERROR - ISO not found"
    fi

else
    echo "ERROR - Writing requires ISOs drive connected"
fi