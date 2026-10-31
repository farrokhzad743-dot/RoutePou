from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_android_upstream_monitor_is_observational():
    src = (ROOT / 'android/app/src/main/java/com/pou/routepou/AndroidUpstreamMonitor.kt').read_text()
    assert 'NET_CAPABILITY_INTERNET' in src
    assert 'NET_CAPABILITY_VALIDATED' in src
    assert 'registerNetworkCallback' in src
    assert 'unregisterNetworkCallback' in src
    assert 'never changes routes' in src


def test_wireguard_service_owns_monitor_lifecycle():
    src = (ROOT / 'android/app/src/main/java/com/pou/routepou/WireGuardService.kt').read_text()
    assert 'AndroidUpstreamMonitor(this)' in src
    assert 'upstreamMonitor?.stop()' in src
    assert 'WireGuardEngine.stop()' in src


def test_android_version_is_024():
    src = (ROOT / 'android/app/build.gradle.kts').read_text()
    assert 'versionCode = 26' in src
    assert 'versionName = "0.26.0-alpha"' in src
