#!/usr/bin/python2

'''
Basic communication functions with ADC
- Battery & Flow
- RH/Temp/Psys/Pamb
'''

CODE_FOLDER = '/home/pi/py2prog/'
LOG_FOLDER = '/home/pi/logs/'
LOG_ADCBATFLOW = 'ADCBATFLOW_LOG.txt'
LOG_ADC_RH_TEMP_PRESSURE = 'ADC_RH_TEMP_PRESSURE_LOG.txt'

def readADC_bat_flow(Date):
  import os
  import numpy
  import time
  import Adafruit_ADS1x15

  adc = Adafruit_ADS1x15.ADS1115(address=0x49,busnum=1)
  GAIN = 2/3

  values=[0]*4
  
  # read Battery Voltage from ADC channel
  values[0] = adc.read_adc(0, gain=GAIN)
  # Ratio of 15 bit balue to max volts determines the volts
  Ch1volts = values[0]/32767.0*6.144 #battery
  BattVolt = Ch1volts

  # read Flow from ADC channel
  values[1] = adc.read_adc(1, gain=GAIN)
  Ch2volts = values[1]/32767.0*6.144
  Flow = (Ch2volts-1)*0.8

  # read 10V Pwr Volts from ADC channel
  values[2] = adc.read_adc(2, gain=GAIN)
  Ch3volts = values[2]/32767.0*6.144
  Pwr10V = Ch3volts

  os.chdir(LOG_FOLDER)
  temp_data_file = open(LOG_ADCBATFLOW, 'a')
  temp_data_file.write(Date + ',' + str(BattVolt) + ',' + str(Flow) + ',' + str(Pwr10V) + '\n')
  temp_data_file.close()
  os.chdir(CODE_FOLDER)

  return (BattVolt, Flow, Pwr10V)

def readADC_temp_rh_ps_pa(Date):
  import os
  import numpy
  import time
  import datetime
  import Adafruit_ADS1x15 

  adc = Adafruit_ADS1x15.ADS1115(address=0x48,busnum=1)
  GAIN = 1

  values=[0]*4
  
  # Read RH from ADC channel
  values[0] = adc.read_adc(0, gain=GAIN)
  # Ratio of 15 bit balue to max volts determines the volts
  Ch1volts = values[0]/32767.0*4.096
  RH = Ch1volts/2.5*100

  # Read TempC from ADC channel
  values[1] = adc.read_adc(1, gain=GAIN)
  Ch2volts = values[1]/32767.0*4.096
  TempC = (Ch2volts/2.5)*120-40

  # Read Psys from ADC channel
  values[2] = adc.read_adc(2, gain=GAIN)
  PsysV = values[2]/32767.0*4.096
  Psys = (PsysV-0.5)/4*15 # Original Formula: Psys = (PsysV-0.5)/4*50

  # Read Pamb from ADC channel
  values[3] = adc.read_adc(3, gain=GAIN)
  PambV = values[3]/32767.0*4.096
  Pamb = (PambV-0.5)/4*50 # Original formula: Pamb = (PambV-0.5)/4*15
  
  os.chdir(LOG_FOLDER)
  temp_data_file = open(LOG_ADC_RH_TEMP_PRESSURE, 'a')
  temp_data_file.write(Date + ',' + str(RH) + ',' + str(TempC) + ',' + str(Psys) + ',' + str(Pamb) + '\n')
  temp_data_file.close()
  os.chdir(CODE_FOLDER)

  return(RH, TempC, Psys, Pamb)