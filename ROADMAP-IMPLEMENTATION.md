# RoutePou implementation status

## v0.8.0-alpha
- [x] IPv4/IPv6 base-header validation
- [x] MTU bounds and packet length validation
- [x] Length-prefixed packet framing primitives
- [x] Basic UDP destination-port 53 detection
- [x] Unit tests for packet validation/framing
- [ ] Connect packet engine to Wintun RX/TX worker loops
- [ ] Implement authenticated multiplexed transport on Android and Windows
- [ ] Android packet relay and tested tethering/VPN compatibility
- [ ] DNS forwarding end-to-end
- [ ] Transactional routes, rollback, IPv6 leak tests, then kill switch

## Safety gates
No full-tunnel mode or kill switch until the transport is integrated and tested
for IPv4, IPv6, TCP, UDP, DNS, VPN loss, hotspot loss, sleep/resume, and abrupt
process termination. Preserve the physical route to the phone for control traffic.
