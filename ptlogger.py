import Adafruit_BMP.BMP085 as BMP085

import RPi.GPIO as GPIO

import glob

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
toggle = True
while (start==0):
    if ( GPIO.input(SWITCH) == True ):
         start = 1
    cnt = cnt + 1
    if(cnt/10) == int(cnt/10):
        if(toggle):
            GPIO.output(POWERLED, GPIO.HIGH)
            GPIO.output(LED, GPIO.LOW)
        else:
            GPIO.output(POWERLED, GPIO.LOW)
            GPIO.output(LED, GPIO.HIGH)
        toggle =  not toggle

    sleep(0.2)

GPIO.output(POWERLED, GPIO.HIGH)
GPIO.output(LED, GPIO.LOW)

#import socket

#clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#clientsocket.connect(('localhost', 5000))
#clientsocket.send('killusb')
#clientsocket.close()

# Setup 1-wire BUS for temperature probe
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
external_probe = True
base_dir = '/sys/bus/w1/devices/'
try:
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
except:
    print "Error binding to external temperature probe.  Skipping this sensor."
    external_probe = False

def read_temp_raw():
    if os.path.exists(device_file):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
    else:
        raise ValueError('Cannot read temperature probe.')
    return lines
 
def read_probe_temperature():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c



#Instantiate I2C Pressure Sensor 
# Default constructor will pick a default I2C bus.
#
# For the Raspberry Pi this means you should hook up to the only exposed I2C bus
# from the main GPIO header and the library will figure out the bus number based
# on the Pi's revision.

sensor = BMP085.BMP085()
local_altitude = 482   #Pleasant Valley Airport
sealevel_pressure = sensor.read_sealevel_pressure(local_altitude)

# BMP085 modes are one of BMP085_ULTRALOWPOWER, 
# BMP085_STANDARD, BMP085_HIGHRES, or BMP085_ULTRAHIGHRES.  See the BMP085
# datasheet for more details on the meanings of each mode (accuracy and power
# consumption are primarily the differences).  The default mode is STANDARD.
#sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

print 'Current Date/Time is' + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

print 'Initial Altitude = {0:0.2f} m'.format(local_altitude)
print 'Initial Sealevel Pressure = {0:0.2f} Pa'.format(sealevel_pressure)
print 'Initial Temp = {0:0.2f} *C'.format(sensor.read_temperature())
if(external_probe):
    print 'Initial External Temperature = {0:0.2f} C'.format(read_probe_temperature())
print 'Initial Pressure = {0:0.2f} Pa'.format(sensor.read_pressure())
print 'Initial Altitude = {0:0.2f} m'.format(sensor.read_altitude(sealevel_pressure))



FILENAME = '../data/ptdata_' + datetime.datetime.now().strftime("%Y%m%d")
inc=0
checkfile = FILENAME
while path.isfile(checkfile + '.csv'):
    checkfile = FILENAME + '_' + str(inc)
    inc = inc + 1

FILENAME = checkfile + '.csv'

#open log file
f=open(FILENAME,'a')
outstring = 'date,temp,outsidetemp,pressure,altitude,sealevelpressure\n'
f.write(outstring)
f.close()

strOutsideTemp = '0'
quit = False
while not quit:
    
    GPIO.output(LED, GPIO.HIGH)
    
    #open log file
    f=open(FILENAME,'a')

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y/%m/%d %H:%M:%S")

    strTemp = '{0:0.2f}'.format(sensor.read_temperature())
    strPressure = '{0:0.2f}'.format(sensor.read_pressure())
    strAltitude = '{0:0.2f}'.format(sensor.read_altitude(sealevel_pressure))

    if (external_probe):
        try:
            strOutsideTemp = '{0:0.2f}'.format(read_probe_temperature())
            break
        except ValueError:
            strOutsideTemp = '0'

    strLocalAltitude = '{0:0.2f}'.format(local_altitude)
    strSealevelPressure = '{0:0.2f}'.format(sealevel_pressure)

    outstring = timestamp + ',' + strLocalAltitude + ',' + strSealevelPressure + ',' + strTemp + ',' + strOutsideTemp + ',' + strPressure + ',' + strAltitude + '\n'

    print outstring
    f.write(outstring)
    f.close()

    time.sleep(1)
    GPIO.output(LED, GPIO.LOW)
    
    time.sleep(2)
    if ( GPIO.input(SWITCH) == True ):
        quit = True
        
    time.sleep(2)
    if ( GPIO.input(SWITCH) == True and quit == True):
        quit = True
    else:
        quit = False
        

cnt = 0
toggle = True
while (cnt<100):
    cnt = cnt + 1
    if(cnt/10) == int(cnt/10):
        if(toggle):
            GPIO.output(POWERLED, GPIO.HIGH)
        else:
            GPIO.output(POWERLED, GPIO.LOW)
        toggle =  not toggle

    sleep(0.1)
    
GPIO.output(LED, GPIO.LOW)
#GPIO.output(VOLTMETER, GPIO.LOW)
GPIO.output(POWERLED, GPIO.LOW)
GPIO.cleanup()
print "Shutting down..."
os.system('sudo shutdown -h now')
