# RoutePou 0.18.0-alpha — Connection diagnostics

## Delivered
- Added `windows/connection_diagnostics.py`, a read-only preflight report for Windows 10/11.
- Checks OS, worker executable, Wintun runtime, default gateway visibility, adapter enumeration, and IPv4 route-table readability.
- Supports human-readable Persian output and machine-readable JSON (`--json`).
- Added automated tests proving the diagnostic path does not invoke route/firewall mutation commands.

## Run on Windows
From the project root:

```powershell
python windows/connection_diagnostics.py --worker windows/relaywg-client.exe
python windows/connection_diagnostics.py --worker windows/relaywg-client.exe --json
```

Exit code `0` means the static prerequisites were found; `2` means one or more prerequisites are missing. This is a preflight check only. It does not establish a WireGuard handshake, prove that phone hotspot clients are routed through Android's VPN, or validate leak protection.

## Validation performed in this environment
- `python -m pytest -q`: **36 passed**.
- Python syntax/import exercised by pytest.
- Windows executable, Wintun driver, Android handset, real UDP handshake, DNS/IPv6 behavior, and end-to-end traffic were not executable in this environment and remain release gates.

## Safety
The diagnostics are read-only. They do not add/delete routes, change DNS, alter firewall policy, or enable a kill switch. Do not treat `ready=true` as proof that the VPN is connected.
