#!/bin/sh
# Explicit, operator-invoked DB maintenance. NEVER called by web startup.
# These flags are safety interlocks, not substitutes for DBA approval.
set -eu

operation="${1:-}"
case "$operation" in
  upgrade|seed) ;;
  *) echo "Usage: lucky-lab-db-maintenance.sh upgrade|seed" >&2; exit 2 ;;
esac

if [ "${LUCKY_LAB_DB_MAINTENANCE_APPROVED:-}" != "yes" ] ||
   [ "${LUCKY_LAB_DB_BACKUP_VERIFIED:-}" != "yes" ]; then
  echo "BLOCKED: explicit maintenance approval and verified backup required" >&2
  exit 3
fi

if [ "${LUCKY_LAB_DB_TARGET_CONFIRMED:-}" != "yes" ]; then
  echo "BLOCKED: confirm effective DATABASE_URL and target before operation" >&2
  exit 3
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "BLOCKED: DATABASE_URL must be explicitly supplied" >&2
  exit 3
fi

if [ "$operation" = "upgrade" ]; then
  exec flask --app app:create_app db upgrade
fi
exec flask --app app:create_app main seed
