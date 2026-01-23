# SPARK Mobile Database Sync

## Current Status

The app stores the database internally on Android due to Android 11+ scoped storage restrictions.

## Manual Sync Method

### From Mobile to Desktop:

1. Connect your phone to computer via USB
2. Use `adb` to pull the database:
   ```bash
   adb pull /data/data/org.spark.sparkmobile/files/spark.db ~/Desktop/
   ```
3. Copy to your desktop SPARK directory

### From Desktop to Mobile:

1. Connect your phone via USB
2. Use `adb` to push the database:
   ```bash
   adb push ~/.spark/spark.db /data/data/org.spark.sparkmobile/files/spark.db
   ```
3. Restart the app

## Alternative: Use adb for Live Sync

Create a sync script:

```bash
#!/bin/bash
# sync_to_mobile.sh
adb push ~/.spark/spark.db /data/data/org.spark.sparkmobile/files/spark.db
echo "Database synced to mobile"
```

```bash
#!/bin/bash
# sync_from_mobile.sh
adb pull /data/data/org.spark.sparkmobile/files/spark.db ~/.spark/spark.db
echo "Database synced from mobile"
```

Make executable:
```bash
chmod +x sync_to_mobile.sh sync_from_mobile.sh
```

## Future: Cloud Sync

A future version could implement:
- Syncthing integration
- Google Drive sync
- Dropbox sync
- WebDAV sync

This would enable automatic bidirectional sync without USB cables.
