# Changelog

## 0.13.0-alpha
- Connected Android Full Tunnel controls to a dedicated foreground WireGuard endpoint service.
- Generate a fresh server/client WireGuard key pair, start the phone endpoint through the Relay gomobile bridge, and display a versioned pairing QR for Windows.
- Added explicit stop handling and endpoint notifications.
- Android versionCode 13 / versionName 0.13.0-alpha.
- Windows worker supervision and end-to-end handshake remain pending; see IMPLEMENTATION-STATUS-0.13.md.

## 0.12.0-alpha
- Hardened Android gomobile bridge validation and added Windows QR-to-IPC provisioning parser.
