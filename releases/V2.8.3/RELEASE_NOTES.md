# Artisan V2.8.3 community build

This release combines the unchanged Snapmaker Artisan V2.3.4 controller image with the latest platform-signed ARM HMI application from [Screen App PR #2](https://github.com/artisansnapmaker-prog/Snapmaker-Artisan-Screen-App/pull/2).

## Included versions

- Combined package version: `V2.8.3`.
- Controller runtime version: `V2.3.4-0624`; OTA component version: `V2.3.4`.
- Android screen version: `1.8.0` (`versionCode` 1), package `com.snapmaker.fabscreena400`.
- The controller image is byte-identical to V2.8.2; the screen application is the updated component.

## Screen application changes

- Adds Dashboard, Files, G-code Console, Bed Mesh, and Settings views to the LAN interface.
- Adds compact G-code thumbnails, detailed file information, print start controls, and bounded Orca metadata parsing for large files.
- Shows only the nozzles used by a job and supports the original HMI-style nozzle-diameter warning decision.
- Adds configurable temperature and cooling history, enclosure LED and exhaust controls, themes, font sizing, and routine-console-message suppression.
- Shows the measured 9 × 9 bed mesh in 2D and an interactive mouse/touch-draggable 25 × 25 interpolated surface in 3D.
- Keeps printing and calibration behavior aligned with the native HMI, including operation with the enclosure door open.

## Choose an asset

- `SM3_V2.8.3_20260915.bin`: combined USB update for the controller and HMI.
- `A400_MC_V2.3.4_20260817.bin`: unchanged controller-only OTA image.
- `fabscreen-a400_1.8.0_enhanced-dashboard_armeabi-v7a_platform-signed.apk`: standalone HMI Android package.
- `SHA256SUMS.txt`: checksums for all three binary assets.

## Verification

The combined package was byte-for-byte verified against the packaged controller and APK inputs by `build_combined_package.py`. The APK is zip-aligned, contains only the Artisan `armeabi-v7a` native ABI, and uses the same platform signing certificate as V2.8.2 (`C8A2E9BCCF597C2FB6DC66BEE293FC13F2FC47EC77BC6B2B0D52C11F51192AB8`). The Screen App base test suite passed 100/100 tests and the build was smoke-tested on an idle Artisan.

> [!CAUTION]
> This is an unofficial community build. Keep the printer idle during an update, maintain uninterrupted power, and retain a known-good recovery package. The LAN dashboard is intended for trusted local networks.
