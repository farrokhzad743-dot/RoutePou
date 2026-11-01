<div align="center">

<img src="docs/icon.png" width="96" alt="RoutePou" />

# RoutePou

**اینترنت و VPN گوشی اندروید را با یک QR به ویندوز وصل کنید**
*Share your Android phone's internet — and its VPN — with a Windows PC by scanning a QR code.*

`0.27.0-beta` · Android 8.0+ · Windows 10/11 (64-bit) · GPL-3.0

</div>

> ⚠️ **پیش‌انتشار (Pre-release).** کد و بیلد کامل است، اما اتصال واقعی دو دستگاه (به‌ویژه تونل کامل WireGuard) هنوز روی سخت‌افزار واقعی تست نشده است. بخش [محدودیت‌ها](#محدودیت‌ها-و-وضعیت-واقعی) را بخوانید.

---

## RoutePou چیست؟

گوشی هات‌اسپات روشن می‌کند، ویندوز به آن وصل می‌شود، و با اسکن QR اینترنت گوشی — با هر VPN که روی گوشی فعال است — برای ویندوز در دسترس می‌شود. چون ترافیک از سوکت‌های خود گوشی خارج می‌شود، همان مسیر پیش‌فرض (و VPN) گوشی را طی می‌کند.

| حالت | چه می‌کند | وضعیت |
|---|---|---|
| **پروکسی امن (TLS)** | ویندوز پراکسی سیستم (HTTP/HTTPS روی `127.0.0.1:17878`) و SOCKS5 (`127.0.0.1:17879`) را فعال می‌کند و ترافیک را رمزنگاری‌شده به گوشی می‌فرستد | آماده استفاده (بتا) |
| **تونل کامل WireGuard** | یک آداپتر مجازی (Wintun) در ویندوز می‌سازد و **کل** ترافیک (TCP/UDP/DNS) را از طریق گوشی عبور می‌دهد | آزمایشی — نیاز به اجرا با دسترسی Administrator |

## نصب و استفاده

1. از صفحه [Releases](../../releases) دو فایل را بگیرید:
   - `RoutePou-<نسخه>-android.apk` → روی گوشی نصب کنید (نصب از «منبع ناشناس» را برای مرورگر/فایل‌منیجر مجاز کنید).
   - `RoutePou-<نسخه>-windows-x64.exe` → روی ویندوز اجرا کنید (SmartScreen ممکن است هشدار دهد چون فایل امضای دیجیتال ندارد: *More info → Run anyway*).
2. روی گوشی **هات‌اسپات** را روشن کنید و ویندوز را به آن وصل کنید.
3. در برنامه اندروید:
   - برای حالت پروکسی: **شروع اشتراک‌گذاری**.
   - برای تونل کامل: **تنظیمات پیشرفته ← راه‌اندازی تونل کامل WireGuard**.
4. در برنامه ویندوز: **اسکن با دوربین** (یا **انتخاب تصویر QR** / **خواندن از Clipboard**). اتصال خودکار شروع می‌شود.
5. برای قطع: **قطع پراکسی و بازیابی تنظیمات** (تنظیمات قبلی پراکسی ویندوز برمی‌گردد) یا **قطع تونل کامل**.

> QR یک **رمز** است؛ هر کس آن را ببیند می‌تواند از اینترنت گوشی شما استفاده کند. QR تونل کامل پس از ۵ دقیقه منقضی می‌شود.

برای استفاده از VPN گوشی: ابتدا VPN را روی گوشی روشن کنید، سپس RoutePou را شروع کنید. اگر VPN شما «Per-app / Split tunneling» دارد، مطمئن شوید RoutePou از VPN مستثنی نشده باشد.

## محدودیت‌ها و وضعیت واقعی

- ✅ تست‌های واحد (Python و Go) و بیلد در CI.
- ❌ هنوز انجام نشده: تست واقعی جفت‌سازی دو دستگاه، تست انتقال TCP/UDP/DNS، تست نشت (leak) و رفتار روی مدل‌های مختلف گوشی. یک بار روی دستگاه خودتان امتحان کنید و IP خروجی را بررسی کنید.
- حالت پروکسی فقط برنامه‌هایی را پوشش می‌دهد که از پراکسی سیستم ویندوز پیروی کنند؛ VPN سراسری نیست (برای آن از تونل کامل استفاده کنید).
- اندروید ۱۵ ممکن است سرویس‌های پیش‌زمینه از نوع `dataSync` را پس از حدود ۶ ساعت متوقف کند؛ در این صورت دوباره شروع کنید.
- فایل ویندوز و APK (اگر کلید امضا تنظیم نشده باشد) با امضای رسمی منتشر نمی‌شوند؛ به‌روزرسانی روی‌هم فقط با APK امضاشده با کلید ثابت ممکن است — [راهنما](docs/RELEASING.md).
- فقط IPv4 و شبکه‌های خصوصی هات‌اسپات (`10.x`, `172.16–31.x`, `192.168.x`) پشتیبانی می‌شوند.

## معماری

```
Android (RoutePou)                              Windows (RoutePou.exe)
┌──────────────────────────┐   hotspot Wi‑Fi   ┌───────────────────────────────┐
│ ProxyService  TLS :8788  │◄──────────────────│ QR scan → pairing parser      │
│  per-install EC cert     │   TLS + token     │ HTTP/SOCKS5 → TLS bridge      │
│  (Android Keystore)      │                   │  (cert fingerprint pinned)    │
│ WireGuardService :51820  │◄──────────────────│ relaywg-client.exe + Wintun   │
│  gomobile relaywg.aar    │    WireGuard      │  (elevated, WFP leak filters) │
│  wireguard-go + gVisor   │                   │                               │
└────────────┬─────────────┘                   └───────────────────────────────┘
             ▼ phone's default route (and its VPN)
```

مستندات بیشتر: [`SECURITY.md`](SECURITY.md) · [`docs/RELEASING.md`](docs/RELEASING.md) · [`CHANGELOG.md`](CHANGELOG.md) · [`docs/history/`](docs/history) (یادداشت‌های هر نسخه) · [`examples/`](examples) (الگوی گزارش تست E2E).

## ساخت از سورس

**Android** (JDK 17, Go 1.25+, Android SDK 35 و NDK r27):
```bash
export ANDROID_HOME=~/Android/Sdk ANDROID_NDK_HOME=$ANDROID_HOME/ndk/27.2.12479018
./scripts/build-wg-aar.sh            # → android/app/libs/relaywg.aar
cd android && gradle assembleDebug   # یا با Android Studio باز کنید
```
**Windows** (Python 3.12, Go 1.25+):
```powershell
cd windows\wg-client; go build -trimpath -ldflags="-s -w" -o ..\relaywg-client.exe .
# wintun.dll (amd64) را از https://www.wintun.net کنار فایل قرار دهید
pip install pyinstaller zxing-cpp pillow opencv-python
pyinstaller --onefile --windowed --icon windows\routepou.ico --paths windows --collect-all zxingcpp --collect-all PIL --collect-all cv2 --add-binary "windows\relaywg-client.exe;." --add-binary "windows\wintun.dll;." --name RoutePou windows\routepou_windows.py
```
**تست‌ها:** `pip install pytest pyyaml pillow opencv-python && pytest` و `cd third_party/relay-wg && go test ./...`

## انتشار

بعد از Push به GitHub، فقط یک تگ بزنید (`git tag v0.27.0-beta && git push origin v0.27.0-beta`)؛ GitHub Actions تست می‌کند، APK و EXE را می‌سازد و Release را با checksum منتشر می‌کند. جزئیات (از جمله ساخت کلید امضای اندروید): [`docs/RELEASING.md`](docs/RELEASING.md).

## لایسنس

GPL-3.0 — چون شامل کد GPL پروژه [Relay](https://github.com/Mahdi-mortazavi/relay) است. فهرست کامل کتابخانه‌ها: [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

## English summary

RoutePou turns an Android phone into a gateway for a Windows PC: enable the hotspot, connect the PC, scan a QR, and the PC's traffic leaves through the phone — including through whatever VPN the phone is running.

- **Secure proxy mode** (beta): TLS (per-install certificate, fingerprint-pinned) carrying HTTP/HTTPS and SOCKS5 from `127.0.0.1:17878/17879` on Windows.
- **Full tunnel** (experimental): userspace WireGuard endpoint on the phone (wireguard-go + gVisor) and a Wintun-based client on Windows with leak filters; requires Administrator.
- **Status:** unit-tested and CI-built, **not yet validated on real devices**. Treat as a pre-release.
- **Install:** download the APK and EXE from [Releases](../../releases), verify with `SHA256SUMS.txt`.
- **Build / release:** see the Persian sections above and [`docs/RELEASING.md`](docs/RELEASING.md). Pushing a `v*` tag builds and publishes everything.
