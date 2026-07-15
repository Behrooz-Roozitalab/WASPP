#!/usr/bin/python2

from Hdwcom import Valcocom
import time

for _ in range(16):
  sendTo = 0
  Pos1 = Valcocom.comValco(sendTo)
  print('Current: ' + chr(Pos1[0]) + chr(Pos1[1]))
  sendTo = 2
  Pos1 = Valcocom.comValco(sendTo)
  print('Next: ' + chr(Pos1[0]) + chr(Pos1[1]))
  time.sleep(2)
  