#!/bin/bash

set -e

# Validate required ENV vars
if [[ -z "$CRON_SCHEDULE" ]]; then
  echo "[❌] CRON_SCHEDULE is required"
  exit 1
fi

if [[ -z "$USERNAMES" ]]; then
  echo "[❌] USERNAMES is required"
  exit 1
fi

# Expose env vars to cron
printenv | grep -v "no_proxy" >> /etc/environment

# Write out the cron job
echo "$CRON_SCHEDULE /usr/local/bin/python /app/twitch_username_check.py >> /var/log/cron.log 2>&1" > /etc/cron.d/twitch-cron
chmod 0644 /etc/cron.d/twitch-cron
touch /var/log/cron.log

# Register cron job
crontab /etc/cron.d/twitch-cron

# Start cron
echo "[*] Starting cron with schedule: $CRON_SCHEDULE"
cron
tail -f /var/log/cron.log
