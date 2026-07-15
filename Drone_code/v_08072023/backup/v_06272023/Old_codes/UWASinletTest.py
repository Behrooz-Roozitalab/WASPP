#!/usr/bin/python2

#call functions from UWASmod.py
import UWASmod_v1
import time
import datetime
import os

#open file and write header
os.chdir('/home/pi/temp/')
temp_data_file = open('Press6.txt', 'a')
temp_data_file.write('Date, PressVolts'+'\n')
temp_data_file.close()
os.chdir('/home/pi/py2prog/')

DT = datetime.datetime.now()
try:
        TRH = UWASmod_v1.readi2cU9()
        time.sleep(1)
        while(TRH > 0):
                #for number in range (1500): #1500 is 25 min...
                TRH = UWASmod_v1.readi2cU9()
                time.sleep(1)


        UWASmod_v1.softShudown()
        print ("shutting down")

except(KeyboardInterrupt, SystemExit): #press CNTRL C
    print ("Hasta Luego")
