#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import json
import os

from kivy.logger import Logger

from constants import *
from itools import *


###############################################################
#
# Declarations
#
# ###############################################################

PARENT_DIR = '/tmp/' # '/root/indoorpy/logs/'
APP_LOG_TMP_FILE = PARENT_DIR + 'app-log.dat'
SIP_LOG_TMP_FILE = PARENT_DIR + 'sip-log.dat'

MAX_APP_CNT = 1000
MAX_SIP_CNT = 200

app_log = []			# log for last N messages
sip_log = []			# log for last N messages


# ###############################################################
#
# Functions
#
# ###############################################################

def initloggers():
    "Loggers initialization"
    global app_log, sip_log

    Logger.info('%s:' % whoami())

    app_log = []
    sip_log = []

    try:
	with open(APP_LOG_TMP_FILE, 'r') as data_file:
	    app_log = json.load(data_file)
    except: app_log = []

    try:
	with open(SIP_LOG_TMP_FILE, 'r') as data_file:
	    sip_log = json.load(data_file)
    except: sip_log = []

    if app_log == None: app_log = []
    if sip_log == None: sip_log = []


# ##############################################################################

def setloginfo(sipflag=False, msg=''):
    "Save msg to TMP file"
    global app_log, sip_log

    dt = getdatetimestr()

#    print('%s: dt=%s sipflag=%r msg=%s'% (whoami(), dt, sipflag, msg))

    if sipflag:
	sip_log.append(msg)
	if len(sip_log) > MAX_SIP_CNT: sip_log.pop(0)
	filename = SIP_LOG_TMP_FILE
	log = sip_log
    else:
	app_log.append(msg)
	if len(app_log) > MAX_APP_CNT: app_log.pop(0)
	filename = APP_LOG_TMP_FILE
	log = app_log

    try:
	with open(filename, 'w') as data_file:
	    json.dump(log, data_file)
    except Exception as e:
	pass
#	print('%s: e=%s' % (whoami(), str(e)))


# ##############################################################################
