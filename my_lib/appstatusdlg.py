#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

import kivy
kivy.require('1.9.0')

from alertdlg import *


# ###############################################################
#
# Popup Class - show app status info
#
# ###############################################################

def myappstatus(titl, uptime, cinfo):
    info = 'System uptime: %s\n\nIncoming calls: %d\nOutgoing calls: %d\nNot answered calls: %d\nNot responded calls: %d'\
	    % (str(uptime), int(cinfo['in']), int(cinfo['out']), int(cinfo['noansw']), int(cinfo['noresp']))

    MyAlertBox(titl=titl, txt=info, cb=None, ad=True).open()


# ##############################################################################
