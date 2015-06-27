
import RPi.GPIO as GPIO

import time
from time import sleep
import datetime
import socket

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SWITCH = 18
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
             meteron = False
             GPIO.output(VOLTMETER, GPIO.LOW)
            clientsocket.connect(('localhost', 5000))
            clientsocket.send('killusb')
            clientsocket.close()             
             print 'VOLT METER OFF'
             print 'USB OFF'
             sleep(0.5)
        else:
             meteron = True
             GPIO.output(VOLTMETER, GPIO.HIGH)
             print 'VOLT METER ON'
             sleep(0.5)
    sleep(0.2)


GPIO.output(VOLTMETER, GPIO.LOW)
GPIO.cleanup()
