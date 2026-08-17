#!/usr/bin/env python3
"""Build and verify an Artisan app-plus-controller update package."""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
from datetime import datetime
from pathlib import Path


TYPE_MAIN_CONTROLLER = 0
TYPE_SCREEN_APP = 3
BASE_HEADER_SIZE = 39
ENTRY_SIZE = 9
CONTROLLER_HEADER_SIZE = 256
CONTROLLER_MAGIC = b"snapmaker update.bin\0"
A400_CONTROLLER_PACKET_TYPE = 0x0002
A400_APPLICATION_ADDRESS = 0x08010000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def snapmaker_checksum(data: bytes) -> int:
    checksum = sum(
        (data[index] << 8) | data[index + 1]
        for index in range(0, len(data) - 1, 2)
    )
    if len(data) % 2:
        checksum += data[-1]
    return (~checksum) & 0xFFFFFFFF


def controller_version(controller: bytes) -> str:
    if len(controller) < CONTROLLER_HEADER_SIZE:
        raise ValueError("controller image is shorter than its 256-byte header")
    if not controller.startswith(CONTROLLER_MAGIC):
        raise ValueError("not a packaged Snapmaker controller image")

    protocol_version = controller[21]
    packet_type = struct.unpack_from("<H", controller, 22)[0]
    run_address = struct.unpack_from("<I", controller, 91)[0]
    if protocol_version != 1:
        raise ValueError(f"unsupported controller protocol version {protocol_version}")
    if packet_type != A400_CONTROLLER_PACKET_TYPE:
        raise ValueError(f"expected A400 controller packet type 2, found {packet_type}")
    if run_address != A400_APPLICATION_ADDRESS:
        raise ValueError(f"unexpected controller run address 0x{run_address:08X}")

    try:
        version = controller[29:61].split(b"\0", 1)[0].decode("ascii")
    except UnicodeDecodeError as error:
        raise ValueError("controller version is not ASCII") from error
    if not re.fullmatch(r"V\d+\.\d+\.\d+", version):
        raise ValueError(f"invalid controller version {version!r}")

    payload = controller[CONTROLLER_HEADER_SIZE:]
    declared_size = struct.unpack_from("<I", controller, 83)[0]
    declared_checksum = struct.unpack_from("<I", controller, 87)[0]
    declared_header_checksum = struct.unpack_from("<I", controller, 97)[0]
    if declared_size != len(payload):
        raise ValueError(
            f"controller payload size mismatch: header={declared_size}, actual={len(payload)}"
        )
    if declared_checksum != snapmaker_checksum(payload):
        raise ValueError("controller payload checksum mismatch")
    if declared_header_checksum != snapmaker_checksum(controller[:97]):
        raise ValueError("controller header checksum mismatch")

    return version


def package_version(version: str, date: str) -> str:
    if not re.fullmatch(r"V\d+\.\d+\.\d+", version):
        raise ValueError("version must have the form V1.2.3")
    if not re.fullmatch(r"\d{8}", date):
        raise ValueError("date must have the form YYYYMMDD")
    return f"SM3_{version}_{date}"


def encode_version(version: str) -> bytes:
    encoded = version.encode("ascii")
    if len(encoded) > 31:
        raise ValueError("package version is too long")
    return encoded.ljust(32, b"\0")


def build(controller_path: Path, screen_path: Path, output_path: Path, version: str) -> None:
    controller = controller_path.read_bytes()
    screen = screen_path.read_bytes()

    try:
        controller_version(controller)
    except ValueError as error:
        raise ValueError(f"invalid controller image {controller_path}: {error}") from error
    if not screen.startswith(b"PK\x03\x04"):
        raise ValueError(f"not an APK/ZIP payload: {screen_path}")

    entries = (
        (TYPE_MAIN_CONTROLLER, controller),
        (TYPE_SCREEN_APP, screen),
    )
    header_size = BASE_HEADER_SIZE + ENTRY_SIZE * len(entries)
    offset = header_size

    header = bytearray()
    header.extend(struct.pack(">h", header_size))
    header.extend(encode_version(version))
    header.extend(struct.pack(">i", 0))
    header.extend(struct.pack(">b", len(entries)))

    for payload_type, payload in entries:
        header.extend(struct.pack(">bii", payload_type, offset, len(payload)))
        offset += len(payload)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary_path.open("wb") as output:
        output.write(header)
        for _, payload in entries:
            output.write(payload)
    temporary_path.replace(output_path)


def verify(output_path: Path, controller_path: Path, screen_path: Path) -> None:
    package = output_path.read_bytes()
    expected = {
        TYPE_MAIN_CONTROLLER: controller_path.read_bytes(),
        TYPE_SCREEN_APP: screen_path.read_bytes(),
    }

    header_size = struct.unpack_from(">h", package, 0)[0]
    version = package[2:34].rstrip(b"\0").decode("ascii")
    count = package[38]
    if header_size != BASE_HEADER_SIZE + ENTRY_SIZE * count:
        raise ValueError("invalid major-image header size")
    if count != len(expected):
        raise ValueError(f"expected {len(expected)} payloads, found {count}")

    cursor = BASE_HEADER_SIZE
    for _ in range(count):
        payload_type, offset, size = struct.unpack_from(">bii", package, cursor)
        cursor += ENTRY_SIZE
        if payload_type not in expected:
            raise ValueError(f"unexpected payload type {payload_type}")
        actual_payload = package[offset : offset + size]
        if actual_payload != expected[payload_type]:
            raise ValueError(f"payload type {payload_type} does not match its input file")

    print(f"Package: {output_path}")
    print(f"Version: {version}")
    print(f"Size: {len(package)}")
    print(f"SHA256: {sha256(package)}")
    embedded_controller_version = controller_version(expected[TYPE_MAIN_CONTROLLER])
    print(f"Controller version: {embedded_controller_version}")
    print(f"Controller SHA256: {sha256(expected[TYPE_MAIN_CONTROLLER])}")
    print(f"Screen APK SHA256: {sha256(expected[TYPE_SCREEN_APP])}")
    print("Payload types: 0=controller, 3=screen app")
    print("Verification: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller", required=True, type=Path)
    parser.add_argument("--screen", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    version = package_version(args.version, args.date)
    output = args.output or Path("combined") / f"{version}.bin"
    build(args.controller, args.screen, output, version)
    verify(output, args.controller, args.screen)


if __name__ == "__main__":
    main()
