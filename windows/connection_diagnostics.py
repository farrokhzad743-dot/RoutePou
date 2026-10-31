"""Read-only preflight diagnostics for RoutePou full-tunnel mode.

This module never changes routes, firewall rules, adapters, or DNS. It is safe
 to run before connecting and produces actionable Persian diagnostics.
"""
from __future__ import annotations
import ctypes
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


def _run(args: list[str], timeout: int = 5) -> tuple[int, str]:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return p.returncode, (p.stdout or p.stderr or "").strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def _is_windows() -> bool:
    return os.name == "nt"


def collect_diagnostics(worker_path: str | os.PathLike | None = None) -> dict:
    windows = _is_windows()
    result = {"platform": platform.platform(), "checks": []}

    def add(key: str, ok: bool | None, title: str, detail: str):
        result["checks"].append({"id": key, "ok": ok, "title": title, "detail": detail})

    add("os", windows, "سیستم‌عامل", "Windows 10/11 پشتیبانی می‌شود." if windows else "این بررسی فقط روی ویندوز اجرا می‌شود.")
    if not windows:
        result["ready"] = False
        return result

    try:
        admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        admin = False
    add("admin", admin, "دسترسی مدیر", "برنامه با دسترسی مدیر اجرا شده است." if admin else "برای ساخت آداپتور و مسیرها، هنگام اتصال درخواست UAC را تأیید کنید.")

    worker = Path(worker_path) if worker_path else Path(__file__).with_name("relaywg-client.exe")
    exists = worker.is_file()
    add("worker", exists, "موتور WireGuard", str(worker) if exists else "relaywg-client.exe در کنار برنامه پیدا نشد؛ بسته ویندوز ناقص است.")

    wintun = worker.parent / "wintun.dll"
    wintun_ok = wintun.is_file() or bool(shutil.which("wintun.dll"))
    add("wintun", wintun_ok, "درایور Wintun", "فایل Wintun پیدا شد." if wintun_ok else "wintun.dll پیدا نشد؛ فایل رسمی متناسب با معماری ویندوز را کنار موتور قرار دهید.")

    code, ipcfg = _run(["ipconfig", "/all"])
    has_gateway = code == 0 and ("Default Gateway" in ipcfg or "دروازه پیش‌فرض" in ipcfg)
    add("network", has_gateway, "شبکه و دروازه پیش‌فرض", "خروجی ipconfig بررسی شد." if has_gateway else "دروازه پیش‌فرض شناسایی نشد؛ اتصال Wi-Fi یا هات‌اسپات گوشی را بررسی کنید.")

    code, adapters = _run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                           "Get-NetAdapter -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name"])
    adapter_names = [x.strip() for x in adapters.splitlines() if x.strip()] if code == 0 else []
    add("adapter", code == 0, "کارت‌های شبکه", ", ".join(adapter_names[:8]) if adapter_names else "فهرست کارت‌های شبکه خوانده نشد.")

    code, routes = _run(["route", "print", "-4"])
    add("routes", code == 0, "جدول مسیر IPv4", "جدول مسیر قابل خواندن است؛ پیش از اتصال تغییری اعمال نشده." if code == 0 else "خواندن جدول مسیر ناموفق بود.")

    result["ready"] = all(c["ok"] is True for c in result["checks"] if c["id"] in {"os", "worker", "wintun", "network", "routes"})
    result["note"] = "این گزارش فقط پیش‌نیازها را می‌خواند؛ موفقیت Handshake یا عبور ترافیک را اثبات نمی‌کند."
    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="RoutePou read-only connection diagnostics")
    parser.add_argument("--worker", help="Path to relaywg-client.exe")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    args = parser.parse_args()
    report = collect_diagnostics(args.worker)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("RoutePou — گزارش پیش‌بررسی")
        for check in report["checks"]:
            mark = "✓" if check["ok"] else ("!" if check["ok"] is None else "✗")
            print(f"{mark} {check['title']}: {check['detail']}")
        print("\n" + report.get("note", ""))
    return 0 if report.get("ready") else 2

if __name__ == "__main__":
    raise SystemExit(main())
