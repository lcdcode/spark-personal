[app]

# Application metadata
title = SPARK Mobile
package.name = sparkmobile
package.domain = com.lcdcode

# Source configuration
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,xml

# App icon - standard icon for older Android versions (< API 26)
icon.filename = res/mipmap-xxxhdpi/ic_launcher.png

# Adaptive icons for Android 8.0+ (API 26+)
# Foreground should be your logo in the safe 66% center area with transparent background
# Background can be a solid color image or pattern
icon.adaptive_foreground.filename = res/mipmap-xxxhdpi/ic_launcher_foreground.png
icon.adaptive_background.filename = %(source.dir)s/adaptive_background_white.png

# Version
version = 1.0

# Internal Version
android.numeric_version = 63

# Requirements
# Pinning to Python 3 compatible versions (p4a defaults have Python 2 'long' type)
requirements = python3,kivy==2.3.0,pyjnius==1.7.0,markdown

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Application config
fullscreen = 0
orientation = portrait

# We're targeting API 29 due to the easy storage management - no Play Store intent anyway.
android.api = 29
android.minapi = 21

# Request legacy external storage for Android 10+
android.manifest_attrs = android:requestLegacyExternalStorage="true"
android.ndk = 25b
android.accept_sdk_license = True

# Architecture
android.archs = arm64-v8a

[buildozer]

# Buildozer settings
log_level = 2
warn_on_root = 1
