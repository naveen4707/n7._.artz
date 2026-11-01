# LoomisAI — Android & Mobile Packaging Guide

This guide details how to package **LoomisAI** as a high-performance Android application suitable for Google Play Store release.

---

## 1. Architecture Overview

LoomisAI is engineered with a hybrid mobile architecture:
- **Core Studio Client**: Responsive PWA (`web/`) with Service Worker caching (`web/sw.js`), modern touch UI, and Web App Manifest (`web/manifest.json`).
- **AI Engine Backend**: Python FastAPI / HTTP service (`ai-engine/`) executing MediaPipe 478-landmark analysis, 3D Loomis projective geometry, and progressive graphite rendering.
- **Android Runtime**: Packaged via **Capacitor** (native bridge) or **Bubblewrap TWA** (Trusted Web Activity) with full offline caching and hardware acceleration.

---

## 2. Option A: Capacitor Android Packaging (Recommended)

Capacitor bridges the web studio directly into a native Android Studio project with access to device hardware (camera, gallery, file system).

### Step 1: Install Dependencies
From the repository root (`e:/LoomisAI`):
```bash
npm install -D @capacitor/cli @capacitor/core @capacitor/android
```

### Step 2: Initialize Capacitor
```bash
npx cap init LoomisAI com.loomisai.app --web-dir web
npx cap add android
```

### Step 3: Sync Web Assets
Whenever changes are made to `web/`:
```bash
npx cap sync android
```

### Step 4: Open in Android Studio
```bash
npx cap open android
```

### Step 5: Configure Permissions & Build
1. Open the project in **Android Studio**.
2. Verify `app/src/main/AndroidManifest.xml` matches the template in `android/AndroidManifest.xml`.
3. Select **Build > Generate Signed Bundle / APK**.
4. Select **Android App Bundle (.aab)** for Google Play Store upload.

---

## 3. Option B: Bubblewrap TWA (Trusted Web Activity)

For hosted deployments (e.g. `https://app.loomisai.com`), Google's official **Bubblewrap CLI** produces a signed Android APK/AAB directly from `manifest.json`.

### Step 1: Install Bubblewrap
```bash
npm install -g @bubblewrap/cli
```

### Step 2: Initialize from Manifest
```bash
bubblewrap init --manifest https://app.loomisai.com/web/manifest.json
```

### Step 3: Build Signed Android App Bundle
```bash
bubblewrap build
```
This generates `app-release-signed.aab` ready for upload to Google Play Console.

---

## 4. Keystore Generation & Production Signing

To publish to Google Play, sign the `.aab` with an upload keystore:

```bash
keytool -genkey -v -keystore loomisai-release.keystore \
  -alias loomisai \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

Add your signing credentials to `android/key.properties` (never commit passwords to git):
```properties
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=loomisai
storeFile=/path/to/loomisai-release.keystore
```

---

## 5. Google Play Store Release Checklist

| Requirement | Specification | Status |
| :--- | :--- | :--- |
| **Package Name** | `com.loomisai.app` | Configured |
| **Target SDK** | Android 14 (API level 34+) | Configured |
| **App Icon** | 512x512 px PNG (32-bit with alpha) | Provided in `web/icons/` |
| **Feature Graphic** | 1024x500 px JPG or PNG (no alpha) | Required before submission |
| **Screenshots** | Min 4 phone screenshots (16:9 or 9:16) + 7"/10" tablet | Capture from Web Studio |
| **App Category** | Education / Art & Design | Specified in `manifest.json` |
| **Privacy Policy** | URL explaining camera & gallery access for portrait drawing | Required for Play Console |
| **Offline Shell** | PWA Service Worker caching app shell | Implemented in `web/sw.js` |
