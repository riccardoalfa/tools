#!/bin/bash

# You can add this function to your ~/.bashrc file (which gets executed at the
# initialization of each bash shell), so that they remains available to use.
# see http://unix.stackexchange.com/questions/9123/is-there-a-one-liner-that-allows-me-to-create-a-directory-and-move-into-it-at-th

# Create a directory and cd into in in one command
mkcd () {
  case "$1" in
    */..|*/../) cd -- "$1";; # that doesn't make any sense unless the directory already exists
    /*/../*) (cd "${1%/../*}/.." && mkdir -p "./${1##*/../}") && cd -- "$1";;
    /*) mkdir -p "$1" && cd "$1";;
    */../*) (cd "./${1%/../*}/.." && mkdir -p "./${1##*/../}") && cd "./$1";;
    ../*) (cd .. && mkdir -p "${1#.}") && cd "$1";;
    *) mkdir -p "./$1" && cd "./$1";;
  esac
}

# Remove all bullshit files and folders created by Ubuntu's graphical interface
# AND .retry files (might be left behind by Ansible procedure)
cleanhome () {
    cd
    if [ -d Desktop ]; then
        rm -rf Desktop
        rm -rf Music
        rm -rf Templates
        rm -rf Videos
        rm -rf Pictures
        rm -rf Documents
        rm -rf Downloads
    fi

    if [ -d Public ]; then
        rm -rf Public
    fi

    if [ -f examples.desktop ]; then
        rm -f examples.desktop
    fi

    rm -f *.retry
}
