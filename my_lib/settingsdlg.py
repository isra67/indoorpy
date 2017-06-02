#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################


import kivy
kivy.require('1.9.0')


from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger, LoggerHistory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemLabel
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from config import *
from constants import *
from itools import *


mainLayout = None

# ###############################################################
#
# Classes
#
# ###############################################################

class SettingsPopupDlg(BoxLayout):
    "settings popup content"
    def __init__(self, **kwargs):
	super(BoxLayout, self).__init__(**kwargs)
#	self.music = self.ids.setline3.subbox2.musicspinner
#	self.clock = self.ids.setline3.subbox2.clockspinner
#	self.music = spinner.bind(text=self.show_selected_value)
#	self.clock = spinner.bind(text=self.show_selected_value)

    def closePopupSettings(self):
        global mainLayout
        mainLayout.closePopupSettings()
        mainLayout.showPlayers()

    def openDetailSettings(self):
        global mainLayout
        mainLayout.closePopupSettings(False)
        mainLayout.openAppSettings()

    def brightslider(self):
	val = self.setline2.subbox1.brightslider.value
	Logger.info('%s: %d' % (whoami(), val))
	send_command('%s %d' % (BRIGHTNESS_SCRIPT, val))
	return val

    def show_selected_value(self,spinner,text):
	Logger.info('%s: %r %s' % (whoami(), spinner, text))


# ##############################################################################

