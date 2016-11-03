#!/bin/bash

# useful variables obtained from _mount_drives.sh
#   mount_iso   -> path where the ISOs drive is mounted
#   sdx_iso     -> device letter (sdX) for ISOs drive, empty string if missing
#   sdx_flash   -> array of device letters (sdX) of all other usb devices
source _mount_drives.sh

if [ -n "$sdx_iso" ]; then
    echo "--------------"
    res=$(ls -1 "$mount_iso"/ISO | sort -n)
    printf "$res\n"
    echo "--------------"
else
    echo "ERROR - ISOs drive not found!"
fi