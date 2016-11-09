#!/bin/bash

# useful variables obtained from _mount_drives.sh
#   mount_iso   -> path where the ISOs drive is mounted
#   sdx_iso     -> device letter (sdX) for ISOs drive, empty string if missing
#   sdx_flash   -> array of device letters (sdX) of all other usb devices
source _mount_drives.sh

if [ -n "$sdx_iso" ] && [ ! "${#sdx_flash[@]}" = "0" ]; then
    if [ -z "$1" ]; then
        source list_iso.sh
        read -p "Which image NUMBER would you like to write? " iso_id
    else
        iso_id="$1"
    fi

    iso_file=$(ls -1 "$mount_iso/ISO/$iso_id-"* | head -1)
    # oddly enough  $iso_file here already includes the full path

    x_last=${sdx_flash[-1]}         # save last element of array
    unset sdx_flash[${#sdx_flash[@]}-1]     # remove last element of array
    if [ ${#sdx_flash[@]} -eq 0 ]; then
        # if only one destination
        write_cmd="pv -s 16G $iso_file | dd of=/dev/sd$x bs=1M"
    else
        # if multiple destinations
        write_cmd="pv -s 16G $iso_file | tee "
        for x in "${sdx_flash[@]}"
        do
            write_cmd="$write_cmd >(dd of=/dev/sd$x bs=1M)"
        done

        write_cmd="$write_cmd | dd of=/dev/sd$x_last bs=1M"
    fi

    eval $write_cmd

else
    echo "ERROR - Writing requires ISOs drive and AT LEAST one Flash connected"
fi