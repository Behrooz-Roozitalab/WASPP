#!/usr/bin/python2

#call functions from UWASmod.py
import UWASmod_v1
import time
import numpy
import os

gpsData = UWASmod_v1.GPSsetup() #GPS
time.sleep(45) #45 -time to get a GPS fix # normally 45
Date = gpsData[0]#Date is hhmmss.ss
BT = UWASmod_v1.readi2cU10(Date)#check battery power
Winds = UWASmod_v1.comTriMini(Date) #check winds

if Winds != 50:
    print('no wind data available, shutting down now')
    UWASmod_v1.softShutdown()
    
else:
    time.sleep(900) #45 -time to drive to site # normally 45
    for z in range(900): #45
        time.sleep(1)
        gpsData = UWASmod_v1.GPSsetup() #GPS
        Date = gpsData[0]
        TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb
        Winds = UWASmod_v1.comTriMini(Date)


    print('End of Program, shutting down now')
    UWASmod_v1.softShutdown()


