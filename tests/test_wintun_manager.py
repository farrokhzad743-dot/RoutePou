import importlib.util
import sys
from pathlib import Path

MODULE = Path(__file__).parents[1] / "windows" / "wintun_manager.py"
spec = importlib.util.spec_from_file_location("wintun_manager", MODULE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

def test_diagnostic_returns_structured_status(monkeypatch):
    monkeypatch.setattr(mod.platform, "system", lambda: "Windows")
    monkeypatch.setattr(mod.platform, "release", lambda: "11")
    monkeypatch.setattr(mod.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(mod, "_find_dll", lambda: False)
    monkeypatch.setattr(mod, "_adapter_found", lambda: False)
    monkeypatch.setattr(mod, "_is_admin", lambda: False)
    result = mod.diagnose()
    assert result.supported_os
    assert not result.ready
    assert "wintun.dll is missing" in result.details

def test_non_windows_never_ready(monkeypatch):
    monkeypatch.setattr(mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(mod, "_find_dll", lambda: True)
    monkeypatch.setattr(mod, "_adapter_found", lambda: True)
    monkeypatch.setattr(mod, "_is_admin", lambda: True)
    assert not mod.diagnose().ready
