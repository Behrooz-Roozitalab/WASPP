# Import necessary libraries
import time
import numpy
import os
import sys
import argparse
import csv
import math
from Hdwcom import GPScom, Windcom, RunSignal, Valcocom, ADCcom, Pumpcom, RunSignal
'''
### Getting GPS data ###
gpsData = GPScom.getGPS()
Date, Lat, Lon, Alt, sat = gpsData[0], gpsData[1], gpsData[2], gpsData[3], gpsData[4] # Date format is hhmmss.ss
print('GPS')
print('Date: ' + str(Date) + ', Lat: ' + str(Lat) + ', Lon: ' + str(Lon) + ', Alt: ' + str(Alt) + ', sat: ' + str(sat))
'''

### Communicating with Valco Valve ###
sendTo = 0 # Getting current position
Pos1 = Valcocom.comValco(sendTo)
print('Valco Valve')
print('Current Position: ' + chr(Pos1[0]) + chr(Pos1[1]))


'''
### Testing Battery & Flow (Thermistor) ###
BT = ADCcom.readADC_bat_flow('')
print('Battery & Flow')
print('Battery voltage: ' + str(BT[0]))
print('Flow: ' + str(BT[1]))
print('Pwr10V: ' + str(BT[2]))
'''
'''
### Testing Temp/Humidity/Pressure sensors ###
TRH = ADCcom.readADC_temp_rh_ps_pa('')
RH, Temp, pSys, pAmb = TRH[0], TRH[1], TRH[2], TRH[3]
print('Temp/Humidity/Pressure')
print('RH: ' + str(RH))
print('Temp: ' + str(Temp))
print('pSys: ' + str(pSys))
print('pAmb: ' + str(pAmb))
'''
'''
### Testing pump ###
print('Pump')
onOff = 1
PumpStatus = Pumpcom.pumpOn(onOff)

time.sleep(5)
  
onOff = 0
PumpStatus = Pumpcom.pumpOn(onOff)
'''


'''
wind = Windcom.getWind('')
print(wind)
'''

#RunSignal.blink(5)
