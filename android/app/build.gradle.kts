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
        versionCode = 27
        versionName = "0.27.0-beta"

        // The project currently targets phones; keep native ABIs explicit so
        // gomobile's AAR and the APK package the same supported architectures.
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86")
        }
    }

    buildFeatures {
        buildConfig = true
    }

    // Release signing is supplied by environment variables (CI secrets or a local shell).
    // Without them the release APK falls back to the debug key so it stays installable,
    // but such builds cannot be updated in place by a later, properly signed release.
    val keystoreFile = System.getenv("ROUTEPOU_KEYSTORE_FILE")
    if (!keystoreFile.isNullOrBlank() && file(keystoreFile).exists()) {
        signingConfigs {
            create("release") {
                storeFile = file(keystoreFile)
                storePassword = System.getenv("ROUTEPOU_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("ROUTEPOU_KEY_ALIAS")
                keyPassword = System.getenv("ROUTEPOU_KEY_PASSWORD")
            }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildTypes {
        getByName("debug") {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        getByName("release") {
            signingConfig = signingConfigs.findByName("release") ?: signingConfigs.getByName("debug")
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    packaging {
        jniLibs {
            useLegacyPackaging = false
        }
    }
}

dependencies {
    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.aar"))))
    implementation("com.google.zxing:core:3.5.3")
    // Official WireGuard Android crypto API used for per-session key generation.
    implementation("com.wireguard.android:tunnel:1.0.20260102")
}
