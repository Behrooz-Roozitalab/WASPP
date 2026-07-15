'''
fills all canisters
'''

# NOTE: GETTING Hdw.status() TAKES ~ 10 SECONDS

import time
import numpy
import os
import sys
import argparse
import csv
import math
from datetime import datetime
from HardwareWrapper import UWASHardware

Hdw = UWASHardware()

def main():
    #Hdw.set_pump(0)
    #return
    pos = Hdw.get_valve_position()
    pos = pos["pos"]
    if pos == 16:
        print("already reset, filling...")
    else:
        while pos != 16:
            next = Hdw.move_valve_next()
            pos = next["result"]
            print(pos)
    Hdw.set_pump(1)
    print("filling")
    next = Hdw.move_valve_next()
    pos = next["result"]
    while pos != 16:
        if pos % 2 == 1:
            time.sleep(10)
        next = Hdw.move_valve_next()
        pos = next["result"]
        print(pos)
    Hdw.set_pump(0)
    print("done")
    return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Hdw.set_pump(0)
        print("\nStopped.")
