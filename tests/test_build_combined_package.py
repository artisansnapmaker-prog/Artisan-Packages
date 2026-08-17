import contextlib
import io
import struct
import tempfile
import unittest
from pathlib import Path

from build_combined_package import (
    BASE_HEADER_SIZE,
    ENTRY_SIZE,
    TYPE_MAIN_CONTROLLER,
    TYPE_SCREEN_APP,
    build,
    package_version,
    verify,
)


class CombinedPackageTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.controller = self.root / "controller.bin"
        self.screen = self.root / "screen.apk"
        self.output = self.root / "combined.bin"
        self.controller_bytes = b"snapmaker update.bin" + bytes(range(64))
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
        self.assertIn("Verification: OK", output.getvalue())

    def test_rejects_invalid_input_signatures(self):
        self.controller.write_bytes(b"not a controller image")
        with self.assertRaisesRegex(ValueError, "not a packaged Snapmaker controller image"):
            build(self.controller, self.screen, self.output, "SM3_V2.8.1_20260817")

        self.controller.write_bytes(self.controller_bytes)
        self.screen.write_bytes(b"not an APK")
        with self.assertRaisesRegex(ValueError, "not an APK/ZIP payload"):
            build(self.controller, self.screen, self.output, "SM3_V2.8.1_20260817")

    def test_validates_release_version_and_date(self):
        self.assertEqual("SM3_V2.8.1_20260817", package_version("V2.8.1", "20260817"))
        with self.assertRaisesRegex(ValueError, "version must have the form"):
            package_version("2.8.1", "20260817")
        with self.assertRaisesRegex(ValueError, "date must have the form"):
            package_version("V2.8.1", "2026-08-17")


if __name__ == "__main__":
    unittest.main()
