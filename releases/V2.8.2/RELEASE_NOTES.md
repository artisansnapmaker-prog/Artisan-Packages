# Artisan V2.8.2 community build

This prerelease combines Snapmaker's official Artisan controller source, the USART2 linker fix, and the modified ARM HMI application.

## Included versions and changes

- Combined package version: `V2.8.2`.
- Controller runtime version: `V2.3.4-0624`; OTA component version: `V2.3.4`.
- Controller includes Snapmaker's latest dual-zone bed, enclosure-check, M2000 validation, and extruder-monitoring changes.
- HMI and LAN dashboard support bounded Orca/Prusa multiline G-code thumbnails while retaining Luban thumbnail support.
- FDM dashboard shows dual-nozzle, heated-bed, safety, and active-job information.
- Dashboard provides guarded pause, resume, and cancel controls.

## Choose an asset

- `SM3_V2.8.2_20260817.bin`: combined USB update for the controller and HMI.
- `A400_MC_V2.3.4_20260817.bin`: controller-only OTA image.
- `fabscreen-a400_1.8.0_orca-thumbnail-dashboard_armeabi-v7a_platform-signed.apk`: HMI-only Android package.
- `SHA256SUMS.txt`: checksums for all three update assets.

## Verification

The controller and bootloader were built from a clean checkout. The combined package was byte-for-byte verified against the packaged controller and APK inputs by `build_combined_package.py`.

> [!CAUTION]
> This is an unofficial community build. Keep the printer idle during an update, maintain uninterrupted power, and retain a known-good recovery package.
