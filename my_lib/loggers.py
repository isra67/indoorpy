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

MAX_APP_CNT = 500 #1000
MAX_SIP_CNT = 250

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
#    send_command('echo "start" > /tmp/deb.txt')

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

    #create files if not exists
    if app_log == None or len(app_log) == 0:
	app_log = []
	try:
	    with open(APP_LOG_TMP_FILE, 'w+') as data_file:
		json.dump(app_log, data_file)
	except: pass

    if sip_log == None or len(sip_log) == 0:
	sip_log = []
	try:
	    with open(SIP_LOG_TMP_FILE, 'w+') as data_file:
		json.dump(sip_log, data_file)
	except: pass


# ##############################################################################

def setloginfo(sipflag=False, msg=''):
    "Save msg to TMP file"
    global app_log, sip_log

#    print('%s: dt=%s sipflag=%r msg=%s'% (whoami(), getdatetimestr(), sipflag, msg))
#    if not '/tmp/deb.txt' in msg: send_command('echo "%s" >> /tmp/deb.txt' % msg)

    if sipflag:
	sip_log.append('%s %s' % (getdatetimestr(), msg))
	if len(sip_log) > MAX_SIP_CNT: sip_log.pop(0)
	filename = SIP_LOG_TMP_FILE
	log = sip_log
    else:
	if '[DEBUG' in msg or '[TRACE' in msg: return
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
