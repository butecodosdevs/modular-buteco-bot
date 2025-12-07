#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "[farm-api] DATABASE_URL is not set. Aborting." >&2
  exit 1
fi

echo "[farm-api] Running database migrations..."
bunx drizzle-kit migrate

echo "[farm-api] Migrations finished successfully."
