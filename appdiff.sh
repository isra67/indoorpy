#! /bin/bash

# #################################################################################
#
# Indoor system script
#       autoupdate files from repository
#
# #################################################################################


## working repository
if [ -z "$1" ]; then
    REPO="inoteska"
else
    REPO="$1"
fi


## working dir
cd /root/indoorpy


VER_LOCAL=`git log -1 | grep commit | awk '{print $2}'`
VER_REMOTE=`git ls-remote https://github.com/$REPO/indoorpy.git | grep HEAD | cut -f 1`

if [ "$VER_LOCAL" == "$VER_REMOTE" ]
then

    echo "Nothing to do"

else

    ## synchronize
#    if [ -z "$1" ]; then
#        ./share/update.sh
#    else
#        ./share/update.sh $1
#    fi
    ./share/update.sh $REPO

    sync

    PID=`ps aux | grep -i 'python pjindoor' | grep -iv 'grep ' | sed 's/\s\+/ /g' | cut -d' ' -f 2`
    kill $PID

fi

