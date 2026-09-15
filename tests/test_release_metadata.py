import json
import re
import unittest
from pathlib import Path


class ReleaseMetadataTest(unittest.TestCase):
    def setUp(self):
        self.repository = Path(__file__).resolve().parents[1]
        manifest_path = self.repository / "releases" / "V2.8.3" / "manifest.json"
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    def test_current_release_uses_artisan_controller_fork(self):
        firmware = self.manifest["sources"]["firmware"]
        self.assertEqual(
            "https://github.com/artisansnapmaker-prog/Artisan-Controller",
            firmware["repository"],
        )
        self.assertEqual(
            "https://github.com/Snapmaker/Artisan-Controller",
            firmware["upstreamRepository"],
        )
        self.assertRegex(firmware["commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(firmware["upstreamCommit"], r"^[0-9a-f]{40}$")

    def test_component_versions_are_not_conflated(self):
        components = self.manifest["components"]
        self.assertEqual("V2.8.3", self.manifest["releaseVersion"])
        self.assertEqual("V2.3.4-0624", components["controllerRuntimeVersion"])
        self.assertEqual("V2.3.4", components["controllerOtaVersion"])

    def test_current_release_uses_latest_screen_app(self):
        screen = self.manifest["sources"]["screen"]
        self.assertEqual(
            "https://github.com/artisansnapmaker-prog/Snapmaker-Artisan-Screen-App",
            screen["repository"],
        )
        self.assertEqual(
            "f1f50ae8be2d75bc179287500bf8013b31d5bb04",
            screen["commit"],
        )
        self.assertEqual(
            "1dcc5f6e8255efbf975a35d3f36f4534ec02cfce",
            screen["tree"],
        )

    def test_artifact_metadata_is_well_formed(self):
        self.assertEqual(
            {
                "SM3_V2.8.3_20260915.bin",
                "A400_MC_V2.3.4_20260817.bin",
                "fabscreen-a400_1.8.0_enhanced-dashboard_armeabi-v7a_platform-signed.apk",
            },
            {artifact["name"] for artifact in self.manifest["artifacts"]},
        )
        for artifact in self.manifest["artifacts"]:
            self.assertGreater(artifact["size"], 0)
            self.assertTrue(re.fullmatch(r"[0-9A-F]{64}", artifact["sha256"]))

    def test_retired_repository_is_not_referenced(self):
        checked_paths = [
            self.repository / "README.md",
            self.repository / "releases" / "V2.8.1" / "manifest.json",
            self.repository / "releases" / "V2.8.2" / "manifest.json",
            self.repository / "releases" / "V2.8.3" / "manifest.json",
        ]
        for path in checked_paths:
            self.assertNotIn("Artisan-Marlin-fw", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
