# RoutePou 0.25.0-alpha — explicit Android SOCKS5 upstream

## Delivered

- Added an optional Android UI field for a local SOCKS5 upstream (`host:port`).
- The value is validated before service launch and passed as an Intent extra; no proxy credentials are accepted or persisted.
- Only loopback endpoints (`127.0.0.1`, `localhost`) are accepted, with a bounded input length and valid TCP port range.
- `WireGuardService` now passes the selected upstream to the existing gomobile bridge (`StartEndpointVia`) instead of always starting with the default route.
- Empty field preserves the existing default-route behavior.
- Android version metadata updated to 0.25.0-alpha / versionCode 25.

## Important limits

- This configures the Go userspace forwarder's SOCKS5 upstream. It does not create Android tethering NAT, does not automatically discover a VPN app's local SOCKS port, and does not prove that the chosen listener belongs to a trusted VPN app.
- The Go SOCKS5 implementation supports TCP CONNECT and UDP ASSOCIATE in source, but compatibility depends on the specific VPN app. Many local SOCKS listeners support TCP only or expose UDP differently.
- SOCKS5 IPv6 literal parsing is not exposed in this UI; use IPv4 loopback or `localhost`.
- No real Android APK build, device runtime, packet capture, or TCP/UDP end-to-end acceptance was run in this environment.

## Device validation

1. Build and install the debug APK on Android 8+ (minSdk 26); Android 10+ remains the intended primary test range.
2. Test once with the upstream field empty; confirm default-route behavior.
3. Start a VPN app that explicitly documents a local SOCKS5 listener; enter its loopback host and port.
4. Verify that the VPN app's own status/counters show forwarded connections.
5. From the Windows peer, test TCP and UDP separately; capture packets on both ends.
6. Confirm external IP, DNS behavior, IPv6 behavior, and fail-closed behavior before describing this as a full-device VPN.
