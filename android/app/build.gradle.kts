plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.pou.routepou"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.pou.routepou"
        minSdk = 26
        targetSdk = 35
        versionCode = 13
        versionName = "0.13.0-alpha"
    }
}


dependencies {
    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.aar"))))
    implementation("com.google.zxing:core:3.5.3")
    // Official WireGuard Android crypto API used only for per-session key generation.
    implementation("com.wireguard.android:tunnel:1.0.20260102")
}
