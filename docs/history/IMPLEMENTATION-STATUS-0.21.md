# RoutePou 0.21.0-alpha — Pairing hardening & end-to-end acceptance

## Scope
This release does **not** claim that a full tunnel has been proven on physical devices. It closes a concrete security gap in the v1 pairing flow and adds a repeatable acceptance procedure so a successful handshake cannot be confused with working internet forwarding.

## Changes
- WireGuard QR payloads are now time-bounded: Windows rejects payloads older than 300 seconds and payloads more than 60 seconds in the future.
- Android decoder applies the same age and clock-skew policy.
- Windows rejects loopback, link-local and multicast endpoints in addition to non-private/non-IPv4 hosts.
- Private keys remain in-memory IPC only; do not log, persist, screenshot or share QR codes.
- Added tests for expired/future QR payloads and invalid loopback endpoint.

## End-to-end acceptance gates
Run these gates on a physical Android phone with hotspot enabled and a Windows 10/11 machine. A green result is required for every gate before calling RoutePou a working full-tunnel product.

1. **Pairing** — generate a new QR on the phone; scan it within five minutes; confirm stale QR is rejected and regenerate it.
2. **Endpoint reachability** — from Windows, verify the phone hotspot address is reachable and UDP 51820 is not blocked by the hotspot/device configuration.
3. **Handshake** — start the tunnel and verify a recent WireGuard handshake timestamp on both sides. Adapter creation alone is not success.
4. **IPv4 data plane** — test a known TCP endpoint and a UDP/DNS query; confirm Windows' public egress is the phone's egress, not the Windows network's egress.
5. **DNS** — query through the configured tunnel resolver and verify no parallel resolver request escapes on the physical adapter.
6. **IPv6** — confirm IPv6 is either routed through a separately verified IPv6 tunnel or blocked while full-tunnel mode is active; do not silently leave native IPv6 enabled.
7. **Leak protection** — while connected, temporarily stop the phone endpoint. Verify traffic fails closed and does not fall back to the Windows physical adapter.
8. **Recovery** — restore the phone endpoint and verify handshake recovery without leaving stale routes or filters.
9. **Disconnect/rollback** — disconnect normally and force-kill the worker in separate tests; verify adapter, routes, DNS settings and WFP filters are removed/restored.
10. **Regression** — repeat with hotspot reconnect, phone screen-off, Windows sleep/resume and a second pairing session.

## Evidence to collect (never include secrets)
- Windows and Android app version/build identifiers.
- Timestamped worker state transitions: STARTING, HANDSHAKE, READY, PEER-LOST, PEER-BACK, STOPPED.
- Handshake age and byte counters before/after a controlled test transfer.
- `route print` before, during and after the session.
- DNS leak test result and IPv4/IPv6 public egress result.
- Sanitized diagnostic JSON. Never attach QR contents, private keys, pairing tokens or TLS private material.

## Known blockers / honest status
- This repository has not been exercised on the user's physical Android/Windows pair in this environment.
- A WireGuard handshake proves peer reachability and key agreement, **not** that all Windows traffic is forwarded correctly.
- TCP, UDP, DNS, IPv6 leak prevention, WFP rollback and crash cleanup still require the physical acceptance gates above.
- Do not enable unattended kill-switch behavior or advertise production readiness until all gates pass.

## Automated validation
From repository root:

```bash
python -m pytest -q
```

Windows-only worker tests and Android Gradle build must also run in their respective CI runners. A local Python test pass is not evidence of Windows driver behavior or Android VPN-service behavior.
