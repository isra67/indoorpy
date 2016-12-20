#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.network.urlrequest import UrlRequest
#from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

import atexit
import datetime
#import dbus

#import logging
import os
import signal
import socket
#from subprocess import Popen, PIPE
import subprocess
import sys
import time

import pjsua as pj

#from my_lib import my_screensaver as m_ss
import my_lib as m_ss

procs = []

@atexit.register
def kill_subprocesses():
    "tidy up at exit or break"
    print('destroy lib at exit')
    try:
	pj.Lib.destroy()
    except:
	pass
    print('kill subprocesses at exit')
    for proc in procs:
	try:
            proc.kill()
	except:
	    pass

###############################################################
#
# Declarations
#
# ###############################################################

CMD_KILL = 'kill -9 '

CONFIG_FILE = 'indoorconfig.ini'

BUTTON_CALL_ANSWER = '=Answer Call='
BUTTON_CALL_HANGUP = '=HangUp Call='
BUTTON_DO_CALL = '=Do Call='

BUTTON_DOOR_1 = '=Open Door 1='
BUTTON_DOOR_2 = '=Open Door 2='

SERVER_IP_ADDR = '192.168.1.250'

COLOR_BUTTON_BASIC = 1,1,1,1
COLOR_ANSWER_CALL = 1,0,0,1
COLOR_HANGUP_CALL = 1,1,0,1
COLOR_NOMORE_CALL = COLOR_BUTTON_BASIC

LOG_LEVEL = 3
current_call = None
acc = None

main_state = 0
docall_button_global = None

active_display_index = 0

ring_event = None
APLAYER = 'aplay'
APARAMS = '-q -N -f cd -D plughw:1,0'
RING_WAV = APLAYER + ' ' + APARAMS + ' ' +'share/sounds/linphone/rings/oldphone.wav &'

SCREENSAVER_FNAME = 'http://www.spruto.tv/get_file/1/38577f19393369cb2c5d785beb3c3ffc/80000/80730/80730.mp4?start=0'

screensaver_process = None

SMALL_VIDEO_CMD = ['setvideopos','150','0','650','429']
WIDE_VIDEO_CMD = ['setvideopos','0','0','800','429']
TRANSPARENCY_VIDEO_CMD = ['setalpha']

DBUS_PLAYERNAME = 'org.mpris.MediaPlayer2.omxplayer'

transparency_value = 0
transparency_event = None

mainLayout = None

# ###############################################################
#
# Functions
#
# ###############################################################

# Logging callback
def log_cb(level, str, len):
    print str,


def playWAV(dt):
    global RING_WAV
    try:
        os.system(RING_WAV)
    except:
	pass


def stopWAV():
    global ring_event
    Clock.unschedule(ring_event)
    ring_event = None
    os.system('pkill -9 ' + APLAYER)

def send_dbus(dst,args):
    "send DBUS command to omxplayer"
    cmd = ' '.join(map(str, ['./dbuscntrl.sh', dst] + args))
    try:
        os.system(cmd)
    except:
	pass

#    print 'sendDBUS...', cmd


# ###############################################################
#
# Classes
#
# ###############################################################

# Callback to receive events from account
class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    # Notification on incoming call
    def on_incoming_call(self, call):
        global current_call
        if current_call:
            call.answer(486, "Busy")
            return

        print "Incoming call from ", call.info().remote_uri

        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180)


# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global current_call, ring_event, transparency_value
        global main_state, docall_button_global, screensaver_process
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text, self.call.info().state,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        main_state = self.call.info().state
        transparency_value = 0

        if main_state == pj.CallState.DISCONNECTED:
            current_call = None
#            print 'Current call is', current_call

        if main_state == pj.CallState.EARLY:
            ring_event = Clock.schedule_interval(playWAV, 3.5)
            playWAV(3.5)
        else:
            stopWAV()

        if screensaver_process:
#            m_ss.stop_screensaver(screensaver_process)
            screensaver_process = None

        if main_state == pj.CallState.INCOMING or\
           main_state == pj.CallState.EARLY:
            if main_state is not pj.CallState.CALLING:
		docall_button_global.color = COLOR_ANSWER_CALL
		docall_button_global.text = BUTTON_CALL_ANSWER
            m_ss.send_dbus(SMALL_VIDEO_CMD)

        if main_state == pj.CallState.DISCONNECTED:
            docall_button_global.color = COLOR_NOMORE_CALL
            docall_button_global.text = BUTTON_DO_CALL
            m_ss.send_dbus(WIDE_VIDEO_CMD)

        if main_state == pj.CallState.CONFIRMED:
            docall_button_global.color = COLOR_HANGUP_CALL
            docall_button_global.text = BUTTON_CALL_HANGUP

        if main_state == pj.CallState.CALLING:
	    current_call = self.call
            docall_button_global.color = COLOR_HANGUP_CALL
            docall_button_global.text = BUTTON_CALL_HANGUP

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print "Media is now active"
        else:
            print "Media is inactive"


def make_call(uri):
    "Function to make outgoing call"
    global acc
    try:
        print "Making call to", uri, acc
	if acc != None:
	    return acc.make_call(uri, cb=MyCallCallback(pj.CallCallback))
	else:
	    return None
    except pj.Error, e:
        print "Exception: " + str(e)
        return None


# ##############################################################################
class BasicDisplay:
    "basic screen class"
    def __init__(self,winpos,servaddr,streamaddr):
	"init"
	self.screenIndex = len(procs)
	self.winPosition = winpos.split(',')
	self.winPosition = [int(i) for i in self.winPosition]
	self.serverAddr = servaddr
	self.streamUrl = streamaddr
	self.playerPosition = self.winPosition

	self.playerPosition[0] += 2
	self.playerPosition[1] += 2
	self.playerPosition[2] -= 2
	self.playerPosition[3] -= 2
	self.playerPosition = [str(i) for i in self.playerPosition]

	self.playerProcess = self.initPlayer()
	procs.append(self.playerProcess)

	self.color = None
	self.line = None

	self.printInfo()


    def testTouchArea(self, x, y):
	"test if touch is in display area"
	y = 480 - y		# touch position is from bottom to up
	retx = False
	rety = False
	if self.winPosition[0] < x and self.winPosition[2] > x : retx = True
	if self.winPosition[1] < y and self.winPosition[3] > y : rety = True
	ret = retx and rety
	return ret


    def initPlayer(self):
	"start video player"
	return subprocess.Popen(['omxplayer', '--live', '--no-osd',\
	    '--dbus_name',DBUS_PLAYERNAME + str(self.screenIndex),\
	    '--layer', '1', '--no-keys', '--win', ','.join(self.playerPosition), self.streamUrl],\
	    stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE) #, close_fds = True)


    def setActive(self, active=True):
	"add or remove active flag"
	global mainLayout

	#mainLayout.canvas.clear()
	if self.color is not None: mainLayout.canvas.remove(self.color)
	if self.line is not None: mainLayout.canvas.remove(self.line)

	if active:
#	    print self.screenIndex, active
	    self.color = Color(.9,.6,.9)
	else:
	    self.color = Color(0,0,0)

	w = self.winPosition[2] - self.winPosition[0] + 2 # width
	h = self.winPosition[3] - self.winPosition[1] + 2 # height
	ltx = self.winPosition[0] - 1
	rtx = ltx + w
	lbx = ltx
	rbx = rtx
	lty = 480 - self.winPosition[1] - 210  # touch position is from bottom to up
	rty = lty
	lby = lty + h
	rby = lby
#	if active: print ltx, lty, rbx, rby

	self.line = Line(points=[ltx, lty, rtx, rty, rbx, rby, lbx, lby, ltx, lty], width = 4)
	mainLayout.canvas.add(self.color)
	mainLayout.canvas.add(self.line)


    def printInfo(self):
	"print class info"
	print self.screenIndex,'area:',self.winPosition, 'IPaddr:', self.serverAddr, 'stream:', self.streamUrl


# ##############################################################################
class Indoor(FloatLayout):
    def __init__(self, **kwargs):
        global BUTTON_DO_CALL, BUTTON_CALL_ANSWER, BUTTON_CALL_HANGUP
        global BUTTON_DOOR_1, BUTTON_DOOR_2
        global main_state, docall_button_global
	global mainLayout

        super(Indoor, self).__init__(**kwargs)

        self.infinite_event = None

	self.displays = []

        # nacitanie konfiguracie
        config = ConfigParser()
        try:
            config.read('./' + CONFIG_FILE)
        except:
            self.dbg('ERROR 1: read config file!')

            try:
                config.read(dirname(__file__) + '/' + CONFIG_FILE)
            except:
                self.dbg('ERROR 2: read config file!')

        try:
            BUTTON_DO_CALL = config.get('gui', 'btn_docall')
            BUTTON_CALL_ANSWER = config.get('gui', 'btn_call_answer')
            BUTTON_CALL_HANGUP = config.get('gui', 'btn_call_hangup')
            BUTTON_DOOR_1 = config.get('gui', 'btn_door_1')
            BUTTON_DOOR_2 = config.get('gui', 'btn_door_2')
            SERVER_IP_ADDR = config.get('common', 'server_ip_address_1')
        except:
            self.dbg('ERROR: read config file!')

	mainLayout = self   #.ids.mainLayout

        main_state = 0
        self.info_state = 0
        self.myprocess = None

        self.init_myphone()

	self.init_screen(config)

        self.rstTransparency()

        self.infinite_event = Clock.schedule_interval(self.infinite_loop, 6.9)
        Clock.schedule_interval(self.info_state_loop, 10.)

        self.ids.btnDoor1.text = BUTTON_DOOR_1
        self.ids.btnDoor1.color = COLOR_BUTTON_BASIC
        self.ids.btnDoor2.text = BUTTON_DOOR_2
        self.ids.btnDoor2.color = COLOR_BUTTON_BASIC
        docall_button_global = self.ids.btnDoCall
        docall_button_global.text = BUTTON_DO_CALL
        docall_button_global.color = COLOR_BUTTON_BASIC


    def init_screen(self, cfg):
	"define app screen"
	scr_mode = cfg.get('gui', 'screen_mode')
	if scr_mode == None or scr_mode == '': scr_mode = 0

	if scr_mode == 1:
	    wrange = 0
	    wins = ['0,0,800,430']
	elif scr_mode == 2:
	    wrange = 2
	    wins = ['0,0,800,216', '0,216,800,430']
	elif scr_mode == 3:
	    wrange = 2
	    wins = ['0,0,400,430', '400,0,800,430']
	else:
	    wrange = 4
	    wins = ['0,0,400,216', '400,0,800,216', '0,216,400,430', '400,216,800,430']

	self.dbg('scr_mode:' + str( scr_mode ) + ' wrange:' + str(wrange))

	for i in range(0,wrange):
	    win = wins[i]
	    serv = cfg.get('common', 'server_ip_address_'+str(i + 1))
	    vid = cfg.get('common', 'server_stream_'+str(i + 1))

	    displ = BasicDisplay(win,serv,vid)
	    self.displays.append(displ)


    def init_myphone(self):
	"sip phone init"
        global acc

        # Create library instance
        lib = pj.Lib()

        try:
            # Init library with default config and some customized logging config
            lib.init(log_cfg = pj.LogConfig(level=LOG_LEVEL, callback=log_cb))

	    comSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	    comSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Create UDP transport which listens to any available port
            transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5060))

            print "\nListening on", transport.info().host, "port", transport.info().port, "\n"

            # Start the library
            lib.start()

            # Create local account
            acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())

            my_sip_uri = "sip:" + transport.info().host + ":" + str(transport.info().port)
            print "\nAccount", acc, "at URI", my_sip_uri, "\n"

        except pj.Error, e:
            print "Exception: " + str(e)
            lib.destroy()
            lib = None

    def info_state_loop(self, dt):
        global current_call

        if current_call is not None: self.info_state = 0

        if self.info_state == 0:
            self.info_state = 1
            self.ids.btnDoor1.text = BUTTON_DOOR_1
            self.ids.btnDoor2.text = BUTTON_DOOR_2
        elif self.info_state == 1:
            self.info_state = 2
            self.ids.btnDoor2.text = datetime.datetime.now().strftime("%H:%M")
        elif self.info_state == 2:
            self.info_state = 3
            self.ids.btnDoor1.text = BUTTON_DOOR_1 #'(c) Inoteska'
            self.ids.btnDoor2.text = BUTTON_DOOR_2
        elif self.info_state == 3:
            self.info_state = 0
            self.ids.btnDoor2.text = datetime.datetime.now().strftime("%d.%m.%Y")


    def infinite_loop(self, dt):
        global current_call, main_state, screensaver_process
        if screensaver_process is None and\
           current_call is None:
#            screensaver_process = m_ss.start_screensaver(SCREENSAVER_FNAME,'2')
            pass
        self.ids.txtBasicLabel.text = datetime.datetime.now().strftime("%H:%M\n%d.%m.%Y")

	for idx, p in enumerate(procs):
	    if p.poll() is not None:
		self.dbg( "Process" + str(idx) + " (" + str(p.pid) + ") is dead")
		try:
		    os.system(CMD_KILL + str(p.pid))
		    p.kill()
		except:
		    pass
		procs[idx] = self.displays[idx].initPlayer()


    def callback_btn_docall(self):
	"make outgoing call"
        global current_call

        self.dbg(BUTTON_DO_CALL)

        self.rstTransparency()

        if current_call is not None:
            if main_state == pj.CallState.EARLY:
                stopWAV()
                current_call.answer(200)
            else:
                current_call.hangup()
	else:
	    make_call('sip:' + SERVER_IP_ADDR + ':5060')


    def gotResponse(self, req, results):
#        print 'Relay: ', req, results
        pass

    def setRelayRQ(self, relay):
        req = UrlRequest('http://' + SERVER_IP_ADDR + '/cgi-bin/remctrl.sh?id=' + relay,\
                on_success = self.gotResponse, timeout = 5)

    def callback_btn_door1(self):
        self.dbg(BUTTON_DOOR_1)
        self.setRelayRQ('relay1')
        self.rstTransparency()

    def callback_btn_door2(self):
        self.dbg(BUTTON_DOOR_2)
        self.setRelayRQ('relay2')
        self.rstTransparency()

    def settings_callback(self, instance):
        print 'LOOK AT ME!'
        self.rstTransparency()

    def callback_set_options(self):
        self.dbg(self.ids.btnSetOptions.text)
        self.rstTransparency(255)

        popup = Popup(title='Settings',
            content=TextInput(text='To do...',focus=True),
            size_hint=(None, None), size=(700, 350))
        popup.bind(on_dismiss = self.settings_callback)
        popup.open()

    def callback_set_voice(self, value):
        self.dbg('Voice: ' + str(value))
        self.rstTransparency()

    def on_touch_up(self, touch):
	"process touch up event"
#        print 'touchUp: ', touch.x, touch.y, touch.is_double_tap

	if touch.is_double_tap:
	    self.callback_set_options()
#	    self.rstTransparency()
#	    self.hide_video()
	    self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
	    self._keyboard.bind(on_key_down=self._on_keyboard_down)
            print 'keyboard?', self._keyboard
	    return

	rx = int(round(touch.x))
	ry = int(round(touch.y))

	for idx, d in enumerate(self.displays):
	    t = d.testTouchArea(rx, ry)
	    if t:
		active_display_index = idx
	    else:
		d.setActive(False)

	self.displays[active_display_index].setActive()


    def _keyboard_closed(self):
	print 'keyboard closed'
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        self.rstTransparency(200)


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
	print keyboard, keycode, text, modifiers
        if keycode[1] == 'w':
            self.player1.center_y += 10
        elif keycode[1] == 's':
            self.player1.center_y -= 10
        elif keycode[1] == 'up':
            self.player2.center_y += 10
        elif keycode[1] == 'down':
            self.player2.center_y -= 10
        return True


    def main_touch(self):
        global screensaver_process, transparency_value, transparency_event
        global current_call

        if screensaver_process is not None:
            m_ss.stop_screensaver(screensaver_process)
            screensaver_process = None

        Clock.unschedule(self.infinite_event)
        self.infinite_event = Clock.schedule_interval(self.infinite_loop, 6.9)

        if current_call is not None:
            self.rstTransparency()
            return

#        transparency_value = 200
        self.rstTransparency(200)
        if transparency_event is None:
            transparency_event = Clock.schedule_interval(self.transparency_loop, .05)


    def hide_video(self):
        for idx, proc in enumerate(procs):
            send_dbus(DBUS_PLAYERNAME + str(idx), TRANSPARENCY_VIDEO_CMD + [str(0)])


    def transparency_loop(self, dt):
#        self.dbg('transparency ' + str(transparency_value))
        global transparency_value, transparency_event

        if transparency_event is None: return

        if transparency_value > 0 and transparency_value < 250:
            transparency_value -= 8 #4

        for idx, proc in enumerate(procs):
            send_dbus(DBUS_PLAYERNAME + str(idx), TRANSPARENCY_VIDEO_CMD + [str(255 - transparency_value)])

        if transparency_value == 0 and transparency_event is not None:
            Clock.unschedule(transparency_event)
            transparency_event = None


    def rstTransparency(self, val = 0):
        global transparency_value
        transparency_value = val
        self.transparency_loop(0)


    def dbg(self, info):
        print info


# ###############################################################

class IndoorApp(App):
    def build(self):
        self.dbg('Hello')
        return Indoor()

    def on_start(self):
        self.dbg('START')

    def on_stop(self):
        print 'STOP'
#        lib.destroy()

    def dbg(self, info):
        print info


# ###############################################################
#
# Start
#
# ###############################################################

if __name__ == '__main__':
    IndoorApp().run()
