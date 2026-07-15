#call functions from UWASmod.py
import UWASmod_v1
import time
import numpy
import os

Date = 'Date not available'
Data_chk = UWASmod_v1.comTriMini(Date) #Winds
print(chr(Data_chk))
#if Data_chk  == 0:
    #UWASmod_v1.softShutdown()
onOff = 0 #turn pump off
#PumpStatus = UWASmod_v1.pumpOn(onOff)

sendTo = 0#advance to next position (e.g. 16 to 1)
Pos1 = UWASmod_v1.comValco(sendTo)#Comm with Valco Valve
print(chr(Pos1[0])+chr(Pos1[1]))
BAT = 3.8
UWASmod_v1.batteryOK(BAT)
pumpWorks = 1
#UWASmod_v1.pumpTest(pumpWorks)
UWASmod_v1.testSensors(10, 5, 11, 6)
#UWASmod_v1.programRunning(1)
gpsData = UWASmod_v1.GPSsetup() #GPS
print(gpsData)
#Date = gpsData[0]#Date is hhmmss.ss
print('starting Tri mini loop now')
for z in range(2): #test this...#1 minute...each round is ~6 seconds
        Winds = UWASmod_v1.comTriMini(Date)
        #print ('hello')
        #data should be 5Hz; in a loop to sample 250 times
        
BT = UWASmod_v1.readi2cU10(Date)#ADC of Batt, Flow,10VPwr (Thermistor T)
print(BT[0])
print(BT[1])
print(BT[2])
TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb
print(TRH)

time.sleep(5)
#UWASmod_v1.programRunning(0)
