#!/usr/bin/python2

'''
Basic communication functions with Pump
'''

def pumpOn(onOff):
  import RPi.GPIO as GPIO
  import time

  if onOff == 1:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)

    GPIO.output(18, GPIO.HIGH)
    PumpStatus = 1
  else:
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)

    GPIO.output(18, GPIO.LOW)
    time.sleep(2)
    GPIO.cleanup()
    PumpStatus = 0

  return PumpStatus