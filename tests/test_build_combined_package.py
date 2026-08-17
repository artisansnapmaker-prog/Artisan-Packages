import contextlib
import io
import struct
import tempfile
import unittest
from pathlib import Path

from build_combined_package import (
    BASE_HEADER_SIZE,
    CONTROLLER_HEADER_SIZE,
    ENTRY_SIZE,
    TYPE_MAIN_CONTROLLER,
    TYPE_SCREEN_APP,
    build,
    controller_version,
    package_version,
    snapmaker_checksum,
    verify,
)


def make_controller(version="V2.3.4", payload=b"Artisan controller payload"):
    header = bytearray(CONTROLLER_HEADER_SIZE)
    header[:21] = b"snapmaker update.bin\0"
    header[21] = 1
    struct.pack_into("<H", header, 22, 2)
    header[24] = 1
    header[29:61] = version.encode("ascii").ljust(32, b"\0")
    header[61:81] = b"2022.04.28:18:03:01\0"
    struct.pack_into("<H", header, 81, 0xAA00)
    struct.pack_into("<I", header, 83, len(payload))
    struct.pack_into("<I", header, 87, snapmaker_checksum(payload))
    struct.pack_into("<I", header, 91, 0x08010000)
    struct.pack_into("<I", header, 97, snapmaker_checksum(header[:97]))
    return bytes(header) + payload


class CombinedPackageTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.controller = self.root / "controller.bin"
        self.screen = self.root / "screen.apk"
        self.output = self.root / "combined.bin"
        self.controller_bytes = make_controller()
        self.screen_bytes = b"PK\x03\x04" + bytes(reversed(range(64)))
        self.controller.write_bytes(self.controller_bytes)
        self.screen.write_bytes(self.screen_bytes)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_builds_and_verifies_both_payloads(self):
        version = "SM3_V2.8.1_20260817"
        build(self.controller, self.screen, self.output, version)

        package = self.output.read_bytes()
        expected_header_size = BASE_HEADER_SIZE + 2 * ENTRY_SIZE
        self.assertEqual(expected_header_size, struct.unpack_from(">h", package, 0)[0])
        self.assertEqual(version, package[2:34].rstrip(b"\0").decode("ascii"))
        self.assertEqual(2, package[38])

        first_type, first_offset, first_size = struct.unpack_from(">bii", package, BASE_HEADER_SIZE)
        second_type, second_offset, second_size = struct.unpack_from(
            ">bii", package, BASE_HEADER_SIZE + ENTRY_SIZE
        )
        self.assertEqual(TYPE_MAIN_CONTROLLER, first_type)
        self.assertEqual(TYPE_SCREEN_APP, second_type)
        self.assertEqual(expected_header_size, first_offset)
        self.assertEqual(first_offset + first_size, second_offset)
        self.assertEqual(self.controller_bytes, package[first_offset:first_offset + first_size])
        self.assertEqual(self.screen_bytes, package[second_offset:second_offset + second_size])

        with contextlib.redirect_stdout(io.StringIO()) as output:
            verify(self.output, self.controller, self.screen)
        self.assertIn("Controller version: V2.3.4", output.getvalue())
        self.assertIn("Verification: OK", output.getvalue())

    def test_outer_version_is_independent_from_controller_version(self):
        package_release = "SM3_V2.8.2_20260817"
        build(self.controller, self.screen, self.output, package_release)

        package = self.output.read_bytes()
        self.assertEqual(package_release, package[2:34].rstrip(b"\0").decode("ascii"))
        self.assertEqual("V2.3.4", controller_version(self.controller_bytes))

    def test_rejects_invalid_input_signatures(self):
        self.controller.write_bytes(b"not a controller image")
        with self.assertRaisesRegex(ValueError, "shorter than its 256-byte header"):
            build(self.controller, self.screen, self.output, "SM3_V2.8.1_20260817")

        self.controller.write_bytes(self.controller_bytes)
        self.screen.write_bytes(b"not an APK")
        with self.assertRaisesRegex(ValueError, "not an APK/ZIP payload"):
            build(self.controller, self.screen, self.output, "SM3_V2.8.1_20260817")

    def test_rejects_corrupt_controller_payload(self):
        corrupted = bytearray(self.controller_bytes)
        corrupted[-1] ^= 0xFF
        self.controller.write_bytes(corrupted)
        with self.assertRaisesRegex(ValueError, "payload checksum mismatch"):
            build(self.controller, self.screen, self.output, "SM3_V2.8.2_20260817")

    def test_validates_release_version_and_date(self):
        self.assertEqual("SM3_V2.8.1_20260817", package_version("V2.8.1", "20260817"))
        with self.assertRaisesRegex(ValueError, "version must have the form"):
            package_version("2.8.1", "20260817")
        with self.assertRaisesRegex(ValueError, "date must have the form"):
            package_version("V2.8.1", "2026-08-17")


if __name__ == "__main__":
    unittest.main()
