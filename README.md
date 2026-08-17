# Snapmaker Artisan Packages

Community-built Snapmaker Artisan update packages and the reproducible builder used to combine an Artisan controller image with the Android HMI application.

> [!WARNING]
> These are unofficial builds, not Snapmaker releases. Installing controller firmware or a system application can make the machine unusable if the package is incompatible or power is interrupted. Verify the SHA-256 checksum, keep a known-good recovery package, make sure the machine is idle, and use these files at your own risk.

## Current release

[V2.8.2](https://github.com/artisansnapmaker-prog/Artisan-Packages/releases/tag/V2.8.2) contains:

| Asset | Purpose | Size | SHA-256 |
| --- | --- | ---: | --- |
| `SM3_V2.8.2_20260817.bin` | Combined USB update: controller firmware and HMI application | 155,432,810 bytes | `FFA7BC84A3F0D8FACA16F6B25B019A52F347E35557FE85C6DF6595AFFEE44389` |
| `A400_MC_V2.3.4_20260817.bin` | Standalone Artisan controller image | 386,960 bytes | `19E73E2084D252ED64607A77167B2BA4BD1AD13FF0B5383F686606AD0FD33EFE` |
| `fabscreen-a400_1.8.0_orca-thumbnail-dashboard_armeabi-v7a_platform-signed.apk` | Artisan ARM HMI with the FDM dashboard and Orca thumbnail support | 155,045,793 bytes | `DF4B9B77BCE3FBD9798A7AA87D44A19DA3337230A0A7A26625826DB68B4A5FAD` |

The complete machine-readable metadata is in [`releases/V2.8.2/manifest.json`](releases/V2.8.2/manifest.json). The outer package release and controller use independent version schemes: V2.8.2 identifies the combined HMI package, while the official controller source reports `V2.3.4-0624` and its OTA image is `V2.3.4`.

The previous [V2.8.1 prerelease](https://github.com/artisansnapmaker-prog/Artisan-Packages/releases/tag/V2.8.1) remains available as a historical build.

## Install the combined package

1. Download `SM3_V2.8.2_20260817.bin` from the V2.8.2 release.
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
  --screen app/fabscreen-a400_1.8.0_orca-thumbnail-dashboard_armeabi-v7a_platform-signed.apk `
  --version V2.8.2 `
  --date 20260817
```

The builder validates the controller and APK signatures, writes the major-image header, embeds both payloads, and then verifies every packaged byte against its input.

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
