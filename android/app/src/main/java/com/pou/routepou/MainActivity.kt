package com.pou.routepou

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import com.google.zxing.BarcodeFormat
import com.google.zxing.EncodeHintType
import com.google.zxing.qrcode.QRCodeWriter
import java.net.Inet4Address
import java.net.NetworkInterface
import java.net.URLEncoder
import java.security.MessageDigest
import java.security.SecureRandom

class MainActivity : Activity() {
    private lateinit var status: TextView
    private lateinit var addresses: TextView
    private lateinit var tokenView: TextView
    private lateinit var qrView: ImageView
    private var proxyStarted = false
    private var pairingToken = ""
    private var fingerprint = ""
    private var fullModePayload = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 9)
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(28, 36, 28, 28)
            setBackgroundColor(0xFF101114.toInt())
        }
        fun label(text: String, size: Float, color: Int = 0xFFFFFFFF.toInt()) = TextView(this).apply {
            this.text = text; textSize = size; setTextColor(color); setPadding(0, 9, 0, 9)
        }
        root.addView(label("RoutePou", 32f))
        root.addView(label("Mobile VPN → Windows", 16f, 0xFFBBBBBB.toInt()))
        status = label("Status: stopped", 18f, 0xFFFFD2D2.toInt()); root.addView(status)
        root.addView(label("Hotspot IPv4", 14f, 0xFFBBBBBB.toInt()))
        addresses = label(findIpv4(), 15f); root.addView(addresses)

        pairingToken = getOrCreateToken()
        fingerprint = certificateFingerprint()
        tokenView = label("Pairing key: $pairingToken", 12f, 0xFFFFD66B.toInt()); root.addView(tokenView)
        root.addView(label("Scan this QR with a QR reader, then paste the decoded routepou:// text into the Windows app. The QR contains your private pairing key; never share it.", 12f, 0xFFBBBBBB.toInt()))
        qrView = ImageView(this).apply {
            setBackgroundColor(0xFFFFFFFF.toInt())
            setPadding(12, 12, 12, 12)
            adjustViewBounds = true
            scaleType = ImageView.ScaleType.FIT_CENTER
        }
        val qrContainer = LinearLayout(this).apply { gravity = Gravity.CENTER; setPadding(0, 8, 0, 8) }
        qrContainer.addView(qrView, LinearLayout.LayoutParams(560, 560))
        root.addView(qrContainer)
        refreshQr()

        root.addView(Button(this).apply {
            text = "Start Full Tunnel (WireGuard)"
            setOnClickListener { startFullTunnel() }
        })
        root.addView(Button(this).apply {
            text = "Stop Full Tunnel"
            setOnClickListener { stopFullTunnel() }
        })

        val controls = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        controls.addView(Button(this).apply { text = "Start proxy"; setOnClickListener { startProxy() } }, LinearLayout.LayoutParams(0, -2, 1f))
        controls.addView(Button(this).apply { text = "Stop proxy"; setOnClickListener { stopProxy() } }, LinearLayout.LayoutParams(0, -2, 1f))
        root.addView(controls)
        root.addView(Button(this).apply {
            text = "Regenerate pairing key"
            setOnClickListener {
                val wasRunning = proxyStarted
                stopProxy()
                getSharedPreferences("routepou", MODE_PRIVATE).edit().remove("access_token").apply()
                pairingToken = getOrCreateToken()
                tokenView.text = "Pairing key: $pairingToken"
                refreshQr()
                if (wasRunning) startProxy()
                Toast.makeText(this@MainActivity, "Pairing key rotated. Pair Windows again.", Toast.LENGTH_LONG).show()
            }
        })
        root.addView(label("TLS SHA-256 fingerprint:\n$fingerprint", 10f, 0xFF8FD3FF.toInt()))
        root.addView(label("This alpha version provides HTTP/HTTPS and SOCKS5 TCP proxying. It is not a full-device VPN; UDP, Wintun and a system-wide kill switch are not included.", 12f, 0xFFBBBBBB.toInt()))
        val scroll = ScrollView(this).apply { addView(root) }
        setContentView(scroll)
    }

    private fun refreshQr() {
        val host = hotspotIpv4()
        if (fullModePayload.isNotBlank()) {
            renderQr(fullModePayload)
            return
        }
        if (host == null || fingerprint.length != 64) {
            qrView.setImageBitmap(null)
            return
        }
        val payload = "routepou://pair?host=${enc(host)}&port=8788&key=${enc(pairingToken)}&fp=${enc(fingerprint)}"
        renderQr(payload)
    }

    private fun renderQr(payload: String) {
        try {
            val matrix = QRCodeWriter().encode(payload, BarcodeFormat.QR_CODE, 520, 520, mapOf(EncodeHintType.MARGIN to 1))
            val pixels = IntArray(520 * 520)
            for (y in 0 until 520) for (x in 0 until 520) pixels[y * 520 + x] = if (matrix[x, y]) 0xFF000000.toInt() else 0xFFFFFFFF.toInt()
            qrView.setImageBitmap(Bitmap.createBitmap(pixels, 520, 520, Bitmap.Config.ARGB_8888))
        } catch (_: Exception) { qrView.setImageBitmap(null) }
    }

    private fun startFullTunnel() {
        try {
            val host = hotspotIpv4() ?: error("Hotspot IPv4 not found. Turn on the phone hotspot and connect Windows first.")
            check(WireGuardEngine.isAvailable()) { "WireGuard engine is not packaged. Build the Relay AAR first." }
            val keys = RoutePouWgKeys.generate()
            val ipc = RoutePouWgConfig.serverIpc(keys)
            val payload = RoutePouPairingPayload(
                host = host,
                port = RoutePouWgConfig.DEFAULT_PORT,
                serverPublicKey = keys.serverPublicKey,
                clientPrivateKey = keys.clientPrivateKey,
                dns = RoutePouWgConfig.DEFAULT_DNS
            ).encode()
            val intent = Intent(this, WireGuardService::class.java)
                .setAction(WireGuardService.ACTION_START)
                .putExtra(WireGuardService.EXTRA_IPC, ipc)
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent) else startService(intent)
            fullModePayload = payload
            status.text = "Full Tunnel: starting WireGuard endpoint · $host:${RoutePouWgConfig.DEFAULT_PORT}"
            addresses.text = "WireGuard endpoint: $host:${RoutePouWgConfig.DEFAULT_PORT}\nScan the QR on Windows. Keep hotspot enabled."
            renderQr(payload)
        } catch (e: Exception) {
            Toast.makeText(this, e.message ?: "Could not start Full Tunnel", Toast.LENGTH_LONG).show()
            status.text = "Full Tunnel: not started · ${e.message}"
        }
    }

    private fun stopFullTunnel() {
        stopService(Intent(this, WireGuardService::class.java))
        fullModePayload = ""
        status.text = "Full Tunnel: stopped"
        addresses.text = findIpv4()
        refreshQr()
    }

    private fun enc(value: String) = URLEncoder.encode(value, "UTF-8")

    private fun certificateFingerprint(): String = try {
        val cert = assets.open("routepou-server.p12").use { stream ->
            val ks = java.security.KeyStore.getInstance("PKCS12")
            ks.load(stream, "routepou-alpha-keystore".toCharArray())
            ks.getCertificate("routepou")
        }
        MessageDigest.getInstance("SHA-256").digest(cert.encoded).joinToString("") { "%02X".format(it) }
    } catch (_: Exception) { "Fingerprint unavailable" }

    private fun getOrCreateToken(): String {
        val prefs = getSharedPreferences("routepou", MODE_PRIVATE)
        prefs.getString("access_token", null)?.let { return it }
        val bytes = ByteArray(32).also { SecureRandom().nextBytes(it) }
        val value = bytes.joinToString("") { "%02x".format(it) }
        prefs.edit().putString("access_token", value).apply()
        return value
    }

    private fun startProxy() {
        val intent = Intent(this, ProxyService::class.java).setAction(ProxyService.ACTION_START)
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent) else startService(intent)
        proxyStarted = true
        status.text = "Status: starting encrypted TLS on port 8788"
        Toast.makeText(this, "RoutePou proxy starting", Toast.LENGTH_SHORT).show()
        addresses.text = findIpv4(); refreshQr()
    }

    private fun stopProxy() {
        stopService(Intent(this, ProxyService::class.java))
        proxyStarted = false
        status.text = "Status: stopped"
    }

    private fun hotspotIpv4(): String? = try {
        NetworkInterface.getNetworkInterfaces().toList().flatMap { it.inetAddresses.toList() }
            .filterIsInstance<Inet4Address>().filter { !it.isLoopbackAddress }
            .mapNotNull { it.hostAddress }
            .firstOrNull { it.startsWith("192.168.") || it.startsWith("10.") || it.matches(Regex("""172\.(1[6-9]|2[0-9]|3[01])\..*""")) }
    } catch (_: Exception) { null }

    private fun findIpv4(): String = try {
        val all = NetworkInterface.getNetworkInterfaces().toList().flatMap { it.inetAddresses.toList() }
            .filter { it is Inet4Address && !it.isLoopbackAddress }
            .mapNotNull { it.hostAddress }.filter { it.isNotBlank() }
        if (all.isEmpty()) "No active IPv4 found. Check hotspot." else all.joinToString("\n")
    } catch (_: Exception) { "Could not read network addresses" }
}
