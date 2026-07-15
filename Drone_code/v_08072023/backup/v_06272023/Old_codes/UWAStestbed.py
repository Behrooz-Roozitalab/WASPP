#call functions from UWASmod.py
import UWASmod_v1
import time
import numpy
import os

#put in the waypoints for the flight plan HERE! First waypoint is NCAR...
#4002.2646,N,10514.5812,W,1574.3 (Alt m)...for lat lon deg-min-decmin format
#WPlat = [4002.2, 47.5, 48, 49]
#WPlon = [10514.58, 211.05, 208, 209, 210]
#WPalt = [1638, 50, 50, 100, 400]
#TEST THE SENSORS...
gpsData = UWASmod_v1.GPSsetup() #GPS
#print (gpsData)
#lat and lon are degdegminmin.fractmin
Date = gpsData[0]
runningNow = UWASmod_v1.programRunning(1) #set up GPIOs

os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_SamplingLog.txt', 'a')
temp_data_file.write('UTC Time: '+str(Date)+'\n')
temp_data_file.close()
                
#print(Date)
#Date is hhmmss.ss

y=0
#WPlat_curr = WPlat[y]
#WPlon_curr = WPlon[y]
#WPalt_curr = WPalt[y]

#if GPS string is mostly empty '','' then you don't have a fix
#if gpsData[2]:
 #   Dlat = abs(WPlat_curr-float(gpsData[1]))
 #   Dlon = abs(WPlon_curr-float(gpsData[2]))
 #   Dalt = abs(WPalt_curr-float(gpsData[3]))

 #   Match = ((Dlat < 0.08) & (Dlon < 0.08)) & (Dalt < 5)
 #   print (Match)

#Data_chk = UWASmod_v1.comTriMini(Date) #Winds
#print (Data_chk)
onOff = 1 #turn pump on
#PumpStatus = UWASmod_v1.pumpOn(onOff)

for x in range(1):

    sendTo = 0 #advance to next position (e.g. 16 to 1)
    Pos1 = UWASmod_v1.comValco(sendTo)#Comm with Valco Valve

    os.chdir('/home/pi/temp/')
    temp_data_file = open('UWAS_SamplingLog.txt', 'a')
    temp_data_file.write('Valco Position is: '+str(chr(Pos1[0])) + str(chr(Pos1[1])) +'\n')
    temp_data_file.close()

    onOff = 0 #turn pump off
    PumpStatus = UWASmod_v1.pumpOn(onOff)
    time.sleep(6)
    
    onOff = 1 #turn pump on
    #PumpStatus = UWASmod_v1.pumpOn(onOff)
    
    print(chr(Pos1[0]) + chr(Pos1[1]))
    for y in range(5):
        #loop and run pump to fill cans for 10 min
        gpsData = UWASmod_v1.GPSsetup() #GPS
        Date = gpsData[0]
        BT = UWASmod_v1.readi2cU10(Date)#ADC of Batt, Flow,10VPwr (Thermistor T)
        print(BT)
        TRH = UWASmod_v1.readi2cU9(Date)#ADC of RH, T, Psys, Pamb
        print(TRH)
        time.sleep(0.5)

    os.chdir('/home/pi/temp/')
    temp_data_file = open('UWAS_SamplingLog.txt', 'a')
    temp_data_file.write('Sample 1 Batt,Flow,10V:'+str(BT[0])+','+str(BT[1])+','+str(BT[2])+'\n')
    temp_data_file.write('Sample 1 RH,T,Psys,Pamb:'+str(TRH[0])+','+str(TRH[1])+','+str(TRH[2])+','+str(TRH[3])+'\n')
    temp_data_file.close()
    
    #sendTo = 2 #advance to next position (e.g. 16 to 1)
    #Pos1 = UWASmod_v1.comValco(sendTo)#Comm with Valco Valve
    #print(chr(Pos1[0]) + chr(Pos1[1]))
    #time.sleep(4)

onOff = 0 #turn pump off
PumpStatus = UWASmod_v1.pumpOn(onOff)

    

#RH = TRH[0]
#Temp = TRH[1]
#pSys = TRH[2]
#pAmb = TRH[3]

#sensors = UWASmod_v1.testSensors(RH, Temp,pSys, pAmb)
#print(sensors)

#DP = UWASmod_v1.testSysPress(pSys, pAmb)
#print(DP)
runningNow = UWASmod_v1.programRunning(0)
UWASmod_v1.softShutdown()
