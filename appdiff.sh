#! /bin/bash

# #################################################################################
#
# Indoor system script
#       autoupdate files from repository
#
# #################################################################################


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
    ./share/update.sh

    PID=`ps aux | grep -i 'python pjindoor' | grep -iv 'grep ' | sed 's/\s\+/ /g' | cut -d' ' -f 2`
    kill $PID

fi

