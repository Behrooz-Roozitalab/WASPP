#!/usr/bin/python3
#This script enables hardware GPIO controls

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM) #uses GPIO signal number
#GPIO.setmode(GPIO.BOARD) uses the board pin number

##creating a simple output signal
GPIO.setup(18,GPIO.OUT)
GPIO.output(18,GPIO.LOW) #signal 0 or 1 in GPIO (ON or OFF)

#set up inputs
GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(25,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def backdoor(channel):
    GPIO.output(18,GPIO.HIGH)
    print("Back Door")
    time.sleep(0.1)
    GPIO.output(18,GPIO.LOW)

def frontdoor(channel):
    GPIO.output(18,GPIO.HIGH)
    print("Front Door")
    GPIO.output(18,GPIO.LOW)

GPIO.add_event_detect(24,GPIO.FALLING, callback=backdoor)
GPIO.add_event_detect(25,GPIO.FALLING, callback=frontdoor)

try:
    while True:
        pass
except KeyboardInterrupt:
    
#return GPIO ports to neutral setting
    GPIO.cleanup()
print("End of program.")
