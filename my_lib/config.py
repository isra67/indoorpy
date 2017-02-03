#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.config import Config, ConfigParser

from constants import *


###############################################################
#
# Declarations
#
# ###############################################################


# ###############################################################
#
# Functions
#
# ###############################################################

def get_config():
    "nacitanie konfiguracie"
    global config

    config = ConfigParser()
    try:
        config.read('./' + CONFIG_FILE)
    except:
        print('ERROR 1: read config file!')

    try:
        config.read(dirname(__file__) + '/' + CONFIG_FILE)
    except:
        print('ERROR 2: read config file!')

    try:
	APP_NAME = config.get('about', 'app_name')
    except:
        print('ERROR 3: read config file!')
	return None

    return config

    try:
	value = config.get('command', 'watches')
	if value in 'analog': WATCHES = value
	else: WATCHES = 'digital'
#            self.dbg(WATCHES)
    except:
        self.dbg('ERROR 7: read config file!')

    try:
	screen_saver = int(config.get('command', 'screen_saver'))
	if screen_saver > 0 and screen_saver < 120: SCREEN_SAVER = screen_saver * 60
#            self.dbg(SCREEN_SAVER)
    except:
        self.dbg('ERROR 6: read config file!')

#    try:
#	    BACK_LIGHT = config.getboolean('command', 'back_light')
#        except:
#            self.dbg('ERROR 4: read config file!')
#	    BACK_LIGHT = True
#
#        try:
#	    br = int(config.get('command', 'brightness'))
#	    if br > 0 and br < 256: BRIGHTNESS = int(br * 2.55)
#        except:
#            self.dbg('ERROR 5: read config file!')
#	    BRIGHTNESS = 255
#
#	send_command(BRIGHTNESS_SCRIPT + ' ' + str(BRIGHTNESS))
#
#        try:
#            BUTTON_DO_CALL = config.get('gui', 'btn_docall')
#            BUTTON_CALL_ANSWER = config.get('gui', 'btn_call_answer')
#            BUTTON_CALL_HANGUP = config.get('gui', 'btn_call_hangup')
#            BUTTON_DOOR_1 = config.get('gui', 'btn_door_1')
#            BUTTON_DOOR_2 = config.get('gui', 'btn_door_2')
#        except:
#            self.dbg('ERROR: read config file!')

