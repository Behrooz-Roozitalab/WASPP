#!/usr/bin/python2

'''
Basic communication functions with GPS device
'''
CODE_FOLDER = '/home/pi/py2prog/'
LOG_FOLDER = '/home/pi/logs/'
LOG_GPS = 'GPS_LOG.txt'

def getGPS():
  import serial
  import time
  import os

  gps = serial.Serial('/dev/ttyAMA0', baudrate=9600)

  #test- trying to set new output rate to 5Hz from (~1 Hz)
  outstr = '$PMTK220,200*2C\r\n'
  gps.flushInput()
  gps.flushOutput()
  gps.write(outstr)
  time.sleep(0.1)

  # Read data
  Date = 'No Date Available'
  for _ in range(8):
    line = gps.readline()
    data = line.split(',')
    if(data[0]=='$GPGGA'):
      # Read line & parse lat, lon, alt, time, fix, satellites, etc ...
      Date, Lat, Lon, Alt, DGeo, Sat = data[1], data[2], data[4], data[9], data[11], data[7]
      
      # Logging
      os.chdir(LOG_FOLDER)
      temp_data_file = open(LOG_GPS, 'a')
      temp_data_file.write(Date+','+Lat+','+Lon+','+Alt+','+DGeo+','+Sat+'\n')
      temp_data_file.close()
      os.chdir(CODE_FOLDER)
  gps.close()

  return (Date,Lat,Lon,Alt,Sat)

 