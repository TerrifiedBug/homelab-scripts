#!/bin/bash

# Timestamp for backup filename
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# Define backup filename and location
DUMP_FILENAME="codeserver_backup_${TIMESTAMP}.tar.gz"
DUMP_PATH="/tmp/$DUMP_FILENAME"

# MinIO Server connection details
MINIO_HOST="REDACTED"
MINIO_BUCKET="codeserver"
MINIO_ACCESS_KEY="REDACTED"
MINIO_SECRET_KEY="REDACTED"

# Remote target path (YYYYMM format)
TARGET_PATH="/$MINIO_BUCKET/$(date +%Y%m)/$DUMP_FILENAME"

# Archive the code-server directory
if ! tar -zcvf "$DUMP_PATH" /data/compose/150/code-server; then
    echo "Error: Failed to create backup archive!"
    exit 1
fi

# Content type and request date
CONTENT_TYPE="application/octet-stream"
DATE=$(date -R)

# MinIO request signature
STRING_TO_SIGN="PUT\n\n$CONTENT_TYPE\n$DATE\n$TARGET_PATH"
SIGNATURE_ENCODED=$(echo -en "$STRING_TO_SIGN" | openssl sha1 -hmac "$MINIO_SECRET_KEY" -binary | base64)

# Upload the backup file to MinIO
if curl -v -X PUT -T "$DUMP_PATH" \
        -H "Host: $MINIO_HOST" \
        -H "Date: $DATE" \
        -H "Content-Type: $CONTENT_TYPE" \
        -H "Authorization: AWS $MINIO_ACCESS_KEY:$SIGNATURE_ENCODED" \
        "https://$MINIO_HOST$TARGET_PATH"; then
    echo "Backup successfully uploaded to MinIO."
    rm "$DUMP_PATH"
else
    echo "Error: Upload to MinIO failed!"
    exit 1
fi
