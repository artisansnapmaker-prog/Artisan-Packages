import json
import re
import unittest
from pathlib import Path


class ReleaseMetadataTest(unittest.TestCase):
    def setUp(self):
        self.repository = Path(__file__).resolve().parents[1]
        manifest_path = self.repository / "releases" / "V2.8.2" / "manifest.json"
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
        self.assertEqual("V2.8.2", self.manifest["releaseVersion"])
        self.assertEqual("V2.3.4-0624", components["controllerRuntimeVersion"])
        self.assertEqual("V2.3.4", components["controllerOtaVersion"])

    def test_artifact_metadata_is_well_formed(self):
        for artifact in self.manifest["artifacts"]:
            self.assertGreater(artifact["size"], 0)
            self.assertTrue(re.fullmatch(r"[0-9A-F]{64}", artifact["sha256"]))


if __name__ == "__main__":
    unittest.main()
