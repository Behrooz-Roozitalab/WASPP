#!/usr/bin/python3
#this script is a GPIO input program
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM) #uses GPIO signal number
#GPIO.setmode(GPIO.BOARD) uses the board pin number
GPIO.setup(18,GPIO.OUT)

GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(25,GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.output(18,GPIO.LOW) #signal 0 or 1 in GPIO (ON or OFF)

try:
    while True:
        if(GPIO.input(24) == GPIO.LOW):
            print("Back Door")
            GPIO.output(18,GPIO.HIGH)
        elif(GPIO.input(25) == GPIO.HIGH):
            print("Front Door")
            GPIO.output(18,GPIO.LOW)
        else:
            GPIO.output(18, GPIO.LOW)
            time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
print("End of Test")
