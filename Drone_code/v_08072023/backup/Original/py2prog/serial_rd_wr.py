#!/usr/bin/env python2
#write script to read and write to serial Valco Valve

import time
import serial

ser = serial.Serial(

    port='/dev/ttyAMA0',
    baudrate=4800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1

)

counter =0

while 1:
    ser.write('hi')
    time.sleep(1)
    counter +=1
    #x = ser.readline()
    print x
