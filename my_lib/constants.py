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
#BRIGHTNESS = 100
WATCHES = 'analog'
#AUDIO_VOLUME = 100
ROTATION = 0

# ### scripts: ###
DBUSCONTROL_SCRIPT = './dbuscntrl.sh'
BACK_LIGHT_SCRIPT = './backlight.sh'
UNBLANK_SCRIPT = './unblank.sh'
BRIGHTNESS_SCRIPT = './brightness.sh'
SYSTEMINFO_SCRIPT = './sysinfo.sh'
VOLUMEINFO_SCRIPT = './volumeinfo.sh'
SETVOLUME_SCRIPT = './setvolume.sh'
SETMICVOLUME_SCRIPT = './setmicvolume.sh'
SETIPADDRESS_SCRIPT = './setipaddress.sh'

# ### images: ###
MAKE_CALL_IMG = 'imgs/phone-call.png'
ANSWER_CALL_IMG = 'imgs/call-answer.png'
HANGUP_CALL_IMG = 'imgs/call-disconnect.png'
ERROR_CALL_IMG = 'imgs/call-reject.png'
DND_CALL_IMG = 'imgs/call-dnd.png'

VOLUME_IMG = 'imgs/speaker.png'
MICROPHONE_IMG = 'imgs/microphone.png'

SCREEN_SAVER_IMG = 'imgs/monitor.png'
SETTINGS_IMG = 'imgs/settings.png'
LOCK_IMG = 'imgs/lock.png'
UNLOCK_IMG = 'imgs/unlock.png'
INACTIVE_LOCK_IMG = 'imgs/nolock.png'

NO_IMG = 'imgs/nothing.png'

# ### screens: ###
WAIT_SCR = 'waitscr'
#WATCH_SCR = 'clock'
DIGITAL_SCR = 'digiclock'
CAMERA_SCR = 'camera'
SETTINGS_SCR = 'settings'

# ### colors: ###
COLOR_BUTTON_BASIC = .9,.9,.9,1
COLOR_ANSWER_CALL = .9,.9,0,1
COLOR_HANGUP_CALL = 0,0,.9,1
COLOR_ERROR_CALL = .9,0,0,1
COLOR_NOMORE_CALL = COLOR_BUTTON_BASIC

ACTIVE_DISPLAY_BACKGROUND = [.0,.0,.9]
INACTIVE_DISPLAY_BACKGROUND = [.0,.0,.0]

# ### audio player: ###
APLAYER = 'aplay'
APARAMS = '-q -N -f cd -D plughw:0,0 sounds/'
RING_TONE = 'oldphone.wav'
BUSY_TONE = 'dial.wav' # 'busy.wav'
DIAL_TONE = 'tada.wav'
RING_WAV = APLAYER + ' ' + APARAMS + RING_TONE
BUSY_WAV = APLAYER + ' ' + APARAMS + BUSY_TONE
DIAL_WAV = APLAYER + ' ' + APARAMS + DIAL_TONE

ring_event = None

# ### SIP: ###
LOG_LEVEL = 3 #5				# SIP log level
current_call = None
acc = None

# ### variables & constatnts: ###
main_state = 0
docall_button_global = None

active_display_index = 0

TRANSPARENCY_VIDEO_CMD = ['setalpha']

DBUS_PLAYERNAME = 'org.mpris.MediaPlayer2.omxplayer'

#transparency_value = 0
#transparency_event = None

mainLayout = None
scrmngr = None
scr_mode = 0
config = None

procs = []

