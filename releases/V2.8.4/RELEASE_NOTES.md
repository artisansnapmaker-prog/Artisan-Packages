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

- **Recommended for reliable live video — USB UVC with hardware MJPEG:** choose a standards-compliant UVC webcam that advertises MJPEG at 1280×720. Because the camera supplies JPEG frames directly, this gives the simplest setup and usually the best frame rate and lowest processing load. Cameras that expose only uncompressed YUYV are intentionally limited to 640×480 at 5 FPS to protect the Artisan screen's CPU and USB bandwidth.
- **Wireless alternative — direct MJPEG IP camera:** this avoids the H.264 decode-and-convert workload required by RTSP and can provide a more usable wireless live view. MJPEG consumes more network bandwidth than H.264 and cameras may provide weaker authentication options.
- **Experimental — H.264 RTSP:** use only when low frame rates are acceptable. In testing, a Tapo C110 `stream2` at its native 1280×720 fell to roughly 1 FPS after the Artisan screen decoded H.264 and converted frames to JPEG. The camera's higher-resolution stream exceeded the screen decoder's practical capability. RTSP is therefore not recommended for smooth live monitoring or time-critical Obico failure detection on this hardware.

## RTSP limitations

- The limiting device is the Artisan Android screen computer, not the motion-controller MCU or Marlin firmware. FabScreen must decode the RTSP H.264 stream, capture frames, and convert them to JPEG on this constrained hardware.
- Use a full camera-specific URL such as `rtsp://USERNAME:PASSWORD@IP_ADDRESS:554/stream_path`. FabScreen requires a numeric private-LAN address and a non-empty stream path. `stream1` and `stream2` are not universal names, and reserved characters in credentials must be percent-encoded.
- Even native 1280×720 input may achieve only about 1 FPS, as observed with the Tapo C110. The selected frame rate is a maximum request, not guaranteed throughput.
- Higher-resolution streams can exceed the decoder's practical capability and fail before FabScreen can resize them. Camera codec profile, bitrate, frame rate, and firmware also affect whether a stream can be decoded.
- **Output resolution** controls the JPEG frames produced after decoding; it does not reduce the resolution or bitrate entering the decoder. It cannot make an unsupported high-resolution source decodable, and selecting an output larger than the source only upscales the image. Configure the camera's own main/substream settings separately.
- Janus/WebRTC improves transport from FabScreen to a viewer, but it cannot increase the rate at which the Artisan screen decodes RTSP and produces JPEG frames. RTSP can still be useful for occasional snapshots or a low-rate timelapse when its performance is acceptable.
- RTSP traffic is not encrypted. Use it only on a trusted LAN, preferably with a dedicated camera account. FabScreen stores the URL in the Android Keystore and does not return it through the Dashboard API.
- Obico Free live viewing has service-side limits independent of this device-side RTSP bottleneck: up to 5 FPS for a 30-second live-view cycle followed by a cooldown. AI failure detection uses separately uploaded snapshots and is not guaranteed merely by having a live WebRTC feed.

## Choose an asset

- `SM3_V2.8.4_20260919.bin`: combined USB update for the controller and HMI.
- `A400_MC_V2.3.4_20260817.bin`: unchanged controller-only OTA image.
- `fabscreen-a400_1.8.0_camera-obico_armeabi-v7a_platform-signed.apk`: standalone HMI Android package.
- `SHA256SUMS.txt`: checksums for all three binary assets.

## Verification

The combined package was byte-for-byte verified against the packaged controller and APK inputs by `build_combined_package.py`. The APK is zip-aligned, contains only the Artisan `armeabi-v7a` native ABI, and uses the same platform signing certificate as V2.8.3 (`C8A2E9BCCF597C2FB6DC66BEE293FC13F2FC47EC77BC6B2B0D52C11F51192AB8`). The Screen App base suite completed 221 tests with 2 skipped, the Obico WebRTC bridge tests passed, and the package-builder suite passed 10/10 tests.

> [!CAUTION]
> This is an unofficial community build. Keep the printer idle during an update, maintain uninterrupted power, and retain a known-good recovery package. Camera and Dashboard access should be limited to trusted networks.
