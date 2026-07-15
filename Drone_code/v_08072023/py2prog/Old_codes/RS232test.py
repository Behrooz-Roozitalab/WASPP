import serial
import os
import time

tri = serial.Serial('/dev/ttyUSB0',
                    baudrate = 115200,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout=1)

data = tri.readline()
print(data)
data = tri.readline()
print(data)
data = tri.readline()
print(data)
data = tri.readline()
print(data)
