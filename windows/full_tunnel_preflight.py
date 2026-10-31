"""Read-only preflight for RoutePou full-tunnel readiness.

This tool never changes routes, DNS, firewall policy, adapters, or services.
It deliberately reports readiness separately from an established data path.
"""
from __future__ import annotations
import argparse
import ctypes
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    critical: bool = True


def _run(command: list[str], timeout: int = 5) -> tuple[bool, str]:
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return p.returncode == 0, (p.stdout or p.stderr).strip()[:1200]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def _is_windows() -> bool:
    return os.name == "nt"


def is_admin() -> bool:
    if not _is_windows():
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def run_preflight(root: str | Path | None = None) -> dict:
    base = Path(root) if root else Path(__file__).resolve().parent
    checks: list[Check] = []
    is_windows = _is_windows()
    checks.append(Check("platform", is_windows, "Windows 10/11 required" if is_windows else "Run this check on Windows 10/11"))
    worker = base / "relaywg-client.exe"
    checks.append(Check("wireguard_worker", worker.is_file(), str(worker) if worker.is_file() else "relaywg-client.exe missing"))
    wintun = base / "wintun.dll"
    checks.append(Check("wintun_runtime", wintun.is_file(), str(wintun) if wintun.is_file() else "wintun.dll missing"))
    admin = is_admin()
    checks.append(Check("administrator", admin, "Elevated" if admin else "Elevation is required only when starting full tunnel"))
    wg = base / "wg.exe"
    wg_path = str(wg) if wg.is_file() else shutil.which("wg")
    checks.append(Check("wg_cli", bool(wg_path), wg_path or "wg.exe not found; telemetry cannot be queried"))
    if is_windows:
        ok, detail = _run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                           "Get-NetAdapter -IncludeHidden | Select-Object -ExpandProperty Name" ])
        checks.append(Check("network_adapter_query", ok, detail or "Could not query adapters"))
    else:
        checks.append(Check("network_adapter_query", False, "Available on Windows only"))
    critical_ok = all(c.ok for c in checks if c.critical)
    # This is intentionally never a claim that packets are being forwarded.
    return {"product": "RoutePou", "version": "0.20.0-alpha", "mode": "read-only-preflight",
            "preflight_ready": critical_ok, "data_plane_verified": False,
            "warning": "Preflight checks do not prove handshake, packet forwarding, DNS, IPv6, or leak protection.",
            "checks": [asdict(c) for c in checks]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only RoutePou full-tunnel preflight")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()
    result = run_preflight()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("RoutePou 0.20 — بررسی پیش‌نیاز تونل کامل (فقط خواندنی)")
        for item in result["checks"]:
            print(f"{'OK' if item['ok'] else 'FAIL'}  {item['name']}: {item['detail']}")
        print("آمادگی پیش‌نیازها:", "بله" if result["preflight_ready"] else "خیر")
        print("مسیر واقعی داده تأیید شده: خیر — نیازمند آزمایش روی دو دستگاه")
    return 0 if result["preflight_ready"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
