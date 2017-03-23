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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemLabel
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

from constants import *


mainLayout = None

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
        mainLayout.closePopupSettings(False)
        mainLayout.openAppSettings()


# ##############################################################################

