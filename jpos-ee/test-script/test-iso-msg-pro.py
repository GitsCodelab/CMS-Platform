#!/usr/bin/env python3

import socket
import struct
import sys
from datetime import datetime
from typing import Dict


TPDU = b"\x60\x00\x00\x00\x00"


FIELD_DEFINITION = {
    2: {"type": "LLVAR"},
    3: {"type": "FIXED", "len": 6},
    4: {"type": "FIXED", "len": 12},
    7: {"type": "FIXED", "len": 10},
    11: {"type": "FIXED", "len": 6},
    12: {"type": "FIXED", "len": 6},
    13: {"type": "FIXED", "len": 4},
    22: {"type": "FIXED", "len": 3},
    25: {"type": "FIXED", "len": 2},
    35: {"type": "LLVAR"},
    41: {"type": "FIXED", "len": 8},
    42: {"type": "FIXED", "len": 15},
    49: {"type": "FIXED", "len": 3},
    52: {"type": "BINARY", "len": 8},
    55: {"type": "LLLVAR_BIN"},
}


# 🔒 SAFE PIN BLOCK (NO SHIFT EVER)
def generate_pin_block():
    return bytes.fromhex("1234FFFFFFFFFFFF")[:8]


def encode_field(field_num, value):
    spec = FIELD_DEFINITION[field_num]

    if spec["type"] == "FIXED":
        return value.encode()

    elif spec["type"] == "LLVAR":
        return f"{len(value):02}".encode() + value.encode()

    elif spec["type"] == "LLLVAR_BIN":
        raw = bytes.fromhex(value)
        return f"{len(raw):03}".encode() + raw

    elif spec["type"] == "BINARY":
        if len(value) != spec["len"]:
            raise ValueError(f"Field {field_num} must be {spec['len']} bytes")
        return value


class ISO8583:

    @staticmethod
    def build_0200(pan, amount, stan):
        now = datetime.now()

        fields = {
            2: pan,
            3: "000000",
            4: amount.zfill(12),
            7: now.strftime("%m%d%H%M%S"),
            11: stan.zfill(6),
            12: now.strftime("%H%M%S"),
            13: now.strftime("%m%d"),
            22: "021",
            25: "00",
            35: f"{pan}=25122010000000000000",
            41: "TERMID01",
            42: "MERCHANT0000010",  # ✅ FIXED LENGTH = 15
            49: "840",
            52: generate_pin_block(),  # ✅ EXACT 8 bytes
            55: "9F2608A1A2A3A4A5A6A7",
        }

        return ISO8583._build("0200", fields)

    @staticmethod
    def _build(mti, fields: Dict[int, str]):
        bitmap = 0
        for f in fields:
            bitmap |= (1 << (64 - f))

        bitmap_bytes = bitmap.to_bytes(8, "big")

        data = mti.encode() + bitmap_bytes

        for f in sorted(fields):
            data += encode_field(f, fields[f])

        full_msg = TPDU + data

        return struct.pack(">H", len(full_msg)) + full_msg


class ISOParser:

    @staticmethod
    def parse(data: bytes):
        try:
            length = struct.unpack(">H", data[:2])[0]
            msg = data[2:2 + length]

            tpdu = msg[:5]
            msg = msg[5:]

            mti = msg[:4].decode()
            bitmap = int.from_bytes(msg[4:12], "big")

            pos = 12
            fields = {}

            for f in range(2, 65):
                if bitmap & (1 << (64 - f)):
                    spec = FIELD_DEFINITION.get(f)
                    if not spec:
                        continue

                    try:
                        if spec["type"] == "FIXED":
                            l = spec["len"]
                            val = msg[pos:pos + l].decode()
                            pos += l

                        elif spec["type"] == "LLVAR":
                            l = int(msg[pos:pos + 2].decode())
                            pos += 2
                            val = msg[pos:pos + l].decode()
                            pos += l

                        elif spec["type"] == "BINARY":
                            l = spec["len"]
                            val = msg[pos:pos + l].hex().upper()
                            pos += l

                        elif spec["type"] == "LLLVAR_BIN":
                            l = int(msg[pos:pos + 3].decode())
                            pos += 3
                            val = msg[pos:pos + l].hex().upper()
                            pos += l

                        fields[f] = val

                    except Exception:
                        fields[f] = "PARSE_ERROR"
                        break

            return {
                "mti": mti,
                "tpdu": tpdu.hex().upper(),
                "fields": fields
            }

        except Exception as e:
            return {"error": str(e)}


class Client:

    def __init__(self, host="localhost", port=8583):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.host, self.port))
            print("✓ Connected")
            return True
        except Exception as e:
            print(e)
            return False

    def send(self, msg):
        self.sock.sendall(msg)
        resp = self.sock.recv(4096)
        return ISOParser.parse(resp)

    def close(self):
        if self.sock:
            self.sock.close()


def run():
    c = Client()

    if not c.connect():
        sys.exit(1)

    msg = ISO8583.build_0200(
        pan="4111111111111111",
        amount="10000",
        stan="123456"
    )

    print("\nSENT HEX:\n", msg.hex().upper())

    resp = c.send(msg)

    print("\nRESPONSE:\n", resp)

    c.close()


if __name__ == "__main__":
    run()