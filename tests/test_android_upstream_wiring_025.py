from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_optional_upstream_is_validated_and_passed_to_service():
    activity = (ROOT / 'android/app/src/main/java/com/pou/routepou/MainActivity.kt').read_text()
    service = (ROOT / 'android/app/src/main/java/com/pou/routepou/WireGuardService.kt').read_text()
    engine = (ROOT / 'android/app/src/main/java/com/pou/routepou/WireGuardEngine.kt').read_text()
    assert 'RoutePouUpstream.validate(upstreamInput.text.toString())' in activity
    assert 'EXTRA_UPSTREAM, upstream' in activity
    assert 'intent.getStringExtra(EXTRA_UPSTREAM)' in service
    assert 'WireGuardEngine.start(ipc, upstream)' in service
    assert 'startEndpointVia' in engine


def test_upstream_validator_is_loopback_only_and_bounded():
    source = (ROOT / 'android/app/src/main/java/com/pou/routepou/RoutePouUpstream.kt').read_text()
    assert 'value.length <= 64' in source
    assert 'isLoopbackAddress' in source
    assert 'port in 1..65535' in source
    assert 'contains("@")' in source
    assert 'contains("/")' in source


def test_version_bumped_to_025():
    gradle = (ROOT / 'android/app/build.gradle.kts').read_text()
    assert 'versionCode = 26' in gradle
    assert 'versionName = "0.26.0-alpha"' in gradle
