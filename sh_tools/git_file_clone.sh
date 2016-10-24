#!/usr/bin/env bash

# Ric101 - git file clone - v. 1.0.0
#
# This AMAZING script gets a single file from a Git repo (not supported natively)
# It is NOT efficient (downloads whole repo, gets file, deletes repo)
#

DEST="$1"
FILE="$2"
REPO_URL="$3"
REPO_BRANCH="$4"
CHMOD="$5"

if [ -z "$4" ]; then
  echo
  echo "usage: git_file_clone <dest_folder> <name_of_file_to_clone> <git_repo_url> <git_repo_branch> [<perimissions (chmod format)>]"
  echo

else
    git clone $REPO_URL --branch $REPO_BRANCH --single-branch git_file_clone_tmp
    if [ -n "$CHMOD" ]; then
      chmod $CHMOD git_file_clone_tmp/$FILE
    fi
    cp -p git_file_clone_tmp/$FILE $DEST
    rm -rf git_file_clone_tmp
fi
