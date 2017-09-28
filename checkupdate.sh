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

    echo "equal"

else

    echo "different"

fi

