import kivy

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config#, ConfigParser
from kivy.lang import Builder
#from kivy.properties import NumericProperty

import os
import socket
import struct
import threading

from my_lib import *


Builder.load_string("""
<Root>:
    orientation: 'vertical'
    lblLink: lblLink
    lblNet: lblNet
    lblInet: lblInet
    lblAudio: lblAudio
    lblApp: lblApp
    lblRemc: lblRemc
    lblDebug: lblDebug
    lbOrientation: 'horizontal'

    Label:
        size_hint: 1, 2.5
        text: 'Indoor'
        font_size: self.height/2
    BoxLayout:
        orientation: root.lbOrientation
        Label:
            text: 'System: OK'
            font_size: self.height/2
        Label:
            id: lblLink
            text: 'ETH link: wait...'
            font_size: self.height/2
    BoxLayout:
        orientation: root.lbOrientation
        Label:
            id: lblNet
            text: 'Network: wait...'
            font_size: self.height/2
        Label:
            id: lblInet
            text: 'Internet: wait...'
            font_size: self.height/2
    BoxLayout:
        orientation: root.lbOrientation
        Label:
            id: lblAudio
            text: 'Audio: wait...'
            font_size: self.height/2
        Label:
            id: lblRemc
            text: 'Remote control: wait...'
            font_size: self.height/2
    BoxLayout:
        orientation: root.lbOrientation
        Label:
            id: lblApp
            text: 'Application: wait...'
            font_size: self.height/2
        Label:
            id: lblSrv
            text: 'Internal webserver: wait...'
            font_size: self.height/2
    Label:
        id: lblDebug
        text: '...'
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

#    counter = NumericProperty(0)
    stop = threading.Event()

    def __init__(self, **kwargs):
	super(Root, self).__init__(**kwargs)

	self.lNet = self.ids.lblNet
	self.lInet = self.ids.lblInet
	self.lLink = self.ids.lblLink
	self.lAudio = self.ids.lblAudio
	self.lRemc = self.ids.lblRemc
	self.lApp = self.ids.lblApp
	self.lSrv = self.ids.lblSrv
	self.lDebug = self.ids.lblDebug

	self.ipaddr = ''

	self.update()

	threading.Thread(target=self.procNetlink).start()

#	Config.read('/root/.kivy/config.ini')

	rot = Config.getint('graphics','rotation')
	if rot in [90, 270]:
	    self.lbOrientation = 'vertical'

	print whoami(), rot, self.lbOrientation


    def update(self):
	self.getNetwork()
	self.getINet()
	self.getAudio()
	self.getTunnel()
	self.getNodeServer()


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

	old_msg = -1
	link_status = ''

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

	    if old_msg == msg_type: continue

	    old_msg = msg_type

	    # We fundamentally only care about NEWLINK messages in this version.
	    #if msg_type != RTM_NEWLINK:
	    if not msg_type in [RTM_NEWLINK, RTM_DELLINK, RTM_NEWADDR, RTM_DELADDR]:
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

#		self.lDebug.text = ('%s: %d %s' % (whoami(), msg_type, rta_data))
#		print('%s: %d %s' % (whoami(), msg_type, rta_data))

		ip = ''
		# Hoorah, a link is up!
		if msg_type == RTM_NEWLINK:
		    ip = UP_TXT
		elif msg_type == RTM_DELLINK:
		    ip = DOWN_TXT
		elif msg_type in [RTM_NEWADDR, RTM_DELADDR]:
		    ip = WAIT_TXT

		if len(ip) == 0: continue

		t = self.lLink.text
		if WAIT_TXT in t: t = t[:len(t) - len(WAIT_TXT)]
		elif UP_TXT in t: t = t[:len(t) - len(UP_TXT)]
		elif DOWN_TXT in t: t = t[:len(t) - len(DOWN_TXT)]
		t = t + ip
		self.lLink.text = t
#		print('%s: %s %s' % (whoami(), t, ip))

		if rta_type == IFLA_IFNAME and msg_type in [RTM_NEWLINK, RTM_DELLINK]:
		    if link_status != ip and ip != WAIT_TXT:
			link_status = ip
		    continue
		elif rta_type == IFLA_IFNAME and msg_type == RTM_NEWADDR:
		    continue



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
#	print('%s: %s %r' % (whoami(), t, info))
	interval = 12 if ip is OK_TXT else 2
	Clock.schedule_once(self.getNetwork, interval)

    def getINet(self, speed=30):
	try:
	    info = get_info('./checkinet.sh')
	except Exception as e:
	    info = '0'
	ip = OK_TXT if '1' in info else NO_TXT
	t = self.lInet.text
	if WAIT_TXT in t: t = t[:len(t) - len(WAIT_TXT)]
	elif OK_TXT in t: t = t[:len(t) - len(OK_TXT)]
	elif NO_TXT in t: t = t[:len(t) - len(NO_TXT)]
	t = t + ip
	self.lInet.text = t
	print('%s: %s %r' % (whoami(), t, info))
	interval = 14 if ip == OK_TXT else 5
	Clock.schedule_once(self.getINet, interval)

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
#	print('%s: %s %s' % (whoami(), t, info))
	interval = 13
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
#	print('%s: %s %s' % (whoami(), t, info))
	interval = 10
	Clock.schedule_once(self.getAudio, interval)

    def getNodeServer(self, speed=30):
	ps = subprocess.Popen("ps aux | grep node | grep -c -v 'grep node'", shell=True, stdout=subprocess.PIPE)
	info = ps.stdout.read()
	ps.stdout.close()
	ps.wait()
	ip = OK_TXT if '1' in info else NO_TXT
	t = self.lSrv.text
	if WAIT_TXT in t: t = t[:len(t) - len(WAIT_TXT)]
	elif NO_TXT in t: t = t[:len(t) - len(NO_TXT)]
	elif OK_TXT in t: t = t[:len(t) - len(OK_TXT)]
	t = t + ip
	self.lSrv.text = t
#	print('%s: %s %s' % (whoami(), t, info))
	interval = 15
	Clock.schedule_once(self.getNodeServer, interval)


class Tester(App):
    def build(self):
	return Root()


if __name__ == '__main__':
    Tester().run()
