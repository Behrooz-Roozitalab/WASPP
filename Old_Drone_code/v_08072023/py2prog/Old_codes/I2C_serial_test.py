#!/usr/bin/python2
#I2C test
import os
import numpy
import smbus
from time import sleep

bus = smbus.SMBus(1) # i2c device detected on bus 1 i2cdetect -y 1

DEVICE_ADDRESS = 0x48 # does this change based on read-write bit?

def sensT():
    sensorT = bus.read_byte_data(DEVICE_ADDRESS,1)
    return sensorT

def sensRH():
    sensorRH = bus.read_byte_data(DEVICE_ADDRESS,0)
    return sensorRH

def range():
    range1 = bus.read_byte_data(DEVICE_ADDRESS,2)
    range2 = bus.read_byte_data(DEVICE_ADDRESS,3)
    range3 = (range1 <<8) + range2
    return range3

#Main LOOP
try:

    while 1:
       
        sensorRH = sensRH()
        sleep(1)
        sensorT = sensT()
        print sensorRH
        #print sensorT

except(KeyboardInterrupt, SystemExit): #press
    print "Hasta Luego"
