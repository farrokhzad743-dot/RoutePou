# RoutePou 0.15.0-alpha — Android UI refresh

## Delivered in this increment
- Replaced the developer-style vertical form with a responsive dark dashboard.
- Added separate, labeled cards for connection status, hotspot/network address, full WireGuard tunnel, TLS proxy, and Windows QR pairing.
- Added Persian guidance for setup and security-sensitive QR handling.
- Added explicit start/stop button states and a pairing-key rotation action.
- Preserved existing service intents, QR payload formats, and key generation calls.
- Bumped Android package metadata to versionCode 15 / versionName 0.15.0-alpha.

## Validation and limitations
- Source-level review only; a real Android Gradle build and physical-device run are still required.
- The dashboard reports a requested service start, not a verified end-to-end tunnel.
- Proxy mode remains an app-configured HTTP/SOCKS proxy, not a system-wide VPN.
- Hotspot IPv4 discovery remains heuristic and must be validated across Android OEMs.
- The existing embedded PKCS#12 certificate/password remains a release-blocking security issue.
- The QR payload includes sensitive pairing material; do not share screenshots or QR images.
- Windows pairing/worker integration and a real WireGuard handshake are not completed by this UI increment.
