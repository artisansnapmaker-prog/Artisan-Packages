# Artisan V2.8.4 community build

This release combines the unchanged Snapmaker Artisan V2.3.4 controller image with the latest platform-signed ARM FabScreen application from the [`codex/camera-obico-integration`](https://github.com/artisansnapmaker-prog/Snapmaker-Artisan-Screen-App/tree/codex/camera-obico-integration) branch.

## Included versions

- Combined package version: `V2.8.4`.
- Controller runtime version: `V2.3.4-0624`; OTA component version: `V2.3.4`.
- Android screen version: `1.8.0` (`versionCode` 1), package `com.snapmaker.fabscreena400`.
- The controller image is byte-identical to V2.8.3; the screen application is the updated component.

## Screen application changes

- Adds direct support for USB UVC, LAN MJPEG, and LAN RTSP cameras, with separately saved MJPEG and RTSP addresses, selectable output resolution and frame rate, and an optional larger camera view on the Dashboard.
- Adds direct Obico integration without a Raspberry Pi: six-digit manual linking, printer status and temperature telemetry, Artisan file browsing, cloud G-code download/start, allowlisted remote controls, snapshots for AI monitoring, and Janus-compatible WebRTC live viewing.
- Keeps temperature and fan history on FabScreen so the Dashboard graph remains continuous while the browser is closed or backgrounded.
- Adds installable-web-app icons and manifest data for browser tabs and Android home-screen shortcuts.
- Restores the user's enclosure LED brightness after a power cycle when Auto Lighting is enabled.

## Recommended cameras

- **Best default — USB UVC with hardware MJPEG:** choose a standards-compliant UVC webcam that advertises MJPEG at 1280×720. It gives the simplest setup and usually the lowest latency. Cameras that expose only uncompressed YUYV are intentionally limited to 640×480 at 5 FPS to protect the Artisan screen's CPU and USB bandwidth.
- **Best wireless option — local H.264 RTSP:** choose a camera with a configurable local RTSP stream and a lower-resolution substream. The Tapo C110 has been tested; its standard-quality `stream2` is a good responsive live-view choice. Use a dedicated camera account and confirm the exact path and native stream resolution in the camera documentation or firmware.
- **MJPEG IP camera — compatibility fallback:** useful for simple or older LAN cameras when RTSP is unavailable, but MJPEG consumes more network bandwidth than H.264 and often provides weaker authentication options.

## RTSP limitations

- Use a full camera-specific URL such as `rtsp://USERNAME:PASSWORD@IP_ADDRESS:554/stream_path`. FabScreen requires a numeric private-LAN address and a non-empty stream path. `stream1` and `stream2` are not universal names, and reserved characters in credentials must be percent-encoded.
- Use H.264 at no more than 1920×1080. The Artisan decoder supports up to 1920×1088, but a larger or unsupported camera stream can fail before FabScreen has a chance to resize it.
- **Output resolution** controls the JPEG frames produced after decoding; it does not change the resolution or bitrate sent by the camera. Configure the camera's own main/substream settings separately.
- Higher resolution and frame rate increase decoding, resizing, memory, and WebRTC load on the Artisan. For responsive monitoring, prefer 1280×720 at a modest frame rate. For timelapses, select a higher output resolution and lower frame rate.
- RTSP traffic is not encrypted. Use it only on a trusted LAN, preferably with a dedicated camera account. FabScreen stores the URL in the Android Keystore and does not return it through the Dashboard API.
- Obico Free live viewing has service-side limits independent of the camera: up to 5 FPS for a 30-second live-view cycle followed by a cooldown. AI failure detection uses separately uploaded snapshots and is not guaranteed merely by having a live WebRTC feed.

## Choose an asset

- `SM3_V2.8.4_20260919.bin`: combined USB update for the controller and HMI.
- `A400_MC_V2.3.4_20260817.bin`: unchanged controller-only OTA image.
- `fabscreen-a400_1.8.0_camera-obico_armeabi-v7a_platform-signed.apk`: standalone HMI Android package.
- `SHA256SUMS.txt`: checksums for all three binary assets.

## Verification

The combined package was byte-for-byte verified against the packaged controller and APK inputs by `build_combined_package.py`. The APK is zip-aligned, contains only the Artisan `armeabi-v7a` native ABI, and uses the same platform signing certificate as V2.8.3 (`C8A2E9BCCF597C2FB6DC66BEE293FC13F2FC47EC77BC6B2B0D52C11F51192AB8`). The Screen App base suite completed 221 tests with 2 skipped, the Obico WebRTC bridge tests passed, and the package-builder suite passed 10/10 tests.

> [!CAUTION]
> This is an unofficial community build. Keep the printer idle during an update, maintain uninterrupted power, and retain a known-good recovery package. Camera and Dashboard access should be limited to trusted networks.
