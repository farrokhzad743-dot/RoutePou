import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_supervisor_monitors_worker_after_handshake():
    source = (ROOT / "windows" / "wg_supervisor.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'line == "READY"' in source
    assert '_monitor_worker' in source
    assert "self.on_status(line)" in source
    worker = (ROOT / "windows" / "wg-client" / "main.go").read_text(encoding="utf-8")
    assert 'peerLostLine = "PEER-LOST"' in worker
    assert 'peerBackLine = "PEER-BACK"' in worker
    assert 'self.on_exit(reason)' in source


def test_full_tunnel_uses_hold_on_loss_and_validates_dns_ip():
    source = (ROOT / "windows" / "wg_supervisor.py").read_text(encoding="utf-8")
    assert "-hold-on-loss=true" in source
    assert "ipaddress.ip_address(dns)" in source


def test_ui_reflects_peer_loss_and_recovery():
    source = (ROOT / "windows" / "routepou_windows.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'line == "PEER-LOST"' in source
    assert 'line == "PEER-BACK"' in source
    assert "on_exit=worker_exit" in source
