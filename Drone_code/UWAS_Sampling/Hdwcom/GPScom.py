#!/usr/bin/python2

'''
Basic communication functions with GPS device
'''
def getGPS():
  import serial
  import time
  import os
  import codecs

  gps = serial.Serial('/dev/ttyAMA0', baudrate=9600)

  #test- trying to set new output rate to 5Hz from (~1 Hz)
  outstr = '$PMTK220,200*2C\r\n'
  gps.flushInput()
  gps.flushOutput()
  gps.write(outstr.encode())
  time.sleep(0.1)

  # Read data
  Date = 'No Date Available'
  for _ in range(8):
    line = gps.readline()
    line = str(line)[2:-5]
    data = line.split(',')
    if(data[0]=='$GPGGA'):
      # Read line & parse lat, lon, alt, time, fix, satellites, etc ...
      Date, Lat, Lon, Alt, DGeo, Sat = data[1], data[2], data[4], data[9], data[11], data[7]
  gps.close()

  return (Date,Lat,Lon,Alt,Sat)

 
