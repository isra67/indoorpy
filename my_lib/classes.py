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
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.listview import ListView, ListItemLabel
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from constants import *


mainLayout = None

# ###############################################################
#
# Classes
#
# ###############################################################

class SetScreen(Screen):
    "setscreen"
    pass


# ##############################################################################

class MyListViewLabel(Label):
    "debug message item in listview"
    pass


# ##############################################################################

class MySetLabel(Label):
    "show value near slider"
    pass


# ##############################################################################

class VideoLabel(Label):
    "text behind the video"
    pass


# ##############################################################################

class MyAsyncImage(AsyncImage):
    "image class"
    pass


# ##############################################################################

class ImageButton(Button):
    "button line at the bottom of the page"
    pass


# ##############################################################################

class DoorButton(Button):
    "four images door lock/unlock button at the bottom of the page"
    pass


# ##############################################################################

class MBoxLayout(BoxLayout):
    "layout + black color background"
    pass


# ##############################################################################

class HorizontalCameraLayout(BoxLayout):
    "landscape camera layout"
    pass


# ##############################################################################

class VerticalCameraLayout(BoxLayout):
    "portrait camera layout"
    pass


# ##############################################################################

class SliderArea(MBoxLayout):
    "volume slider next to the call window"
    pass


# ##############################################################################

