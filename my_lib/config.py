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
    print 'get_config'

    config = ConfigParser()
    try:
        config.read('./' + CONFIG_FILE)
    except:
        print('ERROR 1: read config file!')

	try:
	    config.read(dirname(__file__) + '/' + CONFIG_FILE)
	except:
	    print('ERROR 2: read config file!')
	    return None

    print '***** tone: ', config.get('devices', 'ringtone')

    return config
