# RoutePou 0.13.0-alpha

RoutePou is being built to share a phone's network/VPN connection with a Windows PC over the phone hotspot. This alpha now connects the Android Full Tunnel controls to the phone-side WireGuard endpoint service and generates a matching Windows pairing QR.

## 0.13.0-alpha

- Android Full Tunnel start/stop controls call a dedicated foreground service.
- A fresh WireGuard key pair is generated using the official WireGuard crypto library.
- The phone endpoint IPC configuration is passed to the Relay gomobile bridge; the Windows peer QR is rendered from the same session keys.
- The endpoint service owns the tunnel lifetime and tears it down when stopped.
- See `IMPLEMENTATION-STATUS-0.13.md` for exact limitations and validation.

## 0.11.0-alpha

- Versioned `routepou://p/` WireGuard pairing payload with strict field checks.
- Per-session WireGuard key generation via the official Android WireGuard crypto API.
- Matching IPC configuration builders for the phone endpoint and Windows peer.
- Shared tunnel contract: phone `10.13.37.1`, Windows `10.13.37.2`, MTU 1420,
  UDP 51820, Windows route `0.0.0.0/0`, keepalive 25 seconds.
- Windows worker integration notes: private configuration must travel through
  a live named pipe and remain memory-only.

## Build

Android: Java 17, Android SDK, NDK r27+, Go 1.25+, gomobile and Gradle 8.9.
Run `./scripts-build-wg-aar.sh`, then `cd android && gradle assembleDebug`.

Windows worker: build/test on Windows with Go 1.25+ from `windows/wg-client`.
The worker needs Administrator permission to create Wintun and configure routes.

## Honest implementation status

This alpha adds the WireGuard provisioning contract and key/config primitives.
It is **not yet an end-to-end working full-device VPN**: the current Android screen
still uses the earlier proxy flow; the QR codec/key generator are not wired into
that screen; the Windows GUI does not yet supervise the worker through a named
pipe; and hotspot/VPN-provider compatibility has not been verified on devices.
Do not enable a system-wide kill switch until those pieces and leak tests pass.

The phone endpoint can forward through the phone's default route, or through a
VPN app's local SOCKS5 proxy if that VPN explicitly exposes one. Android does not
generally route hotspot clients through its own VPN automatically.

## Licensing

Relay-derived components are GPL-3.0. See `THIRD_PARTY_NOTICES.md` and the
license files before redistribution.
