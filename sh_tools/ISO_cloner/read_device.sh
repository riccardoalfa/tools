#!/bin/bash

# useful variables obtained from _mount_drives.sh
#   mount_iso   -> path where the ISOs drive is mounted
#   sdx_iso     -> device letter (sdX) for ISOs drive, empty string if missing
#   sdx_flash   -> array of device letters (sdX) of all other usb devices
thisfile=$(readlink -f "$0")
thisfilepath=$(dirname "$thisfile")
source "$thisfilepath"/_mount_drives.sh

if [ -n "$sdx_iso" ] && [ "${#sdx_flash[@]}" = "1" ]; then
    if [ -z "$1" ]; then
        echo
        read -p "How would you like to call this Image? " iso_name
    else
        iso_name="$1"
    fi

    iso_id=$(ls -1 "$mount_iso"/ISO | sort -n | tail -1 | cut -c-6)
    if [ -z "$iso_id" ]; then
        iso_id="000000"
    fi
    iso_id_=$(echo "$iso_id" | sed 's/^0*//')
    iso_id_=$((iso_id_ + 1))
    iso_id=$(seq -w "$iso_id" "$iso_id_" | tail -1)
    datetime="$(date +%Y-%m-%d@%H:%M)"
    iso_file="$mount_iso/ISO/$iso_id---$datetime---$iso_name.iso"
    if [ ! -f "$iso_file" ]; then
        pv -s "$iso_size" "/dev/sd${sdx_flash[0]}" | dd of="$iso_file" bs=1M
    else
        echo "ERROR - ISO file already exists!"
    fi

else
    echo "ERROR - Reading requires ISOs drive and EXACTLY one Flash connected"
fi