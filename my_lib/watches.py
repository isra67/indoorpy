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
#from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from kivy.logger import Logger

from math import cos, sin, pi

import datetime

from constants import *


###############################################################
#
# Declarations
#
# ###############################################################

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
#        Clock.schedule_interval(self.update, 1)
	self.starttimer()

    def update(self, *args):
	t = datetime.datetime.now()
        self.text = t.strftime("%H:%M:%S")

    def starttimer(self):
        Clock.schedule_interval(self.update, 1)

    def stoptimer(self):
        Clock.unschedule(self.update)

# ##############################################################################

class MyClockWidget(FloatLayout):
    "Clock class - analog"
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

#        Clock.schedule_interval(self.update_clock, 1)
	self.starttimer()


    def starttimer(self):
        Clock.schedule_interval(self.update_clock, 1)

    def stoptimer(self):
        Clock.unschedule(self.update_clock)

    def update_clock(self, *args):
        time = datetime.datetime.now()
        self.canvas.clear()

        self.clear_widgets()
#	self.ln.parent = None
#        self.ln.pos = self.pos
#        self.ln.size = self.size
#        self.ln.text = '[color=0000f0] ' + APP_LABEL + ' [/color]'
#        self.ln.text_size = self.size
#        self.add_widget(self.ln)

	self.temps = 208
	self.postemp = [self.center_x - self.temps, self.center_y - self.temps]
	self.sizetemp = [self.temps * 2, self.temps * 2]

#	Logger.debug('watch: w:%d h:%d x:%d y:%d cx:%d cy:%d' % (self.width, self.height, self.x, self.y, self.center_x, self.center_y))

        with self.canvas:
            Color(.2, .2, .2, .1)
	    Ellipse(pos=self.postemp, size=self.sizetemp)

            Color(.9, .9, .9)
            Line(points = [self.center_x, self.center_y, self.center_x+0.7*self.r*sin(pi/30*time.second),
                self.center_y+0.7*self.r*cos(pi/30*time.second)], width=1, cap="round")
            Color(.7, .7, .7)
            Line(points = [self.center_x, self.center_y, self.center_x+0.6*self.r*sin(pi/30*time.minute),
                self.center_y+0.6*self.r*cos(pi/30*time.minute)], width=2, cap="round")
            Color(.7, .7, .7)
            th = time.hour * 60 + time.minute
            Line(points = [self.center_x, self.center_y, self.center_x+0.5*self.r*sin(pi/360*th),
            self.center_y+0.5*self.r*cos(pi/360*th)], width=3, cap="round")


# ##############################################################################
