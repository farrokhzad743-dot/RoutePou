# RoutePou 0.23.0-alpha — Worker supervision & fail-closed session lifecycle

## Scope
This increment closes a concrete integration gap in the Windows GUI/controller: after receiving `READY`, the controller previously stopped reading the worker's named-pipe stream. It could therefore continue displaying a connected state after the privileged worker had exited or the phone peer had gone away.

## Implemented
- The Windows supervisor now continues consuming worker events after the first successful handshake.
- `PEER-LOST` and `PEER-BACK` are surfaced to the UI.
- Unexpected worker/pipe termination clears the supervisor's connected state and invokes an exit callback.
- The Windows GUI reports peer loss as a degraded/error state and reports recovery separately.
- Full-tunnel worker launch now enables the worker's existing `-hold-on-loss` mode. This keeps the tunnel route/filter lifecycle alive during peer loss rather than silently falling back to the physical adapter; the worker still owns teardown when the parent pipe closes.
- DNS passed to the elevated worker is validated as a literal IPv4/IPv6 address before it is interpolated into arguments.
- Added regression tests for supervision, fail-closed flag selection and UI event handling.

## Important limitation
This does **not** complete or prove Android hotspot forwarding/NAT, nor does it prove public egress through the phone. The Go worker contains the Wintun + WireGuard userspace tunnel path, but the complete Android-side forwarding and real device-to-device data-plane acceptance remain unverified. `READY` still means a WireGuard handshake, not proof that arbitrary Windows traffic reaches the public internet through the phone.

## Validation
Run from repository root:

```bash
python -m pytest -q
```

Windows-only validation still required:
- Build `relaywg-client.exe` with the Windows CI workflow.
- Exercise named-pipe READY / PEER-LOST / PEER-BACK / pipe-close lifecycle on Windows 10/11.
- Verify that peer loss does not leak traffic and that disconnect removes the adapter/routes/filters.
- Confirm Android hotspot forwarding/NAT, TCP, UDP, DNS and IPv6 behavior on physical devices.

No APK/EXE build or physical-device test is claimed by this source-level increment.
