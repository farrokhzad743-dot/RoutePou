# Changelog

## 0.27.0-beta — Release readiness
### Security
- **Removed the shared TLS identity.** Earlier builds shipped one PKCS#12 keystore (with its password in the source) inside every APK, so anyone holding the APK could impersonate any phone. Each installation now generates its own EC key and self-signed certificate inside the Android Keystore; the key never leaves the device. "New pairing key" also rotates the certificate.
- Proxy byte counter is now thread-safe; proxy startup failures are logged instead of silently swallowed.
- Windows: the system proxy setting is restored on any normal interpreter exit, not only when the window is closed.

### Build and release
- One workflow (`.github/workflows/build.yml`) runs tests, builds the Android APK and `RoutePou.exe`, and on a `v*` tag publishes a GitHub Release with SHA-256 checksums. The three earlier workflows disagreed about paths and could not both succeed.
- Fixed the `windows/wg-clinet` directory typo (now `windows/wg-client`) that broke the Windows build.
- Android release APK is signed from CI secrets (`ANDROID_KEYSTORE_BASE64`, …); without them it falls back to the debug key so it stays installable. `scripts/make-android-keystore.sh` creates the key.
- Added Android launcher icon, Windows `.ico`, `LICENSE` (GPL-3.0), `SECURITY.md`, `docs/RELEASING.md` and a rewritten README.
- Moved the per-version status notes to `docs/history/`; removed stray files and caches from the tree.
- `VERSION` is the single source of truth, checked by tests against Gradle, the Windows app and the changelog.
- `scripts/build-wg-aar.sh` now also verifies 16 KB page alignment of the native libraries.

### Not changed
- Real-device pairing, data-plane and leak testing of the full WireGuard tunnel are still outstanding; this stays a pre-release.

## 0.13.0-alpha
- Connected Android Full Tunnel controls to a dedicated foreground WireGuard endpoint service.
- Generate a fresh server/client WireGuard key pair, start the phone endpoint through the Relay gomobile bridge, and display a versioned pairing QR for Windows.
- Added explicit stop handling and endpoint notifications.
- Android versionCode 13 / versionName 0.13.0-alpha.
- Windows worker supervision and end-to-end handshake remain pending; see IMPLEMENTATION-STATUS-0.13.md.

## 0.12.0-alpha
- Hardened Android gomobile bridge validation and added Windows QR-to-IPC provisioning parser.

## 0.14.0-alpha
- Rebuilt Android CI around pinned SDK/NDK components and verified AAR/APK outputs.
- Updated Android build metadata, ABI declarations, Java 17 targets, and reflection keep rules.
- Hardened application defaults by disabling backup and cleartext traffic.


## 0.15.0-alpha
- Replaced the plain Android form with a responsive dark dashboard and card-based layout.
- Grouped full-tunnel and TLS proxy actions into separate, clearly labeled connection modes.
- Added connection-state messaging, hotspot address summary, QR pairing panel, and pairing-key rotation control.
- Added button state handling to reduce accidental duplicate starts/stops.
- Kept the existing Android services, pairing payload formats, and QR encoding flow.
- Clarified alpha limitations: proxy mode is not a system-wide VPN and a requested WireGuard start is not proof of a completed Windows handshake.
- Android versionCode 15 / versionName 0.15.0-alpha.

## 0.16.0-alpha
- Redesigned the Windows companion as a guided Persian-first dashboard with clearer connection status, pairing-code import, and proxy endpoint cards.
- Added one-click paste from clipboard for decoded RoutePou pairing payloads and kept strict payload validation.
- Moved the phone TLS probe and Windows proxy setup off the UI thread to keep the window responsive while connecting.
- Added explicit alpha limitation messaging: this Windows client still operates the TLS HTTP/SOCKS5 TCP proxy bridge, not the full-device WireGuard tunnel.
- Kept Android source at 0.15.0-alpha; this increment is focused on the Windows companion.

## 0.17.0-alpha — Windows WireGuard bridge integration
- Integrated the existing Windows WireGuard worker with a per-session named-pipe supervisor.
- Added full-tunnel QR import and separate WireGuard connect/disconnect controls.
- Connected status now waits for the worker's post-handshake `READY` signal.
- Added Windows CI build/package steps for the Go worker and official Wintun runtime.
- Kept legacy TLS proxy mode separate and available.

## 0.19.0-alpha
- Added read-only WireGuard peer telemetry from `wg show <interface> dump`.
- Added handshake freshness classification and real peer RX/TX counters.
- Added a CLI report and parser regression tests; no network settings are modified.

## 0.20.0-alpha — Full-tunnel preflight
- Added a read-only Windows preflight for the privileged WireGuard worker, Wintun runtime, elevation, `wg` CLI, and adapter-query capability.
- Added JSON output for support diagnostics and explicit separation between prerequisite readiness and verified data-plane connectivity.
- No routes, DNS, firewall rules, adapters, or services are modified by the preflight.


## 0.21.0-alpha — Pairing hardening & end-to-end acceptance
- Enforced five-minute expiry and bounded clock skew for WireGuard QR pairing on Android and Windows.
- Rejected loopback, link-local and multicast private IPv4 endpoints in Windows provisioning.
- Added a detailed physical-device acceptance procedure covering handshake, TCP/UDP, DNS, IPv6, leak protection, recovery and rollback.
- Android versionCode 21 / versionName 0.21.0-alpha.

## 0.22.0-alpha — Data-plane acceptance gate
- Added read-only evidence evaluator distinguishing blocked, handshake-only, partial and fully accepted states.
- Requires TCP, UDP, DNS, IPv6 leak policy, fail-closed, recovery and rollback evidence beyond handshake.
- Rejects secret-bearing reports; added sanitized test-report template and regression tests.
- No route/DNS/firewall changes and no claim of a working full tunnel.

## 0.25.0-alpha
- Added explicit optional loopback SOCKS5 upstream configuration to Android Full Tunnel startup.
- Passed the selected upstream through the foreground service into the gomobile WireGuard engine.
- Added strict loopback-only validation; no remote proxy or credentials are accepted.

## 0.26.0-alpha — QR-first pairing and visual refresh
- Windows QR-first pairing: scan the phone QR with a webcam, select a saved QR image, or paste QR text.
- A valid proxy QR now imports all pairing fields and starts the proxy bridge automatically; a full-tunnel QR starts the WireGuard connection path.
- Added dark/light appearance toggle with a crimson/burgundy palette to Windows and Android.
- Added QR scanner runtime dependencies to the Windows PyInstaller workflow.
- Added acceptance notes that distinguish source/CI build from real device connectivity validation.
