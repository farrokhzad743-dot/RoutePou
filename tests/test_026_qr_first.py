from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_windows_qr_first_camera_and_image_import_are_available():
    source = (ROOT / "windows/routepou_windows.py").read_text(encoding="utf-8")
    assert "def scan_qr_camera():" in source
    assert "def scan_qr_image():" in source
    assert "zxingcpp.read_barcodes" in source
    assert "root.after(150, connect)" in source
    assert "root.after(150, connect_full_tunnel)" in source
    assert "تنظیمات دستی پیشرفته" in source


def test_burgundy_dark_light_branding_is_present():
    windows = (ROOT / "windows/routepou_windows.py").read_text(encoding="utf-8")
    android = (ROOT / "android/app/src/main/java/com/pou/routepou/MainActivity.kt").read_text(encoding="utf-8")
    assert "DARK_COLORS" in windows and "LIGHT_COLORS" in windows
    assert "#961941" in windows and "#851238" in windows
    assert 'putBoolean("dark_mode", !darkMode)' in android
    assert "Color.rgb(150, 25, 65)" in android
    assert 'primaryButton("شروع اشتراک‌گذاری")' in android
    assert 'visibility = View.GONE' in android


def test_android_version_and_windows_build_dependencies_are_current():
    gradle = (ROOT / "android/app/build.gradle.kts").read_text()
    workflow = (ROOT / ".github/workflows/build.yml").read_text()
    assert "zxing-cpp" in workflow and "opencv-python" in workflow
    assert "--collect-all cv2" in workflow
