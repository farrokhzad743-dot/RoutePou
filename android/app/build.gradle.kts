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
        versionCode = 26
        versionName = "0.26.0-alpha"

        // The project currently targets phones; keep native ABIs explicit so
        // gomobile's AAR and the APK package the same supported architectures.
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64", "x86")
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
