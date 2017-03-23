#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

#import datetime

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
REGISTRATION_PATH = 'licences.php'


# ###############################################################
#
# Functions
#
# ###############################################################

def send_regs_request(dst, args):
    "send registration request to obtain licence key"

    #t = datetime.datetime.now()
    dt = getdatetimestr()        #t.strftime('%Y-%m-%d %H:%M:%S')

    url = dst + REGISTRATION_PATH
    values = {'sn' : args[0], 'email' : args[1], 'lk' : args[2], 'date' : dt }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    try:
	response = urllib2.urlopen(req)
	rsp = response.read()
	Logger.info('%s: dst=%s args=[%s,%s] >> rsp=%s' % (whoami(), dst, ','.join(args), dt, rsp))
    except URLError as e:
	Logger.warning('%s: dst=%s args=[%s,%s] ERR=%s' % (whoami(), dst, ','.join(args), dt, str(e)))


# ##############################################################################
