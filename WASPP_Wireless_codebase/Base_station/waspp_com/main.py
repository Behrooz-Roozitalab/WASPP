'''
 ----------- Drone Pi <---> Feather < - - - > Base Station Pi ------------
                    (USB)           (LoRa)

 -------------- Full Network configuration (works with WAS) ---------------
 --- Sends sensor data from feather on request and displays on OLED UI ---
 --- Sends commands from BS through FTR to DrPi, HANDLES COMMANDS LIVE ---
 ------------ Nathan Bartley - NSF NCAR-UCAR CISL Intern 2026 ------------
      Note: due to delays in the HDWCom scripts on the DrPi, there is
            some latency when receiving status from the DrPi, but
            commands send and trigger in less than a second of being received
'''

import time
import board
import busio
import digitalio
import adafruit_rfm9x
import adafruit_ssd1306
import json
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from pathlib import Path

############# PACKET SETUP !! SUPER IMPORTANT !! #################

SYS_ID = "demo"
BASE_ID = "BS"
FEATHER_ID = "FTR"
DRONEPI_ID = "DrPi"

ACK_TIMEOUT_S = 5

seq = 0

waiting_for_ack = False
waiting_seq = None
waiting_cmd = None
ack_deadline = 0

live_mode = False

sensor_page = 0
status_page = 0

status_mode = False

num_sensor_pages = 3
num_status_pages = 4

latest_sensor = {
    "id": "--",
    "ms": "--",
    "tmp117_c": "--",
    "bme_t": "--",
    "bme_rh": "--",
    "bme_p": "--",
    "bme_g": "--",
    "uvs": "--",
    "als": "--",
    "rssi": "--",
    "pm25": "--",
}
latest_status = {
    "msg": "--",
    "date": "--",
    "lat": "--",
    "lon": "--",
    "alt": "--",
    "sat": "--",
    "pump": "--",
    "pos": "--",
    "run": "--",    # running sampling sequence
    "samp": "--",   # number of samples taken
    "pS": "--",
    "pA": "--",
    "BV": "--",
    "flow": "--",
    "pwr": "--",
}
def make_cmd_pkt(to,seq,cmd):  # Commands: "take_sample", "status"
    return {
        "sys": SYS_ID,
        "t": "CMD",            #packet type
        "sid": BASE_ID,        #from
        "to": to,	      #destination
        "seq": seq,            # sequence ID (so commands arent repeated)       
        "cmd": cmd,            # command: sample or status
    }               

def is_demo_pkt(pkt):
    return pkt.get("sys") == SYS_ID

def packet_type(pkt):
    return pkt.get("t", "")

def packet_seq(pkt):
    return pkt.get("seq")

################## Oled stuff #############################
 
i2c = busio.I2C(board.SCL, board.SDA)
display_reset = DigitalInOut(board.D4)

display = adafruit_ssd1306.SSD1306_I2C(
    128,    #OLED object W
    32,     #OLED object H
    i2c,    #OLED communication bus pins 
    reset=display_reset #sets reset pin
)

font = ImageFont.load_default()

def clear_display():
    display.fill(0)
    display.show()

def shutdown_display():
    draw_screen(
        "Demo stopping...",
        "Goodbye . . .",
	"-------------",
    )
    time.sleep(5)
    clear_display()

def draw_screen(line1="", line2="", line3=""): # add line 4 if it works
    image = Image.new("1", (128, 32)) # creates a binary blank 128 by 32 canvas
    draw = ImageDraw.Draw(image) # object to write to the canvas

    draw.text((0,0), str(line1)[:21], font=font, fill = 255) # 255 for for crosscompatibility with grayscale. 1 also works
    draw.text((0,10), str(line2)[:21], font=font, fill = 255)
    draw.text((0,20), str(line3)[:21], font=font, fill = 255)
   # draw.text((0,24), str(line4)[:21], font=font, fill = 255)
    
    display.image(image)
    display.show()

def print_idle():
    draw_screen(
        "A: | Sample  |",
        "B: | Status  |",
        "C: | Sensors |"
    )

def draw_sensor_page():
    time = get_time()
    if sensor_page == 0:
        draw_screen(
            f"FTR sens. (1/3) {time}",
            f"BME_g: {fmt(latest_sensor['bme_g'])}",
            f"BME_t: {fmt(latest_sensor['bme_t'])}C"
        )

    elif sensor_page == 1:
        draw_screen(
            f"FTR sens. (2/3) {time}",
            f"RH: {fmt(latest_sensor['bme_rh'])}%",
            f"PM2.5: {fmt(latest_sensor['pm25'])}ug/m3"
        )

    elif sensor_page == 2:
        draw_screen(
            f"FTR sens. (3/3) {time}",
            f"UV: {latest_sensor['uvs']}",
            f"ALS: {latest_sensor['als']}"
        )
def draw_status_page():
    time = get_time()

    if status_page == 0:
        draw_screen(
            f"(1/4) SAMPLING: {latest_status.get('run', '--')}",
            f"msg: {latest_status.get('msg', '--')}",
            f"samp:{latest_status.get('samp', '--')} pump:{latest_status.get('pump', '--')}"
        )

    elif status_page == 1:
        draw_screen(
            f"(2/4) GPS | {latest_status.get('date', '--')}",
            f"Sat:{latest_status.get('sat', '--')} | A:{latest_status.get('alt', '--')}",
            f"La:{latest_status.get('lat', '--')} | Lo:{latest_status.get('lon', '--')}"
        )

    elif status_page == 2:
        draw_screen(
            f"Valve/P (3/4) {time}",
            f"Vpos:{latest_status.get('pos', '--')}",
            f"pS:{latest_status.get('pS', '--')} pA:{latest_status.get('pA', '--')}"
        )

    elif status_page == 3:
        draw_screen(
            f"Power (4/4) {time}",
            f"BV:{latest_status.get('BV', '--')}",
            f"flow:{latest_status.get('flow', '--')} pwr:{latest_status.get('pwr', '--')}"
        )
################# Buttons ##################

button_a = DigitalInOut(board.D5)
button_a.direction = Direction.INPUT
button_a.pull = Pull.UP

button_b = DigitalInOut(board.D6)
button_b.direction = Direction.INPUT
button_b.pull = Pull.UP

button_c = DigitalInOut(board.D12)
button_c.direction = Direction.INPUT
button_c.pull = Pull.UP

    #Debounce stuff

BUTTON_DEBOUNCE_S = .5

last_press_time = {
    "A": 0,
    "B": 0,
    "C": 0,
}

def b_a(name): # button_allowed
    now = time.monotonic()

    if now -last_press_time[name] >= BUTTON_DEBOUNCE_S:
        last_press_time[name] = now
        return True

    return False

def handle_c_button():
    global live_mode, sensor_page

    if not live_mode:
        print("Starting live sensor mode")
        cmd, seq_num = send_command("live_start")
        draw_screen("LIVE START", f"CMD: {cmd}", f"SEQ: {seq_num}")
        return

    sensor_page = (sensor_page + 1) % num_sensor_pages
    draw_sensor_page()

def handle_b_button():
    global status_mode, status_page

    if not status_mode:
        print("Waiting for Status Packet...")
        cmd, seq_num = send_command("status")
        draw_screen("Status Requested", f"CMD: {cmd}", f"SEQ: {seq_num}")
        return

    status_page = (status_page + 1) % num_status_pages
    draw_status_page()

############ lora init #####################

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs = digitalio.DigitalInOut(board.CE1)
reset = digitalio.DigitalInOut(board.D25)

radio = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
radio.tx_power = 20
radio.spreading_factor = 7
radio.signal_bandwidth = 125000
radio.coding_rate = 5

############## system logging ############
LOG_FILE = Path("waspp_packet_log.jsonl")

def log_packet(direction, packet, note=""):
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "direction": direction,
        "note": note,
        "packet": packet
    }
    
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        print(f"[logger error] {e}")

############# Sensor Logging #############
SENSOR_LOG_FILE = Path("waspp_sensors.jsonl")

def sensor_log(sensor_packet):
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "packet": sensor_packet
    }
    
    try:
        with SENSOR_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        print(f"[logger error] {e}")

############## packet handling ###########
def clear_ack_state():
    global waiting_for_ack, waiting_seq, waiting_cmd, ack_deadline

    waiting_for_ack = False
    waiting_seq = None
    waiting_cmd = None
    ack_deadline = 0


def send_command(cmd):
    global seq, waiting_for_ack, waiting_seq, waiting_cmd, ack_deadline

    seq += 1
    if cmd == "live_start":
        to = "FTR"
    else:
        to = "DrPi"

    packet = make_cmd_pkt(to, seq, cmd)
    raw = json.dumps(packet, separators=(",", ":"))

    waiting_for_ack = True
    waiting_seq = seq
    waiting_cmd = cmd
    ack_deadline = time.monotonic() + ACK_TIMEOUT_S

    radio.send(raw.encode("utf-8"))
    print("TX:", raw)
    log_packet("TX", raw, "Command Sent")
    return cmd, seq


def handle_rx_packet(raw_packet):
    global status_mode
        # Ignore obvious non-JSON/binary packets before UTF-8 decoding.
    if not raw_packet:
        return

    if raw_packet[0] != ord("{"):
 #       print("Ignored non-JSON LoRa packet:", raw_packet[:12])
        return

    try:
        text = raw_packet.decode("utf-8").strip()
        packet = json.loads(text)
    except Exception as e:
        print("RX parse error:", e)
        print("Raw packet:", raw_packet)
        draw_screen("RX parse error", "bad JSON/UTF8", "")
        return

    print("RX:", packet)

    if not is_demo_pkt(packet):
#        print("Ignored non-demo packet")
        return

    log_packet("RX", packet, "BS LoRa Received")
    rx_type = packet_type(packet)
    rx_seq = packet_seq(packet)
    rx_cmd = packet.get("cmd")
    rssi = getattr(radio, "last_rssi", "--")

    if rx_type == "SENSOR":
        handle_sensor_packet(packet, rssi)
        print(f"sensor Packet Received. Live sensor mode: {live_mode}")
        return
    if rx_type == "STT": #status
        status_mode = True
        handle_status_packet(packet, rssi)
        print(f"status packet received. status_mode: {status_mode}")
        return
    if not waiting_for_ack:
        draw_screen(
            "Unexpected packet",
            f"Type: {rx_type}",
            f"Seq: {rx_seq}"
        )
        return

    if rx_seq != waiting_seq:
        draw_screen(
            "ACK seq mismatch",
            f"Got: {rx_seq}",
            f"Want: {waiting_seq}"
        )
        return

    if rx_cmd != waiting_cmd:
        draw_screen(
            "ACK cmd mismatch",
            f"Got: {rx_cmd}",
            f"Want: {waiting_cmd}"
        )
        return

    if rx_type == "ACK":
        handle_ack(packet, rssi)

    else:
        draw_screen(
            "Unknown ACK type",
            f"Type: {rx_type}",
            f"RSSI: {rssi}"
        )

def handle_ack(packet, rssi):
    global status_mode

    ok = packet.get("ok", 0)
    cmd = packet.get("cmd", "")
    msg = packet.get("msg", "")
    global live_mode

    if not ok:
        draw_screen(
            "Command failed",
            msg,
            f"RSSI: {rssi}"
        )
        clear_ack_state()
        return

    if cmd == "take_sample":
        draw_screen(
            "Take Sample Ack",
            msg,
            f"RSSI: {rssi}"
        )

    elif cmd == "status":
        status_mode = True
        draw_screen(
            "WAIT! TAKES TIME...",
            msg,
            f"RSSI: {rssi}"
        )
    elif cmd == "live_start":
        live_mode = True
        draw_screen(
            f"Live Start Ack...",
            msg,
            f"RSSI: {rssi}"
        )
    else:
        draw_screen(
            "ACK received",
            f"CMD: {cmd}",
            f"RSSI: {rssi}"
        )

    clear_ack_state()

def fmt(value):
    try:
        return f"{float(value):.1f}"
    except Exception:
        return str(value)


################ Sensor Packet Handling: #############################

def handle_sensor_packet(packet, rssi):
    global latest_sensor

    sensor_log(packet)

    latest_sensor["id"] = packet.get("id", "--")
    latest_sensor["ms"] = packet.get("ms", "--")
    latest_sensor["tmp117_c"] = packet.get("tmp117_c", "--")
    latest_sensor["bme_t"] = packet.get("bme_t", "--")
    latest_sensor["bme_rh"] = packet.get("bme_rh", "--")
    latest_sensor["bme_p"] = packet.get("bme_p", "--")
    latest_sensor["bme_g"] = packet.get("bme_g", "--")
    latest_sensor["uvs"] = packet.get("uvs", "--")
    latest_sensor["als"] = packet.get("als", "--")
    latest_sensor["rssi"] = rssi
    latest_sensor["pm25"] = packet.get("pm25", "--")
    if live_mode:
        draw_sensor_page()

def handle_status_packet(packet, rssi):
    global latest_status

    latest_status["msg"] = packet.get("msg", "--")
    latest_status["date"] = packet.get("date", "--")
    latest_status["lat"] = packet.get("lat", "--")
    latest_status["lon"] = packet.get("lon", "--")
    latest_status["alt"] = packet.get("alt", "--")
    latest_status["sat"] = packet.get("sat", "--")
    latest_status["pump"] = packet.get("pump", "--")
    latest_status["pos"] = packet.get("pos", "--")
    latest_status["run"] = packet.get("run", "--")
    latest_status["samp"] = packet.get("samp", "--")
    latest_status["pS"] = packet.get("pS", "--")
    latest_status["pA"] = packet.get("pA", "--")
    latest_status["BV"] = packet.get("BV", "--")
    latest_status["flow"] = packet.get("flow", "--")
    latest_status["pwr"] = packet.get("pwr", "--")
    
    draw_status_page()

############## Misc ###################

def get_time():
    current_time = datetime.now().strftime("%H.%M.%S")
    return current_time

###################### Main ##########################

try:
    print_idle()
    print("Live Sensor Demo")
    print("A: Sample | B: Status | C: Sensor")
    print("Ctrl+C to stop")

    while True:
        now = time.monotonic()

        packet = radio.receive(timeout=0.05)

        if packet is not None:
            handle_rx_packet(packet)

        if not button_a.value and b_a("A"):
            print("Button A pressed")
            live_mode = False
            status_mode = False
            cmd, seq_num = send_command("take_sample")
            draw_screen("CMD SENT", f"CMD: {cmd}", f"SEQ: {seq_num}")

        if not button_b.value and b_a("B"):
            print("Button B pressed")
            live_mode = False
            handle_b_button()

        if not button_c.value and b_a("C"):
            print("Button C Pressed")
            handle_c_button()
            status_mode = False

        if waiting_for_ack and now > ack_deadline:
            draw_screen(
                "ACK TIMEOUT",
                f"CMD: {waiting_cmd}",
                f"SEQ: {waiting_seq}"
            )
            clear_ack_state()

except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Stopping demo.")

except Exception as e:
    print(f"\nUnexpected error: {e}")

    try:
        draw_screen(
            "Demo error",
            str(type(e).__name__),
            "See terminal"
        )
        time.sleep(2)
    except Exception:
        pass

finally:
    try:
        shutdown_display()
    except Exception as e:
        print(f"Display shutdown failed: {e}")
