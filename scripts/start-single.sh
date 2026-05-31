#!/bin/sh
set -e
uvicorn src.main:app --host 0.0.0.0 --port 8080 &
cd /app/apps/web && pnpm start --port 3000 --hostname 0.0.0.0
