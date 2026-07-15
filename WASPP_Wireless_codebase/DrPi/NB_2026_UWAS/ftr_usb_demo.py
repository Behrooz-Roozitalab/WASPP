# demo communication with the Adafruit 2040 feather over USB

import serial
import time
import json
from pathlib import Path

from packet_handler import (
    parse_packet,
    handle_command_packet,
    encode_packet,
    make_ack,
)
 
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

def wait_for_serial_port(port):
    while not Path(port).exists():
        print(f"Waiting for serial port: {port}")
        time.sleep(1)


def main():
    
    wait_for_serial_port(SERIAL_PORT)
    print(f"Opening USB serial port {SERIAL_PORT} at {BAUD_RATE} ...")
    print("Waiting for commands...")

    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)

        while True:
            raw = ser.readline()

            if not raw:
                continue

            line = raw.decode("utf-8", errors = "replace").strip()

            if not line:
                continue

            print(f"RX: {line}")

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

            encoded_ack = encode_packet(ack)

            ser.write(encoded_ack)
            ser.flush()

            print(f"TX: {encoded_ack.decode('utf-8').strip()}")

##### Main ########

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
