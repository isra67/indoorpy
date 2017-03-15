#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################


import kivy
kivy.require('1.9.0')


#from kivy.app import App
#from kivy.adapters.listadapter import ListAdapter
#from kivy.clock import Clock
#from kivy.config import Config, ConfigParser
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger, LoggerHistory
#from kivy.network.urlrequest import UrlRequest
#from kivy.properties import ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemLabel
from kivy.uix.popup import Popup
#from kivy.uix.settings import Settings, SettingsWithSidebar
#from kivy.uix.scatter import Scatter
#from kivy.uix.screenmanager import ScreenManager, Screen
#from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

#import inspect
#import os
#import signal
#import socket
#import subprocess
#import sys
#import time

#from kivy.logger import Logger

from constants import *


# ###############################################################
#
# Classes
#
# ###############################################################

class MyListViewLabel(Label):
    "debug message item in listview"
    pass


# ##############################################################################

class ImageButton(Button):
    "button line at tho bottom of the page"
    pass


# ##############################################################################

class SliderArea(BoxLayout):
    "volume slider next to the call window"
#    def __init__(self, **kwargs):
#       "init"
#        global BUTTON_DO_CALL, BUTTON_CALL_ANSWER, BUTTON_CALL_HANGUP
#        global BUTTON_DOOR_1, BUTTON_DOOR_2
#       global APP_NAME, SCREEN_SAVER, BRIGHTNESS, WATCHES, RING_TONE
#        global main_state, docall_button_global, mainLayout, scrmngr, config
#
#        super(SliderArea, self).__init__(**kwargs)
    pass


# ##############################################################################

class SettingsPopupDlg(BoxLayout):
    "settings popup content"
    def closePopupSettings(self):
        global mainLayout
        mainLayout.closePopupSettings()
        mainLayout.showPlayers()

    def openDetailSettings(self):
        global mainLayout
        mainLayout.closePopupSettings()
        mainLayout.openAppSettings(self)


# ##############################################################################

