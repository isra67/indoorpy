#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import os
import time

from kivy.logger import Logger

from itools import *


###############################################################
#
# Declarations
#
# ###############################################################

SW_WD_PATH = '/tmp/indoor_wd.dat'
SW_WD_TIME = 5.01
wd_val = 0


# ###############################################################
#
# Functions
#
# ###############################################################

def init_sw_watchdog():
    "SW watchdoq"
    global wd_val

    Logger.debug('%s:' % whoami())

    wd_val = 0
    ln = ''

    try:
	with open(SW_WD_PATH, "r+") as text_file:
	    ln = text_file.read()
    except:
	pass

    if len(ln) > 0 and not ln.isdigit():
	Logger.critical('%s: RESTART REASON: %s' % (whoami(), ln))


# ##############################################################################

def sw_watchdog(dt=0):
    "SW watchdoq"
    global wd_val

    Logger.trace('%s: %d' % (whoami(), wd_val))

    wd_val = 1 if wd_val > 99 else wd_val + 1
    #if wd_val > 10: return

    with open(SW_WD_PATH, "w+") as text_file:
	text_file.write("%02d" % wd_val)


# ##############################################################################

def stop_sw_watchdog():
    "SW watchdoq"
    global wd_val

    Logger.debug('%s:' % whoami())

    wd_val = 0

    ln = ''

    try:
	with open(SW_WD_PATH, "r+") as text_file:
	    ln = text_file.read()
    except:
	pass

    if len(ln) > 0 and ln.isdigit():
	with open(SW_WD_PATH, "w+") as text_file:
	    text_file.write("")


# ##############################################################################
