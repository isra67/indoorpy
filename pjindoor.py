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
from kivy.network.urlrequest import UrlRequest
from kivy.uix.floatlayout import FloatLayout

import datetime
import logging
import os
import signal
import sys
import time

import pjsua as pj

# ###############################################################
#
# Declarations
#
# ###############################################################

CONFIG_FILE = 'indoorconfig.ini'

BUTTON_CALL_NONE = '=No Call='
BUTTON_CALL_ANSWER = '=Answer Call='
BUTTON_CALL_HANGUP = '=HangUp Call='

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
call_button_global = None

current_play = 0

APLAYER = 'aplay'
APARAMS = '-q -N -f cd -D plughw:1,0'
RING_WAV = APLAYER + ' ' + APARAMS + ' ' +'share/sounds/linphone/rings/oldphone.wav &'


# ###############################################################
#
# Functions
#
# ###############################################################

# Logging callback
def log_cb(level, str, len):
    print str,


def playWAV(dt):
    global current_play, RING_WAV
    current_play = 1
    os.system(RING_WAV)


def stopWAV():
    global current_play
    current_play = 0
    Clock.unschedule(playWAV)
    os.system('pkill -9 ' + APLAYER)


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
        global current_call, main_state, call_button_global
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code,
        print "(" + self.call.info().last_reason + ")"

        main_state = self.call.info().state

        if self.call.info().state == pj.CallState.DISCONNECTED:
            current_call = None
#            print 'Current call is', current_call

        if main_state == pj.CallState.EARLY:
            Clock.schedule_interval(playWAV, 3.)
        else:
            stopWAV()

        if main_state == pj.CallState.INCOMING or\
           main_state == pj.CallState.EARLY:
            call_button_global.color = COLOR_ANSWER_CALL
            call_button_global.text = BUTTON_CALL_ANSWER
            call_button_global.size_hint = 2,1
            call_button_global.size = 0,0
            call_button_global.pos = 0,0

        if main_state == pj.CallState.DISCONNECTED:
            call_button_global.color = COLOR_NOMORE_CALL
            call_button_global.text = BUTTON_CALL_NONE
            call_button_global.size_hint = None,None
            call_button_global.size = 0,0
            call_button_global.pos = 100,100

        if main_state == pj.CallState.CONFIRMED:
            call_button_global.color = COLOR_HANGUP_CALL
            call_button_global.text = BUTTON_CALL_HANGUP
            call_button_global.size_hint = 2,1
            call_button_global.size = 0,0
            call_button_global.pos = 0,0


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


# Function to make call
#def make_call(uri):
#    global acc
#    try:
#        print "Making call to", uri
#        return acc.make_call(uri, cb=MyCallCallback())
#    except pj.Error, e:
#        print "Exception: " + str(e)
#        return None


class Indoor(FloatLayout):
    def __init__(self, **kwargs):
        global CMD_PKILL
        global CMD_PLAYVIDEO
        global BUTTON_CALL_NONE
        global BUTTON_CALL_ANSWER
        global BUTTON_CALL_HANGUP
        global BUTTON_DOOR_1
        global BUTTON_DOOR_2
        global main_state, call_button_global

        super(Indoor, self).__init__(**kwargs)

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
            CMD_PKILL = config.get('command', 'kill_cmd')
            CMD_PLAYVIDEO = config.get('command', 'play_cmd')
            BUTTON_CALL_NONE = config.get('gui', 'btn_call_none')
            BUTTON_CALL_ANSWER = config.get('gui', 'btn_call_answer')
            BUTTON_CALL_HANGUP = config.get('gui', 'btn_call_hangup')
            BUTTON_DOOR_1 = config.get('gui', 'btn_door_1')
            BUTTON_DOOR_2 = config.get('gui', 'btn_door_2')
            SERVER_IP_ADDR = config.get('common', 'server_ip_address')
        except:
            self.dbg('ERROR: read config file!')

        os.system(CMD_PKILL)

        main_state = 0

        self.info_state = 0

        self.init_myphone()

        Clock.schedule_interval(self.infinite_loop, .5)
        Clock.schedule_interval(self.info_state_loop, 10.)

        self.callbutton = self.ids.btnCall
        call_button_global = self.callbutton
        self.callbutton.text = BUTTON_CALL_NONE
        self.callbutton.color = COLOR_BUTTON_BASIC
        self.callbutton.size = 0,0
        self.callbutton.size_hint = None,None
        self.callbutton.pos = 100,100
        self.ids.btnDoor1.text = BUTTON_DOOR_1
        self.ids.btnDoor1.color = COLOR_BUTTON_BASIC
        self.ids.btnDoor2.text = BUTTON_DOOR_2
        self.ids.btnDoor2.color = COLOR_BUTTON_BASIC

    def init_myphone(self):
        global acc

        # Create library instance
        lib = pj.Lib()

        try:
            # Init library with default config and some customized
            # logging config
            lib.init(log_cfg = pj.LogConfig(level=LOG_LEVEL, callback=log_cb))

            # Create UDP transport which listens to any available port
            transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5060))

            print "\nListening on", transport.info().host, "port", transport.info().port, "\n"

            # Start the library
            lib.start()

            # Create local account
            acc = lib.create_account_for_transport(transport, cb=MyAccountCallback())

            my_sip_uri = "sip:" + transport.info().host + ":" + str(transport.info().port)

        except pj.Error, e:
            print "Exception: " + str(e)
            lib.destroy()
            lib = None

    def info_state_loop(self, dt):
        if self.info_state == 0:
            self.info_state = 1
            self.ids.btnDoor1.text = BUTTON_DOOR_1
            self.ids.btnDoor2.text = BUTTON_DOOR_2
        elif self.info_state == 1:
            self.info_state = 2
            self.ids.btnDoor2.text = datetime.datetime.now().strftime("%H:%M")
        elif self.info_state == 2:
            self.info_state = 3
            self.ids.btnDoor1.text = '(c) Inoteska'
            self.ids.btnDoor2.text = BUTTON_DOOR_2
        elif self.info_state == 3:
            self.info_state = 0
            self.ids.btnDoor2.text = datetime.datetime.now().strftime("%d.%m.%Y")

    def infinite_loop(self, dt):
        pass

    def callback_btn_call(self):
        global current_call, main_state

        self.dbg(self.callbutton.text)
        if current_call:
            if main_state == pj.CallState.EARLY:
                stopWAV()
                current_call.answer(200)
            else:
                current_call.hangup()

    def gotResponse(self, req, results):
#        print 'Relay: ', req, results
        pass

    def setRelayRQ(self, relay):
        req = UrlRequest('http://' + SERVER_IP_ADDR + '/cgi-bin/remctrl.sh?id=' + relay,\
                on_success = self.gotResponse, timeout = 5)

    def callback_btn_door1(self):
        self.dbg(BUTTON_DOOR_1)
        self.setRelayRQ('relay1')

    def callback_btn_door2(self):
        self.dbg(BUTTON_DOOR_2)
        self.setRelayRQ('relay2')

    def callback_restart_player(self):
        self.dbg(self.ids.rstplayerbutton.text)
        os.system(CMD_PKILL)

    def callback_set_options(self):
        self.dbg(self.ids.settingsbutton.text)

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
