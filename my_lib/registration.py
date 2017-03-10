#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################


#import inspect
#import os
#import signal
#import socket
#import subprocess
#import sys
import datetime

import urllib
import urllib2

from kivy.logger import Logger

from constants import *
from itools import *

###############################################################
#
# Declarations
#
# ###############################################################


REGISTRATION_URL_ADDRESS = 'http://livebackups.inoteska.sk/'


# ###############################################################
#
# Functions
#
# ###############################################################

def send_regs_request(dst, args):
    "send registration request to obtain licence key"

    t = datetime.datetime.now()
    dt = t.strftime('%Y-%m-%d %H:%M:%S')

    url = dst + 'licences.php'
    values = {'sn' : args[0],
          'email' : args[1],
          'lk' : args[2],
          'date' : dt }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    try:
	response = urllib2.urlopen(req)
	rsp = response.read()
	Logger.debug(whoami()+': dst=%s args=[%s,%s] >> rsp=%s' % (dst, ','.join(args), dt, rsp))
    except URLError as e:
	Logger.warning(whoami()+': dst=%s args=[%s,%s] ERR=%s' % (dst, ','.join(args), dt, str(e)))

#    subprocess.Popen([DBUSCONTROL_SCRIPT, dst] + args)
#    return True
    """
    try:
	proc = subprocess.check_output([DBUSCONTROL_SCRIPT, dst] + args)
	Logger.debug(whoami()+': dst=%s args=[%s]' % (dst, ','.join(args)))
    except subprocess.CalledProcessError, e:
	Logger.warning(whoami()+': dst=%s args=[%s] ERR=%s' % (dst, ','.join(args), e.output))
	return False

    return True
    """


# ##############################################################################

