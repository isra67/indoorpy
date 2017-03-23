#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import kivy
kivy.require('1.9.0')


from kivy.lang import Builder
from kivy.logger import Logger, LoggerHistory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from constants import *
from itools import *


# ###############################################################
#
# Popup Class - input text
#
# ###############################################################

KV = '''
BoxLayout:
    orientation: 'vertical'
    lbl1: lbl1
    btno: btno
    btok: btok
    spacing: 10

    Label:
        text: ''
        id: lbl1

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: 48
        spacing: 5

        Button:
            text: 'OK'
            id: btok
        Button:
            text: 'Cancel'
            id: btno
'''


class MyYesNoBox(Popup):
    "Yes or no  popup box"
    def __init__(self, **kwargs):
        super(MyYesNoBox, self).__init__(**kwargs)

        Logger.debug('%s: titl=$%s msg=%s' % (whoami(),kwargs.get('titl'),kwargs.get('txt')))

	self.p = Builder.load_string(KV)
	self.p.lbl1.text = kwargs.get('txt') or 'Are you sure?'
        self.p.btok.bind(on_press=self.buttonOk)
        self.p.btno.bind(on_press=self.buttonNo)

	self.title = kwargs.get('titl') or 'Confirm'
	self.auto_dismiss = kwargs.get('ad') or True
	self.cb = kwargs.get('cb') or None
	self.size_hint = (.69, .6)
	self.content = self.p


    def buttonOk(self, b):
        Logger.debug('%s: Yes' % (whoami()))
	self.dismiss()
	if not self.cb is None: self.cb()


    def buttonNo(self, b):
        Logger.debug('%s: No' % (whoami()))
	self.dismiss()


# ##############################################################################
