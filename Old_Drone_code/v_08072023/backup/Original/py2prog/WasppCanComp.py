#!/usr/bin/python2
#clean valve

#call functions from UWASmod.py
import UWASmod_v1
import time
import numpy
import os


gpsData = UWASmod_v1.GPSsetup() #GPS
time.sleep(45) #time to get a GPS fix # normally 60
Date = gpsData[0]#Date is hhmmss.ss

runningNow = UWASmod_v1.programRunning(1) #set up GPIOs
BT = UWASmod_v1.readi2cU10(Date)#ADC of Batt, Flow,10VPwr (Thermistor T)
TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb

sendTo = 0 #Make this send to position 16
Pos1 = UWASmod_v1.comValco(sendTo)#Comm with Valco Valve
Position1= chr(Pos1[0]) + chr(Pos1[1])
print(Position1)

os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_SamplingLog.txt', 'a')
temp_data_file.write('Initial Valco Position is: '+str(chr(Pos1[0]))+str(chr(Pos1[1]))+'\n')
temp_data_file.write('Initial GPS data: ' + Date +','+str(gpsData[1])+','+str(gpsData[2])+','+str(gpsData[3])+','+str(gpsData[4])+'\n')
temp_data_file.write('Pump starting now...' +'\n')
temp_data_file.close()


for x in range(16):

    Position = int(float(Position1))
                   
    if (Position%2 == 1):
        print(x)
        onOff = 0 #turn pump off
        PumpStatus = UWASmod_v1.pumpOn(onOff)
        time.sleep(8) #normally 10?

        gpsData = UWASmod_v1.GPSsetup() #GPS
        BT = UWASmod_v1.readi2cU10(Date)#ADC of Batt, Flow,10VPwr (Thermistor T)
        TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb

        os.chdir('/home/pi/temp/')
        temp_data_file = open('UWAS_SamplingLog.txt', 'a')
        temp_data_file.write('x of 16: '+str(chr(x))+'\n')
        temp_data_file.write('Current Valco Position is: ' +str(chr(Pos1[0]))+str(chr(Pos1[1]))+'\n')
        temp_data_file.write('WP (&Sat #) start GPS data: ' + Date +','+str(gpsData[1])+','+str(gpsData[2])+','+str(gpsData[3])+','+str(gpsData[4])+'\n')
        temp_data_file.write('Sample start Batt,Flow,10V:'+str(BT[0])+','+str(BT[1])+','+str(BT[2])+'\n')
        temp_data_file.write('Sample start RH,T,Psys,Pamb:'+str(TRH[0])+','+str(TRH[1])+','+str(TRH[2])+','+str(TRH[3])+'\n')
        temp_data_file.close()

        onOff = 1 #turn pump on
        PumpStatus = UWASmod_v1.pumpOn(onOff)
        if (Position < 12):
            time.sleep(90)
        else:
            time.sleep(10)
        gpsData = UWASmod_v1.GPSsetup() #GPS
        BT = UWASmod_v1.readi2cU10(Date)#ADC of Batt, Flow,10VPwr (Thermistor T)
        TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb

        os.chdir('/home/pi/temp/')
        temp_data_file = open('UWAS_SamplingLog.txt', 'a')
        temp_data_file.write('WP (&Sat #) end GPS data: ' + Date +','+str(gpsData[1])+','+str(gpsData[2])+','+str(gpsData[3])+','+str(gpsData[4])+'\n')
        temp_data_file.write('Sample end Batt,Flow,10V:'+str(BT[0])+','+str(BT[1])+','+str(BT[2])+'\n')
        temp_data_file.write('Sample end RH,T,Psys,Pamb:'+str(TRH[0])+','+str(TRH[1])+','+str(TRH[2])+','+str(TRH[3])+'\n')
        temp_data_file.close()

        sendTo = 2 #increment position
        Pos1 = UWASmod_v1.comValco(sendTo)
        Position1= chr(Pos1[0]) + chr(Pos1[1])
        print(Position1)
    else:

        time.sleep(5) #clean tubes only for less long...
        sendTo = 2 #increment position
        Pos1 = UWASmod_v1.comValco(sendTo)
        Position1= chr(Pos1[0]) + chr(Pos1[1])
        print(Position1)

onOff = 0 #turn pump off
PumpStatus = UWASmod_v1.pumpOn(onOff)

os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_SamplingLog.txt', 'a')
temp_data_file.write('Canister Sampling Ended...' +'\n')
temp_data_file.close()

runningNow = UWASmod_v1.programRunning(0)
UWASmod_v1.softShutdown()
