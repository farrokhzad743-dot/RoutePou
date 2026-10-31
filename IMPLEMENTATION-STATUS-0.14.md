# RoutePou 0.14.0-alpha — Android rebuild increment

## Changes in this increment
- Bumped Android package metadata to `0.14.0-alpha` / versionCode `14`.
- Made Java/Kotlin bytecode target explicit at Java 17.
- Declared the four Android ABIs expected from the gomobile AAR.
- Added explicit release ProGuard rules for the reflection-based `relaywg` bridge.
- Tightened Android application defaults: backup disabled, cleartext traffic disabled, RTL supported.
- Reworked Android GitHub Actions to install pinned SDK/NDK components, build and verify `relaywg.aar`, assemble both APK variants, verify their presence, and upload them as artifacts.
- Limited Android workflow triggers to Android/engine/build-script changes, while retaining manual dispatch and tagged releases.

## Important limitations
- This increment improves reproducibility of Android builds; it does not establish that the full WireGuard phone-to-Windows tunnel works.
- Release APK is still unsigned unless a signing workflow and protected signing secrets are configured. The debug APK is intended for testing only.
- A successful GitHub Actions run is still required to confirm that the gomobile AAR compiles with the pinned toolchain.
- Physical-device tests are still required, especially hotspot address discovery, foreground-service behavior, QR pairing, and a real WireGuard handshake.
- The alpha PKCS#12 asset and its embedded password remain a security issue to replace before public distribution.
