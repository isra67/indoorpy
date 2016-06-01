# ###############################################################
#
# Imports
#
# ###############################################################

import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout

import logging
import os
import signal
import time

import linphone


# ###############################################################
#
# Declarations
#
# ###############################################################

PKILL1 = 'pkill -9 omxplayer'
PKILL2 = 'pkill -9 omxplayer.bin'
PLAYVI = '/usr/bin/omxplayer --win "100 10 700 410" --no-osd --no-keys "http://192.168.1.253:8080/stream/video.h264" > /dev/null &'


# ###############################################################
#
# Classes
#
# ###############################################################

class MyPhone:
    def __init__(self, username='', password='', whitelist=[], camera='', snd_capture='', snd_playback=''):
        self.quit = False
        self.whitelist = whitelist
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
        self.core.video_capture_enabled = False #True
        self.core.video_display_enabled = False
        #self.core.stun_server = 'stun.linphone.org'
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

        self.configure_sip_account(username, password)

    def signal_handler(self, signal, frame):
        self.core.terminate_all_calls()
        self.quit = True

    def log_handler(self, level, msg):
        method = getattr(logging, level)
        method(msg)

    def call_state_changed(self, core, call, state, message):
        if state == linphone.CallState.IncomingReceived:
            params = core.create_call_params(call)
            core.accept_call_with_params(call, params)

#            if call.remote_address.as_string_uri_only() in self.whitelist:
#                params = core.create_call_params(call)
#                core.accept_call_with_params(call, params)
#            else:
#                core.decline_call(call, linphone.Reason.Declined)
#                chat_room = core.get_chat_room_from_uri(self.whitelist[0])
#                msg = chat_room.create_message(call.remote_address_as_string + ' tried to call')
#                chat_room.send_chat_message(msg)

    def configure_sip_account(self, username, password):
        # Configure the SIP account
        proxy_cfg = self.core.create_proxy_config()
        proxy_cfg.identity_address = self.core.create_address('sip:{username}@sip.linphone.org'.format(username=username))
        proxy_cfg.server_addr = 'sip:sip.linphone.org;transport=tls'
        proxy_cfg.register_enabled = True
        self.core.add_proxy_config(proxy_cfg)
        auth_info = self.core.create_auth_info(username, None, password, None, None, 'sip.linphone.org')
        self.core.add_auth_info(auth_info)

    def run(self):
        print('RUN PHONE')
        while not self.quit:
            self.core.iterate()
            time.sleep(0.05)


# ###############################################################

class Indoor(BoxLayout):
    pass


# ###############################################################

class IndoorApp(App):
    def build(self):
        self.dbg('Hello')
        os.system(PKILL1)
        os.system(PKILL2)
        os.system(PLAYVI)

        self.init_myphone()
#            username='raspberry', password='pi',\
#            whitelist=[],\
#            camera='V4L2: /dev/video0',\
#            snd_capture='ALSA: USB Device 0x46d:0x825')
        Clock.schedule_interval(self.infinite_loop, .5)

#        self.callbutton = self.ids.callbutton
#        self.callbutton.color = [0,1,0,1]

        return Indoor()

    def init_myphone(self, username='', password='', whitelist=[], camera='', snd_capture='', snd_playback=''):
        self.quit = False
        self.whitelist = whitelist
        callbacks = {
            'call_state_changed': self.call_state_changed,
        }

        # Configure the linphone core
#        logging.basicConfig(level=logging.INFO)
        logging.basicConfig(level=logging.WARNING)
        signal.signal(signal.SIGINT, self.signal_handler)
        linphone.set_log_handler(self.log_handler)
        self.core = linphone.Core.new(callbacks, None, None)
        self.core.max_calls = 1
        self.core.echo_cancellation_enabled = False
        self.core.video_capture_enabled = False #True
        self.core.video_display_enabled = False
        #self.core.stun_server = 'stun.linphone.org'
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

#        self.configure_sip_account(username, password)

    def signal_handler(self, signal, frame):
        self.core.terminate_all_calls()
        self.quit = True

    def log_handler(self, level, msg):
        method = getattr(logging, level)
        method(msg)

    def call_state_changed(self, core, call, state, message):
        print('**** STATE: ',state,' ****')
        if state == linphone.CallState.IncomingReceived:
            params = core.create_call_params(call)
            core.accept_call_with_params(call, params)
#            self.btnCall.color = Color(.1, .1, .6, .15)
#            self.callbutton.color = [1,0,0,1]

#            if call.remote_address.as_string_uri_only() in self.whitelist:
#                params = core.create_call_params(call)
#                core.accept_call_with_params(call, params)
#            else:
#                core.decline_call(call, linphone.Reason.Declined)
#                chat_room = core.get_chat_room_from_uri(self.whitelist[0])
#                msg = chat_room.create_message(call.remote_address_as_string + ' tried to call')
#                chat_room.send_chat_message(msg)

    def configure_sip_account(self, username, password):
        # Configure the SIP account
        proxy_cfg = self.core.create_proxy_config()
        proxy_cfg.identity_address = self.core.create_address('sip:{username}@sip.linphone.org'.format(username=username))
        proxy_cfg.server_addr = 'sip:sip.linphone.org;transport=tls'
        proxy_cfg.register_enabled = True
        self.core.add_proxy_config(proxy_cfg)
        auth_info = self.core.create_auth_info(username, None, password, None, None, 'sip.linphone.org')
        self.core.add_auth_info(auth_info)

    def infinite_loop(self, dt):
        if not self.quit:
            self.core.iterate()
#        while not self.quit:
#            self.core.iterate()
#            time.sleep(0.05)

    def on_stop(self):
        self.quit = True
        self.dbg('Bye')
        os.system(PKILL1)
        os.system(PKILL2)

    def dbg(self, info):
        print(info)


# ###############################################################
#
# Start
#
# ###############################################################

if __name__ == '__main__':
    IndoorApp().run()
