# RoutePou 0.24.0-alpha — Android upstream monitoring

## Scope delivered

- Added `AndroidUpstreamMonitor`, an Android `ConnectivityManager` observer.
- Reports whether the current default network advertises Internet and whether Android has validated it.
- Identifies the default transport (Wi-Fi, cellular, Ethernet, VPN, other).
- Registers/unregisters the network callback with the WireGuard foreground service lifecycle.
- Updates the foreground notification when default-network state changes.
- Bumped Android app metadata to 0.24.0-alpha / versionCode 24.

## Important architecture distinction

The phone-side relay uses a userspace WireGuard/netstack endpoint. Its outbound forwarding is performed by ordinary Go sockets or by an explicitly configured SOCKS5 upstream (`StartEndpointVia`). This is not Android tethering NAT, and this change does not implement kernel IP forwarding, hotspot NAT, or an Android `VpnService`.

The monitor is observational only. `NET_CAPABILITY_VALIDATED` is a useful OS signal, not proof that the Windows peer's packets traverse the desired upstream. A validated cellular/Wi-Fi default route can still differ from a VPN client's policy. To send forwarded flows through a third-party VPN, the SOCKS5 upstream must be configured and verified for both TCP CONNECT and UDP ASSOCIATE. The current UI does not yet expose that configuration end-to-end.

## Not claimed / remaining

- No real-device Android build or runtime test was performed in this environment.
- No verified TCP/UDP end-to-end forwarding result is claimed.
- No automatic hotspot configuration, NAT, DNS interception, IPv6 leak prevention, or kill switch was added.
- Android 10+ support still requires device/API-level testing; this project currently has `minSdk 26`.
- Notification text explicitly says traffic forwarding requires separate testing.

## Device acceptance plan

1. Build the AAR with `scripts-build-wg-aar.sh`, then run Android CI.
2. Start Full Tunnel while connected by cellular, then Wi-Fi; confirm the monitor reports the default transport.
3. Disable the default Internet network and confirm the notification changes to unavailable.
4. Restore connectivity and confirm the monitor recovers without falsely claiming a Windows data-plane pass.
5. With a configured SOCKS5 upstream, run TCP and UDP tests from the Windows peer and capture both sides.
6. Compare the peer's WireGuard counters with real external reachability tests; a handshake alone is not acceptance.
