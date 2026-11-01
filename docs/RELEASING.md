# Releasing RoutePou

## 1. One-time: publish the source to GitHub
```bash
cd RoutePou-main
git init -b main
git add .
git status            # confirm there is no *.jks, *.p12 or android/app/libs in the list
git commit -m "RoutePou 0.27.0-beta"
git remote add origin https://github.com/<your-user>/RoutePou.git
git push -u origin main
```
The *Build and Release* workflow starts automatically; open **Actions** to watch it. Download the `RoutePou-Android` and `RoutePou-Windows` artifacts to test before publishing.

## 2. One-time: Android signing key (strongly recommended)
Without it the release APK is signed with a throw-away debug key. It installs and works, but a future properly signed build can only be installed after uninstalling the old one.
```bash
./scripts/make-android-keystore.sh routepou-release.jks routepou
base64 -w0 routepou-release.jks      # copy the output
```
In GitHub → *Settings → Secrets and variables → Actions* add:

| Secret | Value |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | output of the `base64` command |
| `ANDROID_KEYSTORE_PASSWORD` | the keystore password |
| `ANDROID_KEY_ALIAS` | `routepou` |
| `ANDROID_KEY_PASSWORD` | the key password (same as above if you used the script) |

**Back up `routepou-release.jks` and the passwords outside the repo.** If they are lost, users can never update in place.

## 3. Cut a release
1. Edit `VERSION` (e.g. `0.27.1-beta`), `android/app/build.gradle.kts` (`versionCode` + `versionName`), `APP_VERSION` in `windows/routepou_windows.py`, and add a `## <version>` section to `CHANGELOG.md` — `pytest` fails if these disagree.
2. Commit and push, then:
   ```bash
   git tag v0.27.1-beta
   git push origin v0.27.1-beta
   ```
3. The workflow builds everything, checks that the tag equals `v` + `VERSION`, and creates the GitHub Release (marked *pre-release* when the version contains `-`) with the APK, the EXE and `SHA256SUMS.txt`.

## Optional improvements
- Windows code signing (an Authenticode certificate) removes the SmartScreen warning.
- Wintun: the workflow prints the SHA-256 of the downloaded archive; pin it in `build.yml` once you have verified it against https://www.wintun.net.
- Real-device acceptance: follow `examples/e2e-report.template.json` and `docs/history/IMPLEMENTATION-STATUS-0.22.md` before dropping the *beta* label.
