# RoutePou 0.17.0-alpha — Windows WireGuard bridge integration

## Delivered in source
- Added a Windows named-pipe supervisor for the privileged WireGuard worker.
- The desktop controller creates a per-session random pipe name, requests UAC elevation, sends WireGuard IPC configuration over the pipe, and keeps the pipe open for the tunnel lifetime.
- The peer private key is not written to a file, command-line argument, or log.
- Added recognition of the Android full-tunnel QR contract (`routepou://p/`) while retaining the legacy TLS proxy QR (`routepou://pair?...`).
- Added separate full-tunnel connect/disconnect controls. The UI reports connected only after the worker reports `READY`, which is emitted after a WireGuard handshake.
- Windows CI now builds the Go worker, packages the official Wintun runtime, runs tests, and bundles both with the desktop executable.

## Important limitations / release gates
- This increment is source-integrated; the current execution environment is not Windows and cannot validate UAC, named-pipe ACL behavior, Wintun adapter creation, route installation, or a real Android-to-Windows handshake.
- The Android QR contains a per-session Windows client private key. Treat it as a password; do not share screenshots or copied QR payloads.
- The phone endpoint forwards traffic through the phone's default network. Whether that is the intended egress (including any Android VPN) depends on the phone's network/VPN configuration and must be tested on-device.
- Windows full tunnel currently configures IPv4 default routing. The worker now fails closed if Windows leak protection cannot be installed.
- The full tunnel worker needs administrator approval to create the Wintun adapter and install routes.
- The old TLS HTTP/SOCKS5 proxy remains a separate mode and is not the full tunnel.
- The APK build and Android service lifecycle have not been changed in this increment; Android still needs a fresh CI build and physical-device validation.

## Validation
- Python source syntax and unit tests are run in CI.
- A successful source test does not establish Windows driver availability or end-to-end tunnel functionality.
