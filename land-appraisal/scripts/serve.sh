#!/usr/bin/env bash
# Serve the report folder on port 8099 (preview + LAN access from a phone).
#   bash scripts/serve.sh [port]
set -euo pipefail
PORT="${1:-8099}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# refuse to double-bind the port
if (ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -q ":${PORT} "; then
  echo "port ${PORT} is already in use — stop the old server first (pkill -f 'http.server ${PORT}')"
  exit 1
fi

echo "serving ${ROOT} on http://0.0.0.0:${PORT}"
echo "  local   : http://127.0.0.1:${PORT}/viewer.html"
if command -v hostname >/dev/null 2>&1; then
  LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
  [ -n "${LAN_IP:-}" ] && echo "  phone   : http://${LAN_IP}:${PORT}/viewer.html"
fi
exec python3 -m http.server "${PORT}" --bind 0.0.0.0 --directory "${ROOT}"
