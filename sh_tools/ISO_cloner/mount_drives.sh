#!/usr/bin/env bash

# this file can be set to run at boot, io properly searches for and mounts
# the hard drive and ssd card reader
# it searches for and Alfa usb key (must have a file called "alfa_usb_run.sh"
# on its root), and, if found, executes it (in a subshell)

usb_mount="/mnt/ISO"
usb_id_file="ISO_cloner.sh"
declare -a device_letters=("a" "b" "c" "d" "e" "f" "g")

if [ ! -d "$usb_mount" ]; then
    mkdir "$usb_mount"
fi

for x in "${device_letters[@]}"; do
    # echo "testing SD$x -> sd$x"1
    if [ -n $(ls /dev/ | grep "sd$x"1) ]; then
        mount "/dev/sd$x"1/ "$usb_mount"
        if [ ! -f "$usb_mount/$usb_id_file" ]; then
            umount "$usb_mount"
        fi
    fi
done
