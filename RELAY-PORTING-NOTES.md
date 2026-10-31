# RoutePou v0.9.0-alpha — Relay-based WireGuard integration baseline

This release changes direction from the experimental Python packet framing code to the real, tested architecture found in the user-supplied Relay source archive.

## What was brought in

- `third_party/relay-wg/`: the Relay phone-side userspace WireGuard endpoint and gVisor TCP/UDP forwarding stack, copied intact for attribution and license compliance.
- `windows/wg-client/`: the Relay Windows WireGuard/Wintun client process, copied intact. It owns the privileged adapter and route lifecycle in a child process rather than embedding elevation in the UI.
- `shared/relay-wg-test-vectors.json`: shared IPC configuration test vectors.
- `scripts-build-wg-aar.reference.sh`: upstream Android AAR build script for reference.

## Architecture learned from Relay

Windows virtual IP packets -> Wintun -> wireguard-go client -> encrypted WireGuard UDP -> Android endpoint -> gVisor TCP/UDP forwarders -> ordinary Android sockets.

This is important: Android does not need root or iptables. The phone terminates WireGuard in userspace and opens outbound sockets. Whether those sockets traverse a third-party VPN depends on Android VPN routing/per-app exclusions and the VPN provider. Relay's upstreamProxy hook exists for VPN clients that expose a local SOCKS5 proxy; this must be configured deliberately, not assumed.

## Important status: integration baseline, not a finished full-tunnel release

The upstream Go sources are vendored as a reference baseline, but RoutePou's existing Kotlin app does not yet invoke the gomobile AAR, and the Python desktop UI does not yet launch/configure `relaywg-client.exe`. The current QR payload is not yet the WireGuard peer configuration contract. Do not advertise v0.9 as working full-device VPN until those adapters are implemented and cross-platform tests pass.

The copied upstream Go module declares Go 1.25.0. Local environment used for preparation may have an older Go toolchain; CI is configured to use Go 1.25. Windows client builds must run on Windows or cross-compile with the required Windows toolchain. Android AAR requires Android NDK + gomobile.

## Build/test commands

Phone engine (Go 1.25+):

```sh
cd third_party/relay-wg
go test ./...
```

Windows tunnel client (Go 1.25+):

```powershell
cd windows/wg-client
go test ./...
go build -o RoutePou-WgClient.exe .
```

Android AAR: inspect and adapt `scripts-build-wg-aar.reference.sh`; do not run a release build until the Kotlin bridge and Android NDK toolchain are wired into CI.

## Safety

- No routes or DNS are changed by the existing RoutePou Python app as part of this baseline.
- The upstream Windows client can alter system networking when run elevated. Only run it on a test machine with a recovery path.
- Kill switch / leak blocking must remain off until RoutePou has verified the actual installed WFP/route protection path and can prove teardown/rollback.
- Use official Wintun distributions only; do not bundle DLLs from unofficial mirrors.
