from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_shared_tls_keystore_is_shipped():
    """A PKCS#12 identity (and password) in the repo would be shared by every install."""
    assert not list(ROOT.rglob("*.p12")) and not list(ROOT.rglob("*.jks")) and not list(ROOT.rglob("*.keystore"))
    sources = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "android").rglob("*.kt"))
    assert "routepou-alpha-keystore" not in sources
    assert "AndroidKeyStore" in sources


def test_proxy_service_uses_per_install_identity():
    service = (ROOT / "android/app/src/main/java/com/pou/routepou/ProxyService.kt").read_text(encoding="utf-8")
    activity = (ROOT / "android/app/src/main/java/com/pou/routepou/MainActivity.kt").read_text(encoding="utf-8")
    assert "TlsIdentity.sslContext()" in service
    assert "TlsIdentity.fingerprint()" in activity
    assert "TlsIdentity.regenerate()" in activity


def test_windows_client_requires_certificate_pin():
    source = (ROOT / "windows" / "routepou_windows.py").read_text(encoding="utf-8")
    assert "hashlib.sha256(wrapped.getpeercert(binary_form=True))" in source
    assert "certificate fingerprint mismatch" in source
    assert 'PHONE_PORT_DEFAULT = "8788"' in source
