# RoutePou 0.19.0-alpha — WireGuard telemetry

## Delivered
- Added a read-only parser for `wg show <interface> dump` output.
- Reports peer endpoint, allowed IPs, last handshake age, received/sent byte counters, and a freshness-based handshake indicator.
- Added a CLI (`python windows/wg_telemetry.py --interface RoutePou --wg windows/wg.exe`). Exit 0 means at least one peer has a handshake no older than 180 seconds; exit 3 means no fresh handshake; exit 2 means the command/output failed.
- Added parser tests for fresh, stale, never-established, malformed, and empty output.

## Important limitation
This is telemetry, not a packet-forwarding implementation or proof that Windows application traffic exits through the phone. It does not change routes, DNS, firewall rules, or enable a kill switch. The current worker/Android path still requires real-device verification for handshake, forwarding, DNS, IPv6, UDP, and leak behavior.

## Validation
Run `python -m pytest -q`. Live telemetry requires Windows and the matching official `wg.exe` binary.
