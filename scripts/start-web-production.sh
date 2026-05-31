#!/usr/bin/env bash
# Run Next.js standalone server (matches Docker production layout).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WEB="$ROOT/apps/web"
STANDALONE="$WEB/.next/standalone/apps/web"

if [[ ! -f "$STANDALONE/server.js" ]]; then
  echo "Run: pnpm --filter @pdf-to-rag-chunks/web build" >&2
  exit 1
fi

mkdir -p "$STANDALONE/.next"
cp -r "$WEB/public" "$STANDALONE/"
cp -r "$WEB/.next/static" "$STANDALONE/.next/"

export HOSTNAME="${HOSTNAME:-0.0.0.0}"
export PORT="${PORT:-3000}"
cd "$STANDALONE"
exec node server.js
