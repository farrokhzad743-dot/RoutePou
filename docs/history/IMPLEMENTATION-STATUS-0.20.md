# RoutePou 0.20.0-alpha — Full-tunnel preflight

## Delivered
- Added `windows/full_tunnel_preflight.py`, a read-only prerequisite check for Windows 10/11.
- Checks worker and Wintun runtime files, elevation state, `wg` CLI availability, and whether Windows adapter enumeration can be queried.
- Supports human-readable Persian output and `--json` for support diagnostics.
- Explicitly reports `data_plane_verified: false`; preflight readiness is not a VPN connection claim.
- Added unit tests for missing runtime files, positive file detection, and JSON serialization.

## Safety
- The preflight does not create adapters, change routes, configure DNS, edit firewall policy, or start/stop services.
- It does not collect private keys, QR payloads, or other pairing secrets.

## Remaining blockers before claiming a working full tunnel
- The phone-side WireGuard server must be running and reachable over the hotspot.
- A fresh handshake must be verified on physical Android and Windows devices.
- Packet forwarding must be proven with controlled IPv4 and IPv6 TCP/UDP tests.
- DNS behavior, IPv6 leak behavior, route rollback, and kill-switch behavior need independent tests.
- The GUI-to-worker lifecycle and disconnect cleanup must be verified on Windows 10/11.

## Validation
Run `python -m pytest -q`. Live preflight requires Windows. This environment cannot certify physical-device forwarding or Windows driver behavior.
