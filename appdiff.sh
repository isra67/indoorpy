#! /bin/bash

# #################################################################################
#
# Indoor system script
#       autoupdate files from repository
#
# #################################################################################


## working dir
cd /root/indoorpy


VER_REMOTE=`git ls-remote https://github.com/isra67/indoorpy.git | grep master | cut -f 1`
GITDIFF=`git cherry -v | grep $VER_REMOTE`

if [ "$GITDIFF" != "" ]
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

