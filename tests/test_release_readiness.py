"""Guards the things that silently break a public release."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def test_version_is_consistent_everywhere():
    assert re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?", VERSION)
    gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
    assert f'versionName = "{VERSION}"' in gradle
    major, minor, patch = (int(x) for x in VERSION.split("-")[0].split("."))
    assert f"versionCode = {minor}" in gradle or f"versionCode = {major * 10000 + minor * 100 + patch}" in gradle
    windows = (ROOT / "windows/routepou_windows.py").read_text(encoding="utf-8")
    assert f'APP_VERSION = "{VERSION}"' in windows
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {VERSION}" in changelog, "CHANGELOG needs a section for the released version"


def test_workflow_paths_exist():
    workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
    yaml.safe_load(workflow)
    for rel in re.findall(r"(?:working-directory:|cache-dependency-path:)\s*(\S+)", workflow):
        assert (ROOT / rel).exists(), rel
    for rel in ("scripts/build-wg-aar.sh", "windows/routepou.ico", "windows/wg-client/main.go", "VERSION"):
        assert (ROOT / rel).exists(), rel
    assert not (ROOT / "windows/wg-clinet").exists()


def test_single_workflow_and_gitignore_guards_secrets():
    assert [p.name for p in (ROOT / ".github/workflows").glob("*.yml")] == ["build.yml"]
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in ("__pycache__/", "*.jks", "*.p12", "android/app/libs/"):
        assert pattern in ignore


def test_android_release_signing_is_wired_and_apk_path_matches_workflow():
    gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
    assert "ROUTEPOU_KEYSTORE_FILE" in gradle and "ROUTEPOU_KEYSTORE_FILE" in workflow
    assert "app-release.apk" in workflow
    assert "buildConfig = true" in gradle


def test_license_and_notices_present():
    assert "GNU GENERAL PUBLIC LICENSE" in (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Wintun" in (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
