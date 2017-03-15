#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import kivy
kivy.require('1.9.0')


from kivy.app import App
from kivy.adapters.listadapter import ListAdapter
from kivy.clock import Clock
from kivy.config import Config, ConfigParser
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger, LoggerHistory
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemLabel
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingsWithSidebar
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import ScreenManager, Screen
#from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

import atexit
import datetime
from datetime import timedelta
import json

import errno
import signal
import socket
import fcntl
import subprocess
from threading import Thread
import time

import pjsua as pj

from my_lib import *


###############################################################
#
# Declarations
#
# ###############################################################

config = get_config()


# ###############################################################
#
# Functions
#
# ###############################################################

@atexit.register
def kill_subprocesses():
    "tidy up at exit or break"
    global mainLayout

    Logger.info(whoami() +': destroy lib at exit')
    try:
	pj.Lib.destroy()
    except:
	pass

    Logger.info(whoami() +': kill subprocesses at exit')
    for proc in procs:
	try:
            proc.kill()
	except:
	    pass

    send_command('pkill omxplayer')
#    send_command('pkill dbus-daemon')


# ###############################################################
#
# Classes
#
# ###############################################################


class MyAccountCallback(pj.AccountCallback):
    "Callback to receive events from account"
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)


    def on_incoming_call(self, call):
	"Notification on incoming call"
        global current_call, mainLayout

	Logger.trace(whoami() +': DND mode = '+ str(mainLayout.dnd_mode))

        if current_call or mainLayout.dnd_mode:
            call.answer(486, "Busy")
            return

        Logger.info(whoami() +": Incoming call from " + call.info().remote_uri)
        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180)


class MyCallCallback(pj.CallCallback):
    "Callback to receive events from Call"

    sip_call_id_last = '***'
    callTimerEvent = None
    CALL_TIMEOUT = 60 * 3

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)


    def on_state(self):
	"Notification when call state has changed"
        global current_call, ring_event, transparency_value
        global main_state, mainLayout, docall_button_global

	ci = self.call.info()
	role = 'CALLER' if ci.role == 0 else 'CALLEE'

	Logger.info('pjSip on_state: Call width=%s is %s (%d) last code=%d (%s) as role=%s'\
	    % (ci.remote_uri, ci.state_text, ci.state, ci.last_code, ci.last_reason, role))
	Logger.debug('pjSip on_state: sip_call_id='+ci.sip_call_id+'  outgoing call='\
	    + str(mainLayout.outgoingCall) + ' current call='+str(current_call))

        main_state = ci.state
        transparency_value = 0

        if main_state == pj.CallState.EARLY:
	    mainLayout.findTargetWindow(ci.remote_uri)
	    if not ring_event and not mainLayout.outgoingCall:
		ring_event = Clock.schedule_interval(playWAV, 3.5)
		playWAV(3.5)
        else:
	    if ring_event:
		Clock.unschedule(ring_event)
		ring_event = None
		stopWAV()

	if self.sip_call_id_last is ci.sip_call_id:
	    Logger.error('pjSip '+whoami()+': Unwanted message='+ci.state_text+' from '+ci.remote_uri+' as '+role)
	    return

	if self.callTimerEvent is None:
	    Clock.unschedule(self.callTimerEvent)
	    self.callTimerEvent = Clock.schedule_once(self.callTimerWD, self.CALL_TIMEOUT)

        if main_state == pj.CallState.INCOMING or main_state == pj.CallState.EARLY:
	    if not mainLayout.outgoingCall:
#		docall_button_global.color = COLOR_ANSWER_CALL
#		docall_button_global.text = BUTTON_CALL_ANSWER
		docall_button_global.imgpath = ANSWER_CALL_IMG
	    mainLayout.setButtons(True)
	    mainLayout.finishScreenTiming()

        if main_state == pj.CallState.DISCONNECTED:
            current_call = None
	    mainLayout.setButtons(False)
#            docall_button_global.color = COLOR_NOMORE_CALL
#            docall_button_global.text = BUTTON_DO_CALL
	    docall_button_global.imgpath = MAKE_CALL_IMG
	    mainLayout.startScreenTiming()
	    mainLayout.del_sliders()
	    mainLayout.showPlayers()
	    mainLayout.outgoingCall = False
	    self.sip_call_id_last = ci.sip_call_id
	    if not self.callTimerEvent is None:
		Clock.unschedule(self.callTimerEvent)
		self.callTimerEvent = None

        if main_state == pj.CallState.CONFIRMED:
#            docall_button_global.color = COLOR_HANGUP_CALL
#            docall_button_global.text = BUTTON_CALL_HANGUP
	    docall_button_global.imgpath = HANGUP_CALL_IMG
	    Logger.info('pjSip call status:' + self.call.dump_status())

        if main_state == pj.CallState.CALLING:
	    if not current_call is None:
		Logger.warning('pjSip bad call: CALLING state %s <<>> %s' %(str(current_call), str(self.call)))
		self.call.hangup()
		return
	    current_call = self.call
#            docall_button_global.color = COLOR_ANSWER_CALL
#            docall_button_global.text = BUTTON_CALL_HANGUP
	    docall_button_global.imgpath = ANSWER_CALL_IMG


    def on_media_state(self):
	"Notification when call's media state has changed"
        global mainLayout

        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
	    try:
        	pj.Lib.instance().conf_connect(call_slot, 0)
        	pj.Lib.instance().conf_connect(0, call_slot)
        	Logger.debug("pjSip "+whoami()+": Media is now active")
	    except pj.Error, e:
        	Logger.error("pjSip "+whoami()+": Media is inactive due to ERROR: " + str(e))
		mainLayout.mediaErrorFlag = True
        else:
            Logger.debug("pjSip "+whoami()+": Media is inactive")
	    mainLayout.mediaErrorFlag = False


    def callTimerWD(self, dt):
	"SIP call watch dog"
        global current_call, ring_event
        global main_state, mainLayout, acc

	Logger.warning(whoami()+':')

	self.callTimerEvent = None
	main_state = pj.CallState.DISCONNECTED
	mainLayout.setButtons(False)
#        docall_button_global.color = COLOR_NOMORE_CALL
#        docall_button_global.text = BUTTON_DO_CALL
	docall_button_global.imgpath = MAKE_CALL_IMG
	mainLayout.startScreenTiming()
	mainLayout.showPlayers()
	mainLayout.outgoingCall = False

	if not ring_event is None:
	    Clock.unschedule(ring_event)
	    ring_event = None
	    stopWAV()

	if not current_call is None:
	    try:
		if current_call.is_valid(): current_call.hangup()
	    except:
		pass
	    current_call = None


def make_call(uri):
    "Function to make outgoing call"
    global acc

    Logger.debug(whoami() + ': ' + uri)

    try:
	if acc != None: return acc.make_call(uri, cb=MyCallCallback(pj.CallCallback))
    except pj.Error, e:
        Logger.error("pjSip "+whoami()+" Exception: " + str(e))
	mainLayout.mediaErrorFlag = True

    return None


# ##############################################################################

class BasicDisplay:
    "basic screen class"
    def __init__(self,winpos,servaddr,sipcall,streamaddr,relaycmd):
	"display area init"
	global scr_mode, mainLayout

	self.screenIndex = len(procs)
	self.winPosition = winpos.split(',')
	self.winPosition = [int(i) for i in self.winPosition]
	self.serverAddr = str(servaddr)
	self.sipcall = str(sipcall)
	self.streamUrl = str(streamaddr)
	self.relayCmd = str(relaycmd)
	self.playerPosition = [i for i in self.winPosition]

	delta = 2
	self.playerPosition[0] += delta
	self.playerPosition[1] += delta
	self.playerPosition[2] -= delta
	self.playerPosition[3] -= delta
	self.playerPosition = [str(i) for i in self.playerPosition]

	procs.append(self.initPlayer())

	self.socket = None
	self.bgrThread = Thread(target=self.tcpip_worker, kwargs={'addr': servaddr})
	self.bgrThread.daemon = True
	self.bgrThread.start()

	self.color = INACTIVE_DISPLAY_BACKGROUND

	if scr_mode == 1:
	    self.actScreen = mainLayout.ids.videoLabel1
	elif scr_mode == 2:
	    self.actScreen = mainLayout.ids.videoLabel1 if self.screenIndex == 0 else\
		mainLayout.ids.videoLabel3
	elif scr_mode == 3:
	    self.actScreen = mainLayout.ids.videoLabel1 if self.screenIndex == 0 else\
		mainLayout.ids.videoLabel2
	else:
	    self.actScreen = mainLayout.ids.videoLabel1 if self.screenIndex == 0 else\
		mainLayout.ids.videoLabel2 if self.screenIndex == 1 else\
		mainLayout.ids.videoLabel3 if self.screenIndex == 2 else\
		mainLayout.ids.videoLabel4

	self.printInfo()
	self.setActive(False)


    def testTouchArea(self, x, y):
	"test if touch is in display area"
	y = 480 - y                        # touch position is from bottom to up
	retx = self.winPosition[0] < x and self.winPosition[2] > x
	rety = self.winPosition[1] < y and self.winPosition[3] > y
	ret = retx and rety
	Logger.trace('%s: winID=%d ret=%d' % (whoami(), self.screenIndex, ret))
	return ret


    def initPlayer(self):
	"start video player"

	Logger.debug(whoami()+':')
	try:
	    if len(itools.omxl) and DBUS_PLAYERNAME + str(self.screenIndex) in itools.omxl:
		del itools.omxl[DBUS_PLAYERNAME + str(self.screenIndex)]
	except:
	    pass

	return subprocess.Popen(['omxplayer', '--live', '--no-osd', '--no-keys',\
	    '--dbus_name', DBUS_PLAYERNAME + str(self.screenIndex),\
	    '--aspect-mode', 'fill', '--display','0', '--orientation', '0',\
	    '--layer', '1', '--win', ','.join(self.playerPosition), self.streamUrl],\
	    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)


    def resizePlayer(self, newpos=''):
	"resize video player area"
	global mainLayout, scr_mode

	Logger.debug(whoami() + ': ' + newpos)

	self.hidePlayer()

	if scr_mode == 1: return

	pos = []
	pos = newpos.split(',') if len(newpos) else self.playerPosition

	self.dbus_command(['setvideopos'] + pos)


    def tcpip_worker(self, addr):
	"TCPIP thread"
	Logger.debug('%s: (%d) %s' % (whoami(), self.screenIndex, addr))

	SERVER_REQ = 'GET /events.txt HTTP/1.1\n\n'

	if ':' in addr:
	    b = addr.split(':')
	    a = (b[0],int(b[1]))
	else:
	    a = (addr, 80)

	try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(a)
	    time.sleep(1)
	    fcntl.fcntl(self.socket, fcntl.F_SETFL, os.O_NONBLOCK)
	    time.sleep(1)
	    self.socket.send(SERVER_REQ)
        except IOError as e:
            Logger.warning('%s: (%d) %s CONNECT ERROR %s' % (whoami(), self.screenIndex, addr, str(e)))
	    return

	msg = ''
	noDataCounter = 0
	while True:
	    try:
		msg = self.socket.recv(4096) if not self.socket is None else ''
	    except socket.error, e:
		err = e.args[0]
		if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
		    time.sleep(1)				# No data available
		    noDataCounter += 1
		    if noDataCounter > 40: break		# try reconnect
		    continue
		else:
		    # a "real" error occurred
		    Logger.warning('%s: (%d) %s  ERROR: %s' % (whoami(), self.screenIndex, addr, str(e)))
		    msg = ''
        	    break

	    if not msg is '':
		# got a message, do something :)
		noDataCounter = 0
		if not msg is '' and '[' in msg and ']' in msg:
		    m = msg.splitlines()	# split to separate lines
		    l = m[m.index('') + 1:]	# skip over header part
		    Logger.info('%s: (%d) %s' % (whoami(), self.screenIndex, str(l)))
		    ####### TODO:


	    else:
		Logger.warning('%s: (%d) Reinit connection: %s' % (whoami(), self.screenIndex, addr))
		try:
		    self.socket.close()
		except: pass

		try:
		    time.sleep(5)
		    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		    self.socket.connect(a)
		    time.sleep(1)
		    fcntl.fcntl(self.socket, fcntl.F_SETFL, os.O_NONBLOCK)
		    time.sleep(1)
		    self.socket.send(SERVER_REQ)
		except:
		    self.socket = None
		    time.sleep(5)


    def dbus_worker(self, params):
	"DBUS thread"
	if not send_dbus(DBUS_PLAYERNAME + str(self.screenIndex), params):
	    self.restart_player_window(self.screenIndex)


    def dbus_command(self, params=[]):
	"d-bus command"
	Logger.debug(whoami()+': ' + str(params))

	Thread(target=self.dbus_worker, kwargs={'params': params}).start()


    def hidePlayer(self):
	"hide video player area"

	Logger.debug(whoami()+':')

	self.color = INACTIVE_DISPLAY_BACKGROUND
	self.actScreen.bgcolor = self.color


    def setActive(self, active=True):
	"add or remove active flag"
	global current_call, scr_mode

	Logger.debug('%s: index=%d active=%d scr_mode=%d' % (whoami(), self.screenIndex, active, scr_mode))

	if current_call: return

	self.color = ACTIVE_DISPLAY_BACKGROUND if active and (scr_mode != 1) else INACTIVE_DISPLAY_BACKGROUND

	self.actScreen.bgcolor = self.color


    def printInfo(self):
	"print class info"
	Logger.debug('Display: id=%d area=%s IP=%s SIPcall=%s stream=%s'\
	    % (self.screenIndex, self.playerPosition, self.serverAddr, self.sipcall, self.streamUrl))


# ##############################################################################

class Indoor(FloatLayout):

    lib = None
    outgoingCall = False
    dnd_mode = False
    appRestartEvent = None
    mediaErrorFlag = False
    popupSettings = None
    volslider = None
    micslider = None

    def __init__(self, **kwargs):
	"app init"
        global BUTTON_DO_CALL, BUTTON_CALL_ANSWER, BUTTON_CALL_HANGUP
        global BUTTON_DOOR_1, BUTTON_DOOR_2
	global APP_NAME, SCREEN_SAVER, BRIGHTNESS, WATCHES, RING_TONE
        global main_state, docall_button_global, mainLayout, scrmngr, config

        super(Indoor, self).__init__(**kwargs)

	mainLayout = self

	self.testPlayerIdx = 0
	self.loseNextTouch = False

	self.displays = []

	self.screenTimerEvent = None

        main_state = 0
        self.info_state = 0
        self.myprocess = None

	self.scrmngr = self.ids._screen_manager
	scrmngr = self.scrmngr
	self.sipServerAddr = ''

        # nacitanie konfiguracie
        try:
	    APP_NAME = config.get('about', 'app_name')
        except:
            Logger.warning('Indoor init: ERROR 3 = read config file!')

	watches.APP_LABEL = APP_NAME

        try:
	    value = config.get('command', 'watches').strip()
	    if value in 'analog' or value in 'digital': WATCHES = value
	    else: WATCHES = 'None'
        except:
            Logger.warning('Indoor init: ERROR 4 = read config file!')

        try:
	    screen_saver = config.getint('command', 'screen_saver')
	    if screen_saver > 0 and screen_saver < 120: SCREEN_SAVER = screen_saver * 60
        except:
            Logger.warning('Indoor init: ERROR 5 = read config file!')

        try:
	    self.dnd_mode = config.getint('command', 'dnd_mode') > 0
        except:
            Logger.warning('Indoor init: ERROR 6 = read config file!')

        try:
	    br = config.getint('command', 'brightness')
	    if br > 0 and br < 256: BRIGHTNESS = int(br * 2.55)
        except:
            Logger.warning('Indoor init: ERROR 7 = read config file!')
	    BRIGHTNESS = 255

	send_command(BRIGHTNESS_SCRIPT + ' ' + str(BRIGHTNESS))

        try:
	    RING_TONE = config.get('devices', 'ringtone').strip()
        except:
            Logger.warning('Indoor init: ERROR 11 = read config file!')
	    RING_TONE = 'oldphone.wav'

	itools.PHONERING_PLAYER = APLAYER + ' ' + APARAMS + RING_TONE

        try:
            BUTTON_DO_CALL = config.get('gui', 'btn_docall')
            BUTTON_CALL_ANSWER = config.get('gui', 'btn_call_answer')
            BUTTON_CALL_HANGUP = config.get('gui', 'btn_call_hangup')
            BUTTON_DOOR_1 = config.get('gui', 'btn_door_1')
            BUTTON_DOOR_2 = config.get('gui', 'btn_door_2')
        except:
            Logger.warning('Indoor init: ERROR 8 = read config file!')

#        self.ids.btnDoor1.text = BUTTON_DOOR_1
#        self.ids.btnDoor1.color = COLOR_BUTTON_BASIC
#        self.ids.btnDoor2.text = BUTTON_DOOR_2
#        self.ids.btnDoor2.color = COLOR_BUTTON_BASIC
        docall_button_global = self.ids.btnDoCall
#        docall_button_global.text = BUTTON_DO_CALL
#        docall_button_global.color = COLOR_BUTTON_BASIC
#	self.ids.btnScreenClock.color = COLOR_ERROR_CALL
#	self.ids.btnSetOptions.color = COLOR_ERROR_CALL

	self.infoText = self.ids.txtBasicLabel

        self.init_myphone()

	self.init_screen()
	self.init_sliders()

        self.infinite_event = Clock.schedule_interval(self.infinite_loop, 6.9)
        Clock.schedule_interval(self.info_state_loop, 10.)


    def init_screen(self):
	"define app screen"
	global config, scr_mode

	Logger.debug(whoami()+':')

	scr_mode = 0
	try:
	    scr_mode = config.getint('gui', 'screen_mode')
	except:
            Logger.warning('Indoor init_screen: ERROR 9 = read config file!')
	    scr_mode = 0

	if scr_mode == 1:
	    wins = ['0,0,800,432']
	    self.ids.cameras1.remove_widget(self.ids.videoLabel2)
	    self.ids.cameras2.remove_widget(self.ids.videoLabel3)
	    self.ids.cameras2.remove_widget(self.ids.videoLabel4)
	    self.ids.cameras.remove_widget(self.ids.cameras2)
	elif scr_mode == 2:
	    wins = ['0,0,800,216', '0,216,800,432']
	    self.ids.cameras1.remove_widget(self.ids.videoLabel2)
	    self.ids.cameras2.remove_widget(self.ids.videoLabel4)
	elif scr_mode == 3:
	    wins = ['0,0,400,432', '400,0,800,432']
	    self.ids.cameras2.remove_widget(self.ids.videoLabel3)
	    self.ids.cameras2.remove_widget(self.ids.videoLabel4)
	    self.ids.cameras.remove_widget(self.ids.cameras2)
	else:
	    wins = ['0,0,400,216', '400,0,800,216', '0,216,400,432', '400,216,800,432']

        Logger.warning('win1 size: ' + str(self.ids.cameras1.size) + ' ' + str(wins))

	for i in range(0,len(wins)):
	    win = wins[i]
	    serv = config.get('common', 'server_ip_address_'+str(i + 1)).strip()
	    sipc = config.get('common', 'sip_call'+str(i + 1)).strip()
	    vid = config.get('common', 'server_stream_'+str(i + 1)).strip()
	    relay = 'http://' + serv + '/cgi-bin/remctrl.sh?id='
#	    try:
#		relay = config.get('common', 'server_relay_'+str(i + 1)).strip()
#	    except:
#        	Logger.warning('Indoor init_screen: ERROR 12 = read config file!')
#		relay = 'http://' + serv + '/cgi-bin/remctrl.sh?id='
#
#	    self.dbg(whoami() + ' relay: ' + str(relay))

	    displ = BasicDisplay(win,serv,sipc,vid,relay)
	    self.displays.append(displ)

	self.scrmngr.current = CAMERA_SCR

	# prepare settings:
	App.get_running_app().open_settings()
	App.get_running_app().close_settings()

	self.setButtons(False)

	self.displays[0].setActive()


    def init_myphone(self):
	"sip phone init"
        global acc, config

	Logger.debug(whoami()+':')

        # Create library instance
        lib = pj.Lib()
	self.lib = lib

	accounttype = 'peer-to-peer'
	try:
	    accounttype = config.get('sip', 'sip_mode').strip()
	except:
            Logger.warning('Indoor init_myphone: ERROR 10 = read config file!')

        try:
            # Init library with default config and some customized logging config
            lib.init(log_cfg = pj.LogConfig(level=LOG_LEVEL, callback=log_cb),\
		    media_cfg = setMediaConfig(), licence=1)

	    comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    comSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	    # bug fix: bad PJSIP start - port in use with another process
	    send_command("netstat -tulpn | grep :5060 | awk '{print $6}' | sed -e 's/\\//\\n/g' | awk 'NR==1 {print $1}' | xargs kill -9")

	    # Create UDP transport which listens to any available port
	    transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5060))

            # Start the library
            lib.start()

	    cl = lib.enum_codecs()
	    for c in cl:
		Logger.debug(whoami() + ' CODEC ' + c.name + ' priority ' + str(c.priority))

	    # Create local account
	    if accounttype in 'peer-to-peer':
        	acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())
		self.sipServerAddr = ''
	    else:
		s = str(config.get('sip', 'sip_server_addr')).strip()
		u = str(config.get('sip', 'sip_username')).strip()
		p = str(config.get('sip', 'sip_p4ssw0rd')).strip()
		self.sipServerAddr = s

		acc_cfg = pj.AccountConfig(domain=s, username=u, password=p)
#		acc_cfg = pj.AccountConfig()
#		acc_cfg.id = "sip:" + u + "@" + s
#		acc_cfg.reg_uri = "sip:" + s + ":5060"
#		acc_cfg.proxy = [ "sip:" + s + ";lr" ]
#		acc_cfg.auth_cred = [pj.AuthCred("*", u, p)]

		acc = lib.create_account(acc_cfg)
		cb = MyAccountCallback(acc)
		acc.set_callback(cb)

	    Logger.info(whoami()+': Listening on %s port %d Account type=%s SIP server=%s'\
		% (transport.info().host, transport.info().port, accounttype, self.sipServerAddr))

        except pj.Error, e:
            Logger.critical("pjSip Exception: " + str(e))

            lib.destroy()
            self.lib = lib = None
	    docall_button_global.text = "No Licence"
	    docall_button_global.color = COLOR_ERROR_CALL
	    docall_button_global.disabled = True
	    docall_button_global.imgpath = ERROR_CALL_IMG


    def info_state_loop(self, dt):
	"state loop"
        global current_call, active_display_index, docall_button_global, BUTTON_DO_CALL, COLOR_BUTTON_BASIC

#	Logger.debug(whoami()+': call='+str(current_call)+' state='+str(self.info_state))

        if not current_call is None: self.info_state = 0

        if self.info_state == 0:
            if current_call is None:
		self.info_state = 1
	    else:
		self.displays[active_display_index].dbus_command(TRANSPARENCY_VIDEO_CMD + [str(255)])
        elif self.info_state == 1:
            self.info_state = 2
	    # test if player is alive:
	    val = 255 if self.scrmngr.current in CAMERA_SCR else 0
	    self.displays[self.testPlayerIdx].dbus_command(TRANSPARENCY_VIDEO_CMD + [str(val)])
	    self.testPlayerIdx += 1
	    self.testPlayerIdx %= len(self.displays)
        elif self.info_state == 2:
            self.info_state = 0
	    if not self.lib is None and self.scrmngr.current in CAMERA_SCR:
#		docall_button_global.text = BUTTON_DO_CALL + ' (DND)' if self.dnd_mode else BUTTON_DO_CALL
#		docall_button_global.color = COLOR_BUTTON_BASIC
		self.setButtons(False)

	if self.lib is None:
	    docall_button_global.text = "No Licence"
	    docall_button_global.color = COLOR_ERROR_CALL
	    docall_button_global.disabled = True
	    docall_button_global.imgpath = ERROR_CALL_IMG


    def infinite_loop(self, dt):
	"main neverendig loop"
        global current_call, active_display_index, procs

	if len(procs) == 0: return

	for idx, p in enumerate(procs):
	    if p.poll() is not None:
#		Logger.debug( "Process" + str(idx) + " (" + str(p.pid) + ") is dead" )
		try:
		    p.kill()
		except:
		    pass
		if current_call is None or idx == active_display_index:
		    procs[idx] = self.displays[idx].initPlayer()


    def startScreenTiming(self):
	"start screen timer"
	global SCREEN_SAVER

        Logger.debug('ScrnEnter: screen saver at %d sec' % SCREEN_SAVER)

	if self.screenTimerEvent: Clock.unschedule(self.screenTimerEvent)
        if SCREEN_SAVER > 0:
	    self.screenTimerEvent = Clock.schedule_once(self.return2clock, SCREEN_SAVER)

	send_command(UNBLANK_SCRIPT)
	send_command(BACK_LIGHT_SCRIPT + ' 0')


    def return2clock(self, *args):
	"swap screen to CLOCK"
	global current_call, WATCHES

        Logger.info(whoami() + ': %s --> %s' % (self.scrmngr.current, WATCHES))

        Clock.unschedule(self.screenTimerEvent)
	self.screenTimerEvent = None

	if current_call is None and self.scrmngr.current in CAMERA_SCR:
	    self.scrmngr.current = WATCH_SCR if WATCHES in 'analog' else DIGITAL_SCR
	    if WATCHES in 'None': send_command(BACK_LIGHT_SCRIPT + ' 1')


    def finishScreenTiming(self):
	"finist screen timer"

        Logger.debug('ScrnLeave: ')

        Clock.unschedule(self.screenTimerEvent)
	self.screenTimerEvent = None


    def swap2camera(self):
	"swap screen to CAMERA"

        Logger.info(whoami()+':')

	self.on_touch_up(None)
	self.scrmngr.current = CAMERA_SCR


    def enterCameraScreen(self):
	"swap screen to CAMERA"
	global current_call

        Logger.debug(whoami() + ': call=' + str(current_call))

	if current_call is None: self.showPlayers()


    def callback_btn_docall(self):
	"make outgoing call"
        global current_call, active_display_index, docall_button_global, BUTTON_DO_CALL
	global ring_event

	Logger.info(whoami() + ': call=' + str(current_call) + ' state=' + str(main_state) +\
	    ' outgoing=' + str(self.outgoingCall))

	if len(procs) == 0: return

        if current_call:
	    Logger.info(whoami() + ' call state: ' + str(current_call.dump_status()))

            if current_call.is_valid() and main_state == pj.CallState.EARLY:
		if not ring_event is None: Clock.unschedule(ring_event)
		ring_event = None
                stopWAV()

		if not self.outgoingCall:
        	    current_call.answer(200)
		else:
		    current_call.hangup()
            else:
                if current_call.is_valid(): current_call.hangup()
		current_call = None
		self.outgoingCall = False
#		docall_button_global.text = BUTTON_DO_CALL
#		docall_button_global.color = COLOR_BUTTON_BASIC
		docall_button_global.imgpath = MAKE_CALL_IMG
		self.setButtons(False)
	else:
	    target = self.displays[active_display_index].sipcall

	    if len(target) == 0: return

	    if len(self.sipServerAddr) and '.' not in target:
		target = target + '@' + self.sipServerAddr

	    lck = self.lib.auto_lock()
	    self.outgoingCall = True
	    if make_call('sip:' + target + ':5060') is None:
		txt = 'Audio ERROR' if self.mediaErrorFlag else '--> ' + str(active_display_index + 1) + ' ERROR'
		docall_button_global.color = COLOR_ERROR_CALL
		docall_button_global.text = txt
		docall_button_global.imgpath = ERROR_CALL_IMG
	    else:
		self.setButtons(True)
	    del lck


    def gotResponse(self, req, results):
	"relay result"
        Logger.debug('Relay: req=' + str(req) + ' res=' + results)


    def setRelayRQ(self, relay):
	"send relay request"
        global active_display_index

        Logger.trace('SetRelay: ' + relay)

	if len(procs) == 0: return

        req = UrlRequest(self.displays[active_display_index].relayCmd + relay,\
                on_success = self.gotResponse, timeout = 5)


    def callback_btn_door1(self):
	"door 1 button"
        Logger.debug(BUTTON_DOOR_1+':')
        self.setRelayRQ('relay1')


    def callback_btn_door2(self):
	"door 2 button"
        Logger.debug(BUTTON_DOOR_2+':')
        self.setRelayRQ('relay2')


    def callback_set_options(self):
	"start settings"
        Logger.debug(whoami() + ": ")

	self.hidePlayers()

        self.popupSettings = Popup(title="Options",
              content=SettingsPopupDlg(),
              size_hint=(0.86, 0.96), auto_dismiss=False)
	
#              on_dismiss=self.openAppSettings)
#	self.popupSettings.detailbutton.bind(on_press=self.openAppSettings)
	self.popupSettings.open()

##	App.get_running_app().open_settings()
##	self.scrmngr.current = SETTINGS_SCR


    def closePopupSettings(self):
	self.popupSettings.dismiss()
	self.popupSettings = None


    def openAppSettings(self, popup):
	"swap to Settings screen"
	Logger.debug('%s: %s' % (whoami(), str(popup)))
	Logger.debug(popup.text)
	"""
	if popup.content.text in '1234':
	    self.scrmngr.current = SETTINGS_SCR
	    App.get_running_app().open_settings()
	else:
	    self.showPlayers()
	"""
	self.scrmngr.current = SETTINGS_SCR
	App.get_running_app().open_settings()


    def callback_set_voice(self, value):
	"volume buttons"
	global AUDIO_VOLUME, current_call

	Logger.debug('%s: value=%d' % (whoami(), value))

	if current_call is None:
	    if value == 1:
		self.callback_set_options()
	    else:
		Clock.schedule_once(self.return2clock, .2)
	"""
	else:
	    vol = AUDIO_VOLUME + int(value) * 20
	    if vol > 80: vol = 100
	    elif vol > 60: vol = 80
	    elif vol > 40: vol = 60
	    elif vol > 20: vol = 40
	    else: vol = 20
	    AUDIO_VOLUME = vol

	    self.ids.btnScreenClock.disabled = vol < 40
	    self.ids.btnSetOptions.disabled = vol > 80
	    self.ids.btnScreenClock.imgpath = VOLUME_DISABLED_IMG if AUDIO_VOLUME < 40 else VOLUME_DOWN_IMG
	    self.ids.btnSetOptions.imgpath = VOLUME_DISABLED_IMG if AUDIO_VOLUME > 80 else VOLUME_UP_IMG

	    send_command(SETVOLUME_SCRIPT + ' ' + str(AUDIO_VOLUME))
	"""


    def restart_player_window(self, idx):
	"process is bad - restart"

	Logger.info(whoami()+': idx='+str(idx))

	self.displays[idx].hidePlayer()
	send_command("ps aux | grep omxplayer"+str(idx)+" | grep -v grep | awk '{print $2}' | xargs kill -9")
	send_command(CMD_KILL + str(procs[idx].pid))


    def supporter1(self, dt):
	"clear restart flag"
	Logger.debug(whoami()+ ': clear restart flag')
	self.appRestartEvent = None


    def checkTripleTap(self,touch):
	"check if triple tap is in valid area, if yes -> finish app"

	Logger.info(whoami()+':')

	x = touch.x
	y = touch.y
	if x < 50 and y > 430:
	    if self.appRestartEvent is None:
		self.appRestartEvent = Clock.schedule_once(self.supporter1, 5.)
	    else:
		Clock.unschedule(self.appRestartEvent)
		self.appRestartEvent = None

	if x > 730 and y > 430 and not self.appRestartEvent is None:
	    Logger.error(whoami() + ': valid triple tap -> restart')
	    App.get_running_app().stop()


    def on_touch_up(self, touch):
	"process touch up event"
	global active_display_index, current_call

	Logger.info(whoami()+': loseNext='+str(self.loseNextTouch))
	if not touch is None:
	    Logger.debug(whoami()+': touch=%d,%d double=%d triple=%d'\
		% (touch.x, touch.y, touch.is_double_tap, touch.is_triple_tap))

	if self.loseNextTouch:
	    self.loseNextTouch = False
	    return

#	if not self.collide_point(*touch.pos): return
#	Logger.debug( whoami() +': '+ str(self.collide_point(*touch.pos)))

	if len(procs) == 0: return

	if not touch is None and touch.is_triple_tap:
	    self.checkTripleTap(touch)

	if not touch is None and touch.is_double_tap:
	    if not current_call and self.scrmngr.current in CAMERA_SCR:
		self.restart_player_window(active_display_index)
	    return

	if current_call is None: self.startScreenTiming()

#	for child in self.walk():
#	    if child is self: continue
#	    if child.collide_point(*touch.pos):
#		Logger.trace('%s: child colide point = %d, %d' %(whoami(), touch.x, touch.y))
#		return

	if touch is None:
	    self.loseNextTouch = True
	    return

	if not self.scrmngr.current in CAMERA_SCR or not current_call is None: return

	rx = int(round(touch.x))
	ry = int(round(touch.y))

	for idx, d in enumerate(self.displays):
	    t = d.testTouchArea(rx, ry)
	    if t:
		active_display_index = idx
	    else:
		d.setActive(False)

	self.displays[active_display_index].setActive()


    def showPlayers(self):
	"d-bus command to show video"

	Logger.debug(whoami()+': ')

	for d in self.displays:
	    d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(255)])

	self.displays[active_display_index].resizePlayer()
	self.infoText.text = ''
	self.displays[active_display_index].setActive()


    def worker1serial(self):
	"thread - hide video serial"
	for d in self.displays:
	    d.hidePlayer()
	    d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(0)])


    def hidePlayers(self, serial=False):
	"d-bus command to hide video"
	Logger.debug(whoami()+': ')

	if serial:
	    Thread(target=self.worker1serial).start()
	else:
	    for d in self.displays:
		d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(0)])


    def setButtons(self, visible):
	"set buttons (ScrSaver, Options, Voice+-) to accurate state"
	global AUDIO_VOLUME

	Logger.debug('%s: volume=%d' % (whoami(), AUDIO_VOLUME))

	if visible:
	    self.ids.btnScreenClock.disabled = True #AUDIO_VOLUME < 40
	    self.ids.btnSetOptions.disabled = True #AUDIO_VOLUME > 80
	    self.ids.btnScreenClock.imgpath = NO_IMG
	    self.ids.btnSetOptions.imgpath = NO_IMG
#	    self.ids.btnScreenClock.imgpath = VOLUME_DISABLED_IMG if AUDIO_VOLUME < 40 else VOLUME_DOWN_IMG
#	    self.ids.btnSetOptions.imgpath = VOLUME_DISABLED_IMG if AUDIO_VOLUME > 80 else VOLUME_UP_IMG
	else:
	    self.ids.btnScreenClock.imgpath = SCREEN_SAVER_IMG
	    self.ids.btnSetOptions.imgpath = SETTINGS_IMG
	    self.ids.btnScreenClock.disabled = False
	    self.ids.btnSetOptions.disabled = False


    def init_sliders(self):
	"prepare volume sliders"
	global AUDIO_VOLUME

	Logger.debug('%s:' % (whoami()))

	self.micslider = SliderArea()
	self.micslider.imgpath = MICROPHONE_IMG
	self.micslider.on_val = self.onMicVal
	self.micslider.val = 100
	self.volslider = SliderArea()
	self.volslider.imgpath = VOLUME_IMG
	self.volslider.on_val = self.onVolVal
	self.volslider.val = AUDIO_VOLUME


    def onMicVal(self):
	"set microphone value"
	Logger.debug('%s: %d' % (whoami(), self.micslider.audioslider.value))


    def onVolVal(self):
	"set speaker volume value"
	global AUDIO_VOLUME

	Logger.debug('%s: %d' % (whoami(), self.volslider.audioslider.value))
	AUDIO_VOLUME = self.volslider.audioslider.value
	send_command(SETVOLUME_SCRIPT + ' ' + str(AUDIO_VOLUME))


    def add_sliders(self):
	"add sliders to the working area"
	Logger.debug('%s:' % (whoami()))

	l = self.ids.workarea
	Logger.debug('%s: cnt:%d' % (whoami(), len(l.children)))
	if len(l.children) > 1: return

	l.add_widget(self.micslider, 1)
	l.add_widget(self.volslider)


    def del_sliders(self):
	"delete sliders from the working area"
	Logger.debug('%s:' % (whoami()))

	l = self.ids.workarea
	l.remove_widget(self.micslider)
	l.remove_widget(self.volslider)


    def findTargetWindow(self, addr):
	"find target window according to calling address"
	global active_display_index

        Logger.info('find target window: address=' + addr)

	ret = False
	self.infoText.text = addr

	if addr != '':
	    active_display_index = 0
	    for idx, d in enumerate(self.displays):
		d.setActive(False)
		d.hidePlayer()
		if not ret and d.sipcall in addr and d.sipcall != '':
		    active_display_index = idx
		    self.infoText.text = d.sipcall
		    d.resizePlayer('90,10,710,390')
		    ret = True
		else:
		    d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(0)])

	if ret:
	    self.add_sliders()

	    if not self.scrmngr.current in CAMERA_SCR:
		self.displays[active_display_index].dbus_command(TRANSPARENCY_VIDEO_CMD + [str(255)])

	self.scrmngr.current = CAMERA_SCR

	return ret


# ###############################################################

class IndoorApp(App):

    restartAppFlag = False

    def build(self):
	global config

        Logger.warning('Hello Indoor 2.0')

	self.config = config

	kill_subprocesses()

##        Config.set('kivy', 'keyboard_mode','')
        Logger.debug('Configuration: keyboard_mode=%r, keyboard_layout=%r'\
	    % (Config.get('kivy', 'keyboard_mode'), Config.get('kivy', 'keyboard_layout')))

	self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False

	self.changeInet = False
	self.get_volume_value()

	return Indoor()


#    def on_start(self):
#        self.dbg(whoami())
#
#    def on_stop(self):
#        self.dbg(whoami())
#	self.root.stop.set()


    def build_config(self, cfg):
	"build config"
	global config

        Logger.debug(whoami()+': ')

	config.setdefaults('command', {
	    'screen_saver': 1,
	    'dnd_mode': 0,
	    'brightness': 100,
	    'watches': 'analog' })
	config.setdefaults('sip', {
	    'sip_mode': 'peer-to-peer',
	    'sip_server_addr': '',
	    'sip_username': '',
	    'sip_p4ssw0rd': '' })
	config.setdefaults('devices', {
	    'sound_device_in': '',
	    'sound_device_out': '',
	    'ringtone': 'oldphone.wav',
	    'volume': 100 })
	config.setdefaults('gui', {
	    'screen_mode': 0 }) #,
#	    'btn_docall': 'Make Call',
#	    'btn_call_answer': 'Answer Call',
#	    'btn_call_hangup': 'HangUp Call',
#	    'btn_door_1': 'Open Door 1',
#	    'btn_door_2': 'Open Door 2' })
	config.setdefaults('common', {
	    'server_ip_address_1': '192.168.1.250',
	    'server_stream_1': 'http://192.168.1.250:80/video.mjpg',
	    'sip_call1': '',
	    'server_ip_address_2': '',
#	    'server_stream_2': 'http://192.168.1.241:8080/stream/video.mjpeg',
	    'server_stream_2': '',
	    'sip_call2': '',
	    'server_ip_address_3': '',
#	    'server_stream_3': 'http://192.168.1.241:8080/stream/video.mjpeg',
	    'server_stream_3': '',
	    'sip_call3': '',
	    'server_ip_address_4': '',
	    'server_stream_4': '',
	    'sip_call4': '' })

	s = get_info(SYSTEMINFO_SCRIPT).split()
	config.setdefaults('about', {
	    'app_name': 'Indoor 2.0',
	    'app_ver': '2.0.0.0',
	    'licencekey': '0000-000000-0000-000000-0000',
	    'regaddress': '',
	    'serial': s[1] })
	config.set('about', 'serial', s[1])

	dns = ''
	try:
	    dns = s[8]
	except:
	    dns = ''

	config.setdefaults('system', {
	    'inet': s[2],
	    'ipaddress': s[3],
	    'gateway': s[6],
	    'netmask': s[4],
	    'dns': dns })
	config.set('system', 'inet', s[2])
	config.set('system', 'ipaddress', s[3])
	config.set('system', 'gateway', s[6])
	config.set('system', 'netmask', s[4])
	config.set('system', 'dns', dns)


    def get_uptime_value(self):
	"retrieve system uptime"
	with open('/proc/uptime', 'r') as f:
	    uptime_seconds = float(f.readline().split()[0]) or 0
	    uptime_string = str(timedelta(seconds = uptime_seconds))

        Logger.debug(whoami() + ': uptime=' + uptime_string)

	return uptime_string


    def get_volume_value(self):
	"retrieve current volume level"
	global AUDIO_VOLUME

        Logger.debug(whoami()+': ')

	s = get_info(VOLUMEINFO_SCRIPT).split()
	if len(s) < 4:
	    vol = 0		# script problem!
	else:
	    vol = int(round(float(s[1]) / (int(s[3]) - int(s[2])) * 100.0)) or 0

	# available volume steps:
	if vol > 80: vol = 100
	elif vol > 60: vol = 80
	elif vol > 40: vol = 60
	elif vol > 20: vol = 40
	else: vol = 20
	AUDIO_VOLUME = vol

	return vol


    def build_settings(self, settings):
	"display settings screen"
	global config

        Logger.debug(whoami()+': ')

	settings.register_type('buttons', SettingButtons)

	config.set('devices', 'volume', AUDIO_VOLUME)
	config.set('devices', 'ringtone', RING_TONE)

	asystem = settings_system
	"""
	# enable|disable network parameters
	vDhcp = config.get('system', 'inet') in 'dhcp'
	sys = json.loads(settings_system)
	asystem = []
	for s in sys:
	    item = s
	    if s['type'] not in 'title' and s['key'] not in 'inet': item['disabled'] = vDhcp
	    asystem.append(item)
	asystem = json.dumps(asystem)
	"""

	asip = settings_sip
	"""
	# enable|disalbe SIP parameters
	vSip = config.get('sip', 'sip_mode')
	sys = json.loads(settings_sip)
	asip = []
	for s in sys:
	    item = s
	    if s['type'] not in 'title' and s['key'] not in 'sip_mode': item['disabled'] = vSip
	    asip.append(item)
	asip = json.dumps(asip)
	"""

	acomm = settings_outdoor
	"""
	# enable|disalbe players
	wins = config.getint('gui', 'screen_mode')
	if wins == 0 or wins == 4:
	    acomm = settings_outdoor
	elif wins == 1:
	    enabledWin = '1'
	    sys = json.loads(settings_outdoor)
	    acomm = []
	    for s in sys:
		item = s
		if not (s['type'] not in 'title' and enabledWin not in s['key']):
		    acomm.append(item)
	    acomm = json.dumps(acomm)
	else:
	    sys = json.loads(settings_outdoor)
	    acomm = []
	    for s in sys:
		item = s
		if not (s['type'] not in 'title' and ('3' in s['key'] or '4' in s['key'])):
		    acomm.append(item)
	    acomm = json.dumps(acomm)
	"""

        settings.add_json_panel('Application',
                                config,
                                data=settings_app)
        settings.add_json_panel('GUI',
                                config,
                                data=settings_gui)
        settings.add_json_panel('Outdoor Devices',
                                config,
                                data=acomm)
        settings.add_json_panel('Audio Device',
                                config,
                                data=settings_audio)
        settings.add_json_panel('SIP',
                                config,
                                data=asip)
        settings.add_json_panel('Network',
                                config,
                                data=asystem)
        settings.add_json_panel('Service',
                                config,
                                data=settings_services)
        settings.add_json_panel('About',
                                config,
                                data=settings_about)


    def display_settings(self, settings):
	"display settings"
	global mainLayout

        Logger.debug(whoami()+': ')

#        return super(IndoorApp, self).display_settings(settings)
	mainLayout.ids.settings.add_widget(settings)


    def on_config_change(self, cfg, section, key, value):
	"config item changed"
	global config, SCREEN_SAVER, BRIGHTNESS, WATCHES, VOLUME, mainLayout

        Logger.info(whoami()+': sec=%s key=%s val=%s' % (section, key, value))
	token = (section, key)
	value = value.strip()

	config.set(section, key, value)
	config.write()

	if section == 'common':
	    self.restartAppFlag = True
	elif token == ('command', 'brightness'):
	    try:
		v = int(value)
		BRIGHTNESS = int(v * 2.55)
	    except:
		BRIGHTNESS = 255
	    send_command(BRIGHTNESS_SCRIPT + ' ' + str(BRIGHTNESS))
	elif token == ('command', 'dnd_mode'):
	    mainLayout.dnd_mode = int(value) > 0
	elif token == ('command', 'screen_saver'):
	    try:
		v = int(value)
		SCREEN_SAVER = v * 60
	    except:
		SCREEN_SAVER = 0
	elif token == ('command', 'watches'):
	    if value in 'analog' or value in 'digital': WATCHES = value
	    else: WATCHES = 'None'
	elif token == ('devices', 'volume'):
	    AUDIO_VOLUME = value
	    send_command(SETVOLUME_SCRIPT + ' ' + str(AUDIO_VOLUME))
	elif token == ('devices', 'ringtone'):
	    RING_TONE = value
	    stopWAV()
	    itools.PHONERING_PLAYER = APLAYER + ' ' + APARAMS + RING_TONE
	    playWAV(3.0)
	elif section in 'system' and (key in ['ipaddress', 'netmask', 'gateway', 'dns']):
	    if config.get('system', 'inet') in 'dhcp':
#		config.set(section, key, self.config.get(section, key))
		config.set(section, key, config.getdefault(section, key))
		config.write()
	    else:
		self.changeInet = True
	elif section in 'sip' and (key in ['sip_server_addr', 'sip_username', 'sip_p4ssw0rd']):
	    if config.get('sip', 'sip_mode') in 'peer-to-peer':
		config.set(section, key, self.config.get(section, key))
#		config.set(section, key, config.getdefault(section, key))
		config.write()
	    else:
		self.changeInet = True
	elif token == ('service', 'buttonpress'):
	    if 'button_status' == value:
		self.myAlertBox('App status', 'uptime: ' + self.get_uptime_value())
	elif token == ('about', 'buttonregs'):
	    if 'button_regs' == value:
		send_regs_request(registration.REGISTRATION_URL_ADDRESS,\
		    [self.config.get('about','serial'), self.config.get('about','regaddress'), self.config.get('about','licencekey')])
		self.myAlertBox('Registration', 'Your licence key will come to your email address till 3 working days')
	elif token == ('service', 'buttonlogs'):
	    if 'button_loghist' == value:
	        # LoggerHistory.history:
	        recent_log = [('%d %s' % (record.levelno, record.msg)) for record in LoggerHistory.history] #reversed(LoggerHistory.history
		self.myAlertListBox('Log messages history', recent_log)
	elif token == ('service', 'app_rst'):
	    if 'button_app_rst' == value:
		self.myAlertBox('WARNING', 'Application is going to restart!', self.popupClosed, False)
	elif token == ('system', 'inet'):
	    self.changeInet = True
	elif 'gui' in section or token == ('about', 'licencekey') or token == ('sip', 'sip_mode'):
	    self.restartAppFlag = True
#	    self.destroy_settings()
#	    self.open_settings()


    def popupClosed(self, popup):
	"restart App after alert box"

        Logger.debug(whoami()+': ')

	kill_subprocesses()

	App.get_running_app().stop()


    def close_settings(self, *args):
	"close button pressed"
	global scrmngr, mainLayout, config

        Logger.debug(whoami()+': ')

	mainLayout.ids.settings.clear_widgets()

	if self.changeInet or self.restartAppFlag:
	    if self.changeInet: # start script
		send_command(SETIPADDRESS_SCRIPT\
			 + ' ' + config.get('system', 'inet')\
			 + ' ' + config.get('system', 'ipaddress')\
			 + ' ' + config.get('system', 'netmask')\
			 + ' ' + config.get('system', 'gateway')\
			 + ' ' + config.get('system', 'dns'))

	    self.myAlertBox('App info', 'Application is going to restart to apply your changes!', self.popupClosed, False)
	else:
	    self.changeInet = False
	    scrmngr.current = CAMERA_SCR


    def myAlertBox(self, titl, txt, cb=None, ad=True):
	"Alert box"
	global scrmngr

	Logger.debug(whoami()+': title='+titl+' msg='+txt)

	if not cb is None:
	    scrmngr.current = WAIT_SCR
	    txt = txt + '\n\nPress OK'

	box = BoxLayout(orientation='vertical', spacing=10)
	box.add_widget(Label(text=txt, padding_y=80))
	btn = Button(text='OK', size_hint=(1, 0.4))
	box.add_widget(btn)
	p = Popup(title=titl, content=box, size_hint=(0.8, 0.6), auto_dismiss=ad)
	if cb is None: cb = p.dismiss
	btn.bind(on_press=cb)
	p.bind(on_press=cb)
	p.open()


    def myAlertListBox(self, titl, ldata, cb=None, ad=True):
	"Alert box"
	LJUST = 83

	Logger.debug(whoami()+': title='+titl)

	box = BoxLayout(orientation='vertical', spacing=5)

	# text color:
	c = [int(t[:2]) for t in ldata]
	clr = []
	for x in c:
	    y = (1,1,1,1)
	    if x < 11: y = (1,1,1,1)
	    elif x < 21: y = (.5,1,1,1)
	    elif x < 31: y = (.5,.5,1,1)
	    else: y = (1,.5,0,1)
	    clr.append(y)

	# justify text:
	data = [t[:LJUST] + '...' if len(t) > LJUST else t[:] for t in ldata]

	args_converter = lambda row_idx, rec: {'text': rec,
                                            'size_hint_y': None,
					    'color': clr[row_idx],
                                            'height': 25}

	list_adapter = ListAdapter(data=data, cls=MyListViewLabel,
			    args_converter=args_converter,
			    selection_mode='single', allow_empty_selection=True)

	list_view = ListView(adapter=list_adapter)
	box.add_widget(list_view)

	p = Popup(title=titl, content=box, size_hint=(0.85, 0.95), auto_dismiss=ad)
#	if cb is None: cb = p.dismiss
#	p.bind(on_press=cb)
	p.open()


# ###############################################################
#
# Start
#
# ###############################################################

if __name__ == '__main__':
    IndoorApp().run()
