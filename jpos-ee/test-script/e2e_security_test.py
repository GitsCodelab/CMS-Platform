#!/usr/bin/env python3

import importlib.util
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "Production-raw-ISO_2.py"

spec = importlib.util.spec_from_file_location("iso_client", MODULE_PATH)
iso_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(iso_client)


def parse_response_code(resp: bytes) -> str:
    payload = resp[2:]
    if len(payload) < 5:
        return ""
    iso = payload[5:]
    hex_payload = iso.hex().upper()
    if len(hex_payload) < 20:
        return ""

    mti = hex_payload[:4]
    if mti not in {"0210", "0110", "0410", "0810"}:
        return ""

    primary_bitmap = bytes.fromhex(hex_payload[4:20])
    has_secondary = bool(primary_bitmap[0] & 0x80)
    bitmap = primary_bitmap
    pos = 10
    if has_secondary:
        secondary_bitmap = bytes.fromhex(hex_payload[20:36])
        bitmap += secondary_bitmap
        pos = 18

    fields = []
    for i in range(8 * len(bitmap)):
        if i == 0 and has_secondary:
            continue
        if bitmap[i // 8] & (1 << (7 - (i % 8))):
            fields.append(i + 1)

    data = iso[pos:]
    offset = 0

    def take(size: int) -> bytes:
        nonlocal offset
        part = data[offset:offset + size]
        offset += size
        return part

    values = {}
    for field in fields:
        if field == 39:
            values[field] = take(1).hex().upper()
        elif field == 2:
            l = int(take(1).hex(), 10)
            values[field] = take((l + 1) // 2).hex().upper()
        elif field in {3, 11, 12}:
            values[field] = take(3).hex().upper()
        elif field in {4, 7}:
            size = 6 if field == 4 else 5
            values[field] = take(size).hex().upper()
        elif field in {13, 22, 25, 49, 70}:
            size = {13: 2, 22: 2, 25: 1, 49: 2, 70: 2}[field]
            values[field] = take(size).hex().upper()
        elif field == 35:
            l = int(take(2).hex())
            values[field] = take(l).decode("ascii")
        elif field in {41, 42}:
            size = 8 if field == 41 else 15
            values[field] = take(size).decode("ascii").rstrip()
        elif field == 52:
            values[field] = take(8).hex().upper()
        elif field in {54, 62}:
            l = int(take(3).decode("ascii"))
            values[field] = take(l).decode("ascii")
        elif field == 64:
            values[field] = take(8).hex().upper()
        else:
            raise ValueError(f"Unhandled response field {field}")
    return values.get(39, "")


def assert_case(name: str, expected_code: str, **kwargs) -> None:
    resp = iso_client.send(iso_client.build_message(**kwargs))
    code = parse_response_code(resp)
    if code != expected_code:
        raise AssertionError(f"{name}: expected F39={expected_code}, got {code or '<missing>'}")
    print(f"[PASS] {name}: F39={code}")


def main() -> int:
    seed = int(time.time()) & 0x3FF

    def ksn(offset: int) -> bytes:
        return bytes.fromhex(f"FFFF9876543210E{seed + offset:05X}")

    assert_case("happy_path_0200", "00", ksn=ksn(1), overrides={11: "100001"})
    assert_case("tampered_mac", "96", tamper_mac=True, ksn=ksn(2), overrides={11: "100002"})
    assert_case("bad_pan_luhn", "30", ksn=ksn(3), overrides={11: "100003", 2: "4111111111111112", 35: "4111111111111112=25122010000000000000"})

    reused_ksn = ksn(4)
    assert_case("first_use_of_ksn", "00", ksn=reused_ksn, overrides={11: "100004"})
    assert_case("replayed_ksn_and_stan", "94", ksn=reused_ksn, overrides={11: "100004"})

    assert_case("missing_mac", "30", include_mac=False, ksn=ksn(5), overrides={11: "100005"})
    assert_case("network_management_0800", "00", mti="0800", overrides={11: "100006"})
    print("All end-to-end security checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
