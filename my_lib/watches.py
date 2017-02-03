#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import kivy
kivy.require('1.9.0')

from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from math import cos, sin, pi

import datetime

from constants import *


###############################################################
#
# Declarations
#
# ###############################################################

ACTIVE_DISPLAY_BACKGROUND = Color(.0,.0,.9)
INACTIVE_DISPLAY_BACKGROUND = Color(.0,.0,.0)

APP_LABEL = APP_NAME

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
        self.ln.text = '[color=0000f0] ' + APP_LABEL + ' [/color]'
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

