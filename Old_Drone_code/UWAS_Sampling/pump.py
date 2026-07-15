# Import necessary libraries
import time
import numpy
import os
import sys
import argparse
import csv
import math
from Hdwcom import GPScom, Windcom, RunSignal, Valcocom, ADCcom, Pumpcom, RunSignal

onOff = 0
PumpStatus = Pumpcom.pumpOn(onOff)


### Communicating with Valco Valve ###
sendTo = 2 # Getting current position
Pos1 = Valcocom.comValco(sendTo)
print('Valco Valve')
print('Current Position: ' + chr(Pos1[0]) + chr(Pos1[1]))

