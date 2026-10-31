"""Wintun preflight and adapter diagnostics for RoutePou.

This module intentionally does not install drivers or alter routes. The packet
forwarder is not shipped yet; these checks prevent unsafe partial activation.
"""
from __future__ import annotations
import ctypes.util
import os
import platform
import subprocess
from dataclasses import dataclass

@dataclass
class WintunStatus:
    supported_os: bool
    architecture: str
    dll_found: bool
    adapter_found: bool
    admin: bool
    ready: bool
    details: str


def _is_admin() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _find_dll() -> bool:
    if os.name != "nt":
        return False
    candidates = [
        os.path.join(os.path.dirname(__file__), "wintun.dll"),
        os.path.join(os.getcwd(), "wintun.dll"),
    ]
    return any(os.path.isfile(p) for p in candidates) or bool(ctypes.util.find_library("wintun"))


def _adapter_found() -> bool:
    if os.name != "nt":
        return False
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command",
             "Get-NetAdapter -IncludeHidden | Where-Object {$_.InterfaceDescription -match 'Wintun'} | Select-Object -First 1 -ExpandProperty Name"],
            capture_output=True, text=True, timeout=8, check=False,
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        return False


def diagnose() -> WintunStatus:
    system = platform.system()
    arch = platform.machine()
    supported = system == "Windows" and platform.release() in {"10", "11"}
    dll = _find_dll()
    adapter = _adapter_found()
    admin = _is_admin()
    ready = supported and dll and adapter and admin
    if system != "Windows":
        detail = "Wintun diagnostics require Windows 10/11."
    elif not supported:
        detail = "Unsupported Windows version. Windows 10/11 is required."
    elif not dll:
        detail = "wintun.dll is missing. No driver or route changes were made."
    elif not adapter:
        detail = "Wintun adapter not detected. Install the official Wintun driver before enabling packet routing."
    elif not admin:
        detail = "Administrator privileges are required for adapter and route management."
    else:
        detail = "Preflight passed. Packet forwarding is not included in this alpha."
    return WintunStatus(supported, arch, dll, adapter, admin, ready, detail)

if __name__ == "__main__":
    print(diagnose())
