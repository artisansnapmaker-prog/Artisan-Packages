# Snapmaker Artisan Packages

Community-built Snapmaker Artisan update packages and the reproducible builder used to combine an Artisan controller image with the Android HMI application.

> [!WARNING]
> These are unofficial builds, not Snapmaker releases. Installing controller firmware or a system application can make the machine unusable if the package is incompatible or power is interrupted. Verify the SHA-256 checksum, keep a known-good recovery package, make sure the machine is idle, and use these files at your own risk.

## Current release

[V2.8.3](https://github.com/artisansnapmaker-prog/Artisan-Packages/releases/tag/V2.8.3) contains:

| Asset | Purpose | Size | SHA-256 |
| --- | --- | ---: | --- |
| `SM3_V2.8.3_20260915.bin` | Combined USB update: controller firmware and HMI application | 155,961,715 bytes | `402FBEB497BFD34AD40ADBF14D5E0FA81C897BD70DA346C24A880D5C039C902E` |
| `A400_MC_V2.3.4_20260817.bin` | Standalone Artisan controller image | 386,960 bytes | `19E73E2084D252ED64607A77167B2BA4BD1AD13FF0B5383F686606AD0FD33EFE` |
| `fabscreen-a400_1.8.0_enhanced-dashboard_armeabi-v7a_platform-signed.apk` | Latest Artisan ARM HMI with the enhanced LAN dashboard and optimized G-code workflow | 155,574,698 bytes | `D9F3A9BAE5B63214A976D33D9671F618477C447AF0EABBCF8FFD6BA9BF58DCFC` |

The complete machine-readable metadata is in [`releases/V2.8.3/manifest.json`](releases/V2.8.3/manifest.json). The outer package, Android app, and controller use independent version schemes: V2.8.3 identifies the combined update, the Android package remains version `1.8.0`, and the official controller source reports `V2.3.4-0624` with OTA image version `V2.3.4`. The controller image is byte-identical to V2.8.2; this release updates the screen application.

The previous [V2.8.2 release](https://github.com/artisansnapmaker-prog/Artisan-Packages/releases/tag/V2.8.2) remains available. Historical V2.8.1 controller source is preserved on the controller repository's [`legacy/v2.8.1-imported-source`](https://github.com/artisansnapmaker-prog/Artisan-Controller/tree/legacy/v2.8.1-imported-source) branch.

## Install the combined package

1. Download `SM3_V2.8.3_20260915.bin` from the V2.8.3 release.
2. Verify its SHA-256 checksum against this repository.
3. Copy the file to the root of a USB drive supported by the Artisan.
4. Make sure the printer is idle and connect the USB drive.
5. Open the Artisan's local firmware update screen and select the package.
6. Keep the machine powered until the update and restart have completed.

The combined package updates both payload types:

- `0`: main controller firmware
- `3`: Android screen application

## Build a package

Python 3.9 or newer is sufficient; there are no third-party dependencies.

```powershell
python build_combined_package.py `
  --controller firmware/A400_MC_V2.3.4_20260817.bin `
  --screen app/fabscreen-a400_1.8.0_enhanced-dashboard_armeabi-v7a_platform-signed.apk `
  --version V2.8.3 `
  --date 20260915
```

The builder validates the controller image and APK/ZIP formats, writes the major-image header, embeds both payloads, and then verifies every packaged byte against its input. APK signing is verified separately with Android's `apksigner` before publication.

Run the tests with:

```powershell
python -m unittest discover -s tests -v
```

## Source repositories

- [Snapmaker Artisan Screen App](https://github.com/artisansnapmaker-prog/Snapmaker-Artisan-Screen-App)
- [Artisan Controller](https://github.com/artisansnapmaker-prog/Artisan-Controller), forked from [Snapmaker's official source](https://github.com/Snapmaker/Artisan-Controller)

## Binary policy

APKs and firmware images are intentionally ignored by Git. GitHub rejects ordinary files larger than 100 MB, and update binaries do not produce useful source diffs. Published artifacts belong in GitHub Releases; tracked manifests and checksum files make those assets auditable.

Device-backup APKs are local recovery files and are never published.
