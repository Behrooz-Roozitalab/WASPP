#! /usr/bin/python2
# GPS hat script to import, parse data and save it to file

import os
import numpy
from gps import *
from time import *
import time
import threading

gpsd = None #setting the global variable

os.system('clear') #clear the terminal

class GPSPoller(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd
        gpsd = gps(mode=WATCH_ENABLE) #starting stream of info
        self.current_value = None
        self.running = True #setting thread running to true (continue)

    def run(self):
        global gpsd
        while gpsp.running:
           gpsd.next () #this will continue to loop and grap EACH set of gpsd info

if __name__ == '__main__':
    gpsp = GPSPoller() #create the thread
    try:
        os.chdir('/home/pi/temp/')
        temp_data_file = open('GPSlog.txt', 'a')
        temp_data_file.write('UTC, Latitude, Longitude, Altitude'+'\n')
        temp_data_file.close()
        os.chdir('/home/pi/py2prog/')
        gpsp.start()
        while True:
        #It may take a second to get good data

            
            os.chdir('/home/pi/temp/')
            temp_data_file = open('GPSlog.txt', 'a')
            temp_data_file.write(str(gpsd.utc) +','+ str(gpsd.fix.latitude) +','+ str(gpsd.fix.longitude) +','+ str(gpsd.fix.altitude)+'\n')
            temp_data_file.close()
            os.chdir('/home/pi/py2prog/')


            os.system('clear')
            print 'GPS reading'
            print '---------------------------'
            print 'latitude     ' , gpsd.fix.latitude
            print 'longitude    ' , gpsd.fix.longitude
            print 'time utc     ' , gpsd.utc, '+ ', gpsd.fix.time
            print 'altitude (m) ' , gpsd.fix.altitude
            print 'sat          ' , gpsd.satellites

            time.sleep(3) #seconds

    except(KeyboardInterrupt, SystemExit): #press cntrl + C
            print "\nKilling Thread..."
            gpsp.running = False
            gpsp.join() #wait for the thread to finish what it's doing

    print "Done. \n Exiting"

