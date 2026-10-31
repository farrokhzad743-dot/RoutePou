from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AndroidFullModeWiringTests(unittest.TestCase):
    def test_activity_builds_session_and_starts_service(self):
        source = (ROOT / 'android/app/src/main/java/com/pou/routepou/MainActivity.kt').read_text()
        self.assertIn('RoutePouWgKeys.generate()', source)
        self.assertIn('RoutePouWgConfig.serverIpc(keys)', source)
        self.assertIn('RoutePouPairingPayload(', source)
        self.assertIn('WireGuardService.ACTION_START', source)
        self.assertIn('private fun stopFullTunnel()', source)

    def test_service_owns_engine_lifecycle(self):
        source = (ROOT / 'android/app/src/main/java/com/pou/routepou/WireGuardService.kt').read_text()
        self.assertIn('WireGuardEngine.start(ipc)', source)
        self.assertIn('WireGuardEngine.stop()', source)
        self.assertIn('startForeground(', source)

    def test_service_is_declared_and_version_bumped(self):
        manifest = (ROOT / 'android/app/src/main/AndroidManifest.xml').read_text()
        gradle = (ROOT / 'android/app/build.gradle.kts').read_text()
        self.assertIn('.WireGuardService', manifest)
        self.assertIn('versionCode = 13', gradle)
        self.assertIn('versionName = "0.13.0-alpha"', gradle)

if __name__ == '__main__':
    unittest.main()
