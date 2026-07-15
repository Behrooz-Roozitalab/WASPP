#! /usr/bin/python2
#I2C test
import os
import numpy
from time import sleep
#from Adafruit_CharLCD import Adafruit_CharLCD
#lcd = Adafruit_CharLCD(rs=25,en=24,d4=23,d5=18,d6=15,d7=14,
#                     cols=16,lines=2)

import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115(address=0x48,busnum=1)

#Gain = 2/3 for reading voltages from 0 - 6.144V
#Gain = 1 for reading voltages from 0 - 4.096V
#See table 3 in ADS1115 datasheet

GAIN = 1
        
#Main LOOP
try:
    #open file and write header
    os.chdir('/home/pi/temp/')
    temp_data_file = open('T&Hlog.txt', 'a')
    #temp_data_file.write('Ch1 V, Ch1 Bits'+'\n')
    temp_data_file.write('Ch1 V, RH(%), Ch2 V, Temp (C)'+'\n')
    temp_data_file.close()
    os.chdir('/home/pi/py2prog/')

    while 1:
        values=[0]*2
        #read ADC channel 0 as Humidity (0 - 100%)
        values[0] = adc.read_adc(0,gain=GAIN)
        print ('Value', values[0])
        #Ratio of 15 bit balue to max volts determines the volts
        Ch1volts = values[0]/32767.0*4.096 #battery
        print ('Ch1 Volts  ', Ch1volts)
        TempC = (Ch1volts/2.5)*120-40
        print ('TempC ', TempC)

        #print values[0]
        values[1] = adc.read_adc(1,gain=GAIN)
        Ch2volts = values[1]/32767.0*4.096
        print ('CH2 Volts  ', Ch2volts)
        RH = Ch2volts/2.5*100
        print ('RH (%) ', RH)

        os.chdir('/home/pi/temp/')
        temp_data_file = open('T&Hlog.txt', 'a')
        #temp_data_file.write(str(Ch1volts) +','+ str(values[0])+'\n')
        temp_data_file.write(str(Ch1volts) +','+ str(TempC) +','+ str(Ch2volts) +','+ str(RH)+'\n')
        temp_data_file.close()
        os.chdir('/home/pi/py2prog/')

    
        #lcd.clear()
        #lcd.message("{0.03f}V[{1}]".format(volts, value[0]))
        #lcd.message("\n{0.0f} psi {1:0.1f} bar".format(psi,bar))

        sleep(3)

except(KeyboardInterrupt, SystemExit): #press
    print ("Hasta Luego")
