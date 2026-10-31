import ast
from pathlib import Path

def test_windows_client_parses():
    root = Path(__file__).resolve().parents[1]
    ast.parse((root / "windows" / "routepou_windows.py").read_text(encoding="utf-8"))
