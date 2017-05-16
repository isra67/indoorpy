import RPi.GPIO as GPIO
from time import sleep

RST_PIN = 24
RST_TIME = .2

#print GPIO.VERSION

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)

#sleep(RST_TIME)
GPIO.setup(RST_PIN, GPIO.OUT, initial=GPIO.LOW)
#GPIO.setup(RST_PIN, GPIO.OUT, initial=GPIO.HIGH)
sleep(RST_TIME)


GPIO.output(RST_PIN, GPIO.LOW)
#print('Low')
#sleep(RST_TIME)
GPIO.output(RST_PIN, GPIO.HIGH)
#print('High')
sleep(RST_TIME)
GPIO.output(RST_PIN, GPIO.LOW)
#print('Low')
#sleep(RST_TIME)

a = """
while True:
    GPIO.output(RST_PIN, GPIO.LOW)
    print('Low')
    sleep(RST_TIME)
    GPIO.output(RST_PIN, GPIO.HIGH)
    print('High')
    sleep(RST_TIME)
    GPIO.output(RST_PIN, GPIO.LOW)
    print('Low')
    sleep(RST_TIME)
#    GPIO.output(RST_PIN, GPIO.LOW)
#    sleep(.2)
#    GPIO.output(RST_PIN, GPIO.HIGH)
"""