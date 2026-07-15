#!/usr/bin/python2

#call functions from UWASmod.py
import UWASmod_v1
import time
import numpy
import os
#import RPi.GPIO as GPIO

#GPIO.cleanup()

#put in the waypoints for the flight plan HERE!
#4002.2646,N,10514.5812,W,1574.3 (Alt m)...for lat lon deg-min-decmin format
#Boulder Resevoir 4002.26 N 10514.5664 W
#Fly vertical profile T, H, P first..
#WPlat = [0,0,0,0,0,0,0,0]
#WPlon = [0,0,0,0,0,0,0,0]
#WPalt = [120,100,80,60,40,30,20,10]
#WPlat = [0,0]
#WPlon = [0,0]
#WPalt = [0,0]


#TEST THE SENSORS...
gpsData = UWASmod_v1.GPSsetup() #GPS
Date = gpsData[0]#Date is hhmmss.ss
Data_chk = UWASmod_v1.comTriMini(Date) #Winds
#if Data_chk == 0:
        #UWASmod_v1.softShutdown() #restart program

runningNow = UWASmod_v1.programRunning(1)
sendTo = 0
Pos1 = UWASmod_v1.comValco(sendTo)#Comm with Valco Valve - should be even number like 16
#print(chr(Pos1[0])+chr(Pos1[1]))
os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_SamplingLog.txt', 'a')
temp_data_file.write('Starting Valco Position is: '+str(chr(Pos1[0]))+str(chr(Pos1[1]))+'\n')
temp_data_file.close()

BT = UWASmod_v1.readi2cU10(Date)#ADC of Batt, Flow,10VPwr (Thermistor T)
TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb
RH = TRH[0]
Temp = TRH[1]
pSys = TRH[2]
pAmb = TRH[3]

sensors = UWASmod_v1.testSensors(RH, Temp,pSys, pAmb)
#print ('Sensors are OK (1) or not OK (0): ' + str(sensors))
time.sleep(60) #time to get a GPS fix


onOff = 1 #turn pump on
print('Pump on')
PumpStatus = UWASmod_v1.pumpOn(onOff)
time.sleep(6)
gpsData = UWASmod_v1.GPSsetup() #GPS
Sat = float(gpsData[4])
Date = gpsData[0] #Date is hhmmss.ss
BT = UWASmod_v1.readi2cU10(Date)
TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb
onOff = 0 #turn pump off
PumpStatus = UWASmod_v1.pumpOn(onOff)
print('Pump off')

os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_SamplingLog.txt', 'a')
temp_data_file.write('Pump off now' +'\n')
temp_data_file.close()



while True:
        gpsData = UWASmod_v1.GPSsetup() #GPS
        Sat = float(gpsData[4])
        os.chdir('/home/pi/temp/')
        temp_data_file = open('UWAS_SamplingLog.txt', 'a')
        temp_data_file.write('Num of GPS satellites: '+str(Sat)+'\n')
        temp_data_file.close()
        
        if Sat > 6: #
                break
        


BAT = BT[0]
Flow = BT[1]
pSys = TRH[2]
pAmb = TRH[3]
DP = abs(pSys-pAmb)
#print something to file here

if BAT < 3.65:
        os.chdir('/home/pi/temp/')
        temp_data_file = open('UWAS_SamplingLog.txt', 'a')
        temp_data_file.write('Battery Voltage Low (<2/5)!'+'\n')
        temp_data_file.close()
else:
        UWASmod_v1.batteryOK(BAT)
        
print('Psys is: ' + str(pSys))
print('PAmb is: ' + str(pAmb))
print('Flow is: ' + str(Flow))
print('Pressure difference is: ' + str(DP))


if (DP > 2) & (Flow > 0.3):
#if BAT > 3:
                print('Pump test sucessful')
                pumpWorks = 1
                UWASmod_v1.pumpTest(pumpWorks)  
                gpsData = UWASmod_v1.GPSsetup() #GPS

                Lat_init = float(gpsData[1])
                Lon_init = float(gpsData[2])
                Alt_init = float(gpsData[3])
                #Lat_init = input('Input inital Lat: ')
                #Lon_init = input('Input inital Lon: ')
                #Alt_init = input('Input inital Alt: ')
                os.chdir('/home/pi/temp/')
                temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                temp_data_file.write('Pump Test Sucessful!'+'\n')
                temp_data_file.write('Initial Lat, Lon, Altitude (m), Sat : '+str(Lat_init) +','+str(Lon_init)+','+str(Alt_init) +'\n')
                temp_data_file.close()
                                
                
                
                for y in range(len(WPlat)):
                    arr = 0
                    WPlat_curr = WPlat[y]
                    WPlon_curr = WPlon[y]
                    WPalt_curr = WPalt[y]

                    print('WP' + str(y))
                    print('searching Altitude ' + str(WPalt_curr))
                    os.chdir('/home/pi/temp/')
                    temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                    temp_data_file.write('Way Point (WP) :'+str(y+1)+'\n')
                    temp_data_file.close()
                

                
                    for z in range(1200):
                        print('continuous gps, and ADC loop')
                        gpsData = UWASmod_v1.GPSsetup()
                        #lat, lon, alt are all relative...
                        Date = gpsData[0]
                        Lat_curr = float(gpsData[1])
                        Lon_curr = float(gpsData[2])
                        Alt_curr = float(gpsData[3])

                        #Lat_curr = input('Input current Lat: ')
                        #Lon_curr = input('Input current Lon: ')
                        #Alt_curr = input('Input current Alt: ')
                        
                        Dlat = abs(Lat_init + WPlat_curr- Lat_curr)
                        Dlon = abs(Lon_init + WPlon_curr- Lon_curr)
                        Dalt = abs(Alt_init + WPalt_curr- Alt_curr)
                        #how long does this loop take?
                        BT = UWASmod_v1.readi2cU10(Date)
                        TRH = UWASmod_v1.readi2cU9(Date)
                        

                        Match = ((Dlat < 0.5) & (Dlon < 0.5)) & (Dalt < 90)

                        if Match == 1:
                              break
                              

                    onOff = 1 #turn pump on
                    PumpStatus = UWASmod_v1.pumpOn(onOff)
                    #time.sleep(1)

                    os.chdir('/home/pi/temp/')
                    temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                    temp_data_file.write('Pump On- sampling at WP'+'\n')
                    temp_data_file.close()

                    gpsData = UWASmod_v1.GPSsetup()
                    Date = gpsData[0]
                    BT = UWASmod_v1.readi2cU10(Date)
                    TRH = UWASmod_v1.readi2cU9(Date)

                    #Maybe sometimes print these values to main log? otherwise just to files
                    os.chdir('/home/pi/temp/')
                    temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                    temp_data_file.write('WP (&Sat #) start GPS data: ' + Date +','+str(gpsData[1])+','+str(gpsData[2])+','+str(gpsData[3])+','+str(gpsData[4])+'\n')
                    temp_data_file.write('Sample start Batt,Flow,10V:'+str(BT[0])+','+str(BT[1])+','+str(BT[2])+'\n')
                    temp_data_file.write('Sample start RH,T,Psys,Pamb:'+str(TRH[0])+','+str(TRH[1])+','+str(TRH[2])+','+str(TRH[3])+'\n')
                    temp_data_file.close()
                
                    sendTo = 2 #increment position to odd number like pos 1
                    Pos1 = UWASmod_v1.comValco(sendTo)
                    os.chdir('/home/pi/temp/')
                    temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                    temp_data_file.write('Current Valco Position is: '+str(chr(Pos1[0]))+str(chr(Pos1[1]))+'\n')
                    temp_data_file.close()
                    
                    for z in range(15): #~1:30 is this enough flushing time?
                            Winds = UWASmod_v1.comTriMini(Date)
                            #data is be 5Hz; 

                    time.sleep(1)
                    sendTo = 2 #increment past even position...to next can
                    Pos1 = UWASmod_v1.comValco(sendTo)
                    gpsData = UWASmod_v1.GPSsetup()
                    Date = gpsData[0]
                    BT = UWASmod_v1.readi2cU10(Date)
                    TRH = UWASmod_v1.readi2cU9(Date)

                    onOff = 0 #turn pump off
                    PumpStatus = UWASmod_v1.pumpOn(onOff)
                    
                    os.chdir('/home/pi/temp/')
                    temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                    temp_data_file.write('WP end GPS data: ' + Date +','+str(gpsData[1])+','+str(gpsData[2])+','+str(gpsData[3])+'\n')
                    temp_data_file.write('Sample end Batt,Flow,10V:'+str(BT[0])+','+str(BT[1])+','+str(BT[2])+'\n')
                    temp_data_file.write('Sample end RH,T,Psys,Pamb:'+str(TRH[0])+','+str(TRH[1])+','+str(TRH[2])+','+str(TRH[3])+'\n')
                    temp_data_file.write('Current Valco Position is now: '+str(chr(Pos1[0]))+str(chr(Pos1[1]))+'\n')
                    temp_data_file.close()
                    
                    #print('Pump off')
                    time.sleep(6)
                
                os.chdir('/home/pi/temp/')
                temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                temp_data_file.write('All Way Points have been completed'+'\n')
                temp_data_file.close()
        
else:
                #open file and write header
                os.chdir('/home/pi/temp/')
                temp_data_file = open('UWAS_SamplingLog.txt', 'a')
                temp_data_file.write('pSys-pAmb < 2; pump test and data collection aborted'+'\n')
                temp_data_file.close()
    
#runningNow = UWASmod_v1.programRunning(0)
UWASmod_v1.softShudown()
