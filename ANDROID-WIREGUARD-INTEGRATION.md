# Android WireGuard engine integration (0.10.0-alpha)

RoutePou now has a reproducible CI path to build `third_party/relay-wg` as
`android/app/libs/relaywg.aar` with gomobile. `WireGuardEngine.kt` is the
Kotlin-facing optional bridge for `StartEndpointVia`, `StopEndpoint`,
`IsRunning`, counters and handshake time.

## Local build prerequisites

- Go 1.25+
- Android SDK (set `ANDROID_HOME`)
- Android NDK r27+ (set `ANDROID_NDK_HOME`)
- Java 17 and Gradle 8.9

Run `./scripts-build-wg-aar.sh`, then build the Android app from `android/`.
CI performs these steps on every push, pull request and version tag.

## Current limitations — do not treat this as a finished VPN

- The Kotlin bridge is optional and deliberately does not start a tunnel by
  itself. A correctly generated WireGuard IPC server configuration and a
  matching Windows peer configuration are required.
- The app UI does not yet generate/exchange the peer keys or provision the
  Windows peer. Existing proxy controls remain separate from the WireGuard
  engine.
- Android VPN-app coexistence is not universal. The engine's upstream SOCKS5
  option must be configured to a local proxy exposed by the active VPN client;
  otherwise forwarding follows Android's ordinary default route.
- A real-device test over a phone hotspot, including TCP, UDP, DNS, reconnect
  and leak tests, is required before enabling this as a public feature.
- Do not enable a system-wide kill switch until routing rollback and leak
  prevention have passed Windows integration tests.

## License

The embedded Relay-derived engine is GPL-3.0. Distributions containing it must
comply with GPL-3.0, including corresponding-source and notice requirements.
