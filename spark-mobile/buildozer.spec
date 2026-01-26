[app]

# Application metadata
title = SPARK Mobile
package.name = sparkmobile
package.domain = org.spark

# Source configuration
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db

# App icon - using scaled-up version for better visibility in launchers
# The scaled version has the logo enlarged from adaptive icon safe zone (66%) to 85%
icon.filename = res/mipmap-xxxhdpi/ic_launcher_foreground.png

# Include custom res folder to add mipmap icons
android.res_folder = res

# Version
version = 2.9

# Requirements
# Pinning to Python 3 compatible versions (p4a defaults have Python 2 'long' type)
requirements = python3,kivy==2.3.0,pyjnius==1.7.0,markdown

# Permissions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Application config
fullscreen = 0
orientation = portrait

# Android specific
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
