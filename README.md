# RoutePou 0.26.0-alpha

RoutePou pairs an Android phone and Windows PC through a short-lived QR code. The Windows companion can scan the phone QR using a webcam, read a saved QR image, or import the QR text from the clipboard. Both apps offer dark and light appearances with a burgundy/crimson visual identity.

## Build artifacts
- Android: `.github/workflows/android-release.yml` builds an installable debug APK and an unsigned release APK.
- Windows: `.github/workflows/windows-release.yml` builds `RoutePou.exe` with QR camera/image decoding support.

Read `IMPLEMENTATION-STATUS-0.26.md` before testing. It documents the exact build steps and the difference between QR pairing, proxy mode, and the not-yet-device-validated full WireGuard tunnel.
