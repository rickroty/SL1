
import RPi.GPIO as GPIO

import time
from time import sleep
import datetime

SWITCH = 11
VOLTMETER = 15

GPIO.setmode(GPIO.BOARD)

GPIO.setup(SWITCH, GPIO.IN)

GPIO.setup(VOLTMETER, GPIO.OUT)
GPIO.output(VOLTMETER, GPIO.HIGH)
print 'VOLT METER ON'

meteron = True
run = True
while (run):
    if ( GPIO.input(SWITCH) == True ):
        if meteron:
             meteron = false
             GPIO.output(VOLTMETER, GPIO.LOW)
             print 'VOLT METER OFF'
        else:
             meteron = true
             GPIO.output(VOLTMETER, GPIO.HIGH)
             print 'VOLT METER ON'
    sleep(0.2)


GPIO.output(VOLTMETER, GPIO.LOW)
GPIO.cleanup()
