#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.config import Config, ConfigParser
from kivy.logger import Logger

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
    Logger.debug('get_config: ')

    config = ConfigParser()
    try:
        config.read('./' + CONFIG_FILE)
    except:
        Logger.info('get_config: ERROR 1 - read config file!')

	try:
	    config.read(dirname(__file__) + '/' + CONFIG_FILE)
	except:
	    Logger.warning('get_config: ERROR 2 - read config file!')
	    return None

    return config
