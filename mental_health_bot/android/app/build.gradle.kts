plugins {
    id("com.android.application")
    id("kotlin-android")
    id("org.jetbrains.kotlin.android")
    id("com.google.gms.google-services") // ✅ Good!
    id("dev.flutter.flutter-gradle-plugin") // ✅ Must be last
}

android {
    namespace = "com.ingaw.mentalhealthbot"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = "27.0.12077973"

    defaultConfig {
    applicationId = "com.ingaw.mentalhealthbot"
    minSdk = 23
    targetSdk = flutter.targetSdkVersion
    versionCode = flutter.versionCode
    versionName = flutter.versionName
}

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug") // TODO: Replace with release keys
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = "11"
    }
}

flutter {
    source = "../.."
}

dependencies {
    // ✅ Firebase BoM for version management
    implementation(platform("com.google.firebase:firebase-bom:33.15.0"))
    // ✅ Add required Firebase libraries
    implementation("com.google.firebase:firebase-auth-ktx")


    // Optionally, add Analytics, Storage, Crashlytics, etc.
    // implementation("com.google.firebase:firebase-analytics-ktx")
}
