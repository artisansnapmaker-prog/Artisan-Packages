# Artisan V2.8.1 community build

This prerelease combines the V2.8.1 Artisan controller firmware with the modified ARM HMI application.

## Included changes

- Controller reports firmware version `V2.8.1`.
- HMI and LAN dashboard support bounded Orca/Prusa multiline G-code thumbnails while retaining Luban thumbnail support.
- FDM dashboard shows dual-nozzle, heated-bed, safety, and active-job information.
- Dashboard provides guarded pause, resume, and cancel controls.

## Choose an asset

- `SM3_V2.8.1_20260817.bin`: combined USB update for the controller and HMI.
- `A400_MC_V2.8.1_20260817.bin`: controller-only image.
- `fabscreen-a400_1.8.0_orca-thumbnail-dashboard_armeabi-v7a_platform-signed.apk`: HMI-only Android package.

## Verification

Verify the assets with [`SHA256SUMS.txt`](SHA256SUMS.txt) before installation. The combined package was byte-for-byte verified against the controller and APK inputs by `build_combined_package.py`.

> [!CAUTION]
> This is an unofficial community build. Keep the printer idle during an update, maintain uninterrupted power, and retain a known-good recovery package.
