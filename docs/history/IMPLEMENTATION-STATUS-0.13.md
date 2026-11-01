# RoutePou 0.13.0-alpha implementation status

## Implemented in this increment
- Added an Android foreground service dedicated to the Relay WireGuard endpoint. It owns endpoint lifetime and calls the gomobile bridge on start/stop.
- Added Full Tunnel start/stop actions to the Android screen.
- Android now creates a fresh WireGuard server/client key pair using the official WireGuard crypto library, builds the phone endpoint IPC configuration, and renders a versioned `routepou://p/` QR payload for the Windows peer.
- The pairing QR is generated only after a private hotspot IPv4 address is found. The payload contains a client private key; treat it like a password and do not share screenshots of it.
- Android app version metadata is now `0.13.0-alpha` / versionCode 13.

## Not yet complete / not claimed
- Windows GUI still does not supervise/elevate `relaywg-client`, host the authenticated named pipe, or feed the QR-derived IPC config to the worker. The Windows QR parser remains a tested provisioning component, not a connected UI flow.
- The gomobile AAR is not present in this source package by default. Full Tunnel start will explicitly report that the engine is unavailable until the AAR is built and packaged.
- No Android Gradle build was run in this environment (Gradle is not installed); no Android device test or real WireGuard handshake was performed.
- Android hotspot client traffic is not automatically routed through Android VPN. VPN-provider SOCKS5 upstream integration and provider-specific compatibility are still pending.
- No production kill switch, DNS leak protection, or leak-proof claim is made.

## Validation
- `python -m unittest discover -s tests -v` — 10 tests passed.
- ZIP integrity checked with `unzip -t`.
- Android compilation and physical-device validation remain required.
