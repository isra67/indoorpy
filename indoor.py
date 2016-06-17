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

#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
#from kivy.uix.widget import Widget

import datetime
import logging
import os
import signal
import time

import linphone
#from pyomxplayer import OMXPlayer


# ###############################################################
#
# Declarations
#
# ###############################################################

CONFIG_FILE = 'indoorconfig.ini'

CMD_PKILL = '=pkill -9 omxplayer;pkill -9 omxplayer.bin'
CMD_PLAYVIDEO = '=/usr/bin/omxplayer --win "1 1 799 429" --no-osd --no-keys "http://192.168.1.253:8080/stream/video.h264" > /dev/null &'

BUTTON_CALL_NONE = '=No Call='
BUTTON_CALL_ANSWER = '=Answer Call='
BUTTON_CALL_HANGUP = '=HangUp Call='

BUTTON_DOOR_1 = '=Open Door 1='
BUTTON_DOOR_2 = '=Open Door 2='

COLOR_BUTTON_BASIC = 1,1,1,1
COLOR_ANSWER_CALL = 1,0,0,1
COLOR_HANGUP_CALL = 1,1,0,1
COLOR_NOMORE_CALL = COLOR_BUTTON_BASIC


# ###############################################################
#
# Classes
#
# ###############################################################

class Indoor(FloatLayout):

    def __init__(self, **kwargs):
        global CMD_PKILL
        global CMD_PLAYVIDEO
        global BUTTON_CALL_NONE
        global BUTTON_CALL_ANSWER
        global BUTTON_CALL_HANGUP
        global BUTTON_DOOR_1
        global BUTTON_DOOR_2

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
        except:
            self.dbg('ERROR: read config file!')

        os.system(CMD_PKILL)
##        os.system(CMD_PLAYVIDEO)

        self.state = linphone.CallState.Idle
        self.quit = False

        self.info_state = 0

##        self.init_myphone()
#            username='raspberry', password='pi',\
#            camera='V4L2: /dev/video0',\
#            snd_capture='ALSA: USB Device 0x46d:0x825')
        self.init_myphone(
            username='', password='',\
            camera='',\
            snd_capture='OSS: /dev/dsp1')

        Clock.schedule_interval(self.infinite_loop, .5)
        Clock.schedule_interval(self.info_state_loop, 10.)

        self.callbutton = self.ids.btnCall
        self.callbutton.text = BUTTON_CALL_NONE
        self.callbutton.color = COLOR_BUTTON_BASIC
        self.callbutton.size = 0,0
        self.callbutton.size_hint = None,None
        self.callbutton.pos = 100,100
        self.ids.btnDoor1.text = BUTTON_DOOR_1
        self.ids.btnDoor1.color = COLOR_BUTTON_BASIC
        self.ids.btnDoor2.text = BUTTON_DOOR_2
        self.ids.btnDoor2.color = COLOR_BUTTON_BASIC

    def init_myphone(self,username='',password='',camera='',snd_capture='',snd_playback=''):
        callbacks = {
            'call_state_changed': self.call_state_changed,
        }

        # Configure the linphone core
        logging.basicConfig(level=logging.INFO)
        signal.signal(signal.SIGINT, self.signal_handler)
        linphone.set_log_handler(self.log_handler)
        self.core = linphone.Core.new(callbacks, None, None)
        self.core.max_calls = 1
        self.core.echo_cancellation_enabled = False
        self.core.video_capture_enabled = False
        self.core.video_display_enabled = False
        self.core.stun_server = '' # 'stun.linphone.org'
        self.core.firewall_policy = linphone.FirewallPolicy.PolicyUseIce
        if len(camera):
            self.core.video_device = camera
        if len(snd_capture):
            self.core.capture_device = snd_capture
        if len(snd_playback):
            self.core.playback_device = snd_playback

        # Only enable PCMU and PCMA audio codecs
        for codec in self.core.audio_codecs:
            if codec.mime_type == "PCMA" or codec.mime_type == "PCMU":
                self.core.enable_payload_type(codec, True)
            else:
                self.core.enable_payload_type(codec, False)

        # Only enable VP8 video codec
        for codec in self.core.video_codecs:
          if codec.mime_type == "VP8":
            self.core.enable_payload_type(codec, True)
          else:
            self.core.enable_payload_type(codec, False)

        if username != '' and password != '':
            self.configure_sip_account(username, password)

    def signal_handler(self, signal, frame):
        self.core.terminate_all_calls()
        self.quit = True

    def log_handler(self, level, msg):
        if level == 'warning' or level == 'error':
            method = getattr(logging, level)
            method(msg)

    def call_state_changed(self, core, call, state, message):
        self.corecall = core
        self.call = call
        self.state = state
        self.message = message
        self.params = core.create_call_params(call)

        if state == linphone.CallState.IncomingReceived:
            self.callbutton.color = COLOR_ANSWER_CALL
            self.callbutton.text = BUTTON_CALL_ANSWER
            self.callbutton.size_hint = 2,1
            self.callbutton.size = 0,0
            self.callbutton.pos = 0,0

        if state == linphone.CallState.End or \
           state == linphone.CallState.Released or \
           state == linphone.CallState.Error:
            self.callbutton.color = COLOR_NOMORE_CALL
            self.callbutton.text = BUTTON_CALL_NONE
            self.callbutton.size_hint = None,None
            self.callbutton.size = 0,0
            self.callbutton.pos = 100,100

        if state == linphone.CallState.Connected or \
           state == linphone.CallState.StreamsRunning:
            self.callbutton.color = COLOR_HANGUP_CALL
            self.callbutton.text = BUTTON_CALL_HANGUP
            self.callbutton.size_hint = 2,1
            self.callbutton.size = 0,0
            self.callbutton.pos = 0,0

    def configure_sip_account(self, username, password):
        # Configure the SIP account
        proxy_cfg = self.core.create_proxy_config()
        proxy_cfg.identity_address = self.core.create_address('sip:{username}@sip.linphone.org'.format(username=username))
        proxy_cfg.server_addr = 'sip:sip.linphone.org;transport=tls'
        proxy_cfg.register_enabled = True
        self.core.add_proxy_config(proxy_cfg)
        auth_info = self.core.create_auth_info(username,None,password,None,None,'sip.linphone.org')
        self.core.add_auth_info(auth_info)

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
        if not self.quit:
            self.core.iterate()

#    def on_stop(self):
#        self.quit = True
#        self.dbg('Bye')
#        os.system(CMD_PKILL)

    def callback_btn_call(self):
        self.dbg(self.callbutton.text)
        if self.state > linphone.CallState.Idle:
            if self.state == linphone.CallState.IncomingReceived:
                self.corecall.accept_call_with_params(self.call, self.params)
            else:
                self.core.terminate_all_calls()
                self.state = linphone.CallState.Idle

    def callback_btn_door1(self):
        self.dbg(BUTTON_DOOR_1)

    def callback_btn_door2(self):
        self.dbg(BUTTON_DOOR_2)

    def callback_restart_player(self):
        self.dbg(self.ids.rstplayerbutton.text)
        os.system(CMD_PKILL)
##        os.system(CMD_PLAYVIDEO)

    def callback_set_options(self):
        self.dbg(self.ids.settingsbutton.text)

    def dbg(self, info):
        print info


# ###############################################################

class IndoorApp(App):
    def build(self):
        self.dbg('Hello')
        return Indoor()

    def dbg(self, info):
        print info


# ###############################################################
#
# Start
#
# ###############################################################

if __name__ == '__main__':
    IndoorApp().run()
