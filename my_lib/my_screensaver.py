#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import subprocess


# ###############################################################
#
# Declarations
#
# ###############################################################


# ###############################################################
#
# Body
#
# ###############################################################

def start_screensaver(fname, layerid = '2'):
    myprocess = subprocess.Popen(['omxplayer','--win','0 0 800 480','--live',\
        '--layer',layerid,'-b',fname],\
        stdin = subprocess.PIPE)   ### ,'--loop'
    return myprocess

def stop_screensaver(proc):
    if proc:
        proc.stdin.write('q')
        proc = None

def send_dbus(args):
#    print 'DBUS:', args
    res = ''
    err = ''
    try:
        db = subprocess.Popen(['/usr/local/bin/dbuscontrol.sh'] + args,\
           stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (res, err) = db.communicate()
    except:
        res = ''

    if err:
        res = ''

#    print 'DBUS...', res, err

    return res
