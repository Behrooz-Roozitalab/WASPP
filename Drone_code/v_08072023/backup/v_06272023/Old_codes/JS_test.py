import UWASmod_v1
import time
import os
import JS_functions as JS

gpsData = UWASmod_v1.GPSsetup()
print('Testing GPS data')
print('GPS data: ' + str(gpsData))
print('')
#time.sleep(2)

Date = gpsData[0] 
BT = UWASmod_v1.readi2cU10(Date)
print('Testing Battery checking')
print('BT: ' + str(BT))
print('')

TRH = UWASmod_v1.readi2cU9(Date)
print('Testing Temperature sensor')
print('TRH: ' + str(TRH))
print('')

Data_chk = UWASmod_v1.comTriMini(Date)
print('Testing Wind sensor')
print('Wind: ' + str(Data_chk))
print('')

runningNow = UWASmod_v1.programRunning(1)
print('Testing programRunning function')
print('runningNow: ' + str(runningNow))
print('')

sendTo=0
print('Testing communicating with Valco (Getting current position)')
Pos1 = UWASmod_v1.comValco(sendTo)
print('Position: ' + chr(Pos1[0]) + chr(Pos1[1]))
print('')

print('Testing pump on')
PumpStatus = UWASmod_v1.pumpOn(1)
print('Current PumpStatus: ' + str(PumpStatus))
time.sleep(5)
print('Testing pump off')
PumpStatus = UWASmod_v1.pumpOn(0)
print('Current PumpStatus: ' + str(PumpStatus))
print('')

sendTo=2
print('Testing communicating with Valco (Moving position)')
Pos1 = UWASmod_v1.comValco(sendTo)
print('Position: ' + chr(Pos1[0]) + chr(Pos1[1]))
print('')

sendTo=2
print('Testing communicating with Valco (Moving position)')
Pos1 = UWASmod_v1.comValco(sendTo)
print('Position: ' + chr(Pos1[0]) + chr(Pos1[1]))
print('End of testing')