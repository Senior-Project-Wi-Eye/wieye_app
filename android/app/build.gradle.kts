plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.wieye.wieye_app"
    compileSdk = 35
    ndkVersion = "27.0.12077973"

    compileOptions {
        isCoreLibraryDesugaringEnabled = true
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    defaultConfig {
        applicationId = "com.wieye.wieye_app"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
        multiDexEnabled = true
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    // Enable Core Library Desugaring
    dependencies {
        coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.3") // Use the latest version
        implementation("androidx.window:window:1.1.0")
        implementation("androidx.window:window-java:1.1.0")
    }
}

flutter {
    source = "../.."
}
