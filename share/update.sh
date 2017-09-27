#! /bin/bash

# #################################################################################
#
# Indoor system script
#       update files from repository
#
# #################################################################################


## set working dir
cd /root/indoorpy

## clean backups
rm -f backups/*.*

## backup INI file
cp -f indoor.ini backups

## backup sound files
cp -f sounds/ring_* backups

## stash all changes
git reset --hard


## synchronize
#if [ -z "$1" ]; then
##    git fetch https://github.com/isra67/indoorpy.git master
#    git fetch https://github.com/isra67/indoorpy.git
#else
##    git fetch https://isra67:$1@github.com/isra67/indoorpy.git master
#    git fetch https://isra67:$1@github.com/isra67/indoorpy.git
#fi
#git reset --hard ##gh/master

if [ -z "$1" ]; then
#    git pull --rebase https://github.com/isra67/indoorpy.git master
    git pull --rebase https://github.com/isra67/indoorpy.git
else
#    git pull --rebase https://isra67:$1@github.com/isra67/indoorpy.git master
    git pull --rebase https://isra67:$1@github.com/isra67/indoorpy.git
fi
git clean -dn


## remove unnecessary files
rm -f my_lib/*.py

## restore INI file
cp backups/indoor.ini /root/indoorpy

## restore sound files
cp backups/ring_* /root/indoorpy/sounds
