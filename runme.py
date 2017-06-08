import kivy
from kivy.app import App

from kivy.clock import Clock
#from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty#, StringProperty
#from random import randint

import subprocess

import threading

import os
import socket
import struct

from my_lib import *

Builder.load_string("""
<Root>:
    orientation: 'vertical'
    lblLink: lblLink
    lblNet: lblNet
    lblAudio: lblAudio
    lblApp: lblApp
    lblRemc: lblRemc

    Label:
        size_hint: 1, 2.5
        text: 'Indoor'
        font_size: self.height/2
    Label:
        text: 'System: OK'
        font_size: self.height/2
    Label:
        id: lblLink
        text: 'ETH link: wait...'
        font_size: self.height/2
    Label:
        id: lblNet
        text: 'Network: wait...'
        font_size: self.height/2
    Label:
        id: lblAudio
        text: 'Audio: wait...'
        font_size: self.height/2
    Label:
        id: lblRemc
        text: 'Remote control status: wait...'
        font_size: self.height/2
    Label:
        id: lblApp
        text: 'Application: wait...'
        font_size: self.height/2
    Label:
        text: ''
""")

WAIT_TXT = ' wait...'
OK_TXT = ' OK '
NO_TXT = ' NO '
ERR_TXT = ' ERROR '
NONE_TXT = ' None '
UP_TXT = ' up '
DOWN_TXT = ' down '



class Root(BoxLayout):

    counter = NumericProperty(0)
    stop = threading.Event()

    def __init__(self, **kwargs):
	super(Root, self).__init__(**kwargs)

	self.lNet = self.ids.lblNet
	self.lLink = self.ids.lblLink
	self.lAudio = self.ids.lblAudio
	self.lRemc = self.ids.lblRemc
	self.lApp = self.ids.lblApp

	self.update()

	threading.Thread(target=self.procNetlink).start()


    def update(self):
	self.getNetwork()
	self.getAudio()
	self.getTunnel()


    def procNetlink(self):
	# These constants map to constants in the Linux kernel. This is a crappy
	# way to get at them, but it'll do for now.
	RTMGRP_LINK = 1
	RTMGRP_IPV4_IFADDR = 0x10

	NLMSG_NOOP = 1
	NLMSG_ERROR = 2

	RTM_NEWLINK = 16
	RTM_DELLINK = 17
	RTM_NEWADDR = 20
	RTM_DELADDR = 21

	IFLA_ADDRESS = 1
	IFLA_IFNAME = 3

	# Create the netlink socket and bind to RTMGRP_LINK,
	s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE)
#	s.bind((os.getpid(), RTMGRP_LINK))
	s.bind((0, -1))

	while True:
	    if self.stop.is_set(): return

	    data = s.recv(65535)
	    msg_len, msg_type, flags, seq, pid = struct.unpack("=LHHLL", data[:16])

	    if msg_type == NLMSG_NOOP:
		#print "no-op"
		continue
	    elif msg_type == NLMSG_ERROR:
		#print "error"
		break

	    # We fundamentally only care about NEWLINK messages in this version.
	    #if msg_type != RTM_NEWLINK:
	    if not (msg_type == RTM_NEWLINK or msg_type == RTM_DELLINK or msg_type == RTM_NEWADDR or msg_type == RTM_DELADDR):
		continue

	    data = data[16:]

	    family, _, if_type, index, flags, change = struct.unpack("=BBHiII", data[:16])

	    remaining = msg_len - 32
	    data = data[16:]

	    while remaining and len(data) >= 4:
		rta_len, rta_type = struct.unpack("=HH", data[:4])

		# This check comes from RTA_OK, and terminates a string of routing attributes.
		if rta_len < 4: break

		rta_data = data[4:rta_len]

		increment = (rta_len + 4 - 1) & ~(4 - 1)
		data = data[increment:]
		remaining -= increment

		if not (msg_type == RTM_NEWLINK or msg_type == RTM_DELLINK\
		    or msg_type == RTM_NEWADDR or msg_type == RTM_DELADDR):
		    continue

		ip = ''
		# Hoorah, a link is up!
		if msg_type == RTM_NEWLINK:
#		    print "Link %s is UP" % rta_data
		    ip = UP_TXT
		elif msg_type == RTM_DELLINK:
#		    print "Link %s is DOWN" % rta_data
		    ip = DOWN_TXT

		if len(ip) == 0: continue

		t = self.lLink.text
		if WAIT_TXT in t: t = t[:len(t) - len(WAIT_TXT)]
		elif UP_TXT in t: t = t[:len(t) - len(UP_TXT)]
		elif DOWN_TXT in t: t = t[:len(t) - len(DOWN_TXT)]
		t = t + ip
		self.lLink.text = t
		print('%s: %s %s' % (whoami(), t, ip))

		if rta_type == IFLA_IFNAME and msg_type == RTM_NEWLINK:
		    send_command('./killme.sh')



    def getNetwork(self, speed=30):
	try:
	    info = get_info(SYSTEMINFO_SCRIPT).split()
	except:
	    info = []
	ip = OK_TXT if len(info) >= 6 else WAIT_TXT
	t = self.lNet.text
	if WAIT_TXT in t: t = t[:len(t) - len(WAIT_TXT)]
	elif OK_TXT in t: t = t[:len(t) - len(OK_TXT)]
	t = t + ip
	self.lNet.text = t
	print('%s: %s %r' % (whoami(), t, info))
	interval = 23 if ip is OK_TXT else 2
	Clock.schedule_once(self.getNetwork, interval)

    def getTunnel(self, speed=30):
	ps = subprocess.Popen("ps aux | grep tunnel | grep -c -v 'grep tunnel'", shell=True, stdout=subprocess.PIPE)
	info = ps.stdout.read()
	ps.stdout.close()
	ps.wait()
	ip = OK_TXT if '1' in info else NONE_TXT
	t = self.lRemc.text
	if WAIT_TXT in t: t = t[:len(t) - len(WAIT_TXT)]
	elif NONE_TXT in t: t = t[:len(t) - len(NONE_TXT)]
	elif OK_TXT in t: t = t[:len(t) - len(OK_TXT)]
	t = t + ip
	self.lRemc.text = t
	print('%s: %s %s' % (whoami(), t, info))
	interval = 35
	Clock.schedule_once(self.getTunnel, interval)

    def getAudio(self, speed=30):
	ps = subprocess.Popen("lsusb | grep -i conexant", shell=True, stdout=subprocess.PIPE)
	info = ps.stdout.read()
	ps.stdout.close()
	ps.wait()
	ip = OK_TXT if len(info) > 0 else ERR_TXT
	t = self.lAudio.text
	if WAIT_TXT in t: t = t[:len(t) - len(WAIT_TXT)]
	elif ERR_TXT in t: t = t[:len(t) - len(ERR_TXT)]
	elif OK_TXT in t: t = t[:len(t) - len(OK_TXT)]
	t = t + ip
	self.lAudio.text = t
	print('%s: %s %s' % (whoami(), t, info))
	interval = 10
	Clock.schedule_once(self.getAudio, interval)



class Tester(App):
    def build(self):
	return Root()

#    def on_stop(self):
#	self.root.stop.set()


if __name__ == '__main__':
    Tester().run()
