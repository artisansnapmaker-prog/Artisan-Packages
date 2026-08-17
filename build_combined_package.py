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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


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

    if not controller.startswith(b"snapmaker update.bin"):
        raise ValueError(f"not a packaged Snapmaker controller image: {controller_path}")
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
