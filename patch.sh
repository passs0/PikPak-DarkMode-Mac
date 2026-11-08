#!/usr/bin/env bash
# PikPak Adaptive Dark Mode Launcher
set -e

SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Auto-install dependencies if cloned fresh from GitHub
if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
  echo "[*] First-time setup: installing dependencies..."
  npm install --prefix "$SCRIPT_DIR"
fi

exec python3 "$SCRIPT_DIR/patch_pikpak.py" "$@"
