# RoutePou packet tunnel — v0.8 engineering layer

`windows/packet_engine.py` adds strict IPv4/IPv6 packet validation, MTU checks,
DNS-over-UDP destination detection (basic headers only), and length-prefixed
packet framing suitable for a future authenticated stream transport.

## Current boundary

This is **not yet a working full-tunnel VPN**. The framing helpers are not yet
connected to the Android service or Wintun receive/send loops. IPv6 extension
headers, fragmentation/reassembly, ICMP error handling, UDP DNS relay on Android,
route installation, and transactional rollback remain unimplemented. No routes
or DNS settings are changed by this release.

## Intended data path

`Windows apps -> Wintun -> packet validator/framer -> authenticated transport -> Android relay -> supported Android VPN/tethering path`

Android VPN apps and OEM builds may exclude tethered traffic. RoutePou must test
that behavior on each target device; an ordinary Android app cannot guarantee
that hotspot-originated packets traverse an unrelated VPN app.

## Tests

Run from repository root:

```powershell
python -m unittest discover -s tests -v
```

Default MTU is 1280 to leave room for tunnel overhead. Do not raise it without
path-MTU and fragmentation tests.
