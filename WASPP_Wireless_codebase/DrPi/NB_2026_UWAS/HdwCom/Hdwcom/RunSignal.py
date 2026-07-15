#!/usr/bin/python2

'''
Signaling that the program is running
'''
def testSensors(RH, Temp, pSys, pAmb, BT):
  import RPi.GPIO as GPIO
  import time

  # Output: [pSysTest, pAmbTest, TempTest, RHTest, BTTest, ComTest, Overall]
  # sensors[0]: 0 - pass, 1 - pSys < 8
  # sensors[1]: 0 - pass, 2 - pAmb < 8
  # sensors[2]: 0 - pass, 3 - Temp < -5
  # sensors[3]: 0 - pass, 4 - RH < 2
  # sensors[4]: 0 - pass, 5 - BT < 3.65
  # sensors[5]: 0 - pass, 6 - abs(pSys-pAmb) < 1 
  # sensors[6]: 0 - All pass, 1 - At least one test fails

  sensors = []
  flag = 0

  # Check pSys
  if pSys < 8:
    sensors.append(1)
    flag = 1
  else:
    sensors.append(0)
  
  # Check pAmb
  if pAmb < 8:
    sensors.append(1)
    flag = 1
  else:
    sensors.append(0)

  # Check Temp
  if Temp < -5:
    sensors.append(1)
    flag = 1
  else:
    sensors.append(0)
  
  # Check RH
  if RH < 2:
    sensors.append(1)
    flag = 1
  else:
    sensors.append(0)

  # Check BT
  if BT < 3.65:
    sensors.append(1)
    flag = 1
  else:
    sensors.append(0)

  # Check pSys vs pAmb
  if abs(pSys-pAmb) > 1:
    sensors.append(1)
    flag = 1
  else:
    sensors.append(0)
  
  # Overall
  if flag == 1:
    sensors.append(1)

    # Send signal for battery
    if sensors[4] == 0:
      # D4
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(27, GPIO.OUT)
      GPIO.output(27, GPIO.HIGH)
      time.sleep(3)
      GPIO.output(27, GPIO.LOW)
      GPIO.cleanup()

  else:
    sensors.append(0)

    # Send signal for battery
    if sensors[4] == 0:
      # D4
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(27, GPIO.OUT)
      GPIO.output(27, GPIO.HIGH)
      time.sleep(3)
      GPIO.output(27, GPIO.LOW)
      GPIO.cleanup()
    
    # Send signal for other sensors
    # D6
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(23, GPIO.LOW)
    GPIO.cleanup()
  
  return sensors
  
def pumpTestSig(pumpWorks):
  import RPi.GPIO as GPIO
  import time
  
  # D7
  if pumpWorks==1:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.output(24, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(24, GPIO.LOW)
    GPIO.cleanup()

def programRunning(Run):
  import RPi.GPIO as GPIO
  import time
  
  # prior to pump test, system pressure and ambient pressure should be equal
  # if its over some value (no pump on) pressure is NOT Ok (0)
  if Run > 0:
    runningNow = 1
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(22, GPIO.LOW)
    GPIO.cleanup()
  else:
    runningNow = 0
    GPIO.setmode(GPIO.GCM)
    GPIO.setup(22, GPIO.OUT)
    GPIO.output(22, GPIO.LOW)
    GPIO.cleanup()

  return runningNow

def blink(no):
  import RPi.GPIO as GPIO
  import time
  
  ledpins = [22,24,27,23]
  
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(ledpins, GPIO.OUT)
  for _ in range(no):
    GPIO.output(ledpins, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(ledpins, GPIO.LOW)
    time.sleep(0.5)
    
  GPIO.cleanup()