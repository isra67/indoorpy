#! /bin/bash

# #################################################################################
#
# Indoor system script
#       update files from repository
#
# #################################################################################


## working repository
if [ -z "$1" ]; then
    REPO="inoteska"
else
    REPO="$1"
fi


## set working dir
cd /root/indoorpy

## clean backups
rm -f ../tmp/ring_*

## backup INI file
cp -f indoor.ini ../tmp

## backup sound files
cp -f sounds/ring_* ../tmp

## stash all changes
git reset --hard


#if [ -z "$1" ]; then
##    git pull --rebase https://github.com/isra67/indoorpy.git master
#    git pull --rebase https://github.com/isra67/indoorpy.git
#else
##    git pull --rebase https://isra67:$1@github.com/isra67/indoorpy.git master
#    git pull --rebase https://isra67:$1@github.com/isra67/indoorpy.git
#fi
git pull --rebase https://$REPO@github.com/$REPO/indoorpy.git
git clean -dn


## remove unnecessary files
rm -f my_lib/*.py

## restore INI file
cp -f ../tmp/indoor.ini /root/indoorpy

## restore sound files
cp -f ../tmp/ring_* /root/indoorpy/sounds
