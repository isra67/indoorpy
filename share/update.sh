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
if [ -z "$1" ]; then
    git fetch https://github.com/isra67/indoorpy.git master
else
    git fetch https://isra67:$1@github.com/isra67/indoorpy.git master
fi
git reset --hard gh/master
git clean -dn
if [ -z "$1" ]; then
    git pull --rebase https://github.com/isra67/indoorpy.git master
else
    git pull --rebase https://isra67:$1@github.com/isra67/indoorpy.git master
fi

## remove unnecessary files
rm -f my_lib/*.py

## restore INI file
cp backups/indoor.ini /root/indoorpy

## restore sound files
cp backups/ring_* /root/indoorpy/sounds

## save from cache
sync
