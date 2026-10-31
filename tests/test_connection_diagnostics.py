import importlib.util
from pathlib import Path

MODULE = Path(__file__).parents[1] / "windows" / "connection_diagnostics.py"
spec = importlib.util.spec_from_file_location("connection_diagnostics", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_non_windows_is_read_only_and_not_ready(monkeypatch):
    monkeypatch.setattr(mod, "_is_windows", lambda: False)
    report = mod.collect_diagnostics()
    assert report["ready"] is False
    assert report["checks"][0]["id"] == "os"


def test_windows_diagnostics_do_not_modify_system(monkeypatch, tmp_path):
    monkeypatch.setattr(mod, "_is_windows", lambda: True)
    monkeypatch.setattr(mod.platform, "platform", lambda: "Windows-test")
    monkeypatch.setattr(mod.ctypes, "windll", type("W", (), {"shell32": type("S", (), {"IsUserAnAdmin": staticmethod(lambda: 0)})()})(), raising=False)
    calls = []
    def fake_run(args, timeout=5):
        calls.append(args)
        if args[0] == "ipconfig": return 0, "Default Gateway . . . : 192.168.1.1"
        if args[0] == "powershell": return 0, "Wi-Fi\nWintun"
        if args[0] == "route": return 0, "IPv4 Route Table"
        return 1, ""
    monkeypatch.setattr(mod, "_run", fake_run)
    worker = tmp_path / "relaywg-client.exe"; worker.write_bytes(b"test")
    (tmp_path / "wintun.dll").write_bytes(b"test")
    report = mod.collect_diagnostics(worker)
    assert report["ready"] is True
    assert all(c[0] in {"ipconfig", "powershell", "route"} for c in calls)
    assert not any("add" in " ".join(c).lower() or "delete" in " ".join(c).lower() for c in calls)
