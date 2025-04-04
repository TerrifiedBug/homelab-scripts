#!/bin/bash
curl -k -s -S -X "POST" "https://redacted/api/backup" \
  -H 'x-api-key: redacted' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d '{ "password": "" }' \
  --output /source/scripts/portainer/backups/portainer_snapshot.tar.gz

# Exit with the curl exit code
exit $?
