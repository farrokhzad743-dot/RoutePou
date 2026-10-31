"""Read-only WireGuard handshake and traffic telemetry for RoutePou.

Consumes `wg show <interface> dump` output. It never changes routes, DNS,
firewall rules, interfaces, or tunnel state.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import argparse, json, subprocess, time
from pathlib import Path

@dataclass(frozen=True)
class PeerTelemetry:
    public_key: str
    endpoint: str
    allowed_ips: str
    handshake_epoch: int
    received_bytes: int
    sent_bytes: int
    keepalive_seconds: int
    handshake_age_seconds: int | None
    handshake_fresh: bool

@dataclass(frozen=True)
class TunnelTelemetry:
    interface: str
    listen_port: int
    peers: tuple[PeerTelemetry, ...]
    received_bytes: int
    sent_bytes: int
    handshake_ok: bool
    observed_at: int


def parse_wg_dump(raw: str, *, now: int | None = None, freshness_seconds: int = 180) -> TunnelTelemetry:
    now = int(time.time()) if now is None else int(now)
    lines = [line.split('\t') for line in raw.splitlines() if line.strip()]
    if not lines:
        raise ValueError('WireGuard dump خالی است.')
    if len(lines[0]) != 4:
        raise ValueError('ساختار سطر interface در خروجی wg نامعتبر است.')
    try:
        listen_port = int(lines[0][2])
    except ValueError as exc:
        raise ValueError('پورت WireGuard نامعتبر است.') from exc
    peers = []
    for row in lines[1:]:
        if len(row) != 8:
            raise ValueError('ساختار سطر peer در خروجی wg نامعتبر است.')
        key, _psk, endpoint, allowed, handshake, rx, tx, keepalive = row
        try:
            epoch, received, sent, keep = map(int, (handshake, rx, tx, keepalive))
        except ValueError as exc:
            raise ValueError('شمارنده‌های WireGuard نامعتبر هستند.') from exc
        age = max(0, now - epoch) if epoch else None
        peers.append(PeerTelemetry(key, endpoint, allowed, epoch, received, sent,
                                   keep, age, age is not None and age <= freshness_seconds))
    return TunnelTelemetry('active', listen_port, tuple(peers),
        sum(p.received_bytes for p in peers), sum(p.sent_bytes for p in peers),
        any(p.handshake_fresh for p in peers), now)


def read_telemetry(wg_path: str, interface: str, *, timeout: int = 5) -> TunnelTelemetry:
    proc = subprocess.run([wg_path, 'show', interface, 'dump'], capture_output=True,
                          text=True, timeout=timeout, check=False,
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if proc.returncode:
        detail = (proc.stderr or 'wg command failed').strip()[:300]
        raise RuntimeError(detail)
    return parse_wg_dump(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description='RoutePou read-only WireGuard telemetry')
    parser.add_argument('--wg', default=str(Path(__file__).with_name('wg.exe')))
    parser.add_argument('--interface', default='RoutePou')
    args = parser.parse_args()
    try:
        report = read_telemetry(args.wg, args.interface)
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 2
    data = asdict(report)
    data['peers'] = [asdict(peer) for peer in report.peers]
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if report.handshake_ok else 3

if __name__ == '__main__':
    raise SystemExit(main())
