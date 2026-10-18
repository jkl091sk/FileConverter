#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3,12):
    raise SystemExit("Python 3.12+ is required.")
print("Python:", sys.version.split()[0])
PY
for cmd in ffmpeg libreoffice; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing system dependency: $cmd"
    echo "Ubuntu: sudo apt install ffmpeg libreoffice libmagic1"
    echo "Arch:   sudo pacman -S ffmpeg libreoffice-fresh file"
    exit 1
  fi
done
"$PYTHON" -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
mkdir -p data temp
python - <<'PY'
import asyncio
from database.database import init_db
asyncio.run(init_db())
print("Database initialized.")
PY
echo "Installation complete."
