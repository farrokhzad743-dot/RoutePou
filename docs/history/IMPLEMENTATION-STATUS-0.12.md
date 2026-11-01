# RoutePou 0.12.0-alpha implementation status

## Implemented in this increment
- Kotlin reflection bridge calls the gomobile package API names used by Relay's mobile.go.
- IPC input validation rejects empty, oversized, malformed, missing and duplicate fields.
- Windows parser decodes `routepou://p/` v1 QR payloads and validates scheme, version, private IPv4 hotspot address, port, 32-byte WireGuard keys, DNS and full-tunnel AllowedIPs.
- Windows IPC config is returned as an in-memory string; no private-key file is written.
- Five Python provisioning tests.

## Not yet complete / not claimed
- MainActivity/Android service does not yet start the Relay endpoint from a generated QR payload.
- Windows desktop UI does not yet launch/elevate the worker and feed the config over its named pipe.
- No end-to-end WireGuard handshake has been performed on physical devices.
- Android hotspot-to-VPN behavior depends on the VPN provider exposing a local SOCKS5 upstream; default-route forwarding may bypass the phone VPN.
- No production Kill Switch or leak-proof claim.

## Validation
Run from repository root: `python -m unittest discover -s tests -v`.
Run Go tests separately in `third_party/relay-wg` with Go 1.25+: `go test ./...`.
