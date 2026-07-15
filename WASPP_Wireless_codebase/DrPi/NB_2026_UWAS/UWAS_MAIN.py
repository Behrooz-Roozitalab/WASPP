'''
UWAS Main Program
- remotely take samples and view telemetry via Pi3 base station
- Adafruit RP2040 feather LoRa relay/sensor array (USB)
- Pi 3 B with LoRa/OLED bonnet for UI
- USES OLD Hdwcom PCB CODE > check Hdwcom folder
- look at HardwareWrapper.py for wrapped hardware commands
- Output files:
    packet_log.jsonl
    local_log.txt
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

# Network Stuff
import serial
import json
from pathlib import Path

from packet_handler import (
    parse_packet,
    handle_command_packet,
    encode_packet,
    make_ack,
    make_status_packet,
)

# ____ TEST FLAG ____
# if active...
# -will not reset valves on start
# -Will not move valve on sample
# -only pumps for like 5 seconds
# (frequently edited for testing)

TEST = False

#____________________


status = {
    "date": "--",
    "lat": "--",
    "lon": "--",
    "alt": "--",
    "sat": "--",
    "pump": "--",
    "run": "--",    #actively sampling sampling? (running)
    "samp": 0,      #number of samples taken
    "pos": "--",    #valve position
    "pS": "--",     #pressure of the system (between valve outlet and poppit valve)
    "pA": "--",     #ambient pressure (top of drone)
    "BV": "--",     #sampler battery voltage
    "flow": "--",   #flow sensor (exhaust)
    "pwr": "--",    #power
}
# - Serial com - #
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

sampling = False
samples = 0

# - Logging: saves information to .jsonl files -

LOCAL_LOG = Path("local_log.jsonl")
PACKET_LOG = Path("packet_log.jsonl")

def log_local(message=""):

    time = datetime.now().isoformat(timespec="seconds")

    try:
        with LOCAL_LOG.open("a", encoding="utf-8") as f:
            f.write(time + " | " + message + "\n")
    except Exception as e:
        print(f"[log error] {e}")

def log_packet(direction, packet, note=""):
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "direction": direction,
        "note": note,
        "packet": packet
    }
    try:
        with PACKET_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry,default=str) + "\n")
    except Exception as e:
        print(f"[log error] {e}")

# - waits for serial connection with feather -
def wait_for_serial_port(port):
    while not Path(port).exists():
        print(f"Waiting for serial port: {port}")
        time.sleep(1)


##------------Main Hardware Stuff---------------##
# - resets valve position to 16 to prepare for sampling -
def reset_valve():
    pos = Hdw.get_valve_position()
    pos = pos["pos"]
    log_local(f"VALVE RESETTING TO pos 16... FROM {pos}")
    if pos == 16:
        return
    else:
        while pos != 16:
            next = Hdw.move_valve_next()
            pos = next["result"]
            print(pos)
    log_loca("VALVE RESET")
    return pos

def sample_test(ser):
    '''
    Test sample function.
    - edited frequently to test specific functions
      without altering main sample function
    '''
    global sampling
    global samples
    
    log_local("Starting Test Sample...")

    Pump_ON = Hdw.set_pump(1)
    sampling = True

#    pre_stats = Hdw.get_status()
 #   stat_packet = make_status_packet(sampling, samples, pre_stats, "sample test!")
  #  send_status(ser,stat_packet)


    Valve_Pos = Hdw.move_valve_next()
#    time.sleep(5)
#    Valve_Pos = Hdw.move_valve_next()
#    Pump_ON = Hdw.set_pump(0)
#    post_stats = Hdw.get_status()
    sampling = False
    samples += 1
 #   stat_packet = make_status_packet(sampling, samples, post_stats, "Finished!")
#    send_status(ser,stat_packet)
    log_local("finished test sample sequence")
def sample_sequence(ser):
    '''
    Im trying to copy the original sampling sequence with this function
    so that I can call it when the command is received.
    - RECORD initial DrPi sensors and update STATUS packet before sampling
    - Valve should already be in EVEN (empty) canister slot
    - PUMP ON
    - MOVE VALVE to next slot (odd canister to be filled)
    - Flush for 30 seconds
    - MOVE VALVE to next slot (finished filling, moving to empty slot)
    - PUMP OFF
    - UPDATE and save post-sample sensor info
    '''
    global sampling
    global samples
    global status
      
    log_local("Beginning Sample {status[samp]}...")
    Pump_ON = Hdw.set_pump(1)
    sampling = True

    pre_stats = Hdw.get_status()
    stat_packet = make_status_packet(sampling, samples, pre_stats, "SAMPLING!")
    send_status(ser,stat_packet)
    log_local(f"Pre-sampling Status packet: {stat_packet}")
    Valve_Pos = Hdw.move_valve_next()

    samp_stat_A = Hdw.get_status()
    stat_packet = make_status_packet(sampling, samples, samp_stat_A, "Samp-stat A...")
    send_status(ser,stat_packet)
    
    samp_stat_B = Hdw.get_status()
    stat_packet = make_status_packet(sampling, samples, samp_stat_A, "Samp-stat B...")
    send_status(ser,stat_packet)
    
    Valve_Pos = Hdw.move_valve_next()
    Pump_ON = Hdw.set_pump(0)
    post_stats = Hdw.get_status()
    sampling = False
    samples += 1
    stat_packet = make_status_packet(sampling, samples, post_stats, "Finished!")
    send_status(ser,stat_packet)
    
def send_status(ser, complete_packet):
    '''
    sends status packet to base station
    '''

    encoded_stat_pkt = encode_packet(complete_packet)
    print(f"TX: {encoded_stat_pkt.decode('utf-8').strip()}")
    ser.write(encoded_stat_pkt)
    ser.flush()
    log_packet("TX", complete_packet, "Status Sent")
def main():
    global sampling
    global status
    wait_for_serial_port(SERIAL_PORT)
    print(f"Opening Serial port...")
    print("waiting for commands...")
    last_status = {}

    # begin serial com with feather
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)
        print(ser.is_open)
        # ENSURE VALVE IS AT 16 PRIOR TO STARTING #
        valve_pos = Hdw.get_valve_position()
        status["pos"] = valve_pos

        if TEST == True:
            pkt = make_status_packet(sampling, samples, status, "TEST MODE")
            send_status(ser, pkt)
        else:
            if valve_pos != 16:
                pkt = make_status_packet(sampling, samples, status, "RESETTING VALVE")
                send_status(ser, pkt)
                reset_pos = reset_valve()
                status["pos"] = reset_pos
                pkt = make_status_packet(sampling, samples, status, "Valve Reset.")
                send_status(ser, pkt)

        # --- begin main loop ---#

        while True:

            # - get json packets, ignore everything else - #
            raw = ser.readline()
    
            if not raw:
                continue
            line = raw.decode("utf-8", errors = "replace").strip()
            
            if not line:
                continue
        
            print(f"RX: {line}")
            log_packet("RX", line, "Packet Recived")
            
            # - handle received packet - 
            try:
                packet = json.loads(line)
                ack = handle_command_packet(packet)

            except ValueError as exc:
                ack = make_ack(
                    seq=None,
                    cmd=None,
                    ok=False,
                    msg=str(exc),
                )
            log_packet("TX", ack, "Ack Sent")            
            encoded_ack = encode_packet(ack)

            # return ack packet for each received packet
            ser.write(encoded_ack)
            ser.flush()

            # if ack status is ok, handle the command
            if ack["ok"]:

                if ack["cmd"] == "take_sample":
                    if TEST == False:
                        sample_sequence(ser)
                    else:
                        sample_test(ser)
                # get status and send stat packet
                if ack["cmd"] == "status":
                    last_status.update(Hdw.get_status())
                    stat_packet = make_status_packet(sampling, samples, last_status, "Hello from Drone!")
                    send_status(ser, stat_packet)
            print(f"TX: {encoded_ack.decode('utf-8').strip()}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Hdw.set_pump(0)
        print("\nStopped.")
