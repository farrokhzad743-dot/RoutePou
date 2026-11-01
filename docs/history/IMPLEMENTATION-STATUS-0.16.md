# RoutePou 0.16.0-alpha — Windows companion UI refresh

## Delivered
- Replaced the developer-oriented Tkinter form with a Persian-first dark dashboard.
- Added a prominent connection state, guided pairing-code entry, clipboard paste, and strict QR-payload validation.
- Grouped the optional manual connection fields under an advanced section.
- Clearly displayed the local HTTP/HTTPS and SOCKS5 proxy endpoints.
- Moved the TLS reachability probe and Windows proxy configuration into a background thread so the UI remains responsive.
- Preserved the existing TLS certificate SHA-256 pinning, phone-side pairing token, and restoration of previous Windows proxy registry values on disconnect.

## What this increment does not deliver
- It does not add camera-based QR scanning. The Windows app accepts the decoded `routepou://pair?...` payload pasted from the clipboard or typed into the pairing field.
- It does not activate or supervise the WireGuard worker.
- It does not provide full-device routing, UDP forwarding, or a verified end-to-end VPN tunnel. The existing Windows bridge is an authenticated TLS TCP HTTP/SOCKS5 proxy.
- It does not show trustworthy live throughput or data-usage statistics; those require traffic accounting in the bridge and are not fabricated in this UI.

## Validation
- Python source syntax and project tests pass in the development environment.
- Windows GUI execution, registry restoration, PyInstaller packaging, and phone-to-PC connectivity still require testing on a Windows machine with a compatible Android build and hotspot.
