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
CALL_CNTR_TMP_FILE = PARENT_DIR + 'call-cntr.dat'
CALL_LOG_TMP_FILE = PARENT_DIR + 'call-log.dat'

call_statistics = None		# call counters
call_log = None			# call log for last N calls


# ###############################################################
#
# Functions
#
# ###############################################################

def initcallstat():
    "Call statistics initialization"
    global call_statistics, call_log

    Logger.debug('%s:' % (whoami()))

    call_statistics = None
    call_log = None

    try:
	with open(CALL_CNTR_TMP_FILE, 'r') as data_file:
	    call_statistics = json.load(data_file)
    except: call_statistics = {}

    if call_statistics == {} or call_statistics == None:
	call_statistics = {'in':0, 'out':0, 'noansw': 0, 'noresp':0}

    try:
	with open(CALL_LOG_TMP_FILE, 'r') as data_file:
	    call_log = json.load(data_file)
    except: call_log = []

    if call_log == None: call_log = []


# ##############################################################################

"""
Call state constants:
====================
0 - NULL            -- call is not initialized.
1 - CALLING         -- initial INVITE is sent.
2 - INCOMING        -- initial INVITE is received.
3 - EARLY           -- provisional response has been sent or received.
4 - CONNECTING      -- 200/OK response has been sent or received.
5 - CONFIRMED       -- ACK has been sent or received.
6 - DISCONNECTED    -- call is disconnected.
"""

STATUS = ['','CALLING','INCOMING','EARLY','CONNECTING','CONFIRM','DISCONNECTED']

def setcallstat(outflag=False, status=0, prev_status=0, call=''):
    "Increment call stat counters and save to TMP file"
    global call_statistics, call_log

    dt = getdatetimestr()

    if status == 0 or status == 4 or ((status == 3) and outflag): return

    Logger.debug('%s: dt=%s outflag=%r state=%d %s (prev=%d %s) call=%s'\
	% (whoami(), dt, outflag, status, STATUS[status], prev_status, STATUS[prev_status], call))

    #call_statistics = {'in':0, 'out':0, 'noansw': 0, 'noresp':0}
    if outflag:
	if status == 6:
	    if prev_status == 5: call_statistics['out'] += 1
	    else: call_statistics['noresp'] += 1
    else:
	if status == 6:
	    if prev_status == 5: call_statistics['in'] += 1
	    else: call_statistics['noansw'] += 1

    filename = CALL_CNTR_TMP_FILE
    try:
	with open(filename, 'w') as data_file:
	    json.dump(call_statistics, data_file)
    except Exception as e:# pass
	Logger.error('%s: e=%s' % (whoami(), str(e)))

    typ = 'OUT' if outflag else 'IN '
    rec = '%s %s (%d) %s %s' % (dt, typ, status, STATUS[status], call)
    call_log.append(rec)
    if len(call_log) > 100: call_log.pop(0)

    filename = CALL_LOG_TMP_FILE
    try:
	with open(filename, 'w') as data_file:
	    json.dump(call_log, data_file)
    except Exception as e:# pass
	Logger.error('%s: e=%s' % (whoami(), str(e)))


# ##############################################################################
