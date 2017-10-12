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
#from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemLabel
from kivy.uix.popup import Popup
from kivy.uix.settings import Settings, SettingsWithSpinner, SettingsWithSidebar
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

import atexit
#import ConfigParser
import datetime
import errno
import fcntl
import json
import signal
import socket
import StringIO
import subprocess
from threading import Thread

import pjsua as pj

from my_lib import *

from kivy.cache import Cache
Cache._categories['kv.image']['limit'] = 0
Cache._categories['kv.texture']['limit'] = 0


###############################################################
#
# Declarations
#
# ###############################################################

config = get_config()

sipRegEvent = None

# ###############################################################
#
# Functions
#
# ###############################################################

@atexit.register
def kill_subprocesses():
    "tidy up at exit or break"
    global mainLayout

    sendNodeInfo('[***]STOP')

    stop_sw_watchdog()

    Logger.info('%s: destroy lib at exit' % whoami())
    try:
	pj.Lib.destroy()
    except:
	pass

    Logger.info('%s: kill subprocesses at exit' % whoami())
    for proc in procs:
	try:
            proc.kill()
	except:
	    pass

    send_command('pkill -9 omxplayer')


# ###############################################################
#
# Classes
#
# ###############################################################

class MyAccountCallback(pj.AccountCallback):
    "Callback to receive events from account"
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    # ###############################################################
    def on_reg_state(self):
	"SIP account registration callback"
	global sipRegStatus, sipRegEvent

	info = self.account.info()
	sipRegStatus = info.reg_status == 200

        Logger.info("pjSip on_reg_state: Registration complete, status=%d expires in %d sec"\
	    % (info.reg_status, info.reg_expires))
        Logger.debug("pjSip on_reg_state: account reason=%s oltext=%s active=%d olstatus=%s"\
	    % (info.reg_reason, info.online_text, info.reg_active, info.online_status))

	if sipRegStatus:
	    sendNodeInfo('[***]SIPREG: REGISTERED')
	    sendNodeInfo('[***]SIP: FREE')
	    sipRegStatus = True
	else:
	    sendNodeInfo('[***]SIPREG: ERROR ( %d )' % info.reg_status)
	    sipRegStatus = False

	if sipRegEvent: Clock.unschedule(sipRegEvent)
	sipRegEvent = Clock.schedule_once(self.registrationTimerWD, 15 if not sipRegStatus else info.reg_expires + 10)


    # ###############################################################
    def registrationTimerWD(self, dt):
	"SIP registration watch dog"
	global sipRegStatus, sipRegEvent, acc, mainLayout

        Logger.warning("pjSip registration TO, status=%r" % (not sipRegStatus))

	sendNodeInfo('[***]SIP: REG TimeOut')

	sipRegStatus = False

	Clock.schedule_once(lambda dt: mainLayout.init_myphone(), 1)


    # ###############################################################
    def on_incoming_call(self, call):
	"Notification on incoming call"
        global current_call, mainLayout, docall_button_global, ROTATION, active_display_index

	Logger.trace('pjSip %s: DND mode=%d' % (whoami(), mainLayout.dnd_mode))

        if current_call or mainLayout.dnd_mode:
            call.answer(486, "Busy")
            return

	if mainLayout.showVideoEvent or mainLayout.popupSettings:
	    if mainLayout.popupSettings:
		mainLayout.popupSettings.dismiss()
		mainLayout.popupSettings = None
#		mainLayout.showPlayers()
		Window.release_all_keyboards()

	    if mainLayout.showVideoEvent:
		mainLayout.displays[active_display_index].resizePlayer()
		Clock.unschedule(mainLayout.showVideoEvent)
		mainLayout.showVideoEvent = None

	    mainLayout.showPlayers()

        Logger.info("pjSip %s: Incoming call from %s" % (whoami(), call.info().remote_uri))
        current_call = call

	docall_button_global.parent.add_widget(mainLayout.btnReject, 2 if ROTATION in [0,180] else 0)

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180)


# ###############################################################
class MyCallCallback(pj.CallCallback):
    "Callback to receive events from Call"

    sip_call_id_last = '***'
    callTimerEvent = None
    CALL_TIMEOUT = 60 * 3
    RING_TIME = 5.0

    # ###############################################################
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # ###############################################################
    def on_state(self):
	"Notification when call state has changed"
        global current_call, ring_event, main_state, mainLayout, docall_button_global

	ci = self.call.info()
	role = 'CALLER' if ci.role == 0 else 'CALLEE'

	setloginfo(True, 'Call width=%s is %s (%d) last code=%d (%s) as role=%s'\
	    % (ci.remote_uri, ci.state_text, ci.state, ci.last_code, ci.last_reason, role))
#	Logger.info('pjSip on_state: Call width=%s is %s (%d) last code=%d (%s) as role=%s'\
#	    % (ci.remote_uri, ci.state_text, ci.state, ci.last_code, ci.last_reason, role))
	Logger.debug('pjSip on_state: sip_call_id=%s outgoing call=%r current call=%s'\
	    % (ci.sip_call_id, mainLayout.outgoingCall, str(current_call)))

	if main_state == ci.state:# and self.sip_call_id_last == ci.sip_call_id:
	    Logger.warning('pjSip on_state: Call width=%s is %s (%d) last code=%d (%s) as role=%s'\
		% (ci.remote_uri, ci.state_text, ci.state, ci.last_code, ci.last_reason, role))
	    return

	prev_state = main_state
        main_state = ci.state

        if main_state == pj.CallState.EARLY:
	    mainLayout.findTargetWindow(ci.remote_uri)
	    if not ring_event and not mainLayout.outgoingCall:
		ring_event = Clock.schedule_interval(playWAV, self.RING_TIME)
		playWAV(self.RING_TIME)
        else:
	    if ring_event:
		Clock.unschedule(ring_event)
		ring_event = None
		stopWAV()

	if self.sip_call_id_last == ci.sip_call_id:
	    Logger.error('pjSip %s: Unwanted message=%s from %s as %s'\
		% (whoami(), ci.state_text, ci.remote_uri, role))
	    return

	if self.callTimerEvent is None:
	    Clock.unschedule(self.callTimerEvent)
	    self.callTimerEvent = Clock.schedule_once(self.callTimerWD, self.CALL_TIMEOUT)

        if main_state == pj.CallState.INCOMING or main_state == pj.CallState.EARLY:
	    docall_button_global.imgpath = HANGUP_OUTGOING_CALL_IMG if mainLayout.outgoingCall else ANSWER_CALL_IMG
	    mainLayout.setButtons(True)
	    mainLayout.finishScreenTiming()

        elif main_state == pj.CallState.DISCONNECTED:
            current_call = None
	    mainLayout.setButtons(False)
	    docall_button_global.imgpath = DND_CALL_IMG if mainLayout.dnd_mode else MAKE_CALL_IMG
	    docall_button_global.btntext = ''
	    mainLayout.startScreenTiming()
	    mainLayout.del_sliders()
	    mainLayout.showPlayers()
	    mainLayout.outgoingCall = False
	    self.sip_call_id_last = ci.sip_call_id
	    if not self.callTimerEvent is None:
		Clock.unschedule(self.callTimerEvent)
		self.callTimerEvent = None
	    try: docall_button_global.parent.remove_widget(mainLayout.btnReject)
	    except: pass
##	    playTone(BUSY_WAV)
	    sendNodeInfo('[***]SIP: FREE')

        elif main_state == pj.CallState.CONFIRMED:
	    if docall_button_global.imgpath != HANGUP_CALL_IMG:
		docall_button_global.imgpath = HANGUP_CALL_IMG
	    try: docall_button_global.parent.remove_widget(mainLayout.btnReject)
	    except: pass
	    Logger.info('pjSip call status: %s' % self.call.dump_status())
	    sendNodeInfo('[***]SIP: CALL')

        elif main_state == pj.CallState.CALLING:
	    if not current_call is None:
		Logger.warning('pjSip bad call: CALLING state %s <<>> %s' %(str(current_call), str(self.call)))
		self.call.hangup()
		return
##	    playTone(DIAL_WAV)
	    current_call = self.call
#	    docall_button_global.imgpath = ANSWER_CALL_IMG

	setcallstat(outflag=(ci.role==0), status=main_state, prev_status=prev_state, call=ci.remote_uri)
	if main_state == 6: main_state = 0

    # ###############################################################
    def on_media_state(self):
	"Notification when call's media state has changed"
        global mainLayout

        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
	    try:
        	pj.Lib.instance().conf_connect(call_slot, 0)
        	pj.Lib.instance().conf_connect(0, call_slot)
        	Logger.debug("pjSip %s: Media is now active" % whoami())
	    except pj.Error, e:
        	Logger.error("pjSip %s: Media is inactive due to ERROR: %s" % (whoami(), str(e)))
		sendNodeInfo('[***]MEDIA: ERROR')

		mainLayout.mediaErrorFlag = True
		if check_usb_audio() > 0: mainLayout.reinitbackgroundtasks()
        else:
            Logger.debug("pjSip %s: Media is inactive" % whoami())
	    mainLayout.mediaErrorFlag = False

    # ###############################################################
    def callTimerWD(self, dt):
	"SIP call watch dog"
        global current_call, ring_event, main_state, mainLayout, acc

	Logger.warning('%s:' % whoami())

	self.callTimerEvent = None
	main_state = pj.CallState.DISCONNECTED
	mainLayout.setButtons(False)
	docall_button_global.imgpath = DND_CALL_IMG if mainLayout.dnd_mode else MAKE_CALL_IMG
	mainLayout.startScreenTiming()
	mainLayout.del_sliders()
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


# ###############################################################
def make_call(uri):
    "Function to make outgoing call"
    global acc, mainLayout

    Logger.info('%s: %s' % (whoami(), uri))

    if not mainLayout.outgoing_mode: return None

    Logger.info('%s: %s' % (whoami(), uri))

    try:
	if acc != None: return acc.make_call(uri, cb=MyCallCallback(pj.CallCallback))
    except pj.Error, e:
	reason = str(e)
        Logger.error("pjSip %s exception: %s" % (whoami(), reason))
	mainLayout.mediaErrorFlag = True if 'udio' in reason else False
	if mainLayout.mediaErrorFlag and check_usb_audio() > 0:
	    mainLayout.reinitbackgroundtasks()
	    sendNodeInfo('[***]MEDIA: AUDIO ERROR')
	else:
	    sendNodeInfo('[***]SIP: ERROR')

    return None


# ###############################################################

#def log_cb(level, str, len):
#    "pjSip logging callback"
#    Logger.info('pjSip cb: (%d) %s' % (level, str))



# ##############################################################################

class BasicDisplay:
    "basic screen class"

    locks = 0		# stav zamkov na dverach
    checkEvent = 0	# uloha kontroly stavu videa

    def __init__(self,winpos,servaddr,sipcall,streamaddr,relaycmd,rotation=0,aspectratio='fill'):
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
	self.rotation = (360 - rotation) % 360
	self.aspectratio = aspectratio # 'letterbox | stretch | fill'
	self.isPlaying = True

	delta = 2
	self.playerPosition[0] += delta
	self.playerPosition[1] += delta
	self.playerPosition[2] -= 2*delta
	self.playerPosition[3] -= 2*delta

	if aspectratio in ['16:9','4:3']:
	    ### keep aspect ratio:
	    keepW = False
	    if rotation in [0,180] and scr_mode in [2]\
		or rotation in [90,270] and scr_mode in [1,2]:
		keepW = True

	    pheight = self.playerPosition[3] - self.playerPosition[1] if rotation in [0,180] else self.playerPosition[2] - self.playerPosition[0]
	    pwidth = self.playerPosition[2] - self.playerPosition[0] if rotation in [0,180] else self.playerPosition[3] - self.playerPosition[1]

	    pdelta = 0
	    if keepW: #rotation in [0,180]:
		if aspectratio == '16:9':
		    pdelta = int((pheight - (int(pwidth / 16) * 9)) / 2)
		elif aspectratio == '4:3':
		    pdelta = int((pheight - (int(pwidth / 4) * 3)) / 2)
	    else:
		if aspectratio == '16:9':
		    pdelta = int((pwidth - (int(pheight / 9) * 16)) / 2)
		elif aspectratio == '4:3':
		    pdelta = int((pwidth - (int(pheight / 3) * 4)) / 2)

	    if pdelta < 0: pdelta = 0
	    Logger.info('%s: WxH=%dx%d d=%d %s' % (whoami(), pwidth, pheight, pdelta, aspectratio))

	    if pdelta > 0:
		if rotation in [0,180]:
		    if keepW:
			self.playerPosition[1] += pdelta
			self.playerPosition[3] -= pdelta
		    else:
			self.playerPosition[0] += pdelta
			self.playerPosition[2] -= pdelta
		else:
		    if not keepW:
			self.playerPosition[1] += pdelta
			self.playerPosition[3] -= pdelta
		    else:
			self.playerPosition[0] += pdelta
			self.playerPosition[2] -= pdelta

	self.playerPosition = [str(i) for i in self.playerPosition]

	procs.append(self.initPlayer())

	self.startThread()

	self.color = INACTIVE_DISPLAY_BACKGROUND

	if self.rotation in [0,180]:
	    if scr_mode == 1:
		self.actScreen = mainLayout.cameras1.children[0]
	    elif scr_mode == 2:
		self.actScreen = mainLayout.cameras1.children[1] if self.screenIndex == 0 else mainLayout.cameras1.children[0]
	    elif scr_mode == 3:
		self.actScreen = mainLayout.cameras1.children[0] if self.screenIndex == 0 else mainLayout.cameras2.children[0]
	    else:
		self.actScreen = mainLayout.cameras1.children[1] if self.screenIndex == 0 else\
		    mainLayout.cameras1.children[0] if self.screenIndex == 1 else\
		    mainLayout.cameras2.children[1] if self.screenIndex == 2 else\
		    mainLayout.cameras2.children[0]
	else:
	    cnt = len(mainLayout.cameras.children) - 1
	    self.actScreen = mainLayout.cameras.children[cnt - self.screenIndex]

	self.printInfo()
	self.setActive(False)


    # ###############################################################
    def startThread(self):
	"start communication thread to external devicer"
	Logger.debug('%s: (%d)' % (whoami(), self.screenIndex))

	self.locks = 0x55
	sendNodeInfo('[***]LOCK: %d %.2x' % (self.screenIndex, self.locks))

	self.socket = None
	if len(self.serverAddr):
	    self.bgrThread = Thread(target=self.tcpip_worker, kwargs={'addr': self.serverAddr})
	    self.bgrThread.daemon = True
	    self.bgrThread.start()
	else:
	    self.bgrThread = None


    # ###############################################################
    def initPlayer(self):
	"start video player"
	global mainLayout, current_call, active_display_index

	Logger.debug('%s: (%d)' % (whoami(), self.screenIndex))
	try:
	    if len(itools.omxl) and DBUS_PLAYERNAME + str(self.screenIndex) in itools.omxl:
		del itools.omxl[DBUS_PLAYERNAME + str(self.screenIndex)]
	except:
	    pass

	sendNodeInfo('[***]VIDEO: %d ERROR' % self.screenIndex)

	interval = 19. + .2 * self.screenIndex
	if self.checkEvent > 0: Clock.unschedule(self.checkEvent)
        self.checkEvent = Clock.schedule_interval(self.checkLoop, interval)
	self.isPlaying = (mainLayout.scrmngr.current == CAMERA_SCR and not mainLayout.popupSettings and not current_call) or\
	    (current_call and active_display_index == self.screenIndex)

	return subprocess.Popen(['omxplayer', '--live', '--no-osd', '--no-keys', '--display','0',\
	    '--alpha','0', '--layer', '1',\
	    '--dbus_name', DBUS_PLAYERNAME + str(self.screenIndex), '--orientation', str(self.rotation),\
	    '--aspect-mode', self.aspectratio, '--win', ','.join(self.playerPosition), self.streamUrl],\
	    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)


    # ###############################################################
    def checkLoop(self, dt):
	"check video player state"
	#global mainLayout, current_call, active_display_index

	Logger.trace('%s: (%d)' % (whoami(), self.screenIndex))

	sendNodeInfo('[***]VIDEO: %d OK' % self.screenIndex)

	val = 255 if self.isPlaying else 0

	self.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(val)])

	if self.bgrThread and not self.bgrThread.isAlive(): self.startThread()


    # ###############################################################
    def resizePlayer(self, newpos=''):
	"resize video player area"
	global mainLayout, scr_mode

	Logger.debug('%s: (%d) %s' % (whoami(), self.screenIndex, newpos))

	self.hidePlayer()

	pos = []
	pos = newpos.split(',') if len(newpos) else self.playerPosition
	if len(newpos) > 0:
	    pos = [80,16,720,376] if self.rotation == 0 else [80,104,720,464] if self.rotation == 180\
		else [352,8,700,472] if self.rotation == 90 else [100,8,448,472]

	    if self.aspectratio in ['16:9','4:3']:
		### keep aspect ratio:
		pheight = pos[3] - pos[1] if self.rotation in [0,180] else pos[2] - pos[0]
		pwidth = pos[2] - pos[0] if self.rotation in [0,180] else pos[3] - pos[1]

		if self.aspectratio == '16:9':
		    pdelta = int((pwidth - (int(pheight / 9) * 16)) / 2)
		elif self.aspectratio == '4:3':
		    pdelta = int((pwidth - (int(pheight / 3) * 4)) / 2)
		else: pdelta = 0
		if pdelta < 0: pdelta = 0

		if self.rotation in [0,180]:
		    pos[0] += pdelta
		    pos[2] -= pdelta
		else:
		    pos[1] += pdelta
		    pos[3] -= pdelta

	self.dbus_command(['setvideopos'] + pos)


    # ###############################################################
    def tcpip_worker(self, addr):
	"TCPIP thread"
	Logger.debug('%s: (%d) %s' % (whoami(), self.screenIndex, addr))

	SERVER_REQ = 'GET /events.txt HTTP/1.1\n\n'

	if ':' in addr:
	    b = addr.split(':')
	    a = (b[0],int(b[1]))
	else:
	    a = (addr, 80)

	while True:
	    try:
        	self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        	self.socket.connect(a)
		time.sleep(1)
		fcntl.fcntl(self.socket, fcntl.F_SETFL, os.O_NONBLOCK)
		time.sleep(1)
		self.socket.send(SERVER_REQ)
		break
	    except IOError as e:
		self.socket = None
		Logger.warning('%s: (%d) %s CONNECT ERROR %s' % (whoami(), self.screenIndex, addr, str(e)))
		#return
		time.sleep(60)

	msg = ''
	noDataCounter = 0
	while True:
	    try:
		msg = self.socket.recv(4096) if not self.socket is None else ''
	    except socket.error as e: ###???
#	    except exception as e:
		err = e.args[0]
		if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
		    time.sleep(1)				# No data available
		    noDataCounter += 1
		    if noDataCounter > 40: break		# try reconnect
		    continue
		else:
		    # a "real" error occurred
		    self.socket = None
		    Logger.warning('%s: (%d) %s  ERROR: %s' % (whoami(), self.screenIndex, addr, str(e)))
		    msg = ''
        	    break
	    except:
		self.socket = None

	    if len(msg) > 0:
		# got a message, do something
		noDataCounter = 0
		if '[' in msg and ']' in msg:
		    m = msg.splitlines()	# split to separate lines
		    l = m[m.index('') + 1:]	# skip over header part
#		    Logger.info('%s: (%d) %s' % (whoami(), self.screenIndex, str(l)))
		    self.processMessage(l)
	    else:
		Logger.warning('%s: (%d) Reinit connection: %s' % (whoami(), self.screenIndex, addr))
		try:
		    self.socket.close()
		except: pass

		self.socket = None

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
		    time.sleep(15)


    # ###############################################################
    def processMessage(self, msg):
	"process the message from the thread"

	Logger.debug('%s: (%d)' % (whoami(), self.screenIndex))

	cp = ConfigParser()

	tmsg = []
	for m in msg:
	    if '' == m or '[' in m or ('=' in m and not ';' in m): tmsg.append(m)

	while len(tmsg):
	    msg = tmsg[:tmsg.index('') + 1]
	    s_config = '\n'.join(str(x) for x in msg)
	    #Logger.warning('%s: (%d) s_config=%s' % (whoami(), self.screenIndex, s_config))
	    tmsg = tmsg[tmsg.index('') + 1:]

	    buf = StringIO.StringIO(s_config)
	    cp.readfp(buf)

	    for sec_name in cp.sections():
		#opt = cp.options(sec_name)
		#for n,v in cp.items(sec_name):
		    #Logger.info('%s: (%d) section=%s n=%s v=%s' % (whoami(), self.screenIndex, sec_name, n, v))
		if sec_name in ['evstat', 'event']:
		    x = cp.get(sec_name,'event')
		    if 'GUARD' in x: self.setLock(cp.get(sec_name,'message'))
		#if 'event' == sec_name: pass


    # ###############################################################
    def setLock(self, value):
	"set lock status"
	if not 'S' in value: return

	m = value.strip('"').split('S')
	mask = 0xf if int(m[0]) > 1 else 0xf0
	val = 0xf if int(m[1]) == 1 else 0
	if int(m[0]) > 1: val = val << 4
	self.locks = (self.locks & mask) | val
	Logger.debug('%s: (%d) lock=%.2x (%s m=%.2x v=%.2x)'\
	    % (whoami(), self.screenIndex, self.locks, value, mask, val))
	sendNodeInfo('[***]LOCK: %d %.2x' % (self.screenIndex, self.locks))

	mainLayout.setLockIcons(self.screenIndex, self.locks)


    # ###############################################################
    def dbus_command(self, params=[]):
	"d-bus command"
	global mainLayout
	Logger.trace('%s: (%d) %r' % (whoami(), self.screenIndex, params))

	if not send_dbus(DBUS_PLAYERNAME + str(self.screenIndex), params):
	    sendNodeInfo('[***]VIDEO: %d ERROR' % self.screenIndex)
	    mainLayout.restart_player_window(self.screenIndex)


    # ###############################################################
    def hidePlayer(self):
	"hide video player area"
	Logger.debug('%s:' % whoami())

	self.color = [0,0,0] #NO_DISPLAY_BACKGROUND  # INACTIVE_DISPLAY_BACKGROUND
	self.actScreen.bgcolor = self.color


    # ###############################################################
    def setActive(self, active=True):
	"add or remove active flag"
	global current_call, scr_mode, mainLayout, docall_button_global

	Logger.debug('%s: index=%d active=%d' % (whoami(), self.screenIndex, active))

#	if current_call: return

	self.color = ACTIVE_DISPLAY_BACKGROUND if active and (scr_mode != 1) else INACTIVE_DISPLAY_BACKGROUND

	self.actScreen.bgcolor = self.color

	if current_call: return

	if active:
	    # change phone icon
	    docall_button_global.imgpath = DND_CALL_IMG if mainLayout.dnd_mode else MAKE_CALL_IMG
	    docall_button_global.imgpath = docall_button_global.imgpath if len(self.sipcall) else UNUSED_CALL_IMG


    # ###############################################################
    def printInfo(self):
	"print class info"
	Logger.debug('Display: id=%d area=%s IP=%s SIPcall=%s stream=%s'\
	    % (self.screenIndex, self.playerPosition, self.serverAddr, self.sipcall, self.streamUrl))


# ##############################################################################

class Indoor(FloatLayout):

    lib = None			# pjsip library
    outgoingCall = False
    dnd_mode = False
    outgoing_mode = True
    avolume = 100
    micvolume = 100
    brightness = 255
    appRestartEvent = None
    mediaErrorFlag = False	# audio error
    popupSettings = None	# popup window is opened
    volslider = None
    micslider = None
    masterPwd = '1234'
    scrOrientation = 0
    btnReject = None
    btnDoCall = None
    btnScrSaver = None
    btnSettings = None
    btnDoor1 = None
    btnDoor2 = None
    camerascreen = None
    txtBasicLabel = None
    workAreaHigh = 0
    buttonAreaHigh = 0
    infoAreaHigh = 0
    sipPort = 5060
    touches = {}		# resize video player (to bigger)
    touchdistance = -1.		# touch distance
    showVideoEvent = None	# timer to return size back
    netstatus = -1		# old value of NetLink.netstatus

    def __init__(self, **kwargs):
	"app init"
	global APP_NAME, APP_VERSION_CODE, SCREEN_SAVER, ROTATION, WATCHES, RING_TONE
        global main_state, mainLayout, scrmngr, config, scr_mode

        super(Indoor, self).__init__(**kwargs)

	mainLayout = self

	initloggers()

        init_sw_watchdog()
	sw_watchdog()
        Clock.schedule_interval(sw_watchdog, SW_WD_TIME)

	Clock.schedule_once(lambda dt: self.settings_worker(), 2.)

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
	    if config.get('about', 'app_ver') != APP_VERSION_CODE:
		config.set('about', 'app_ver', APP_VERSION_CODE)
		config.write()
        except:
            Logger.warning('Indoor init: ERROR 3.1 = read config file!')

        try:
	    value = config.get('command', 'watches').strip()
	    if value == 'analog' or value == 'digital': WATCHES = value
	    else: WATCHES = 'none'
        except:
            Logger.warning('Indoor init: ERROR 4 = read config file!')

	scr_mode = 1
	try:
	    scr_mode = config.getint('gui', 'screen_mode')
	except:
            Logger.warning('Indoor init_screen: ERROR 9 = read config file!')
	    scr_mode = 1

        try:
	    screen_saver = config.getint('command', 'screen_saver')
	    if screen_saver > 0 and screen_saver < 120: SCREEN_SAVER = screen_saver * 60
        except:
            Logger.warning('Indoor init: ERROR 5 = read config file!')

        try:
	    value = config.get('command', 'dnd_mode').strip()
	    self.dnd_mode = 'True' == value or '1' == value
        except:
            Logger.warning('Indoor init: ERROR 6 = read config file!')

        try:
	    value = config.get('service', 'autoupdate').strip()
	    if 'True' == value or '1' == value:
		Clock.schedule_interval(self.auto_update_loop, 3600)
        except:
            Logger.warning('Indoor init: ERROR 6.2 = read config file!')

        try:
	    value = config.get('gui', 'outgoing_calls').strip()
	    self.outgoing_mode = 'True' == value or '1' == value
        except:
            Logger.warning('Indoor init: ERROR 6.1 = read config file!')

        try:
	    br = config.getint('command', 'brightness')
	    if br > 0 and br < 256: self.brightness = br
        except:
            Logger.warning('Indoor init: ERROR 7 = read config file!')
	    self.brightness = 255

	send_command('%s %d' % (BRIGHTNESS_SCRIPT, self.brightness))

        try:
	    RING_TONE = config.get('devices', 'ringtone').strip()
        except:
            Logger.warning('Indoor init: ERROR 11 = read config file!')
	    RING_TONE = 'oldphone.wav'

	tones.PHONERING_PLAYER = APLAYER + ' ' + APARAMS + RING_TONE

        try:
	    self.masterPwd = config.get('service', 'masterpwd').strip()
        except:
            Logger.warning('Indoor init: ERROR 8 = read config file!')
	    self.masterPwd = '1234'

        try:
            self.scrOrientation = config.getint('gui', 'screen_orientation')
        except:
            Logger.warning('Indoor init: ERROR 8.1 = read config file!')
	ROTATION = self.scrOrientation

	self.get_volume_value()

	self.init_widgets()

	self.init_myphone()

	initcallstat()

	sendNodeInfo('[***]START')

        self.infinite_event = Clock.schedule_interval(self.infinite_loop, 6.9)
        Clock.schedule_interval(self.info_state_loop, 12.)

        Clock.schedule_once(self.checkNetStatus, 5.)
	Clock.schedule_once(lambda dt: send_command('./diag.sh init'), 15)

	t = threading.Thread(target=procNetlink)
	t.daemon = True
	t.start()


    # ###############################################################
    def init_widgets(self):
	"define app widgets"
	global scr_mode, ROTATION

	screensize = (800,480) if ROTATION in [0,180] else (480,800)

	Logger.debug('%s: scr_mode=%d rotation=%d screensize=%r' % (whoami(), scr_mode, ROTATION, screensize))

	self.ids.waitscr.size = screensize
	self.ids.digiclock.size = screensize
	self.ids.camera.size = screensize
	self.ids.settings.size = screensize

	self.camerascreen = self.ids.scattercameras
	self.camerascreen.size = screensize

	ROTATION = self.scrOrientation

	h3 = 56 if ROTATION in [0,180] else 64			# info area
	h2 = 47 if ROTATION in [0,180] else 94			# buttons
	h1 = screensize[0] - h3 - h2				# cameras

	self.workAreaHigh = h1
	self.buttonAreaHigh = h2
	self.infoAreaHigh = h3

	self.workArea = MBoxLayout(orientation='horizontal')
	self.infoArea = MBoxLayout(orientation='horizontal', size_hint_y=None, height=self.infoAreaHigh)
	self.btnArea = MBoxLayout(orientation='vertical', size_hint_y=None, height=self.buttonAreaHigh)
	self.camerascreen.add_widget(self.workArea)
	self.camerascreen.add_widget(self.infoArea)
	self.camerascreen.add_widget(self.btnArea)

	self.init_buttons()
	self.init_screen()
#	self.init_sliders()


    # ###############################################################
    def init_buttons(self):
	"define app buttons"
	global docall_button_global, scr_mode, mainLayout

	Logger.debug('%s:' % whoami())

	nothing = ImageButton(imgpath=SCREEN_SAVER_IMG)
	btnW = 64 #72
	self.btnScrSaver = ImageButton(imgpath=SCREEN_SAVER_IMG, size_hint_x=None, width=btnW)
	self.btnScrSaver.bind(on_release=self.callback_set_voice)
	self.btnSettings = ImageButton(imgpath=SETTINGS_IMG, size_hint_x=None, width=btnW)
	self.btnSettings.bind(on_release=self.callback_set_options)
	self.btnDoCall = ImageButton(imgpath=MAKE_CALL_IMG)
	self.btnDoCall.bind(on_release=self.callback_btn_docall)
	self.btnDoor1 = DoorButton()
	self.btnDoor1.bind(on_release=self.callback_btn_door1)
	self.btnDoor2 = DoorButton()
	self.btnDoor2.bind(on_release=self.callback_btn_door2)
	self.btnReject = ImageButton(imgpath=HANGUP_CALL_IMG)
	self.btnReject.bind(on_release=self.my_reject_callback)

	docall_button_global = self.btnDoCall
	docall_button_global.imgpath = DND_CALL_IMG if mainLayout.dnd_mode else MAKE_CALL_IMG
	docall_button_global.btntext = ''

	### define button for lockers:
	btnLayout1 = self.btnDoor1.children[0]
	btnLayout2 = self.btnDoor2.children[0]
	if scr_mode < 4:
	    btnLayout1.remove_widget(btnLayout1.children[3])
	    btnLayout2.remove_widget(btnLayout2.children[3])
	if scr_mode in [1,3]:
	    btnLayout1.remove_widget(btnLayout1.children[2])
	    btnLayout2.remove_widget(btnLayout2.children[2])
	if scr_mode in [1,2]:
	    btnLayout1.remove_widget(btnLayout1.children[1])
	    btnLayout2.remove_widget(btnLayout2.children[1])

	cnt = len(btnLayout1.children)

	if self.scrOrientation in [0,180]:
	    w = 48 + 32 * cnt
	    self.btnDoor1.size_hint_x = None
	    self.btnDoor2.size_hint_x = None
	    self.btnDoor1.width = w
	    self.btnDoor2.width = w


    # ###############################################################
    def addCameraArea(self):
	"init camera views"
	global scr_mode

	Logger.debug('%s:' % whoami())

	self.cameras = MBoxLayout(orientation='vertical')
	self.workArea.add_widget(self.cameras)

	if self.scrOrientation in [0,180]:
	    self.cameras1 = MBoxLayout(orientation='horizontal')
	    self.cameras.add_widget(self.cameras1)

	    if scr_mode >= 1:
		self.cameras1.add_widget(VideoLabel(id='0'))
	    if scr_mode in [2,4]:
		self.cameras1.add_widget(VideoLabel(id='1'))
	    if scr_mode >= 3:
		self.cameras2 = MBoxLayout(orientation='horizontal')
		self.cameras.add_widget(self.cameras2)
		self.cameras2.add_widget(VideoLabel(id='2'))
	    if scr_mode == 4:
		self.cameras2.add_widget(VideoLabel(id='3'))
	else:
	    self.cameras.add_widget(VideoLabel(id='0'))
	    if scr_mode in [2,3,4]:
		self.cameras.add_widget(VideoLabel(id='1'))
	    if scr_mode == 4:
		self.cameras.add_widget(VideoLabel(id='2'))
		self.cameras.add_widget(VideoLabel(id='3'))


    # ###############################################################
    def addInfoArea(self):
	"init info text item"
	Logger.debug('%s:' % whoami())

	self.txtBasicLabel = Label(text='Wait...', font_size='40dp')
	self.infoArea.add_widget(self.txtBasicLabel)
	self.addInfoText()


    # ###############################################################
    def addInfoText(self, txt=''):
	"init info text item"
	Logger.debug('%s: txt=%s' % (whoami(), txt))

	if txt == '':
	    self.workArea.height = self.workAreaHigh + self.infoAreaHigh
	    self.infoArea.height = 0
	    self.infoArea.remove_widget(self.txtBasicLabel)
	    wtxt = 'Wait...'
	else:
	    self.workArea.height = self.workAreaHigh - self.infoAreaHigh
	    self.infoArea.height = self.infoAreaHigh
	    if (self.txtBasicLabel.text == ''): self.infoArea.add_widget(self.txtBasicLabel)
	    wtxt = ''

	self.txtBasicLabel.text = txt

	for child in self.workArea.walk():
	    if '.VideoLabel' in str(child): child.text = wtxt


    # ###############################################################
    def addButtonArea(self):
	"init buttons"
	Logger.debug('%s:' % whoami())

	self.btnAreaH = MBoxLayout(orientation='horizontal')
	self.btnArea.add_widget(self.btnAreaH)

	if self.scrOrientation in [0,180]:
	    self.btnAreaH.add_widget(self.btnDoor1)
	    self.btnAreaH.add_widget(self.btnDoCall)
	    self.btnAreaH.add_widget(self.btnDoor2)
	else:
	    self.btnAreaB = MBoxLayout(orientation='horizontal')
	    self.btnArea.add_widget(self.btnAreaB)

	    self.btnAreaH.add_widget(self.btnDoCall)

	    self.btnAreaB.add_widget(self.btnDoor1)
	    self.btnAreaB.add_widget(self.btnDoor2)

	self.btnAreaH.add_widget(self.btnReject)
	self.btnAreaH.remove_widget(self.btnReject)


    # ###############################################################
    def init_screen(self):
	"define app screen"
	global config, scr_mode

	Logger.debug('%s:' % whoami())

	self.addCameraArea()
	self.addInfoArea()
	self.addButtonArea()

	if self.scrOrientation == 0:		# landscape 0
	    if scr_mode == 1:
		wins = ['2,2,799,432']
	    elif scr_mode in [2,3]:
		wins = ['2,2,399,432', '402,2,799,432']
	    else:
		wins = ['2,2,399,216', '402,2,799,216', '2,219,399,432', '402,219,799,432']
	elif self.scrOrientation == 180:	# landscape 180
	    if scr_mode == 1:
		wins = ['3,50,799,479']
	    elif scr_mode in [2,3]:
		wins = ['403,50,799,479', '3,50,399,479']
	    else:
		wins = ['403,266,799,479', '3,266,399,479', '403,50,799,262', '3,50,399,262']
	elif self.scrOrientation == 90:		# portrait 90
	    if scr_mode == 1:
		wins = ['3,3,705,479']
	    elif scr_mode in [2,3]:
		wins = ['3,3,352,479', '356,3,705,479']
	    else:
		wins = ['3,3,176,479', '180,3,352,479', '356,3,529,479', '533,3,705,479']
	else:					# portrait 270
	    if scr_mode == 1:
		wins = ['98,3,799,479']
	    elif scr_mode in [2,3]:
		wins = ['450,3,799,479', '98,3,446,479']
	    else:
		wins = ['627,3,799,479', '450,3,623,479', '275,3,446,479', '98,3,270,479']

	for i in range(0,len(wins)):
	    win = wins[i]
	    serv = config.get('common', 'server_ip_address_'+str(i + 1)).strip()
	    sipc = config.get('common', 'sip_call'+str(i + 1)).strip()
	    vid = config.get('common', 'server_stream_'+str(i + 1)).strip()
	    aspectratio = config.get('common', 'picture_'+str(i + 1)).strip()
	    relay = 'http://' + serv + '/cgi-bin/remctrl.sh?id='
#	    try:
#		relay = config.get('common', 'server_relay_'+str(i + 1)).strip()
#	    except:
#        	Logger.warning('Indoor init_screen: ERROR 12 = read config file!')
#		relay = 'http://' + serv + '/cgi-bin/remctrl.sh?id='
#
#	    self.dbg(whoami() + ' relay: ' + str(relay))

	    displ = BasicDisplay(win,serv,sipc,vid,relay,self.scrOrientation,aspectratio)
	    self.displays.append(displ)

	self.scrmngr.current = CAMERA_SCR

	self.setButtons(False)

	self.refreshLockIcons()

	self.displays[0].setActive()


    # ###############################################################
    def init_myphone(self):
	"sip phone init"
        global acc, config, sipRegStatus, sipRegEvent

	if self.lib: # reinit pjSip library
	    if sipRegEvent: Clock.unschedule(sipRegEvent)
	    try:
		if acc: acc.delete()
	    except pj.Error: pass
	    acc = None
	    try:
		if self.lib: self.lib.destroy()
	    except pj.Error: pass
	    self.lib = None
	    sipRegEvent = None

        # Create library instance
        lib = pj.Lib()
	self.lib = lib

	accounttype = 'peer-to-peer'
	try:
	    accounttype = config.get('sip', 'sip_mode').strip()
	    self.sipPort = int(config.get('sip', 'sip_port').strip())
	except:
            Logger.warning('Indoor init_myphone: ERROR 10 = read config file!')

	logLevel = LOG_LEVEL
	try:
	    v = config.get('service', 'sip_log').strip()
	    logLevel = 6 if 'all' in v else LOG_LEVEL if 'debug' in v else 5 if 'info' in v else 0
	except:
            Logger.warning('Indoor init_myphone: ERROR 11 = read config file!')

	Logger.info('%s: acctype=%s port=%d loglevel=%d' % (whoami(), accounttype, self.sipPort, logLevel))

        try:
            # Init library with default config and some customized logging config
            lib.init(log_cfg=pj.LogConfig(level=logLevel, console_level=logLevel, callback=log_cb),\
		    media_cfg=setMediaConfig(), licence=1)

	    comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    comSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	    # Create UDP transport which listens to any available port
	    transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(self.sipPort))

            # Start the library
            lib.start()

	    cl = lib.enum_codecs()
	    for c in cl:
		Logger.debug('%s CODEC=%s priority=%d' % (whoami(), c.name, c.priority))
##		priority = 16 if 'PCMA' in c.name else 32 if '722' in c.name else 64 if 'PCMU' in c.name else 128
#		priority = 128 if 'PCMA' in c.name else 64 if '722' in c.name else 32 if 'PCMU' in c.name else 16
#		lib.set_codec_priority(c.name, priority)
##		p = lib.get_codec_parameter(c.name)
##		Logger.info('%s: codec param priority=%d' % (whoami(), p.priority))

	    # Create local account
	    if accounttype == 'peer-to-peer':
        	acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())
		self.sipServerAddr = ''
		sendNodeInfo('[***]SIPREG: peer-to-peer')
		sendNodeInfo('[***]SIP: FREE')

		sipRegStatus = True
	    else:
		sendNodeInfo('[***]SIPREG: NONE')
		dn = str(config.get('sip', 'sip_server_addr'))#.strip()
		un = str(config.get('sip', 'sip_username'))#.strip()
		an = str(config.get('sip', 'sip_authentication_name'))#.strip()
		pa = str(config.get('sip', 'sip_p4ssw0rd'))#.strip()
		self.sipServerAddr = dn
		if an == '': an = un

#		acc_cfg = pj.AccountConfig(domain=dn, username=un, password=pa)
		acc_cfg = pj.AccountConfig(domain=dn, display=un, username=un, password=pa)
		if an != un: acc_cfg.auth_cred = [pj.AuthCred("*", an, pa)]

#		acc_cfg = pj.AccountConfig()
#		acc_cfg.id = "sip:" + un + "@" + dn
#		acc_cfg.reg_uri = "sip:" + dn + ":" + self.sipPort
#		acc_cfg.proxy = [ "sip:" + dn + ";lr" ]
#		acc_cfg.auth_cred = [pj.AuthCred("*", an, pa)]

		acc = lib.create_account(acc_cfg, cb=MyAccountCallback())
#		acc = lib.create_account(acc_cfg)
#		cb = MyAccountCallback(acc)
#		acc.set_callback(cb)

	    Logger.info('%s: Listening on %s port %d Account type=%s SIP server=%s'\
		% (whoami(), transport.info().host, transport.info().port, accounttype, self.sipServerAddr))

        except pj.Error, e:
            Logger.critical("%s pjSip Exception: %r" % (whoami(), e))
	    sendNodeInfo('[***]SIP: ERROR')

	    # Shutdown the library
	    transport = None
	    try:
		if acc: acc.delete()
	    except pj.Error: pass
	    acc = None
	    try:
		if lib: lib.destroy()
	    except pj.Error: pass
	    lib = None

            self.lib = lib
	    docall_button_global.btntext = "No Licence"
	    docall_button_global.disabled = True
	    docall_button_global.imgpath = NO_IMG
	    sipRegStatus = False


    # ###############################################################
    def info_state_loop(self, dt):
	"state loop"
        global current_call, active_display_index, docall_button_global, config

        if current_call != None: self.info_state = 0

        if self.info_state == 0:
            if current_call is None:
		self.info_state = 1
        elif self.info_state == 1:
            self.info_state = 2
#	    if self.lib != None and self.scrmngr.current == CAMERA_SCR:
#		self.setButtons(False)
        elif self.info_state == 2:
            self.info_state = 3
	    sendNodeInfo('[***]INDOORVER: %s' % config.get('about','app_ver'))
        elif self.info_state == 3:
            self.info_state = 0
	    sendNodeInfo('[***]RPISN: %s' % config.get('about','serial'))

	if self.lib is None:
	    docall_button_global.btntext = "No Licence"
	    docall_button_global.disabled = True
	    docall_button_global.imgpath = NO_IMG

	if check_usb_audio() > 0: self.reinitbackgroundtasks()
	else: self.mediaErrorFlag = False

	if netlink.netstatus == 0:
	    sendNodeInfo('[***]NETLINK: %d' % netlink.netstatus)
	    docall_button_global.btntext = "ETH ERROR"
	else:
	    if docall_button_global.btntext == "ETH ERROR": docall_button_global.btntext = ''

	if netlink.netstatus == 0 or self.netstatus != netlink.netstatus:
	    self.netstatus = netlink.netstatus
	    Clock.schedule_once(self.checkNetStatus, 5.)


    # ###############################################################
    def infinite_loop(self, dt):
	"main neverendig loop"
        global current_call, active_display_index, procs

	if len(procs) == 0: return

	for idx, p in enumerate(procs):
	    if not p.poll() is None:
		try: p.kill()
		except: pass

		if current_call is None or idx == active_display_index:
		    procs[idx] = self.displays[idx].initPlayer()

#	Clock.schedule_once(self.image_update_loop, .5)


    # ###############################################################
    def image_update_loop(self,dt):
	"image update"
	Logger.debug('%s:' % whoami())

	area = self if self.popupSettings == None else self.popupSettings
	for child in area.walk():
	    if child is area: continue
	    if '.MyAsyncImage' in str(child):
		child.reload()


    # ###############################################################
    def auto_update_loop(self,dt):
	"auto update at 3:00AM"

	h = datetime.datetime.now().hour
	if h == 3:
	    Logger.info('%s:' % whoami())
	    App.get_running_app().appUpdateWorker()


    # ###############################################################
    def checkNetStatus(self, dt=20):
	"test ETH status"
        global docall_button_global, config

	try:
	    s = get_info(SYSTEMINFO_SCRIPT).split()
	    if len(s) > 9: sendNodeInfo('[***]MACADDR: %s' % s[9])
	    sendNodeInfo('[***]IPADDR: %s' % s[3])
	except: s = []

	if netlink.netstatus > 0: netlink.netstatus = 1 if getINet() else -1

	docall_button_global.btntext = '' if self.lib else 'No Licence'
	docall_button_global.btntext = docall_button_global.btntext if len(s) >= 8 else 'Network ERROR'
	docall_button_global.btntext = docall_button_global.btntext if netlink.netstatus > 0 else 'ETH ERROR'
	if netlink.netstatus == -1: docall_button_global.btntext = 'Internet ERROR'

	if '127.0.0.1' == config.get('system', 'ipaddress') and len(s) > 8:
	    Logger.error('%s: network ipaddress %r' % (whoami(), s))

	    try:
		config.set('system', 'inet', s[2])
		config.set('system', 'ipaddress', s[3])
		config.set('system', 'gateway', s[6])
		config.set('system', 'netmask', s[4])
		config.set('system', 'dns', s[8])
		config.write()

		if len(s) > 9: sendNodeInfo('[***]MACADDR: %s' % s[9])
		sendNodeInfo('[***]IPADDR: %s' % s[3])
	    except:
		Logger.error('%s: config %r' % (whoami(), config))
#		docall_button_global.btntext = 'ERROR'


    # ###############################################################
    def reinitbackgroundtasks(self):
	"SIP reinitialization"
	Logger.warning('%s:' % whoami())

#	kill_subprocesses()
#	App.get_running_app().stop()

	reset_usb_audio()
	Clock.schedule_once(lambda dt: send_command(HIDINIT_SCRIPT), 2.)
	Clock.schedule_once(lambda dt: self.init_myphone(), 3.)


    # ###############################################################
    def startScreenTiming(self):
	"start screen timer"
	global SCREEN_SAVER

        Logger.debug('ScrnEnter: screen saver at %d sec' % SCREEN_SAVER)

	if self.screenTimerEvent: Clock.unschedule(self.screenTimerEvent)
        if SCREEN_SAVER > 0:
	    self.screenTimerEvent = Clock.schedule_once(self.return2clock, SCREEN_SAVER)

	send_command(UNBLANK_SCRIPT)
	send_command(BACK_LIGHT_SCRIPT + ' 0')


    # ###############################################################
    def return2clock(self, *args):
	"swap screen to CLOCK"
	global current_call, WATCHES

        Logger.debug('%s: %s --> %s' % (whoami(), self.scrmngr.current, WATCHES))

        Clock.unschedule(self.screenTimerEvent)
	self.screenTimerEvent = None

	if current_call is None and self.scrmngr.current == CAMERA_SCR:
	    self.scrmngr.current = DIGITAL_SCR
	    if WATCHES == 'none': send_command(BACK_LIGHT_SCRIPT + ' 1')
	    else:
		if len(self.ids.clockslayout.children):
		    Logger.error('%s: widgets_cnt=%d' % (whoami(), len(self.ids.clockslayout.children)))
		    self.ids.clockslayout.clear_widgets()
		self.ids.clockslayout.add_widget(MyClockWidget() if WATCHES == 'analog' else DigiClockWidget())


    # ###############################################################
    def finishScreenTiming(self):
	"finist screen timer"
        Logger.debug('ScrnLeave:')

        Clock.unschedule(self.screenTimerEvent)
	self.screenTimerEvent = None


    # ###############################################################
    def swap2camera(self):
	"swap screen to CAMERA"
        Logger.info('%s:' % whoami())

	self.ids.clockslayout.clear_widgets()
	self.scrmngr.current = CAMERA_SCR
	self.on_touch_up(None)


    # ###############################################################
    def enterCameraScreen(self):
	"swap screen to CAMERA"
	global current_call

        Logger.debug('%s: call=%s' % (whoami(), str(current_call)))

	if current_call is None: self.showPlayers()

	Clock.schedule_once(self.image_update_loop)


    # ###############################################################
    def setLockIcons(self, scrnIdx, locks):
	"set lock icons"
	global active_display_index

	Logger.debug('%s: id=%d locks=%.2x' % (whoami(), scrnIdx, locks))

	idi = len(self.btnDoor1.children[0].children) - 1 - scrnIdx
	img = LOCK_IMG if active_display_index == scrnIdx else INACTIVE_LOCK_IMG

	if locks == 0x55:
	    lockimg1 = lockimg2 = UNUSED_LOCK_IMG
	else:
	    lockimg1 = UNLOCK_IMG if (locks & 0x0f) else img
	    lockimg2 = UNLOCK_IMG if (locks & 0xf0) else img

	self.btnDoor1.children[0].children[idi].source = lockimg1
	self.btnDoor2.children[0].children[idi].source = lockimg2


    # ###############################################################
    def refreshLockIcons(self):
	"change lock icon activity"
	global active_display_index

	Logger.debug('%s:' % (whoami()))

	s = len(self.btnDoor1.children[0].children)

	for idx, d in enumerate(self.displays):
	    idi = s - 1 - idx
	    self.setLockIcons(idx, d.locks)

	Clock.schedule_once(self.image_update_loop)


    # ###############################################################
    def my_reject_callback(self, arg):
	"reject incoming call"
        global current_call

	Logger.info('%s:' % whoami())

        if current_call and current_call.is_valid(): current_call.hangup()
	current_call = None
	self.outgoingCall = False
	self.setButtons(False)


    # ###############################################################
    def enable_btn_docall(self, param):
	"enable a call button"
        global docall_button_global, current_call

	olds = docall_button_global.disabled

	if self.outgoingCall or (current_call and current_call.is_valid()):
	    docall_button_global.disabled = False
	else:
	    docall_button_global.disabled = not self.outgoing_mode

	if olds != docall_button_global.disabled: Logger.debug('%s:' % whoami())


    # ###############################################################
    def callback_btn_docall(self, btn=None):
	"make outgoing call"
        global current_call, active_display_index, docall_button_global, ring_event

	Logger.info('%s: call=%r state=%d outgoing=%r' % (whoami(), current_call, main_state, self.outgoingCall))

	if docall_button_global.disabled: return

	docall_button_global.disabled = True
	Clock.schedule_once(self.enable_btn_docall, 1)

	if check_usb_audio() > 0: self.reinitbackgroundtasks()

#	if len(procs) == 0 or not self.outgoing_mode: return

        if current_call:
	    Logger.info('%s call state: %s' % (whoami(), str(current_call.dump_status())))

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
		self.setButtons(False)
		docall_button_global.imgpath = DND_CALL_IMG if mainLayout.dnd_mode else MAKE_CALL_IMG
	else:
	    if self.showVideoEvent: Clock.unschedule(self.showVideoEvent)
	    self.showVideoEvent = None

	    target = self.displays[active_display_index].sipcall

	    if len(target) == 0: return

	    if len(self.sipServerAddr) and not '.' in target:
		target = target + '@' + self.sipServerAddr

	    lck = self.lib.auto_lock()
	    self.outgoingCall = True
	    if make_call('sip:' + target + ':5060') is None:
		txt = 'Audio ERROR' if self.mediaErrorFlag else '--> ' + str(active_display_index + 1) + ' ERROR'
		docall_button_global.color = COLOR_ERROR_CALL
		docall_button_global.btntext = txt
		docall_button_global.imgpath = ERROR_CALL_IMG
	    else:
		self.setButtons(True)
		docall_button_global.btntext = ''
	    del lck


    # ###############################################################
    def gotResponse(self, req, results):
	"relay result"
        Logger.debug('Relay: req=%s res=%s' % (str(req), results))


    # ###############################################################
    def setRelayRQ(self, relay):
	"send relay request"
        global active_display_index

        Logger.trace('SetRelay: %s' % relay)

	if len(procs) == 0: return

        req = UrlRequest(self.displays[active_display_index].relayCmd + relay,\
                on_success = self.gotResponse, timeout = 5)


    # ###############################################################
    def callback_btn_door1(self, btn=None):
	"door 1 button"
        Logger.debug('%s:' % whoami())
        self.setRelayRQ('relay1')


    # ###############################################################
    def callback_btn_door2(self, btn=None):
	"door 2 button"
        Logger.debug('%s:' % whoami())
        self.setRelayRQ('relay2')


    # ###############################################################
    def callback_set_options(self, btn=-1):
	global SCREEN_SAVER, WATCHES, RING_TONE
	"start quick settings"

        Logger.debug("%s: volume=%d mic=%d brightness=%d "\
	    % (whoami(), self.avolume, self.micvolume, self.brightness))

	self.hidePlayers()
	self.finishScreenTiming()

	classes.mainLayout = mainLayout
	settingsdlg.mainLayout = mainLayout

        self.popupSettings = Popup(title="Options", content=SettingsPopupDlg(),
              size_hint=(0.9, 0.9), auto_dismiss=False)

	content = self.popupSettings.content

	direct = 'horizontal' if self.scrOrientation in [0,180] else 'vertical'
	content.setline1.orientation = direct
	content.setline2.orientation = direct
	content.setline3.orientation = direct
	content.setline4.orientation = direct

	spinmusic = content.setline3.subbox2.musicspinner
	spinclock = content.setline3.subbox3.clockspinner
	spinclock.text = WATCHES

	# adjust tone list
	rt = ringingTones()
	sys = json.loads(settings_audio)
	aaudio = []
	for s in sys:
	    item = s
	    if not s['type'] in 'title' and s['key'] == 'ringtone':
		aaudio = s['options'] + rt
#		aaudio.append(item)
	spinmusic.text = RING_TONE
	spinmusic.values = aaudio
	spinmusic.bind(text=self.show_selected_value)

	content.valv = self.avolume
	content.valb = self.brightness
	content.valm = self.micvolume
	content.vald = self.dnd_mode
	content.vals = SCREEN_SAVER / 60

	self.popupSettings.open()


    # ###############################################################
    def show_selected_value(self, spinner, text):
	"clock|tine item change"
#	global SCREEN_SAVER, RING_TONE

	Logger.info('%s: %s' % (whoami(), text))

	content = self.popupSettings.content
	spinmusic = content.setline3.subbox2.musicspinner

	if spinner == spinmusic:
	    stopWAV()
	    Clock.schedule_once(lambda dt: playTone(APLAYER + ' ' + APARAMS + spinmusic.text))


    # ###############################################################
    def closePopupSettings(self, small=True):
	global SCREEN_SAVER, WATCHES, RING_TONE, config
	"close quick settings dialog"

	if not self.popupSettings: return

	content = self.popupSettings.content
	a = int(content.valv)
	m = int(content.valm)
	b = int(content.valb)
	s = int(content.vals)
	d = bool(content.vald)
	music = content.setline3.subbox2.musicspinner.text
	clock = content.setline3.subbox3.clockspinner.text

	stopWAV()

	if a != self.avolume:
	    self.avolume = a
	    config.set('devices', 'volume', self.avolume)
	    send_command('%s %d' % (SETVOLUME_SCRIPT, self.avolume))

	if m != self.micvolume:
	    self.micvolume = m
	    config.set('devices', 'micvolume', self.micvolume)
	    send_command('%s %d' % (SETMICVOLUME_SCRIPT, self.micvolume))

	if b != self.brightness:
	    self.brightness = b
	    config.set('command', 'brightness', self.brightness)
	    send_command('%s %d' % (BRIGHTNESS_SCRIPT, self.brightness))

	if s != (SCREEN_SAVER / 60):
	    SCREEN_SAVER = s * 60
	    config.set('command', 'screen_saver', s)

	if music != RING_TONE:
	    RING_TONE = music
	    tones.PHONERING_PLAYER = APLAYER + ' ' + APARAMS + music
	    config.set('devices', 'ringtone', music)

	if clock != WATCHES:
	    WATCHES = clock
	    config.set('command', 'watches', clock)

	if d != self.dnd_mode:
	    self.dnd_mode = d
	    config.set('command', 'dnd_mode', self.dnd_mode)

	config.write()

	Logger.info('%s: volume=%d mic=%d brightness=%d dnd=%r saver=%d music=%s clock=%s'\
	    % (whoami(), self.avolume, self.micvolume, self.brightness, self.dnd_mode, s, music, clock))

	self.popupSettings.dismiss()
	self.popupSettings = None

	docall_button_global.imgpath = DND_CALL_IMG if self.dnd_mode else MAKE_CALL_IMG

	if small:
	    self.showPlayers()
	    self.startScreenTiming()


    # ###############################################################
    def testPwdSettings(self, val):
	Logger.debug('%s: %s' % (whoami(), val))

	self.popupSettings = None

	if len(val) > 0 and self.masterPwd == val:
	    self.scrmngr.current = SETTINGS_SCR
	    App.get_running_app().open_settings()
	else:
	    self.showPlayers()
	    self.startScreenTiming()


    # ###############################################################
    def settings_worker(self, dt=7.5):
	"prepare settings"
	Logger.info('%s:' % whoami())

	app = App.get_running_app()
	app.open_settings()
	app.close_settings()


    # ###############################################################
    def openAppSettings(self):
	"get password"
	Logger.debug('%s:' % whoami())

	self.popupSettings = MyInputBox(titl='Enter password', txt='', cb=self.testPwdSettings, pwd=True, ad=False)
	self.popupSettings.open()
	Clock.schedule_once(lambda dt: self.popupSettings.refocus_text_input(0), .95)


    # ###############################################################
    def callback_set_voice(self, value=-1):
	"volume buttons"
	global current_call

	Logger.debug('%s:' % whoami())

	if current_call is None:
	    if value == self.btnSettings: self.callback_set_options()
	    else: Clock.schedule_once(self.return2clock, .2)


    # ###############################################################
    def restart_player_window(self, idx):
	"process is bad - restart"
	global active_display_index

	Logger.info('%s: idx=%d' % (whoami(), idx))

	self.displays[idx].hidePlayer()
	send_command("ps aux | grep omxplayer%d | grep -v grep | awk '{print $2}' | xargs kill -9" % idx)
	send_command('%s%d' % (CMD_KILL, procs[idx].pid))

	active_display_index = idx
	self.displays[idx].setActive(True)


    # ###############################################################
    def supporter1(self, dt):
	"clear restart flag"
	Logger.debug('%s: clear restart flag' % whoami())

	self.appRestartEvent = None


    # ###############################################################
    def checkDoubleTap(self,touch):
	"check if double tap is in valid area, if yes -> finish app"
	Logger.info('%s:' % whoami())

	x = touch.x
	y = touch.y
	if x < 50 and y > 430:
	    if self.appRestartEvent is None:
		self.appRestartEvent = Clock.schedule_once(self.supporter1, 5.)
	    else:
		Clock.unschedule(self.appRestartEvent)
		self.appRestartEvent = None

	if x > 730 and y > 430 and not self.appRestartEvent is None:
	    Logger.error('%s: valid triple tap -> restart' % whoami())
	    App.get_running_app().stop()


    # ###############################################################
    def on_touch_up(self, touch):
	"process touch up event"
	global active_display_index, current_call, docall_button_global

#	Logger.info('%s:' % whoami())
	if touch:
	    Logger.debug('%s: touch=%d,%d double=%d triple=%d loseNext=%r'\
		% (whoami(), touch.x, touch.y, touch.is_double_tap, touch.is_triple_tap, self.loseNextTouch))
	    self.touchdistance = -1.

	if self.loseNextTouch:
	    self.loseNextTouch = False
	    return True

	if len(procs) == 0: return True

	if not touch is None and touch.is_triple_tap:
	    if not current_call and self.scrmngr.current == CAMERA_SCR and self.popupSettings is None:
		self.restart_player_window(active_display_index)
	    return True

	if not touch is None and touch.is_double_tap:
	    self.checkDoubleTap(touch)
	    return True

	if current_call is None: self.startScreenTiming()

	if touch is None:
	    self.loseNextTouch = True
	    return True

	if not self.scrmngr.current == CAMERA_SCR or not current_call is None: return True

	self.touches = {}

	idx = 0
	for child in self.walk():
	    if child is self: continue
	    if '.VideoLabel' in str(child):
		if child.collide_point(*touch.pos):
		    active_display_index = idx
		    Logger.info('%s: child=%r setActiveWin=%s' %(whoami(), child, child.id))
		    break
		idx += 1

	for idx, d in enumerate(self.displays):
	    d.setActive(idx == active_display_index)

	if '--> ' in docall_button_global.btntext: docall_button_global.btntext = ''

	self.refreshLockIcons()

	return super(Indoor, self).on_touch_up(touch)


    # ###############################################################
    def on_touch_down(self, touch):
	"touch down event"
	global current_call, scr_mode

	Logger.debug('%s: cnt=%d %r' % (whoami(), len(self.touches)+1, touch.uid))

	if self.scrmngr.current == CAMERA_SCR and not current_call and scr_mode > 1 and self.popupSettings == None:
	    self.touches[touch.uid] = [touch,None]
	    self.touchdistance = -1.

	return super(Indoor, self).on_touch_down(touch)


    # ###############################################################
    def on_touch_move(self, touch):
	"touch move event"
	global current_call

#	Logger.debug('%s: %r' % (whoami(), touch.uid))

	try:
	    if self.scrmngr.current == CAMERA_SCR and not current_call and len(self.touches):
		if len(self.touches[touch.uid]) > 1 and self.popupSettings == None:
		    self.touches[touch.uid][1] = touch
		    self.testTouches()
	except:
	    self.touches = {}

	return super(Indoor, self).on_touch_move(touch)


    # ###############################################################
    def testTouches(self):
	"test multitouch gesture to resize video window"
	global active_display_index

	k = self.touches.keys()

        if self.touchdistance == -1.: self.touchdistance = self.touches[k[0]][0].distance(self.touches[k[1]][0])
	distance = self.touches[k[0]][0].distance(self.touches[k[1]][0])

	Logger.info('%s: n=%d o=%d' % (whoami(), distance, self.touchdistance))

	if (distance - self.touchdistance) > 60:
	    # make video bigger
	    idx = 0
	    for child in self.walk():
		if child is self: continue
		if '.VideoLabel' in str(child):
		    if child.collide_point(*self.touches[k[0]][0].pos):
			active_display_index = idx
			Logger.info('%s: child=%r setActiveWin=%s' %(whoami(), child, child.id))
			break
		    idx += 1

	    for idx, d in enumerate(self.displays):
		d.setActive(False)
		d.hidePlayer()
		if active_display_index == idx:
		    self.addInfoText('')
		    d.resizePlayer('0,0,0,0')
		    d.isPlaying = True
		else:
		    d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(0)])
		    d.isPlaying = False

	    self.showVideoEvent = Clock.schedule_once(lambda dt: self.showPlayers(), 5.)

	    self.touches = {}


    # ###############################################################
    def showPlayers(self):
	"d-bus command to show video"
	global active_display_index

	Logger.debug('%s:' % whoami())

	for d in self.displays:
	    if d.isPlaying:
		d.resizePlayer()
	    else:
		d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(255)])
		d.isPlaying = True
	    d.setActive(False)

	self.addInfoText()
	self.displays[active_display_index].setActive()

	if self.showVideoEvent: Clock.unschedule(self.showVideoEvent)
	self.showVideoEvent = None


    # ###############################################################
    def hideAndResizePlayers(self):
	"d-bus command to hide and resize video"
	Logger.debug('%s:' % whoami())

	# hide video:
	for d in self.displays:
	    d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(0)])
	    d.isPlaying = False

	# resize video:
	for d in self.displays: d.resizePlayer()


    # ###############################################################
    def hidePlayers(self, serial=False):
	"d-bus command to hide video"
	Logger.debug('%s:' % whoami())

	if self.showVideoEvent: Clock.unschedule(self.showVideoEvent)
	self.showVideoEvent = None

	Clock.schedule_once(lambda dt: self.hideAndResizePlayers(),.1)


    # ###############################################################
    def setButtons(self, visible):
	"add/remove buttons"
	global docall_button_global

	Logger.debug('%s: %r' % (whoami(), visible))

	if visible:
	    self.btnAreaH.remove_widget(self.btnScrSaver)
	    self.btnAreaH.remove_widget(self.btnSettings)
	    self.btnScrSaver.parent = None
	    self.btnSettings.parent = None
	else:
	    cnt = 5 if self.scrOrientation in [0,180] else 3
	    if self.btnScrSaver.parent is None:
		self.btnAreaH.add_widget(self.btnScrSaver, cnt)
		self.btnAreaH.add_widget(self.btnSettings)

	if docall_button_global.disabled:
	    Clock.schedule_once(self.enable_btn_docall)

	Clock.schedule_once(self.image_update_loop)


    # ###############################################################
    def init_sliders(self):
	"prepare volume sliders"
	Logger.debug('%s:' % whoami())

	self.micslider = SliderArea()
	self.micslider.imgpath = MICROPHONE_IMG
	self.micslider.on_val = self.onMicVal
	self.micslider.val = self.micvolume
	if self.scrOrientation in [0,180]:
	    self.micslider.orientation = 'vertical'
	    self.micslider.width = 80
	    self.micslider.size_hint = (None, 1.)
	    self.micslider.imgslider.size_hint = (1, None)
	    self.micslider.imgslider.height = 32
	else:
	    self.micslider.orientation = 'horizontal'
	    self.micslider.height = 88
	    self.micslider.size_hint = (1., None)
	    self.micslider.imgslider.size_hint = (None, 1)
	    self.micslider.imgslider.width = 32

	self.volslider = SliderArea()
	self.volslider.imgpath = VOLUME_IMG
	self.volslider.on_val = self.onVolVal
	self.volslider.val = self.avolume
	if self.scrOrientation in [0,180]:
	    self.volslider.orientation = 'vertical'
	    self.volslider.width = 80
	    self.volslider.size_hint = (None, 1.)
	    self.volslider.imgslider.size_hint = (1, None)
	    self.volslider.imgslider.height = 32
	else:
	    self.volslider.orientation = 'horizontal'
	    self.volslider.height = 88
	    self.volslider.size_hint = (1., None)
	    self.volslider.imgslider.size_hint = (None, 1)
	    self.volslider.imgslider.width = 32

	self.micslider.parent = None
	self.volslider.parent = None


    # ###############################################################
    def onMicVal(self):
	"set microphone value"
	global config

	Logger.debug('%s: %d %d' % (whoami(), self.micslider.audioslider.value, self.micslider.val))

	self.micvolume = self.micslider.audioslider.value

	config.set('devices', 'micvolume', self.micvolume)
	config.write()

	send_command('%s %d' % (SETMICVOLUME_SCRIPT, self.micvolume))


    # ###############################################################
    def onVolVal(self):
	"set speaker volume value"
	global config

	Logger.debug('%s: %d %d' % (whoami(), self.volslider.audioslider.value, self.volslider.val))

	self.avolume = self.volslider.audioslider.value

	config.set('devices', 'volume', self.avolume)
	config.write()

	send_command('%s %d' % (SETVOLUME_SCRIPT, self.avolume))


    # ###############################################################
    def add_sliders(self):
	"add sliders to the working area"
	Logger.debug('%s: rep=%d mic=%d' % (whoami(), self.avolume, self.micvolume))

	l = self.workArea if self.scrOrientation in [0,180] else self.cameras

	if self.micslider and self.micslider.parent: l.remove_widget(self.micslider)
	if self.volslider and self.volslider.parent: l.remove_widget(self.volslider)

	self.init_sliders()

	self.micslider.val = self.micvolume
	self.volslider.val = self.avolume

	l.add_widget(self.micslider, 1 if self.scrOrientation in [0,180] else 0)
	l.add_widget(self.volslider)
	#print('%s: cnt=%d' % (whoami(), len(l.children)))


    # ###############################################################
    def del_sliders(self):
	"delete sliders from the working area"
	Logger.debug('%s:' % whoami())

	l = self.workArea if self.scrOrientation in [0,180] else self.cameras
	l.remove_widget(self.micslider)
	l.remove_widget(self.volslider)
	self.micslider.parent = None
	self.volslider.parent = None


    # ###############################################################
    def findTargetWindow(self, addr):
	"find target window according to calling address"
	global active_display_index

        Logger.info('find target window: address=%s' % addr)

	ret = False
	self.addInfoText(addr)

	if addr != '':
	    active_display_index = 0
	    for idx, d in enumerate(self.displays):
		d.setActive(False)
		d.hidePlayer()
		if not ret and d.sipcall in addr and d.sipcall != '':
		    active_display_index = idx
		    self.addInfoText(d.sipcall)
		    d.resizePlayer('90,10,710,390')
		    d.isPlaying = True
		    ret = True
		else:
		    d.dbus_command(TRANSPARENCY_VIDEO_CMD + [str(0)])
		    d.isPlaying = False

	self.refreshLockIcons()
	self.add_sliders()

	if ret and not self.scrmngr.current == CAMERA_SCR:
	    self.displays[active_display_index].dbus_command(TRANSPARENCY_VIDEO_CMD + [str(255)])

	self.scrmngr.current = CAMERA_SCR

	return ret


    # ###############################################################
    def get_volume_value(self):
	"retrieve current volume level"
        Logger.debug('%s:' % whoami())

	try:
	    s = get_info(VOLUMEINFO_SCRIPT).split()
	except:
	    s = []

	# speaker:
	if len(s) < 4: vol = 100		# script problem!
	else: vol = int(round(float(s[1]) / (int(s[3]) - int(s[2])) * 100)) #or 100

	# available volume steps:
	if vol > 99: vol = 100
	elif vol < 20: vol = 20
	self.avolume = vol - vol % 5

	# mic:
	if len(s) < 8: self.micvolume = 100		# script problem!
	else: self.micvolume = int(round(float(s[5]) / (int(s[7]) - int(s[6])) * 100)) #or 100

	# available volume steps:
	if self.micvolume > 99: self.micvolume = 100
	elif self.micvolume < 20: self.micvolume = 20
	self.micvolume = self.micvolume - self.micvolume % 5

	return vol


# ###############################################################

class IndoorApp(App):

    restartAppFlag = False
    rotation = 0

    # ###############################################################
    def build(self):
	global config, ROTATION

        Logger.warning('Hello Indoor 2.0')

	self.config = config

	send_command('pkill -9 omxplayer')

	reset_usb_audio()
	Clock.schedule_once(lambda dt: send_command(HIDINIT_SCRIPT), 2.)

        try: self.rotation = config.getint('gui', 'screen_orientation')
        except: self.rotation = 0
	ROTATION = self.rotation

#        Config.set('kivy', 'keyboard_mode','systemandmulti')##        Config.set('kivy', 'keyboard_mode','')
        Logger.debug('Configuration: keyboard_mode=%r, keyboard_layout=%r, rotation=%r'\
	    % (Config.get('kivy', 'keyboard_mode'), Config.get('kivy', 'keyboard_layout'),\
		Config.get('graphics','rotation')))

	self.settings_cls = SettingsWithSidebar if self.rotation in [0,180] else SettingsWithSpinner
        self.use_kivy_settings = False

	self.changeInet = False

	return Indoor()


#    def on_start(self):
#        self.dbg(whoami())
#
#    def on_stop(self):
#        self.dbg(whoami())
#	self.root.stop.set()


    # ###############################################################
    def build_config(self, cfg):
	"build config"
	global config

        Logger.debug('%s:' % whoami())
	config = setDefaultConfig(config, False)


    # ###############################################################
    def get_uptime_value(self):
	"retrieve system uptime"
	uptime_string = ''
	try:
	    with open('/proc/uptime', 'r') as f:
		uptime_seconds = float(f.readline().split()[0]) or 0
		uptime_string = str(datetime.timedelta(seconds = uptime_seconds))
		uptime_string = uptime_string[:uptime_string.find('.')]
	except: pass

        Logger.debug('%s: uptime=%s' % (whoami(), uptime_string))

	return uptime_string


    # ###############################################################
    def build_settings(self, settings):
	"display settings screen"
	global config

        Logger.debug('%s:' % whoami())

	settings.register_type('buttons', SettingButtons)
	settings.register_type('timezone', TzSettingDialog)
#	settings.register_type('scrolloptions', SettingScrollOptions)

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

	atimezone = timezone_settings
	"""
	# fill timezones
	sys = json.loads(timezone_settings)
	atimezone = []
	for s in sys:
	    item = s
	    if s['type'] in 'scrolloptions' and s['key'] in 'timezone':
		item['options'] = getTimeZoneList()
	    atimezone.append(item)
	atimezone = json.dumps(atimezone)
	"""

        settings.add_json_panel('GUI', config, data=settings_gui)
        settings.add_json_panel('Outdoor Devices', config, data=acomm)
        settings.add_json_panel('SIP', config, data=asip)
        settings.add_json_panel('Network', config, data=asystem)
        settings.add_json_panel('Time zone', config, data=atimezone)
        settings.add_json_panel('Service', config, data=settings_services)
        settings.add_json_panel('About', config, data=settings_about)


    # ###############################################################
    def display_settings(self, settings):
	"display settings"
	global mainLayout, config

        Logger.debug('%s:' % whoami())

	config = get_config()

	mainLayout.ids.settings.clear_widgets()

	mainLayout.ids.settings.add_widget(settings)


    # ###############################################################
    def on_config_change(self, cfg, section, key, value):
	"config item changed"
	global config, SCREEN_SAVER, ROTATION, mainLayout

        Logger.info('%s: sec=%s key=%s val=%s' % (whoami(), section, key, value))
	token = (section, key)
	value = value.strip()

	config.set(section, key, value)
	config.write()

	if section == 'common':
	    self.restartAppFlag = True
	elif 'system' == section:
	    if token == ('system', 'inet'):
		self.changeInet = True
	    elif key in ['ipaddress', 'netmask', 'gateway', 'dns']:
		if config.get('system', 'inet') == 'dhcp':
		    config.set(section, key, self.config.get(section, key))
		    config.write()
		else:
		    self.changeInet = True
	elif 'sip' == section:
	    if (key in ['sip_server_addr', 'sip_username', 'sip_p4ssw0rd']):
		if config.get('sip', 'sip_mode') == 'peer-to-peer':
		    config.set(section, key, self.config.get(section, key))
		    config.write()
		else:
		    self.restartAppFlag = True
	    elif token == ('sip', 'buttoncalllog'):
		if 'button_calllog' == value:
		    self.myAlertListBox('Call log history', reversed(callstats.call_log))
	    elif token == ('sip', 'sip_mode'):
		self.restartAppFlag = True
	elif 'timezones' == section:
	    if token == ('timezones', 'timezone'):
		send_command('./settimezone.sh ' + value)
	elif 'service' == section:
	    if token == ('service', 'app_log'):
		saveKivyCfg('kivy', 'log_level', 'critical' if value == 'none' else value)
		self.restartAppFlag = True
	    elif token == ('service', 'sip_log'):
		self.restartAppFlag = True
	    elif token == ('service', 'buttonpress'):
		if 'button_status' == value:
		    myappstatus(titl='App status', uptime=self.get_uptime_value(), cinfo=callstats.call_statistics)
	    elif token == ('service', 'buttonlogs'):
		if 'button_loghist' == value:
		    # LoggerHistory.history:
		    recent_log = [('%d %s' % (record.levelno, record.msg)) for record in LoggerHistory.history] #reversed(LoggerHistory.history
		    self.myAlertListBox('Log messages history', recent_log)
	    elif token == ('service', 'buttonfactory'):
		if 'button_factory' == value:
		    MyYesNoBox(titl='WARNING', txt='Application is going to rewrite actual configuration!\n\nContinue?',
			cb=self.factoryReset, ad=True).open()
	    elif token == ('service', 'app_upd'):
		if 'button_app_upd' == value:
		    MyAlertBox(titl='WARNING', txt='Application is going to install new version!\n\nPress OK',
			cb=self.appUpdate, ad=False).open()
	    elif token == ('service', 'app_rst'):
		if 'button_app_rst' == value:
		    MyAlertBox(titl='WARNING', txt='Application is going to restart!\n\nPress OK', cb=self.popupClosed, ad=False).open()
	    elif token == ('service', 'tunnel_flag'):
		try:
		    v = int(value) > 0
		except:
		    v = False
		infoTxt = 'Tunnel is ENABLED' if v else 'Tunnel is DISABLED'
		MyAlertBox(titl='WARNING', txt=infoTxt, cb=self.tunnelChanges, ad=False).open()
	    elif token == ('service', 'masterpwd'):
		if len(value) < 1:
		    config.set(section, key, self.config.get(section, key))
		    config.write()
		    MyAlertBox(titl='WARNING', txt='Bad password!\n\nPassword will not change', cb=None, ad=False).open()
		self.restartAppFlag = True
	elif 'about' == section:
	    if token == ('about', 'licencekey'):
		self.restartAppFlag = True
	    elif token == ('about', 'buttonregs'):
		if 'button_regs' == value:
		    rsp = send_regs_request(registration.REGISTRATION_URL_ADDRESS,\
			[self.config.get('about','serial'), self.config.get('about','regaddress'), self.config.get('about','licencekey')])
		    if len(rsp) > 24:
			config.set('about', 'licencekey', rsp.strip())
			config.write()
			self.restartAppFlag = True
			MyAlertBox(titl='WARNING', txt='Application is going to restart!\n\nPress OK', cb=self.popupClosed, ad=False).open()
		    else:
			MyAlertBox(titl='Registration', txt='Your licence key will come to your email address\ntill 3 working days\n\nPress OK',\
			    cb=None, ad=False).open()
	elif 'gui' == section:
	    if token != ('gui', 'outgoing_calls'): self.restartAppFlag = True
	    else:
		val = config.get('gui', 'outgoing_calls').strip()
		self.outgoing_mode = 'True' == val or '1' == val
	    if token == ('gui', 'screen_orientation'):
		saveKivyCfg('graphics', 'rotation', value)


    # ###############################################################
    def popupClosed(self, popup=None):
	"restart App after alert box"
        Logger.debug('%s:' % whoami())

	kill_subprocesses()
	App.get_running_app().stop()


    # ###############################################################
    def appUpdateWorker(self):
	"update the application - task"
	global config

	repo = ''
	try:
	    repo = config.get('service','update_repo')
	except:
	    repo = 'production'
	repo = 'isra67' if repo == 'development' else 'inoteska'

        Logger.debug('%s: repo=%s' % (whoami(), repo))

	if not '085a5ba7f' in self.config.get('about','serial'): # not for development RPi
	    t1 = Thread(target=self.call_script, kwargs={'addr': '/root/app/appdiff.sh ' + repo})
	    t2 = Thread(target=self.call_script, kwargs={'addr': '/root/indoorpy/appdiff.sh ' + repo})
	    t1.daemon = True
	    t2.daemon = True
	    t1.start()
	    t1.join()
	    t2.start()
	    t2.join()

	    kill_subprocesses()
	    App.get_running_app().stop()
	else:
	    Logger.info('%s: repo=%s STOPPED IN THIS DEVICE!' % (whoami(), repo))


    # ###############################################################
    def call_script(self, addr):
	"update the application - command"
        Logger.debug('%s: addr=%s' % (whoami(), addr))

#	subprocess.call(addr)
	send_command(addr)


    # ###############################################################
    def appUpdate(self):
	"update the application - command"
	global scrmngr, config

	repo = ''
	try:
	    repo = config.get('service','update_repo')
	except:
	    repo = 'production'
	repo = 'isra67' if repo == 'development' else 'inoteska'

        Logger.debug('%s: repo=%s' % (whoami(), repo))

	scrmngr.current = WAIT_SCR

	i1 = get_info('/root/indoorpy/checkupdate.sh ' + repo)
	i2 = get_info('/root/app/checkupdate.sh ' + repo)

	if 'equal' == i1 and 'equal' == i2:
	    MyAlertBox(titl='Info', txt='Your version is up to date\nNo new version was installed\n\nPress OK',\
		cb=None, ad=False).open()
	    scrmngr.current = SETTINGS_SCR
	else:
	    self.appUpdateWorker()


    # ###############################################################
    def factoryReset(self):
	"factory reset"
	global config, scrmngr

        Logger.debug('%s: fn=%s' % (whoami(), config.filename))

	scrmngr.current = WAIT_SCR

	delCustomRingingTones()

	config = setDefaultConfig(config, True)
	config.update_config(config.filename, True)

	saveKivyCfg('kivy', 'log_level', 'debug')
	saveKivyCfg('graphics', 'rotation', '0')

	MyAlertBox(titl='WARNING', txt='Success.\n\nApplication is going to restart!\n\nPress OK',
	    cb=self.popupClosed, ad=False).open()


    # ###############################################################
    def tunnelChanges(self):
	"enable/disable tunnel"
	global config

	try:
	    value = config.get('service', 'tunnel_flag').strip()
	    flag = 'True' == value or '1' == value
	except: flag = False
        Logger.warning('%s: flag=%r' % (whoami(), flag))

	if flag: send_command('./tunnelservice.sh')
	else: send_command('./tunnel.sh stop')


    # ###############################################################
    def close_settings(self, *args):
	"close button pressed"
	global scrmngr, mainLayout, config

        Logger.debug('%s:' % whoami())

	mainLayout.ids.settings.clear_widgets()

	if self.changeInet or self.restartAppFlag:
	    if self.changeInet: # start script
		send_command(SETIPADDRESS_SCRIPT\
			 + ' ' + config.get('system', 'inet')\
			 + ' ' + config.get('system', 'ipaddress')\
			 + ' ' + config.get('system', 'netmask')\
			 + ' ' + config.get('system', 'gateway')\
			 + ' ' + config.get('system', 'dns'))
		config.set('system', 'inet', 'manual')
		config.write()
	    MyAlertBox(titl='App info', txt='Application is going to restart\nto apply your changes!\n\nPress OK',
		cb=self.popupClosed, ad=False).open()
	else:
	    self.changeInet = False
	    scrmngr.current = CAMERA_SCR


    # ###############################################################
    def myAlertListBox(self, titl, ldata, cb=None, ad=True):
	"List box"
	LJUST = 83

	Logger.debug('%s: title=%s' % (whoami(), titl))

	box = MBoxLayout(orientation='vertical', spacing=5)

	if 'Call log' in titl:
	    args_converter = lambda row_idx, rec: {'text': rec, 'size_hint_y': None,
					    'color': (), 'height': 25}
	else:
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

	    args_converter = lambda row_idx, rec: {'text': rec, 'size_hint_y': None,
					    'color': clr[row_idx], 'height': 25}

	# justify text:
	data = [t[:LJUST] + '...' if len(t) > LJUST else t[:] for t in ldata]

	list_adapter = ListAdapter(data=data, cls=MyListViewLabel,
			    args_converter=args_converter,
			    selection_mode='single', allow_empty_selection=True)

	list_view = ListView(adapter=list_adapter)
	box.add_widget(list_view)

	p = Popup(title=titl, content=box, size_hint=(0.85, 0.95), auto_dismiss=ad)
	p.open()


# ###############################################################
#
# Start
#
# ###############################################################

if __name__ == '__main__':
    Clock.schedule_once(lambda dt: send_command('./killapp.sh runme.py'), 30)
    IndoorApp().run()
