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
from kivy.config import Config
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, Ellipse
#from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from math import cos, sin, pi

import atexit
import datetime
from datetime import timedelta
#import inspect
import json

import os
import signal
import socket
import subprocess
import sys
import time

import pjsua as pj

from my_lib import *


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


# ###############################################################
#
# Functions
#
# ###############################################################

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


# ###############################################################
#
# Classes
#
# ###############################################################

class DigiClockWidget(FloatLayout):
    "Clock class - digital"
    pass


# ##############################################################################

class DigiClock(Label):
    "Label with date & time"
    def __init__(self, **kwargs):
        super(DigiClock, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
	t = datetime.datetime.now()
        self.text = t.strftime("%H:%M:%S")
#	if int(t.strftime('%S')) % 2:
#            self.text = t.strftime("%H:%M:%S")
#	else:
#            self.text = t.strftime("%H:%M.%S")


# ##############################################################################

class MyClockWidget(FloatLayout):
    "Clock class - analog"
    pass


# ##############################################################################

class SetScreen(Screen):
    "Settings screen"
    pass


# ##############################################################################

class Ticks(Widget):
    "Analog watches"
    galleryIndex = 0
    gallery = []
    ln = Label()

    def __init__(self, **kwargs):
        super(Ticks, self).__init__(**kwargs)
        self.bind(pos = self.update_clock)
        self.bind(size = self.update_clock)

        self.ln.pos = self.pos
        self.ln.size = self.size
        self.ln.font_size = '32sp'
        self.ln.text_size = self.size
        self.ln.halign = 'right'
        self.ln.valign = 'bottom'
        self.ln.markup = True

        Clock.schedule_interval(self.update_clock, 1)


    def update_clock(self, *args):
        time = datetime.datetime.now()
        self.canvas.clear()

        self.remove_widget(self.ln)
        self.ln.pos = self.pos
        self.ln.size = self.size
        self.ln.text = '[color=0000f0] ' + APP_NAME + ' [/color]'
        self.ln.text_size = self.size
        self.add_widget(self.ln)

        with self.canvas:
            Color(.1, .1, .6, .15)
            Ellipse(pos={self.y + 19,self.width / 4}, size={self.width / 2, self.height - 38})

            Color(0.6, 0.6, 0.9)
            Line(points = [self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.second),
                self.center_y+0.7*self.r*cos(pi/30*time.second)], width=1, cap="round")
            Color(0.5, 0.5, 0.8)
            Line(points = [self.center_x, self.center_y, self.center_x+0.6*self.r*sin(pi/30*time.minute),
                self.center_y+0.6*self.r*cos(pi/30*time.minute)], width=2, cap="round")
            Color(0.4, 0.4, 0.7)
            th = time.hour*60 + time.minute
            Line(points = [self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th),
            self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")


# ##############################################################################

class MyAccountCallback(pj.AccountCallback):
    "Callback to receive events from account"
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    # Notification on incoming call
    def on_incoming_call(self, call):
        global current_call, mainLayout
        if current_call:
            call.answer(486, "Busy")
            return

        print "Incoming call from ", call.info().remote_uri
	mainLayout.findTargetWindow(call.info().remote_uri)

        current_call = call

        call_cb = MyCallCallback(current_call)
        current_call.set_callback(call_cb)

        current_call.answer(180)


def log_cb(level, str, len):
    "pjSip logging callback"
    print str,


class MyCallCallback(pj.CallCallback):
    "Callback to receive events from Call"
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    def on_state(self):
	"Notification when call state has changed"
        global current_call, ring_event, transparency_value
        global main_state, mainLayout, docall_button_global
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text, self.call.info().state,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        main_state = self.call.info().state
        transparency_value = 0

        if main_state == pj.CallState.DISCONNECTED:
            current_call = None
	    mainLayout.setButtons(False)
#            print 'Current call is', current_call

        if main_state == pj.CallState.EARLY:
            ring_event = Clock.schedule_interval(playWAV, 3.5)
            playWAV(3.5)
        else:
	    Clock.unschedule(ring_event)
	    ring_event = None
            stopWAV()

        if main_state == pj.CallState.INCOMING:
		mainLayout.findTargetWindow(self.call.info().remote_uri)

        if main_state == pj.CallState.INCOMING or main_state == pj.CallState.EARLY:
            if main_state is not pj.CallState.CALLING:
		docall_button_global.color = COLOR_ANSWER_CALL
		docall_button_global.text = BUTTON_CALL_ANSWER

        if main_state == pj.CallState.DISCONNECTED:
            docall_button_global.color = COLOR_NOMORE_CALL
            docall_button_global.text = BUTTON_DO_CALL
	    mainLayout.startScreenTiming()

        if main_state == pj.CallState.CONFIRMED:
            docall_button_global.color = COLOR_HANGUP_CALL
            docall_button_global.text = BUTTON_CALL_HANGUP

        if main_state == pj.CallState.CALLING:
	    current_call = self.call
            docall_button_global.color = COLOR_HANGUP_CALL
            docall_button_global.text = BUTTON_CALL_HANGUP
	    mainLayout.findTargetWindow('')


    def on_media_state(self):
	"Notification when call's media state has changed"
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
    def __init__(self,winpos,servaddr,streamaddr,relaycmd):
	"display area init"
	self.screenIndex = len(procs)
	self.winPosition = winpos.split(',')
	self.winPosition = [int(i) for i in self.winPosition]
	self.serverAddr = str(servaddr)
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

	self.color = None
	self.frame = None
	self.actScreen = mainLayout.ids.camera

	self.printInfo()
	self.setActive(False)


    def testTouchArea(self, x, y):
	"test if touch is in display area"
	y = 480 - y                        # touch position is from bottom to up
	retx = False
	rety = False
	if self.winPosition[0] < x and self.winPosition[2] > x : retx = True
	if self.winPosition[1] < y and self.winPosition[3] > y : rety = True
	return retx and rety


    def initPlayer(self):
	"start video player"
	print whoami()
	return subprocess.Popen(['omxplayer', '--live', '--no-osd',\
	    '--dbus_name',DBUS_PLAYERNAME + str(self.screenIndex),\
	    '--layer', '1', '--no-keys', '--win', ','.join(self.playerPosition), self.streamUrl],\
	    stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE) #, close_fds = True)


    def hidePlayer(self):
	"hide video player area"
	print whoami()
	if self.color is not None: self.actScreen.canvas.remove(self.color)
	if self.frame is not None: self.actScreen.canvas.remove(self.frame)

	self.color = None
	self.frame = None


    def setActive(self, active=True):
	"add or remove active flag"
	print whoami(), self.screenIndex, active
	self.hidePlayer()

	if active:
	    self.color = ACTIVE_DISPLAY_BACKGROUND
	else:
	    self.color = INACTIVE_DISPLAY_BACKGROUND

	w = self.winPosition[2] - self.winPosition[0] # width
	h = self.winPosition[3] - self.winPosition[1] # height
	ltx = self.winPosition[0]
	lty = 480 - self.winPosition[1] - h           # touch position is from bottom to up

	self.frame = Rectangle(pos=(ltx, lty), size=(w, h))
	self.actScreen.canvas.add(self.color)
	self.actScreen.canvas.add(self.frame)


    def printInfo(self):
	"print class info"
	print self.screenIndex,'area:',self.winPosition, 'IPaddr:', self.serverAddr, 'stream:', self.streamUrl


# ##############################################################################

class Indoor(FloatLayout):
    def __init__(self, **kwargs):
	"app init"
        global BUTTON_DO_CALL, BUTTON_CALL_ANSWER, BUTTON_CALL_HANGUP
        global BUTTON_DOOR_1, BUTTON_DOOR_2, APP_NAME, SCREEN_SAVER, BACK_LIGHT, BRIGHTNESS, WATCHES
        global main_state, docall_button_global, mainLayout, scrmngr, config

        super(Indoor, self).__init__(**kwargs)

	mainLayout = self

	self.displays = []

        main_state = 0
        self.info_state = 0
        self.myprocess = None

	self.scrmngr = self.ids._screen_manager
	scrmngr = self.scrmngr

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
	    APP_NAME = config.get('about', 'app_name')
        except:
            self.dbg('ERROR 3: read config file!')

        try:
	    value = config.get('command', 'watches')
	    if value in 'analog': WATCHES = value
	    else: WATCHES = 'digital'
            self.dbg(WATCHES)
        except:
            self.dbg('ERROR 7: read config file!')

        try:
	    screen_saver = int(config.get('command', 'screen_saver'))
	    if screen_saver > 0 and screen_saver < 120: SCREEN_SAVER = screen_saver * 60
            self.dbg(SCREEN_SAVER)
        except:
            self.dbg('ERROR 6: read config file!')

        try:
	    BACK_LIGHT = config.getboolean('command', 'back_light')
        except:
            self.dbg('ERROR 4: read config file!')
	    BACK_LIGHT = True

        try:
	    br = int(config.get('command', 'brightness'))
	    if br > 0 and br < 256: BRIGHTNESS = int(br * 2.55)
        except:
            self.dbg('ERROR 5: read config file!')
	    BRIGHTNESS = 255

	send_command(BRIGHTNESS_SCRIPT + ' ' + str(BRIGHTNESS))

        try:
            BUTTON_DO_CALL = config.get('gui', 'btn_docall')
            BUTTON_CALL_ANSWER = config.get('gui', 'btn_call_answer')
            BUTTON_CALL_HANGUP = config.get('gui', 'btn_call_hangup')
            BUTTON_DOOR_1 = config.get('gui', 'btn_door_1')
            BUTTON_DOOR_2 = config.get('gui', 'btn_door_2')
        except:
            self.dbg('ERROR: read config file!')

        self.infinite_event = Clock.schedule_interval(self.infinite_loop, 6.9)
        Clock.schedule_interval(self.info_state_loop, 10.)
	self.screenTimerEvent = None

        self.init_myphone()

	self.init_screen(config)

        self.ids.btnDoor1.text = BUTTON_DOOR_1
        self.ids.btnDoor1.color = COLOR_BUTTON_BASIC
        self.ids.btnDoor2.text = BUTTON_DOOR_2
        self.ids.btnDoor2.color = COLOR_BUTTON_BASIC
        docall_button_global = self.ids.btnDoCall
        docall_button_global.text = BUTTON_DO_CALL
        docall_button_global.color = COLOR_BUTTON_BASIC


    def init_screen(self, cfg):
	"define app screen"
	self.dbg(whoami())

	scr_mode = cfg.get('gui', 'screen_mode')
	if scr_mode == None or scr_mode == '': scr_mode = 0

	self.scrmngr.current = WAIT_SCR

	if scr_mode == 1:
	    wins = ['0,0,800,432']
	elif scr_mode == 2:
	    wins = ['0,0,800,216', '0,216,800,432']
	elif scr_mode == 3:
	    wins = ['0,0,400,432', '400,0,800,432']
	else:
	    wins = ['0,0,400,216', '400,0,800,216', '0,216,400,432', '400,216,800,432']

	self.dbg('scr_mode:' + str( scr_mode ) + ' wrange:' + str(len(wins)))

	for i in range(0,len(wins)):
	    win = wins[i]
	    serv = cfg.get('common', 'server_ip_address_'+str(i + 1))
	    vid = cfg.get('common', 'server_stream_'+str(i + 1))
	    relay = 'http://' + serv + '/cgi-bin/remctrl.sh?id='
#	    try:
#		relay = cfg.get('common', 'server_relay_'+str(i + 1))
#	    except:
#		relay = 'http://' + serv + '/cgi-bin/remctrl.sh?id='
#
#	    self.dbg(whoami() + ' relay: ' + str(relay))

	    displ = BasicDisplay(win,serv,vid,relay)
	    self.displays.append(displ)

	if scr_mode != 1: self.displays[0].setActive()

	self.scrmngr.current = CAMERA_SCR
	self.setButtons(False)


    def init_myphone(self):
	"sip phone init"
        global acc

	self.dbg(whoami())

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
	"state loop"
        global current_call, docall_button_global, BUTTON_DO_CALL, COLOR_BUTTON_BASIC

        if current_call is not None: self.info_state = 0

        if self.info_state == 0:
            self.info_state = 1
	    send_command(UNBLANK_SCRIPT)
        elif self.info_state == 1:
            self.info_state = 2
#	    get_info(DBUSCONTROL_SCRIPT + ' ' + DBUS_PLAYERNAME + '0 status')
        elif self.info_state == 2:
            self.info_state = 0
            if current_call is None:
		docall_button_global.text = BUTTON_DO_CALL
		docall_button_global.color = COLOR_BUTTON_BASIC


    def infinite_loop(self, dt):
	"main neverendig loop"
        global procs

	if len(procs) == 0: return

	for idx, p in enumerate(procs):
	    if p.poll() is not None:
		self.dbg( "Process" + str(idx) + " (" + str(p.pid) + ") is dead\nscreen:" + self.scrmngr.current+'/'+CAMERA_SCR )
		try:
		    p.kill()
		except:
		    pass
		procs[idx] = self.displays[idx].initPlayer()

		if self.scrmngr.current not in CAMERA_SCR:
		    self.hidePlayers()


    def startScreenTiming(self):
	"start screen timer"
	global SCREEN_SAVER

        self.dbg('ScrnEnter:'+str(SCREEN_SAVER))
	if self.screenTimerEvent is not None: Clock.unschedule(self.screenTimerEvent)
        if SCREEN_SAVER > 0: self.screenTimerEvent = Clock.schedule_once(self.return2clock, SCREEN_SAVER)

	send_command(UNBLANK_SCRIPT)
	send_command(BACK_LIGHT_SCRIPT + ' 0')


    def return2clock(self, *args):
	"swat screen to CLOCK"
	global current_call, BACK_LIGHT, WATCHES

#        self.dbg('2 clock')
        Clock.unschedule(self.screenTimerEvent)
	self.screenTimerEvent = None

	if current_call is None and self.scrmngr.current == CAMERA_SCR:
	    if WATCHES in 'analog': self.scrmngr.current = WATCH_SCR
	    else: self.scrmngr.current = DIGITAL_SCR
	    if BACK_LIGHT is False: send_command(BACK_LIGHT_SCRIPT + ' 1')


    def finishScreenTiming(self):
	"finist screen timer"
        self.dbg('ScrnLeave')
        Clock.unschedule(self.screenTimerEvent)
	self.screenTimerEvent = None


    def callback_btn_docall(self):
	"make outgoing call"
        global current_call, active_display_index, docall_button_global, BUTTON_DO_CALL
	global ring_event

	self.dbg(whoami())

	if len(procs) == 0: return

	target = self.displays[active_display_index].serverAddr
#        self.dbg(BUTTON_DO_CALL + ' --> ' + 'sip:' + target + ':5060')

        if current_call is not None:
#	    txt = BUTTON_DO_CALL
            if main_state == pj.CallState.EARLY:
		Clock.unschedule(ring_event)
		ring_event = None
                stopWAV()
                current_call.answer(200)
		self.setButtons(True)
            else:
                current_call.hangup()
		self.setButtons(False)
	else:
	    txt = '--> ' + str(active_display_index + 1)
	    if make_call('sip:' + target + ':5060') is None: txt = txt + ' ERROR'

	    docall_button_global.text = txt
	    self.setButtons(True)


    def gotResponse(self, req, results):
	"relay result"
        print 'Relay: ', req, results
        pass


    def setRelayRQ(self, relay):
	"send relay request"
        global active_display_index

	if len(procs) == 0: return

#	target = self.displays[active_display_index].serverAddr
#
#        req = UrlRequest('http://' + target + '/cgi-bin/remctrl.sh?id=' + relay,\
#                on_success = self.gotResponse, timeout = 5)
        req = UrlRequest(self.displays[active_display_index].relayCmd + relay,\
                on_success = self.gotResponse, timeout = 5)


    def callback_btn_door1(self):
	"door 1 button"
        self.dbg(BUTTON_DOOR_1)
        self.setRelayRQ('relay1')


    def callback_btn_door2(self):
	"door 2 button"
        self.dbg(BUTTON_DOOR_2)
        self.setRelayRQ('relay2')


    def callback_set_options(self):
	"start settings"
	global procs

        self.dbg(self.ids.btnSetOptions.text)
	print whoami()

	if len(procs) == 0: return

        self.scrmngr.current = SETTINGS_SCR

	App.get_running_app().open_settings()


    def callback_set_voice(self, value):
	"volume buttons"
	global AUDIO_VOLUME, current_call

	self.dbg(whoami() + ': ' + str(value) + self.ids.btnScreenClock.text)

	if current_call is None:
#	if self.ids.btnScreenClock.text == 'C':
	    if value == 1:
		self.callback_set_options()
	    else:
		Clock.schedule_once(self.return2clock, .2)
#		get_info(DBUSCONTROL_SCRIPT + ' ' + DBUS_PLAYERNAME + str(active_display_index) + ' status')
	else :
	    vol = AUDIO_VOLUME + int(value) * 20
	    if vol > 80: vol = 100
	    elif vol > 60: vol = 80
	    elif vol > 40: vol = 60
	    elif vol > 20: vol = 40
	    else: vol = 20
	    AUDIO_VOLUME = vol

	    self.ids.btnScreenClock.disabled = vol < 40
	    self.ids.btnSetOptions.disabled = vol > 80

            self.dbg('Voice: ' + str(value) + ' >> '+ str(AUDIO_VOLUME))
	    send_command(SETVOLUME_SCRIPT + ' ' + str(AUDIO_VOLUME))


    def on_touch_up(self, touch):
	"process touch up event"
	global active_display_index

	self.dbg(whoami())
#        print 'touchUp: ', touch.x, touch.y, touch.is_double_tap

#	if not self.collide_point(*touch.pos): return

	if len(procs) == 0: return

	if touch.is_double_tap:
	    print 'double touch: ', touch.x, touch.y, touch.is_double_tap
            send_dbus(DBUS_PLAYERNAME + str(active_display_index), TRANSPARENCY_VIDEO_CMD + [str(0)])
	    self.displays[active_display_index].hidePlayer()
	    send_command("ps aux | grep omxplayer"+str(active_display_index)+" | grep -v grep | awk '{print $2}' | xargs kill -9")
	    procs[active_display_index].kill()
	    send_command(CMD_KILL + str(procs[active_display_index].pid))
	    return

	self.startScreenTiming()

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
	self.dbg(whoami())

        for idx, proc in enumerate(procs):
            send_dbus(DBUS_PLAYERNAME + str(idx), TRANSPARENCY_VIDEO_CMD + [str(255)])
#	    self.displays[idx].setActive(False)

	self.displays[active_display_index].setActive()


    def hidePlayers(self):
	"d-bus command to hide video"
	self.dbg(whoami())

        for idx, proc in enumerate(procs):
	    self.displays[idx].hidePlayer()
            send_dbus(DBUS_PLAYERNAME + str(idx), TRANSPARENCY_VIDEO_CMD + [str(0)])

    def setButtons(self, visible):
	"set buttons (ScrSaver, Options, Voice+-) to accurate state"
	global AUDIO_VOLUME

	self.dbg(whoami())

	if visible:
	    self.ids.btnScreenClock.text = '-'
	    self.ids.btnSetOptions.text = '+'
	    self.ids.btnScreenClock.disabled = AUDIO_VOLUME < 40
	    self.ids.btnSetOptions.disabled = AUDIO_VOLUME > 80
	else:
	    self.ids.btnScreenClock.text = 'C'
	    self.ids.btnSetOptions.text = 'S'
	    self.ids.btnScreenClock.disabled = False
	    self.ids.btnSetOptions.disabled = False


    def findTargetWindow(self, addr):
	"find target window according to calling address"
	global active_display_index
        self.dbg('find target window for:' + addr)

	self.scrmngr.current = CAMERA_SCR
	self.finishScreenTiming()

	if addr != '':
	    active_display_index = 0
	    for idx, d in enumerate(self.displays):
		d.setActive(False)
		if d.serverAddr in addr:
		    active_display_index = idx

	    self.dbg('target window:' + str(active_display_index))
	    self.displays[active_display_index].setActive()


    def dbg(self, info):
	"debug outputs"
        print info


# ###############################################################

class IndoorApp(App):
    def build(self):
        self.dbg('Hello Indoor 2.0')
#        Config.set('kivy', 'keyboard_mode','')
	lbl = 'Configuration keyboard_mode is %r, keyboard_layout is %r' % (
	    Config.get('kivy', 'keyboard_mode'),
	    Config.get('kivy', 'keyboard_layout'))
        self.dbg(lbl)

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
##        lib.destroy()


    def dbg(self, info):
        print info


    def build_config(self, config):
	"build config"
        self.dbg(whoami())

	config.setdefaults('command', {
	    'screen_saver': 1,
	    'brightness': 100,
	    'watches': 'analog',
	    'back_light': True })
	config.setdefaults('sip', {
	    'sip_username': '',
	    'sip_p4ssw0rd': '',
	    'sip_server_addr': '',
	    'sip_ident_addr': '',
	    'sip_ident_info': '',
	    'sip_stun_server': '' })
	config.setdefaults('devices', {
	    'sound_device_in': '',
	    'sound_device_out': '',
	    'volume': 100 })
	config.setdefaults('gui', {
	    'screen_mode': 0,
	    'btn_call_none': '',
	    'btn_docall': 'Do Call',
	    'btn_call_answer': 'Answer Call',
	    'btn_call_hangup': 'HangUp Call',
	    'btn_door_1': 'Open Door 1',
	    'btn_door_2': 'Open Door 2' })
	config.setdefaults('common', {
	    'server_ip_address_1': '192.168.1.250',
	    'server_stream_1': 'http://192.168.1.250:80/video.mjpg',
	    'server_ip_address_2': '192.168.1.251:8080',
	    'server_stream_2': 'http://192.168.1.241:8080/stream/video.mjpeg',
	    'server_ip_address_3': '192.168.1.251:8080',
	    'server_stream_3': 'http://192.168.1.241:8080/stream/video.mjpeg',
	    'server_ip_address_4': '192.168.1.250' })

	s = get_info(SYSTEMINFO_SCRIPT).split()
	print whoami(), s
	config.setdefaults('about', {
	    'app_name': 'Indoor 2.0',
	    'app_ver': '2.0.0.0',
	    'uptime': '---',
	    'serial': s[1] })

	config.setdefaults('system', {
	    'inet': s[2],
	    'ipaddress': s[3],
	    'gateway': s[6],
	    'netmask': s[4],
	    'broadcast': s[5],
	    'network': s[7],
	    'dns': s[8] })


    def get_uptime_value(self):
	"retrieve system uptime"
	with open('/proc/uptime', 'r') as f:
	    uptime_seconds = float(f.readline().split()[0])
	    uptime_string = str(timedelta(seconds = uptime_seconds))

	return uptime_string


    def get_volume_value(self):
	"retrieve current volume level"
	global AUDIO_VOLUME

	s = get_info(VOLUMEINFO_SCRIPT).split()
	vol = int(round(float(s[1]) / (int(s[3]) - int(s[2])) * 100.0))

	# available volume steps:
	if vol > 80: vol = 100
	elif vol > 60: vol = 80
	elif vol > 40: vol = 60
	elif vol > 20: vol = 40
	else: vol = 20
	AUDIO_VOLUME = vol
	print s, vol

	return vol


    def build_settings(self, settings):
	"display settings screen"
	global config

        self.dbg(whoami())

	if self.changeInet == False:
	    s = get_info(SYSTEMINFO_SCRIPT).split()
	    config.set('about', 'serial', s[1])
	    config.set('system', 'inet', s[2])
	    config.set('system', 'ipaddress', s[3])
	    config.set('system', 'netmask', s[4])
	    config.set('system', 'broadcast', s[5])
	    config.set('system', 'gateway', s[6])
	    config.set('system', 'network', s[7])
	    config.set('system', 'dns', s[8])

	config.set('about', 'uptime', self.get_uptime_value())
	config.set('devices', 'volume', AUDIO_VOLUME)

	# enable|disable change parameters
	vDhcp = config.get('system', 'inet') in 'dhcp'
	sys = json.loads(settings_system)
	system = []
	for s in sys:
	    item = s
	    if s['type'] not in 'title' and s['key'] not in 'inet': item['disabled'] = vDhcp
	    system.append(item)
#	    print item
	system = json.dumps(system)

        settings.add_json_panel('Application',
                                config,
                                data=settings_app)
        settings.add_json_panel('GUI',
                                config,
                                data=settings_gui)
        settings.add_json_panel('Outdoor Devices',
                                config,
                                data=settings_outdoor)
        settings.add_json_panel('Audio Device',
                                config,
                                data=settings_audio)
        settings.add_json_panel('SIP',
                                config,
                                data=settings_sip)
        settings.add_json_panel('System',
                                config,
                                data=system)
        settings.add_json_panel('About',
                                config,
                                data=settings_about)


    def on_config_change(self, config, section, key, value):
	"config item changed"
	global SCREEN_SAVER, BACK_LIGHT, BRIGHTNESS, WATCHES, VOLUME

	token = (section, key)
        print whoami(),':', section, key, value

	if token == ('command', 'brightness'):
	    try:
		v = int(value)
		BRIGHTNESS = int(v * 2.55)
	    except:
		BRIGHTNESS = 255
	    send_command(BRIGHTNESS_SCRIPT + ' ' + str(BRIGHTNESS))
	elif token == ('command', 'screen_saver'):
	    try:
		v = int(value)
		SCREEN_SAVER = v * 60
	    except:
		SCREEN_SAVER = 0
	elif token == ('command', 'back_light'):
	    try:
		v = int(value)
		BACK_LIGHT = v > 0
	    except:
		BACK_LIGHT = False
	elif token == ('command', 'watches'):
	    if value in 'analog': WATCHES = value
	    else: WATCHES = 'digital'
	elif token == ('devices', 'volume'):
	    AUDIO_VOLUME = value
	    send_command(SETVOLUME_SCRIPT + ' ' + str(AUDIO_VOLUME))
	elif section in 'system' and (key in ['ipaddress', 'netmask', 'broadcast', 'gateway', 'network', 'dns']):
	    if config.get('system', 'inet') in 'dhcp':
		print 'disable changes', config.get(section, key),  self.config.get(section, key)
		config.set(section, key, self.config.get(section, key))
		config.write()
	    else:
		print 'enable changes', config.get('system', 'ipaddress'),  self.config.get('system', 'ipaddress')
		self.changeInet = True
	elif token == ('system', 'inet'):
	    self.changeInet = True
	    config.write()
	    self.destroy_settings()
	    self.open_settings()


    def close_settings(self, *args):
	"close button pressed"
	global scrmngr

        self.dbg(whoami())
        super(IndoorApp, self).close_settings()

	if self.changeInet:
	    # TODO: start script
	    send_command('pkill omxplayer')
	    send_command('pkill dbus-daemon')
	    send_command('pkill python')

	    App.get_running_app().stop()
	    return

	self.changeInet = False
	scrmngr.current = CAMERA_SCR


# ###############################################################
#
# Start
#
# ###############################################################

if __name__ == '__main__':
    IndoorApp().run()
