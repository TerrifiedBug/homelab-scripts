#!/bin/bash

set -e

# === Validate environment variables ===

if [[ -z "$CRON_SCHEDULE" ]]; then
  echo "[❌] Error: CRON_SCHEDULE environment variable is required."
  exit 1
fi

if [[ -z "$USERNAMES" ]]; then
  echo "[❌] Error: USERNAMES environment variable is required."
  exit 1
fi

# === Inject env vars into cron runtime ===
printenv | grep -v "no_proxy" >> /etc/environment

# === Create cron job dynamically ===
echo "$CRON_SCHEDULE /usr/local/bin/python /app/twitch_username_check.py >> /var/log/cron.log 2>&1" > /etc/cron.d/twitch-cron
chmod 0644 /etc/cron.d/twitch-cron
touch /var/log/cron.log

# === Register the new crontab ===
crontab /etc/cron.d/twitch-cron

# === Start cron and tail the log ===
echo "[*] Starting cron with schedule: $CRON_SCHEDULE"
cron
tail -f /var/log/cron.log
