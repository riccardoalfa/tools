#!/bin/bash

# this file can be set to run at boot, io properly searches for and mounts
# the hard drive and ssd card reader
# it searches for an Alfa usb key (must have a file called "ISO_cloner.sh"
# on its root), and, if found, executes it (in a subshell)

if [ "$(whoami)" != "root" ]; then
    echo "ERROR!! Must be root"
    echo
fi

mount_tmp="/mnt/tmp"
mount_iso="/mnt/ISO"
iso_size="15G"

usb_id_file="Alfa_ISO_repo.sh"
declare -a device_letters=("a" "b" "c" "d" "e" "f" "g" "h" "i" "j" "k" "l" "m" "n")

mkdir -p "$mount_tmp" > /dev/null 2>&1
mkdir -p "$mount_iso" > /dev/null 2>&1

sdx_iso=""
declare -a sdx_flash=()
for x in "${device_letters[@]}"; do
    # echo "testing SD$x -> sd$x"1
    present=$(ls /dev/ | grep sd"$x"1)
    if [ -n "$present" ]; then
        # echo "into SD$x -> sd$x"1
        umount "$mount_tmp" > /dev/null 2>&1
        mount "/dev/sd$x"1 "$mount_tmp" > /dev/null 2>&1
        mount_result="$?"
        if [ "$mount_result" = "0" ] && [ -f "$mount_tmp/$usb_id_file" ]; then
            echo ISOs drive found in "sd$x"1!
            sdx_iso="$x"
            mount "/dev/sd$x"1 "$mount_iso" > /dev/null 2>&1
            mkdir -p "$mount_iso/ISO" > /dev/null 2>&1
        fi
        umount "$mount_tmp" > /dev/null 2>&1
    fi
done

for x in "${device_letters[@]}"; do
    present=$(ls /dev/ | grep "sd$x")
    if [ -n "$present" ] && [ "$x" != "$sdx_iso" ]; then
        sdx_flash+=("$x")
    fi
done
