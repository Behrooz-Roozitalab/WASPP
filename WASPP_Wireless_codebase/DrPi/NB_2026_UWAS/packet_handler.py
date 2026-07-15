import json
from typing import Any, Dict, Optional

SYS_ID = "demo"
DRPI_ID = "DrPi"
FEATHER_ID = "FTR"
BASE_STATION_ID = "BS"

PACKET_TYPE_CMD = "CMD"
PACKET_TYPE_ACK = "ACK"
PACKET_TYPE_STT = "STT"

CMD_TAKE_SAMPLE = "take_sample"
CMD_STATUS = "status"

VALID_COMMANDS = {
    CMD_TAKE_SAMPLE,
    CMD_STATUS
}

def make_ack(
    seq: Optional[int],
    cmd: Optional[str],
    ok: bool,
    msg: str,
    ) -> Dict[str, Any]:

    return {
        "sys": SYS_ID,
        "t": PACKET_TYPE_ACK,
        "sid": DRPI_ID,
        "seq": seq,
        "cmd": cmd,
        "ok": 1 if ok else 0,
        "msg": msg,
    }

def parse_packet(line: str) -> Dict[str, Any]:
    try:
        packet = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError("packet must be a JSON thing")

    return packet

def handle_command_packet(packet: Dict[str, Any]) -> Dict[str,Any]:
    sys_id = packet.get("sys")
    packet_type = packet.get("t")
    seq = packet.get("seq")
    cmd = packet.get("cmd")

    if sys_id != SYS_ID:
        return make_ack(
            seq=seq,
            cmd=cmd,
            ok=False,
            msg=f"wrong sys: {sys_id}",
        )
    
    if packet_type != PACKET_TYPE_CMD:
       return make_ack(
            seq=seq,
            cmd=cmd,
            ok=False,
            msg=f"wrong pkt typ: {packet_type}",
        )

    if cmd == CMD_TAKE_SAMPLE:
        # PUT TAKE_SAMPLE CODE TRIGGER*
        return make_ack(
            seq=seq,
            cmd=cmd,
            ok=True,
            msg="take_sample ack'd",
        )

    if cmd == CMD_STATUS:
        # PUT STATUS READ AND SEND
        return make_ack(
            seq=seq,
            cmd=cmd,
            ok=True,
            msg="status ack'd",
        )

    return make_ack(
        seq=seq,
        cmd=cmd,
        ok=False,
        msg="cmd not handle",
    )

def make_status_packet(sampling, samples, status, msg):  # Bool, dict, str
    stat_packet = {
        "sys": SYS_ID,
        "t": PACKET_TYPE_STT,
        "sid": DRPI_ID,
        "msg": msg,
        "date": status["date"],
        "lat": status["lat"],
        "lon": status["lon"],
        "alt": status["alt"],
        "sat": status["sat"],
        "pump": status["pump"],
        "run": sampling,
        "samp": samples,
        "pos": status["pos"],
        "pS": status["pS"],
        "pA": status["pA"],
        "BV": status["BV"],
        "flow": status["flow"],
        "pwr": status["pwr"],
}
 #   print(stat_packet)
    return stat_packet
def encode_packet(packet):
    #turns the json into a sendable packet -> ftr - - -> BS

    return (json.dumps(packet, separators=(",", ":")) + "\n").encode("utf-8")
