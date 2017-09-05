#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import json


# ###############################################################
#
# Declarations
#
# ###############################################################

# basic app settings
settings_app = json.dumps([
    {'type': 'title',
     'title': 'Basic application parameters'},
    {'type': 'numeric',
     'title': 'Screen saver',
     'desc': 'Select time to swap do screen saver mode (0-120 min)',
     'section': 'command',
     'key': 'screen_saver'},
    {'type': 'options',
     'title': 'Watches',
     'desc': 'Choose if you want to analog or digital watches',
     'section': 'command',
     'key': 'watches',
     'options': ['analog','digital','none']}
])

# ###############################################################

# set GUI
settings_gui = json.dumps([
    {'type': 'title',
     'title': 'User interface parameters'},
    {'type': 'options',
     'title': 'Screen mode',
     'desc': 'Choose for the display option',
     'section': 'gui',
     'key': 'screen_mode',
     'options': ['1', '2', '4']},
    {'type': 'options',
     'title': 'Rotate',
     'desc': 'Choose for the display orientation',
     'section': 'gui',
     'key': 'screen_orientation',
     'options': ['0', '90', '180', '270']},
    {'type': 'bool',
     'title': 'Outgoing calls',
     'desc': 'Enable/disable outgoing calls',
     'section': 'gui',
     'key': 'outgoing_calls'}
])

# ###############################################################

# set outdoor devices
settings_outdoor = json.dumps([
    {'type': 'title',
     'title': 'Outdoor devices parameters'},
    {'type': 'string',
     'title': 'Device address 1',
     'desc': 'Enter IP address for relay control',
     'section': 'common',
     'key': 'server_ip_address_1'},
    {'type': 'string',
     'title': 'SIP call 1',
     'desc': 'Type SIP call number or IP address',
     'section': 'common',
     'key': 'sip_call1'},
    {'type': 'string',
     'title': 'Stream address 1',
     'desc': 'Enter address to retrieve video stream',
     'section': 'common',
     'key': 'server_stream_1'},
    {'type': 'options',
     'title': 'Aspect ratio 1',
     'desc': 'Choose how to display the picture',
     'section': 'common',
     'key': 'picture_1',
     'options': ['fill', '4:3', '16:9']},
    {'type': 'string',
     'title': 'Device address 2',
     'desc': 'Enter IP address for relay control',
     'section': 'common',
     'key': 'server_ip_address_2'},
    {'type': 'string',
     'title': 'SIP call 2',
     'desc': 'Type SIP call number or IP address',
     'section': 'common',
     'key': 'sip_call2'},
    {'type': 'string',
     'title': 'Stream address 2',
     'desc': 'Enter address to retrieve video stream',
     'section': 'common',
     'key': 'server_stream_2'},
    {'type': 'options',
     'title': 'Aspect ratio 2',
     'desc': 'Choose how to display the picture',
     'section': 'common',
     'key': 'picture_2',
     'options': ['fill', '4:3', '16:9']},
    {'type': 'string',
     'title': 'Device address 3',
     'desc': 'Enter IP address for relay control',
     'section': 'common',
     'key': 'server_ip_address_3'},
    {'type': 'string',
     'title': 'SIP call 3',
     'desc': 'Type SIP call number or IP address',
     'section': 'common',
     'key': 'sip_call3'},
    {'type': 'string',
     'title': 'Stream address 3',
     'desc': 'Enter address to retrieve video stream',
     'section': 'common',
     'key': 'server_stream_3'},
    {'type': 'options',
     'title': 'Aspect ratio 3',
     'desc': 'Choose how to display the picture',
     'section': 'common',
     'key': 'picture_3',
     'options': ['fill', '4:3', '16:9']},
    {'type': 'string',
     'title': 'Device address 4',
     'desc': 'Enter IP address for relay control',
     'section': 'common',
     'key': 'server_ip_address_4'},
    {'type': 'string',
     'title': 'SIP call 4',
     'desc': 'Type SIP call number or IP address',
     'section': 'common',
     'key': 'sip_call4'},
    {'type': 'string',
     'title': 'Stream address 4',
     'desc': 'Enter address to retrieve video stream',
     'section': 'common',
     'key': 'server_stream_4'},
    {'type': 'options',
     'title': 'Aspect ratio 4',
     'desc': 'Choose how to display the picture',
     'section': 'common',
     'key': 'picture_4',
     'options': ['fill', '4:3', '16:9']}
])

# ###############################################################

# audio settings
settings_audio = json.dumps([
    {'type': 'title',
     'title': 'Ring tone and volume settings'},
    {'type': 'options',
     'title': 'Ringtone',
     'desc': 'Choose ringtone',
     'section': 'devices',
     'key': 'ringtone',
     'options': ['oldphone.wav', 'tone1.wav', 'tone2.wav']}
])

# ###############################################################

# SIP settings
settings_sip = json.dumps([
    {'type': 'title',
     'title': 'SIP parameters'},
    {'type': 'options',
     'title': 'SIP mode',
     'desc': 'Choose SIP account type',
     'section': 'sip',
     'key': 'sip_mode',
     'options': ['peer-to-peer', 'SIP server']},
    {'type': 'string',
     'title': 'SIP server address',
     'desc': 'Type SIP server address',
     'section': 'sip',
     'key': 'sip_server_addr'},
    {'type': 'string',
     'title': 'SIP server port',
     'desc': 'Type SIP server port',
     'section': 'sip',
     'key': 'sip_port'},
    {'type': 'string',
     'title': 'SIP user name',
     'desc': 'Type SIP account name',
     'section': 'sip',
     'key': 'sip_username'},
    {'type': 'string',
     'title': 'SIP authentication name',
     'desc': 'Type SIP account authentication name',
     'section': 'sip',
     'key': 'sip_authentication_name'},
    {'type': 'string',
     'title': 'SIP password',
     'desc': 'Type SIP password',
     'section': 'sip',
     'key': 'sip_p4ssw0rd'},
    {"type": "buttons",
     "title": "Call log","desc": "View SIP activities",
     "section": "sip",
     "key": "buttoncalllog",
     "buttons": [{"title":"Call Log","id":"button_calllog"}]}
#    {'type': 'string',
#     'title': 'SIP ident address',
#     'desc': 'Type SIP ident address',
#     'section': 'sip',
#     'key': 'sip_ident_addr'},
#    {'type': 'string',
#     'title': 'SIP ident info',
#     'desc': 'Type SIP ident info',
#     'section': 'sip',
#     'key': 'sip_ident_info'},
#    {'type': 'string',
#     'title': 'STUNT server',
#     'desc': 'Type STUNT server address',
#     'section': 'sip',
#     'key': 'sip_stun_server'}
])

# ###############################################################

# System parameters
settings_system = json.dumps([
    {'type': 'title',
     'title': 'Network parameters'},
    {'type': 'options',
     'title': 'inet type',
     'desc': 'Choose IP address type',
     'section': 'system',
     'key': 'inet',
     'options': ['static', 'dhcp']},
    {'type': 'string',
     'title': 'IP address',
     'desc': 'Enter Indoor monitor IP address',
     'section': 'system',
     'key': 'ipaddress'},
    {'type': 'string',
     'title': 'Gateway',
     'desc': 'Enter gateway address',
     'section': 'system',
     'key': 'gateway'},
    {'type': 'string',
     'title': 'Network mask',
     'desc': 'Enter netmask address',
     'section': 'system',
     'key': 'netmask'},
    {'type': 'string',
     'title': 'DNS server',
     'desc': 'Type DNS server address',
     'section': 'system',
     'key': 'dns'}
])

# ###############################################################

# about app
settings_about = json.dumps([
    {'type': 'title',
     'title': 'About application'},
    {'type': 'string',
     'title': 'Name',
     'desc': 'The application name to display',
     'section': 'about',
     'disabled': True,
     'key': 'app_name'},
    {'type': 'string',
     'title': 'Version',
     'desc': 'The application version to display',
     'section': 'about',
     'disabled': True,
     'key': 'app_ver'},
    {'type': 'string',
     'title': 'Serial number',
     'desc': 'Indoor monitor serial number',
     'section': 'about',
     'disabled': True,
     'key': 'serial'},
    {'type': 'string',
     'title': 'Licence key',
     'desc': 'Application licence key',
     'section': 'about',
     'disabled': False,
     'key': 'licencekey'},
    {'type': 'string',
     'title': 'Registration email address',
     'desc': 'Enter valid email address to obtain the application licence key',
     'section': 'about',
     'disabled': False,
     'key': 'regaddress'},
    {"type": "buttons",
     "title": "Send registration request","desc": "Send registration request to obtain the licence key",
     "section": "about",
     "key": "buttonregs",
     "buttons": [{"title":"Registration","id":"button_regs"}]}
])

# ###############################################################

# service function
timezone_settings = json.dumps([
    {'type': 'title',
     'title': 'Timezone settings'},
    {'type': 'timezone',
     'title': 'Timezone',
     'desc': 'Choose time zone',
     'section': 'timezones',
     'key': 'timezone',
     'options': []}
])

"""
    {'type': 'string',
     'title': 'Timezone',
     'desc': 'Enter valid timezone string',
     'section': 'timezones',
     'key': 'timezone'}
"""

# ###############################################################

# service function
settings_services = json.dumps([
    {'type': 'title',
     'title': 'Service functions'},
    {'type': 'string',
     'title': 'Master password',
     'desc': 'Enter password for input to the detail settings',
     'section': 'service',
     'key': 'masterpwd'},
    {"type": "buttons",
     "title": "Status","desc": "Show popup window with main status informations",
     "section": "service",
     "key": "buttonpress",
     "buttons": [{"title":"Status","id":"button_status"}]},
    {'type': 'options',
     'title': 'App logging level',
     'desc': 'Choose level for application logging messages',
     'section': 'service',
     'key': 'app_log',
     'options': ['trace', 'debug', 'info', 'error', 'none']},
    {'type': 'options',
     'title': 'SIP logging level',
     'desc': 'Choose level for SIP logging messages',
     'section': 'service',
     'key': 'sip_log',
     'options': ['debug', 'info', 'error', 'none']},
    {"type": "bool",
     "title": "Remote access",
     "desc": "Enable/disable remote connection",
     "section": "service",
     "key": "tunnel_flag"},
    {"type": "buttons",
     "title": "Log history","desc": "Show popup window with last 100 log messages",
     "section": "service",
     "key": "buttonlogs",
     "buttons": [{"title":"Log Msg","id":"button_loghist"}]},
    {"type": "buttons",
     "title": "Factory reset","desc": "Set configuration to default",
     "section": "service",
     "key": "buttonfactory",
     "buttons": [{"title":"Rst Cfg","id":"button_factory"}]},
    {"type": "buttons",
     "title": "Restart","desc": "Restart the application",
     "section": "service",
     "key": "app_rst",
     "buttons": [{"title":"Restart App","id":"button_app_rst"}]} #,{"title":"Del","id":"button_delete"},{"title":"Rename","id":"button_rename"}]}
])

# ###############################################################
