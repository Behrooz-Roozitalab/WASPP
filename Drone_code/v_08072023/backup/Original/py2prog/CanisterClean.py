#!/usr/bin/python2
#clean valve

#call functions from UWASmod.py
import UWASmod_v1
import time
import numpy

sendTo = 0 #Make this send to position 16
Pos1 = UWASmod_v1.comValco(sendTo)#Comm with Valco Valve
Position1= chr(Pos1[0]) + chr(Pos1[1])
print(Pos1)

for x in range(16):

    Position = int(float(Position1))
                   
    if (Position%2 == 1):
        time.sleep(360)
        sendTo = 2 #increment position
        Pos1 = UWASmod_v1.comValco(sendTo)
        Position1= chr(Pos1[0]) + chr(Pos1[1])
        print(Position1)
        
    else:
        time.sleep(30) #clean tubes only for less long...
        sendTo = 2 #increment position
        Pos1 = UWASmod_v1.comValco(sendTo)
        Position1= chr(Pos1[0]) + chr(Pos1[1])
        print(Position1)
        
