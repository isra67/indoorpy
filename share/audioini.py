import RPi.GPIO as GPIO
from time import sleep

RST_PIN = 2
RST_TIME = .2

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

INI_VALUE = GPIO.HIGH
RST_VALUE = GPIO.LOW

GPIO.setup(RST_PIN, GPIO.OUT, initial=INI_VALUE)
sleep(RST_TIME)

GPIO.output(RST_PIN, INI_VALUE)
sleep(RST_TIME)
GPIO.output(RST_PIN, RST_VALUE)
sleep(RST_TIME)
GPIO.output(RST_PIN, INI_VALUE)
