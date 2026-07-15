#!/usr/bin/python3
import UWASmod_v2
import datetime
import time
import numpy
import os

#set Date and time based on UTC local date and time of Lab computer...
#UWASmod_v2.setDate()

#GUI menu choose to read System Pressure, Amb Pressure, Amb T, Amb RH
os.chdir('/home/pi/temp/')
temp_data_file = open('UWAS_Cal.txt', 'a')
temp_data_file.write('Datetime, Psys, raw Psys V, Pamb, raw PambV '+'\n')
temp_data_file.close()

try:
   while True:
          #button in GUI enabled, read ADC and print to file...
          now = datetime.datetime.now()
          print(now)
          TRH = UWASmod_v2.readi2cU9()#ADC of RH, T, Psys, Pamb

          RH = TRH[0]
          Temp = TRH[1]
          pSys = TRH[2]
          pAmb = TRH[3]

          pS = pSys*6.89476 #convert to kPa
          pA = pAmb*6.89476 #convert to kPa
           
          RH_rawV = RH/100*2.5
          T_rawV = (Temp + 40)/120*2.5
          Ps_rawV = pSys/50*4+0.5
          Pa_rawV = pAmb/15*4+0.5

          print('Pamb kPa: ' + str(pA))



          now = datetime.datetime.now()
          os.chdir('/home/pi/temp/')
          temp_data_file = open('UWAS_Cal.txt', 'a')
          temp_data_file.write(str(now)+','+str(pS)+','+str(Ps_rawV)+','+str(pA)+','+str(Pa_rawV)+'\n')
          temp_data_file.close()

          time.sleep(0.5)

except(KeyboardInterrupt, SystemExit): #press cntrl + C
        print "\nQuiting Program..."


