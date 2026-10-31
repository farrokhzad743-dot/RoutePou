from pathlib import Path
import subprocess


def test_android_tls_keystore_exists_and_is_readable():
    root = Path(__file__).resolve().parents[1]
    p12 = root / "android" / "app" / "src" / "main" / "assets" / "routepou-server.p12"
    assert p12.is_file() and p12.stat().st_size > 0
    result = subprocess.run(
        ["openssl", "pkcs12", "-in", str(p12), "-passin", "pass:routepou-alpha-keystore", "-nokeys", "-clcerts"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "BEGIN CERTIFICATE" in result.stdout


def test_windows_client_requires_certificate_pin():
    root = Path(__file__).resolve().parents[1]
    source = (root / "windows" / "routepou_windows.py").read_text(encoding="utf-8")
    assert "hashlib.sha256(wrapped.getpeercert(binary_form=True))" in source
    assert "certificate fingerprint mismatch" in source
    assert 'PHONE_PORT_DEFAULT = "8788"' in source
