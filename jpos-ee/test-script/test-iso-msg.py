#!/usr/bin/env python3

import socket
import struct
import sys
from datetime import datetime
from typing import Dict


# ================= FIELD DEFINITIONS =================
FIELD_DEFINITION = {
    2: {"type": "LLVAR", "max_len": 19},
    3: {"type": "FIXED", "len": 6},
    4: {"type": "FIXED", "len": 12},
    11: {"type": "FIXED", "len": 6},
    12: {"type": "FIXED", "len": 6},
    13: {"type": "FIXED", "len": 4},
    38: {"type": "FIXED", "len": 6},
    39: {"type": "FIXED", "len": 2},
    54: {"type": "LLLVAR", "max_len": 120},
}


# ================= FIELD ENCODER =================
def encode_field(field_num, value):
    spec = FIELD_DEFINITION[field_num]

    if spec["type"] == "FIXED":
        return value.encode()

    elif spec["type"] == "LLVAR":
        length = len(value)
        return f"{length:02}".encode() + value.encode()

    elif spec["type"] == "LLLVAR":
        length = len(value)
        return f"{length:03}".encode() + value.encode()


# ================= ISO BUILDER =================
class ISO8583Packager:

    @staticmethod
    def build_authorization_request(pan, amount, stan):
        return ISO8583Packager._build_message("0100", {
            2: pan,
            3: "000000",
            4: amount.zfill(12),
            11: stan.zfill(6),
            12: datetime.now().strftime("%H%M%S"),
            13: datetime.now().strftime("%m%d"),
        })

    @staticmethod
    def build_balance_inquiry(pan, stan):
        return ISO8583Packager._build_message("0200", {
            2: pan,
            3: "300000",
            11: stan.zfill(6),
            12: datetime.now().strftime("%H%M%S"),
            13: datetime.now().strftime("%m%d"),
        })

    @staticmethod
    def build_reversal_request(stan, amount):
        return ISO8583Packager._build_message("0400", {
            3: "000000",
            4: amount.zfill(12),
            11: stan.zfill(6),
            12: datetime.now().strftime("%H%M%S"),
            13: datetime.now().strftime("%m%d"),
        })

    @staticmethod
    def _build_message(mti: str, fields: Dict[int, str]) -> bytes:
        bitmap = 0
        for f in fields:
            bitmap |= (1 << (64 - f))

        bitmap_bytes = bitmap.to_bytes(8, byteorder="big")

        data = mti.encode() + bitmap_bytes

        for f in sorted(fields.keys()):
            data += encode_field(f, fields[f])

        return struct.pack(">H", len(data)) + data


# ================= PARSER =================
class ISOParser:

    @staticmethod
    def parse(data: bytes):
        if len(data) < 2:
            return {"error": "Invalid message"}

        length = struct.unpack(">H", data[:2])[0]
        msg = data[2:2 + length]

        mti = msg[:4].decode()
        bitmap = int.from_bytes(msg[4:12], "big")

        pos = 12
        fields = {}

        for f in range(2, 65):
            if bitmap & (1 << (64 - f)):
                spec = FIELD_DEFINITION.get(f)
                if not spec:
                    continue

                if spec["type"] == "FIXED":
                    l = spec["len"]
                    value = msg[pos:pos + l].decode()
                    pos += l

                elif spec["type"] == "LLVAR":
                    l = int(msg[pos:pos + 2].decode())
                    pos += 2
                    value = msg[pos:pos + l].decode()
                    pos += l

                elif spec["type"] == "LLLVAR":
                    l = int(msg[pos:pos + 3].decode())
                    pos += 3
                    value = msg[pos:pos + l].decode()
                    pos += l

                fields[f] = value

        return {"mti": mti, "fields": fields}


# ================= CLIENT =================
class JposGatewayClient:

    def __init__(self, host="localhost", port=8583):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.host, self.port))
            print(f"✓ Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    def send(self, msg):
        try:
            self.sock.sendall(msg)
            resp = self.sock.recv(4096)
            return ISOParser.parse(resp)
        except Exception as e:
            return {"error": str(e)}

    def close(self):
        if self.sock:
            self.sock.close()


# ================= TEST =================
def run_tests():
    client = JposGatewayClient()

    if not client.connect():
        sys.exit(1)

    print("\n--- AUTH TEST ---")
    msg = ISO8583Packager.build_authorization_request(
        "4111111111111111", "10000", "000001"
    )
    print(client.send(msg))

    print("\n--- BALANCE TEST ---")
    msg = ISO8583Packager.build_balance_inquiry(
        "4111111111111111", "000002"
    )
    print(client.send(msg))

    print("\n--- REVERSAL TEST ---")
    msg = ISO8583Packager.build_reversal_request(
        "000001", "10000"
    )
    print(client.send(msg))

    client.close()


if __name__ == "__main__":
    run_tests()