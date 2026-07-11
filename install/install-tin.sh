#!/usr/bin/env bash
# Install the submission runtime on an existing Debian/Ubuntu/Kubuntu machine.
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo AGENT_USER=\$USER bash install/install-tin.sh"
  exit 1
fi

AGENT_USER=${AGENT_USER:-${SUDO_USER:-}}
[[ -n "$AGENT_USER" && "$AGENT_USER" != root ]] || { echo "Set AGENT_USER to the desktop owner."; exit 1; }
AGENT_HOME=$(getent passwd "$AGENT_USER" | cut -d: -f6)
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DEST=/opt/tin-os
PORT=${TIN_PORT:-8080}

echo ">>> Installing Tin OS runtime for $AGENT_USER"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y python3 tmux curl ca-certificates

mkdir -p "$DEST"
rm -rf "$DEST/tin_os"
cp -a "$SRC/tin_os" "$DEST/tin_os"
chown -R root:root "$DEST"

cat > /etc/systemd/system/tin-os.service <<EOF
[Unit]
Description=Tin OS browser home and tmux cockpit
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$AGENT_USER
WorkingDirectory=$DEST
Environment=PYTHONUNBUFFERED=1
Environment=TIN_WORKSPACE=$AGENT_HOME
ExecStart=/usr/bin/python3 -m tin_os.server --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now tin-os.service

for _ in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:$PORT/api/status" >/dev/null; then break; fi
  sleep .5
done
curl -fsS "http://127.0.0.1:$PORT/api/status" >/dev/null || { journalctl -u tin-os -n 40 --no-pager; exit 1; }

LAN_IP=$(hostname -I 2>/dev/null | tr ' ' '\n' | grep -E '^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' | head -1 || true)
TS_IP=$(command -v tailscale >/dev/null && tailscale ip -4 2>/dev/null | head -1 || true)

echo
echo "✅ Tin OS is running."
[[ -n "$LAN_IP" ]] && echo "   LAN:      http://$LAN_IP:$PORT"
[[ -n "$TS_IP" ]] && echo "   Tailnet:  http://$TS_IP:$PORT"
echo "   Local:    http://127.0.0.1:$PORT"
echo
echo "Optional AI apps: sudo -u $AGENT_USER bash $SRC/install/install-ai-apps.sh"
echo "Security: expose Tin only on a trusted LAN or private tailnet. Do not publish it to the internet."
