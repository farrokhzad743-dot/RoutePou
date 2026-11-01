# RoutePou Windows WireGuard client

This is the privileged tunnel worker adapted from the Relay reference project.
It creates a Wintun adapter and configures WireGuard from an IPC stream. Run it
only from the RoutePou desktop controller after the user explicitly chooses
Full Tunnel and approves elevation.

The phone's server tunnel address is `10.13.37.1`; the Windows client address
is `10.13.37.2/32`; MTU is 1420; the default route is `0.0.0.0/0`.

The controller must keep the named-pipe stream open for the whole session and
must not write the private key to disk, command-line arguments, or logs. Closing
the pipe is the worker's teardown signal. `READY` is emitted only after a
WireGuard handshake. A missing handshake is not a connected state.

This executable is launched, elevated, by `windows/wg_supervisor.py` (named-pipe session) when the user chooses Full Tunnel in the RoutePou GUI. CI builds it to `windows/relaywg-client.exe` and bundles it into `RoutePou.exe`.
