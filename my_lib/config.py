#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.config import Config, ConfigParser
from kivy.logger import Logger

from constants import *
from itools import *


###############################################################
#
# Declarations
#
# ###############################################################

dict_command = {'screen_saver': 1,
            'dnd_mode': 0,
            'brightness': 100,
            'watches': 'analog' }
dict_sip = {'sip_mode': 'peer-to-peer',
            'sip_server_addr': '',
            'sip_port': '5060',
            'sip_username': '',
            'sip_authentication_name': '',
            'sip_p4ssw0rd': '' }
dict_dev = {'ringtone': 'oldphone.wav',
            'volume': 100,
            'micvolume': 100 }
dict_gui = {'screen_mode': 1,
	    'screen_orientation': 0,
	    'outgoing_calls': 1 }
dict_common = {'server_ip_address_1': '192.168.1.250',
            'server_stream_1': 'http://192.168.1.250:80/video.mjpg',
            'picture_1': 'fill',
            'sip_call1': '192.168.1.250',
            'server_ip_address_2': '',
            'server_stream_2': 'http://192.168.1.250/video.mjpg', # 'http://192.168.1.241:8080/stream/video.mjpeg',
            'picture_2': 'fill',
            'sip_call2': '',
            'server_ip_address_3': '',
            'server_stream_3': 'http://192.168.1.250/video.mjpg',
            'picture_3': 'fill',
            'sip_call3': '',
            'server_ip_address_4': '',
            'server_stream_4': 'http://192.168.1.250/video.mjpg',
            'picture_4': 'fill',
            'sip_call4': '' }
dict_timezone = {'timezone': 'Europe/Brussels'}
dict_service = {'masterpwd': '1234',
            'app_log': 'error',
            'tunnel_flag': False,
            'autoupdate': 0,
            'sip_log': 'error' }
dict_about = {'app_name': 'Indoor 2.0',
            'app_ver': '2.0.0.0',
            'licencekey': '0000-000000-0000-000000-0000',
            'regaddress': '',
            'serial': '' }
dict_system = {'inet': 'manual',
            'ipaddress': '192.168.1.251',
            'gateway': '192.168.1.200',
            'netmask': '255.255.255.0',
            'dns': '192.168.1.201' }


# ###############################################################
#
# Functions
#
# ###############################################################

def get_config():
    "nacitanie konfiguracie"
    Logger.debug('%s: ' % whoami())

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


# ###############################################################

def setDefaultConfig(config, full=False):
    "nastavenie konfiguracnych parametrov"
    Logger.debug('%s: ' % whoami())

    config.setdefaults('command', dict_command)
    config.setdefaults('sip', dict_sip)
    config.setdefaults('devices', dict_dev)
    config.setdefaults('gui', dict_gui)
    config.setdefaults('common', dict_common)
    config.setdefaults('timezones', dict_timezone)
    config.setdefaults('service', dict_service)
    config.setdefaults('about', dict_about)
    config.setdefaults('system', dict_system)

    try:
	s = get_info(SYSTEMINFO_SCRIPT).split()
    except:
	s = []

    cnt = len(s)

    if cnt > 1: config.set('about', 'serial', s[1])

    dns = ''
    try:
        dns = s[8]
    except:
        dns = ''

    if cnt < 6:
	config.set('system', 'inet', 'manual')
	config.set('system', 'ipaddress', '127.0.0.1')
	config.set('system', 'gateway', '')
	config.set('system', 'netmask', '')
	config.set('system', 'dns', dns)
    else:
	config.set('system', 'inet', s[2])
	config.set('system', 'ipaddress', s[3])
	config.set('system', 'gateway', s[6])
	config.set('system', 'netmask', s[4])
	config.set('system', 'dns', dns)

    if full:
	config.setall('command', dict_command)
	config.setall('sip', dict_sip)
	config.setall('devices', dict_dev)
	config.setall('gui', dict_gui)
	config.setall('common', dict_common)
	config.setall('timezones', dict_timezone)
	config.setall('service', dict_service)
	config.setall('system', dict_system)

        for s in config.sections():
            Logger.info('%s: section=%s' % (whoami(),s))
            for k, v in config.items(s):
                Logger.info('%s: key=%s val=%s' % (whoami(), k, v))

	config.write()

    return config


# ###############################################################

def saveKivyCfg(section, item, value):
    "nastavenie konfiguracnych parametrov pre Kivy"
    Logger.debug('%s: [%s] %s = %s' % (whoami(), section, item, value))

    kivycfg = ConfigParser()
    try:
        kivycfg.read(KIVY_CONFIG_FILE)
	kivycfg.set(section, item, value)
	kivycfg.write()
    except:
        Logger.warning('%s: ERROR! ([%s] %s = %s)' % (whoami(), section, item, value))


# ###############################################################
