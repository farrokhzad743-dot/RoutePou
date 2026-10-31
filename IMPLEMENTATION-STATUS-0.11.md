# 0.11.0-alpha implementation status

Implemented in this increment:
- A versioned, bounded RoutePou QR payload format (`routepou://p/`).
- Strict validation of protocol version, mode, IPv4 host, port, WireGuard key shape and port consistency.
- Official WireGuard Android `KeyPair`-based per-session key generation.
- Matching WireGuard IPC builders for phone and Windows with shared addresses.
- A shared JSON contract and Python regression tests.

Not yet integrated or device-verified:
- The Android activity does not yet invoke key generation, create the QR from this new payload, or start the Go endpoint with the generated server config.
- The Windows GUI does not yet decode the new QR or launch `RoutePou-WgClient.exe` via a supervised named pipe.
- No Android hotspot + VPN provider end-to-end test has been run.
- No leak-protection claim is made for this release.

The Windows worker is intentionally not configured to persist private keys. The next step is a named-pipe supervisor that streams IPC config into the elevated worker and waits for the real handshake readiness message before showing Connected.
