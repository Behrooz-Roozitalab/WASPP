#!/usr/bin/python2

#call functions from UWASmod.py
import UWASmod_v1
import time
import numpy
import os


gpsData = UWASmod_v1.GPSsetup() #GPS
Date = gpsData[0]#Date is hhmmss.ss

#check and print Valco Position
sendTo = 0
Pos1 = UWASmod_v1.comValco(sendTo)
print('Position 1:', chr(Pos1[0])+chr(Pos1[1]))
      
os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_MixingTest_Log.txt', 'a')
temp_data_file.write('Valco Valve position: '+ str(Pos1)+'\n')
temp_data_file.close()

#Change Valco position, if desired
sendTo = input ('To send Valco to next positoin, enter 2, to query position, enter 0: ')
sendTo = 0
Pos1 = UWASmod_v1.comValco(sendTo)
print('Position 1:', chr(Pos1[0])+chr(Pos1[1]))

os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_MixingTest_Log.txt', 'a')
temp_data_file.write('Valco Valve position: '+ str(chr(Pos1[0]))+str(chr(Pos1[1]))+'\n')
temp_data_file.write('Date, System Pressure, Flow, 10V'+'\n')
temp_data_file.close()

try:
    onOff = 1 #turn pump on
    print('Turning pump on...')
    PumpStatus = UWASmod_v1.pumpOn(onOff)
    
    while True:
       gpsData = UWASmod_v1.GPSsetup() #GPS
       Date = gpsData[0]#Date is hhmmss.ss
       
       TRH = UWASmod_v1.readi2cU9(Date)
       BT = UWASmod_v1.readi2cU10(Date)
       
       Flow = BT[1] #Flow = 0
       P10V = BT[2]
       pSys = TRH[2]
       
       print('System Pressure: ', pSys)
       print('Flow: ', Flow)
       
       os.chdir('/home/pi/temp/')
       temp_data_file = open('UWAS_MixingTest_Log.txt', 'a')
       temp_data_file.write(str(Date) +','+str(pSys)+','+str(Flow) +','+str(P10V)+'\n')
       temp_data_file.close()
        

except(KeyboardInterrupt, SystemExit): #press cntrl + C
            print "Exiting Loop...turning off pump"

onOff = 0 #turn pump on
PumpStatus = UWASmod_v1.pumpOn(onOff)

        
