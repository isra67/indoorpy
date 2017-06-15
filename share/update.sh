#! /bin/bash

# #################################################################################
#
# Indoor system script
#       update files from repository
#
# #################################################################################

## working dir
cd /root/indoorpy

## clean backups
rm -f backups/*.*

## backup INI file
cp -f indoor.ini backups

## backup sound files
cp -f sounds/ring_* backups

## synchronize
git fetch --all
git reset --hard origin/master
git clean -dn

## remove unnecessary files
rm -f my_lib/*.py

## restore INI file
cp backups/indoor.ini /root/indoorpy

## restore sound files
cp backups/ring_* /root/indoorpy/sounds
