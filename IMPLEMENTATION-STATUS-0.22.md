# RoutePou 0.22.0-alpha — Data-plane acceptance gate

## Why this increment exists
The previous increments added pairing validation, Windows worker primitives, Wintun packet I/O and telemetry. They did not demonstrate that packets read from Wintun are encrypted to the phone and that decrypted packets are forwarded back into the Windows adapter. This release deliberately does not pretend that missing data-plane loop exists.

## Implemented
- Added a read-only, evidence-based end-to-end acceptance evaluator at `windows/e2e_acceptance.py`.
- The evaluator distinguishes `BLOCKED`, `HANDSHAKE_ONLY`, `DATA_PLANE_PARTIAL`, and `ACCEPTED`.
- A recent handshake is explicitly insufficient: TCP, UDP, DNS, IPv6 leak policy, fail-closed behavior, recovery and rollback must all be proven.
- Secret-bearing reports are rejected (private keys, QR payloads, pairing tokens).
- Added automated tests for incomplete, failed, secret-bearing and fully passing reports.
- Android version metadata advanced to 0.22.0-alpha / versionCode 22.

## Run
From repository root:

```bash
python -m pytest -q
python windows/e2e_acceptance.py examples/e2e-report.template.json --json
```

Exit code is `0` only for `ACCEPTED`; incomplete evidence returns `1`. Invalid or secret-bearing input returns `2`. The template is intentionally all-false and cannot produce a false pass.

## Physical test report
Create a copy of `examples/e2e-report.template.json` and set a check to `true` only after performing that test on the actual Android phone + Windows 10/11 pair. Do not infer a pass from adapter creation or a handshake. The `*_through_phone` checks require confirming the public egress IP is the phone's egress. `ipv6_no_leak` means IPv6 is either tunnelled and verified or blocked during full-tunnel mode.

## Critical architecture blockers found during source review
1. `windows/wintun_session.py` exposes Wintun packet read/write primitives, but there is no completed, integrated RX/TX data-plane loop that feeds packets into the WireGuard engine and injects decrypted packets back to Wintun.
2. `windows/wg-clinet/README-ROUTEPOU.md` says the worker is not yet launched by the current Windows GUI, while the Python supervisor assumes a worker protocol. The packaging/launch path needs a real Windows CI build and integration test.
3. The Android service starts the gomobile endpoint, but hotspot-client forwarding through Android's routing/NAT stack and VPN-provider compatibility have not been demonstrated.
4. Android `WireGuardEngine.validateIpc` requires `listen_port`, `public_key` and `allowed_ip`; those must match the exact endpoint-side IPC contract generated for the phone. Do not change these values ad hoc.
5. Current QR contains a client private key. Treat QR as a bearer secret; never place it in logs, issue trackers, screenshots, analytics or test reports.

## Not implemented / not claimed
- No automatic system routes, DNS, firewall or WFP changes are made by this stage.
- No full-tunnel readiness is claimed.
- No production kill switch is enabled.
- No real APK/EXE build or physical-device test is claimed by the local test run.

## Next engineering gate
Implement and review the complete Windows Wintun ↔ WireGuard packet loop and the phone-side forwarding/NAT path, then run the physical acceptance matrix. Only after the acceptance evaluator reports `ACCEPTED` with sanitized evidence should full-tunnel readiness be advertised.
