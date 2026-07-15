#!/usr/bin/python3
#This is my first Robotics Python Script!

#import modules
import os
import math
from fractions import Fraction
import numpy
import calendar
import datetime
import time

print("Booting up.\n...Pump will start when 30m altitude is reached.")


#pick number of samples (no more than 15)
sample_no = 16

while sample_no >= 16:
    sample_no_str = input("How many UWASS samples do you need this flight?  ")
    sample_no_tmp = sample_no_str.lstrip(' ')
    sample_no = int(sample_no_tmp)
        
    if (sample_no >= 16):
        print("The UWASS cannot take more than 15 samples at a time.")

for the_number in range(sample_no):
    print("The UWASS has collected", the_number+1, "sample(s) so far")
    os.chdir('/home/pi/temp/')
    temp_data_file = open('SampleLog.txt', 'a')
    dtnow = datetime.datetime.now()
    temp_data = str(the_number) + ',' + str(dtnow) + '\n'
    temp_data_file.write(temp_data)
    temp_data_file.close()
    time.sleep(5) #five second delay
    os.chdir('/home/pi/py3prog/')

#Py basic math is capable of binary numbers 
a = 0b01001101
bin(a)

#can use fraction module to use fractions
fract_a = Fraction(1,5)
print("you can print a fraction", fract_a)

