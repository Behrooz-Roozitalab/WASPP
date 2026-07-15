#!/usr/bin/python2

# Import necessary libraries
import UWASmod_v1
import time
import numpy
import os

TRH = UWASmod_v1.readi2cU9('')
RH, Temp, pSys, pAmb = TRH[0], TRH[1], TRH[2], TRH[3]
print('RH: ' + str(RH))
print('Temp: ' + str(Temp))
print('pSys: ' + str(pSys))
print('pAmb: ' + str(pAmb))
