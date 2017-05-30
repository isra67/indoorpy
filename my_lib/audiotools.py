#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.logger import Logger
from kivy.clock import Clock

import threading
import RPi.GPIO as GPIO
import usb.core

from time import sleep

from constants import *
from itools import *


###############################################################
#
# Declarations
#
# ###############################################################

VENDOR_ID = 0x0572		# Conexant
PRODUCT_ID = 0x1410		# USB audio

RST_PIN = 2 #24
RST_TIME = .2

device_id = 0


# ###############################################################
#
# Functions
#
# ###############################################################

def check_usb_audio():
    "check if usb audio exists"
    global device_id

    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
	Logger.error('%s: USB AUDIO is not connected' % whoami())
	device_id = 0
    else:
	if device_id > 0 and device_id != dev.address:
	    Logger.error('%s: USB AUDIO address changed' % whoami())
	    device_id = 0
	else:
#	    Logger.debug('%s: USB AUDIO is connected: %d' % (whoami(), dev.address))
	    device_id = dev.address

    return (0 if device_id > 0 else 1)


# ##############################################################################
def reset_usb_audio_worker(dt=0):
    "reset usb audio board"
    "!!!!! USE share/audioini.py !!!!!"
    Logger.error('%s: RESET USB AUDIO BOARD' % whoami())

    VALUE_INI = GPIO.HIGH
    VALUE_RST = GPIO.LOW

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT, initial=VALUE_INI)

    GPIO.output(RST_PIN, VALUE_INI)
    sleep(RST_TIME)
    GPIO.output(RST_PIN, VALUE_RST)
    sleep(RST_TIME)
    GPIO.output(RST_PIN, VALUE_INI)
    sleep(RST_TIME)


# ##############################################################################

def reset_usb_audio():
    "reset usb audio board"
    global device_id

    Logger.debug('%s: RESET USB AUDIO BOARD' % whoami())

    device_id = 0

    send_command('./audioini.sh')
#    threading.Thread(target=reset_usb_audio_worker).start()


# ##############################################################################
