#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################


import pjsua as pj

from kivy.logger import Logger


# ###############################################################
#
# Functions
#
# ###############################################################

def setMediaConfig():
    "pjSip media configuration"
    mc = pj.MediaConfig()
    mc.quality = 6 #0 #8
    mc.ec_tail_len = 0 #200
    mc.clock_rate = 48000 #44100 #16000
    Logger.warning('pjSip setMediaConfig: quality:%d ec_tail_len:%d clock_rater:%d'\
        % (mc.quality, mc.ec_tail_len, mc.clock_rate))
    return mc


def log_cb(level, str, len):
    "pjSip logging callback"
    Logger.info('pjSip cb: ' + str)

