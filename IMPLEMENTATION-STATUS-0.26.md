# RoutePou 0.26.0-alpha — QR-first pairing and visual refresh

## User-facing changes
- Windows pairing is QR-first: scan the phone QR with a webcam, select a QR image (PNG/JPG/WebP), or paste QR text.
- No manual IP, port, token, or TLS fingerprint entry is required in the normal pairing flow.
- A valid proxy QR imports the pairing fields and automatically starts the authenticated proxy bridge.
- A valid full-tunnel QR automatically enters the WireGuard connect path.
- Windows and Android provide dark/light appearance toggles using a minimal crimson/burgundy palette.
- Android version: 0.26.0-alpha / versionCode 26.

## Build pipeline
- Windows CI installs PyInstaller, `zxing-cpp`, Pillow, and OpenCV; it packages QR decoding support into `RoutePou.exe`.
- Android CI builds `app-debug.apk` (debug signing is automatic) and `app-release-unsigned.apk`.
- The debug APK is the installable test artifact. A distributable signed release requires the owner's private signing keystore; no fake signing key is supplied.

## Verified in this workspace
- Python unit tests: 65 passed.
- Windows Python sources: syntax compilation passed.
- ZIP archive structure: checked after packaging.

## Not verified here
- No real APK or Windows EXE was built in this Linux workspace: Android SDK/NDK/Gradle and a Windows build runner are not available here.
- No physical Android/Windows pairing, real TCP/UDP data-plane test, packet capture, or VPN leak test was performed.
- QR scanning is implemented for webcam, saved image, and clipboard. Webcam scanning requires a working camera and is packaged by the Windows CI workflow.
- The proxy QR establishes the authenticated TLS proxy bridge. It does not automatically route every Windows application or all device traffic through a VPN.
- Full WireGuard mode remains dependent on a successful phone engine, Windows worker, Wintun, elevation, handshake, and data-plane validation. Do not treat the GUI state alone as proof of a working full tunnel.

## Build and install
1. Push this source tree to the GitHub repository's `main` branch (or run both workflows manually from Actions).
2. Run `RoutePou Android CI and Release` and `RoutePou Windows CI and Release`.
3. Download the `RoutePou-Android-0.26-*` and `RoutePou-Windows` workflow artifacts.
4. Install `app-debug.apk` on Android and run `RoutePou.exe` on Windows.
5. On Android, enable hotspot and tap **Start Proxy**. Keep the QR visible.
6. On Windows, choose **Scan with camera** (or select a QR screenshot). A valid proxy QR should start pairing automatically.
7. Test with a browser/application configured to use the RoutePou system proxy. Confirm the phone-side counters and external IP before relying on it.
