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
KIVY_CONFIG_FILE = '/root/.kivy/config.ini'

APP_NAME = '-Indoor-2.0-'
APP_VERSION_CODE = '2.0.0.4'

SCREEN_SAVER = 0
WATCHES = 'analog'
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
HIDINIT_SCRIPT = './hid_init.sh'

# ### images: ###
MAKE_CALL_IMG = 'imgs/ww_phone-call.png'
ANSWER_CALL_IMG = 'imgs/w_call-answer.gif' # 'imgs/w_phone-call.png'
HANGUP_OUTGOING_CALL_IMG = 'imgs/w_call-cancel.gif'
HANGUP_CALL_IMG = 'imgs/w_call-disconnect.png'
ERROR_CALL_IMG = 'imgs/nothing.png' # 'imgs/w_call-reject.png'
DND_CALL_IMG = 'imgs/w_call-dnd.png'
UNUSED_CALL_IMG = 'imgs/nothing.png' # 'imgs/w_call_grey.png'

VOLUME_IMG = 'imgs/w_speaker.png'
MICROPHONE_IMG = 'imgs/w_microphone.png'

SCREEN_SAVER_IMG = 'imgs/w_monitor.png'
SETTINGS_IMG = 'imgs/w_settings.png'
LOCK_IMG = 'imgs/w_lock.png'
UNLOCK_IMG = 'imgs/w_unlock.png'
INACTIVE_LOCK_IMG = 'imgs/w_nolock.png'
UNUSED_LOCK_IMG = 'imgs/w_lock_grey.png'

NO_IMG = 'imgs/nothing.png'

# ### screens: ###
WAIT_SCR = 'waitscr'
DIGITAL_SCR = 'digiclock'
CAMERA_SCR = 'camera'
SETTINGS_SCR = 'settings'

# ### colors: ###
COLOR_BUTTON_BASIC = .9,.9,.9,1
COLOR_ANSWER_CALL = .9,.9,0,1
COLOR_HANGUP_CALL = 0,0,.9,1
COLOR_ERROR_CALL = .9,0,0,1
COLOR_NOMORE_CALL = COLOR_BUTTON_BASIC

ACTIVE_DISPLAY_BACKGROUND = [1.,1.,1.] #[.0,.0,.9]
INACTIVE_DISPLAY_BACKGROUND = [.3,.3,.3] #[.0,.0,.0]
N0_DISPLAY_BACKGROUND = [.0,.0,.0]

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
LOG_LEVEL = 3 #5				# basic SIP log level
current_call = None
acc = None
sipRegStatus = False

# ### time: ###
ICON_RELOAD = .3
HIDINIT_TIME = 3. # 4
PHONEINIT_TIME = HIDINIT_TIME + .2 # 3

# ### variables & constatnts: ###
main_state = 0
docall_button_global = None

active_display_index = 0

TRANSPARENCY_VIDEO_CMD = ['setalpha']

DBUS_PLAYERNAME = 'org.mpris.MediaPlayer2.omxplayer'

mainLayout = None
scrmngr = None
scr_mode = 0
config = None

procs = []

