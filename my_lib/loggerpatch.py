from kivy.logger import Logger
from kivy.clock import Clock

import logging
import time

from itools import *
from loggers import *
from nodeclient import *


class LoggerPatch():

    def __init__(self):
        self.emit_org = None

        # we create a formatter object once to avoid inialisation on every log line
        self.oFormatter=logging.Formatter(None)

        # we just need to patch the first Handler as we change the message itself
        oHandler = Logger.handlers[0]
        self.emit_org=oHandler.emit
        oHandler.emit=self.emit

	initNodeConnection()


    def emit(self, record):
        # we do not use the formatter by purpose as it runs on failure
        # if the message string contains format characters

        ct = self.oFormatter.converter(record.created)
        t = time.strftime("%Y-%m-%d %H-%M-%S", ct)
        t = "%s.%03d" % (t, record.msecs)

	msg = '[%-7s] [%s] %s' % (record.levelname, t, record.msg)
        record.msg= t + ': ' + record.msg

        self.emit_org(record)

	Clock.schedule_once(lambda dt: self.save(msg))


    def save(self, msg):
#	print('%s: %s' % (whoami(), msg))
	setloginfo(False, msg)

	sendNodeInfo(msg)


oLoggerPatch = LoggerPatch()