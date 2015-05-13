import Adafruit_BMP.BMP085 as BMP085

import RPi.GPIO as GPIO

import os
import os.path as path
import time
from time import sleep
import datetime


SWITCH = 11
#VOLTMETER = 15
LED = 12
POWERLED = 22

GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)

GPIO.setup(SWITCH, GPIO.IN)

GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

GPIO.setup(POWERLED, GPIO.OUT)
GPIO.output(POWERLED, GPIO.HIGH)

start = 0
cnt = 0
while (start==0):
    if ( GPIO.input(SWITCH) == True ):
         start = 1
    cnt = cnt + 1
    if(cnt/10) = int(cnt/10):
        GPIO.output(POWERLED, GPIO.HIGH)
    else:
        GPIO.output(POWERLED, GPIO.LOW)
        
    sleep(0.2)

GPIO.output(POWERLED, GPIO.HIGH)

# Default constructor will pick a default I2C bus.
#
# For the Raspberry Pi this means you should hook up to the only exposed I2C bus
# from the main GPIO header and the library will figure out the bus number based
# on the Pi's revision.

sensor = BMP085.BMP085()


# BMP085 modes are one of BMP085_ULTRALOWPOWER, 
# BMP085_STANDARD, BMP085_HIGHRES, or BMP085_ULTRAHIGHRES.  See the BMP085
# datasheet for more details on the meanings of each mode (accuracy and power
# consumption are primarily the differences).  The default mode is STANDARD.
#sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

print 'Current Date/Time is' + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

print 'Initial Temp = {0:0.2f} *C'.format(sensor.read_temperature())
print 'Initial Pressure = {0:0.2f} Pa'.format(sensor.read_pressure())
print 'Initial Altitude = {0:0.2f} m'.format(sensor.read_altitude())
print 'Initial Sealevel Pressure = {0:0.2f} Pa'.format(sensor.read_sealevel_pressure())



FILENAME = '../data/ptdata_' + datetime.datetime.now().strftime("%Y%m%d")
inc=0
checkfile = FILENAME
while path.isfile(checkfile + '.csv'):
    checkfile = FILENAME + '_' + str(inc)
    inc = inc + 1

FILENAME = checkfile + '.csv'

#open log file
f=open(FILENAME,'a')
outstring = 'date,temp,pressure,altitude,sealevelpressure\n'
f.write(outstring)
f.close()

while True:
    
    GPIO.output(LED, GPIO.HIGH)
    
    #open log file
    f=open(FILENAME,'a')

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y/%m/%d %H:%M:%S")

    strTemp = '{0:0.2f}'.format(sensor.read_temperature())
    strPressure = '{0:0.2f}'.format(sensor.read_pressure())
    strAltitude = '{0:0.2f}'.format(sensor.read_altitude())
    strSeaLevelPressure = '{0:0.2f}'.format(sensor.read_sealevel_pressure())

    outstring = timestamp + ',' + strTemp + ',' + strPressure + ',' + strAltitude + ',' + strSeaLevelPressure + '\n'

    print outstring
    f.write(outstring)
    f.close()

    time.sleep(1)
    GPIO.output(LED, GPIO.LOW)
    time.sleep(9)

GPIO.output(LED, GPIO.LOW)
GPIO.output(VOLTMETER, GPIO.LOW)
GPIO.cleanup()
