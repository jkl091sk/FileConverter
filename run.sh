#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f .env ]; then echo "Missing .env. Copy .env.example to .env and set BOT_TOKEN."; exit 1; fi
. .venv/bin/activate
exec python bot.py
