import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_supervisor_has_memory_only_pipe_lifecycle():
    source = (ROOT / "windows" / "wg_supervisor.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "CreateNamedPipeW" in source
    assert "END-CONFIG" in source
    assert 'line == "READY"' in source
    assert "ShellExecuteW" in source
    assert "private_key" in source
    assert "write_text" not in source

def test_windows_ui_supports_both_qr_contracts_and_full_tunnel():
    source = (ROOT / "windows" / "routepou_windows.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert 'payload.startswith("routepou://p/")' in source
    assert "parse_qr_to_windows_ipc" in source
    assert "connect_full_tunnel" in source
    assert "disconnect_full_tunnel" in source
