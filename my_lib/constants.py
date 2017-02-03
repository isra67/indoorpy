#!/bin/python

###############################################################
#
# Imports
#
# ###############################################################

from kivy.graphics import Color


###############################################################
#
# Declarations
#
# ###############################################################

CMD_KILL = 'kill -9 '

CONFIG_FILE = 'indoor.ini'  # 'indoorconfig.ini'

APP_NAME = '-Indoor-2.0-'

SCREEN_SAVER = 0
BACK_LIGHT = False
BRIGHTNESS = 100
WATCHES = 'analog'
AUDIO_VOLUME = 100

DBUSCONTROL_SCRIPT = './dbuscntrl.sh'
BACK_LIGHT_SCRIPT = './backlight.sh'
UNBLANK_SCRIPT = './unblank.sh'
BRIGHTNESS_SCRIPT = './brightness.sh'
SYSTEMINFO_SCRIPT = './sysinfo.sh'
VOLUMEINFO_SCRIPT = './volumeinfo.sh'
SETVOLUME_SCRIPT = './setvolume.sh'
SETIPADDRESS_SCRIPT = './setipaddress.sh'

BUTTON_CALL_ANSWER = '=Answer Call='
BUTTON_CALL_HANGUP = '=HangUp Call='
BUTTON_DO_CALL = '=Do Call='

BUTTON_DOOR_1 = '=Open Door 1='
BUTTON_DOOR_2 = '=Open Door 2='

WAIT_SCR = 'waitscr'
WATCH_SCR = 'clock'
DIGITAL_SCR = 'digiclock'
CAMERA_SCR = 'camera'
SETTINGS_SCR = 'settings'

COLOR_BUTTON_BASIC = .9,.9,.9,1
COLOR_ANSWER_CALL = .9,.9,0,1
COLOR_HANGUP_CALL = 0,0,.9,1
COLOR_NOMORE_CALL = COLOR_BUTTON_BASIC

ACTIVE_DISPLAY_BACKGROUND = Color(.0,.0,.9)
INACTIVE_DISPLAY_BACKGROUND = Color(.0,.0,.0)

LOG_LEVEL = 3
current_call = None
acc = None

main_state = 0
docall_button_global = None

active_display_index = 0

ring_event = None

TRANSPARENCY_VIDEO_CMD = ['setalpha']

DBUS_PLAYERNAME = 'org.mpris.MediaPlayer2.omxplayer'

transparency_value = 0
transparency_event = None

mainLayout = None
scrmngr = None

config = None

procs = []

