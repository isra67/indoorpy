#! /bin/bash

# #################################################################################
#
# Indoor system script
#       autoupdate files from repository
#
# #################################################################################


## PATH=/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin


BRANCH="master"


## working dir
cd /root/indoorpy

GITDIFF=`git diff --name-only --ignore-space-change gh/$BRANCH`
len=${#GITDIFF}

if [ $len -lt 3 ]
then

    echo "Nothing to do"

else

    ## synchronize
    if [ -z "$1" ]; then
        ./share/update.sh
    else
        ./share/update.sh $1
    fi

    PID=`ps aux | grep -i 'python pjindoor' | grep -iv 'grep ' | sed 's/\s\+/ /g' | cut -d' ' -f 2`
    kill $PID

fi

