#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import kivy
kivy.require('1.9.0')


from kivy.lang import Builder
from kivy.logger import Logger  #, LoggerHistory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
#from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
#from kivy.uix.textinput import TextInput
#from kivy.uix.widget import Widget

from constants import *
from itools import *


# ###############################################################
#
# Popup Class - alert popup dialog
#
# ###############################################################

KV = '''
BoxLayout:
    orientation: 'vertical'
    lblInfo: lblInfo
    btok: btok
    spacing: 10

    Label:
        text: ''
        id: lblInfo

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: 48
        spacing: 5

        Button:
            text: 'OK'
            id: btok
'''


class MyAlertBox(Popup):
    "Yes or no  popup box"
    def __init__(self, **kwargs):
        super(MyAlertBox, self).__init__(**kwargs)

	header = kwargs.get('titl') or 'Status'
	info = kwargs.get('txt') or ''
	self.cb = kwargs.get('cb') or None
	ad = kwargs.get('ad') or False

        Logger.debug('%s: titl=$%s msg=%s' % (whoami(), header, info))

	self.p = Builder.load_string(KV)
	self.p.lblInfo.text = info
        self.p.btok.bind(on_press=self.buttonOk)

	self.title = header
	self.auto_dismiss = ad
	self.size_hint = (.69, .75)
	self.content = self.p


    def buttonOk(self, b):
        Logger.debug('%s:' % whoami())
	self.dismiss()
	if not self.cb is None: self.cb()


# ##############################################################################
