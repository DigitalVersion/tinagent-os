#!/usr/bin/env bash
# setup-browser.sh — Install Google Chrome + wire it for agent use
# Run as root (or with sudo) after first boot from Tin OS ISO.
# Usage: sudo bash setup-browser.sh [AGENT_USER]
#
# What it does:
#   1. Downloads and installs Google Chrome stable
#   2. Creates /usr/local/bin/chrome-agent wrapper (CDP on :9222, AT-SPI2 on)
#   3. Adds KDE autostart entry so Chrome launches on login, ready for the agent
#
# Why Chrome instead of Chromium snap:
#   Snap confinement blocks the AT-SPI2 dbus interface.
#   Tin OS uses AT-SPI2 for screen_get_accessibility_tree() — snapped
#   Chromium breaks this core feature. Chrome (deb) does not.
#
# Chrome license note:
#   Google Chrome is free to use but not redistributable in OS images.
#   This script lets each user download it themselves, which is permitted.

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash setup-browser.sh"
  exit 1
fi

AGENT_USER="${1:-${SUDO_USER:-tintin}}"
AGENT_HOME="/home/$AGENT_USER"
echo ">>> Installing Chrome for user: $AGENT_USER"

# ── 1. Download and install Chrome ────────────────────────────────────────────
echo "Downloading Google Chrome..."
wget -q --show-progress \
  https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  -O /tmp/chrome.deb

DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/chrome.deb
rm /tmp/chrome.deb

# Suppress Chrome's "not your default browser" nag on first launch
mkdir -p "$AGENT_HOME/.config/google-chrome/Default"
cat > "$AGENT_HOME/.config/google-chrome/Default/Preferences" << 'EOF'
{
  "browser": { "check_default_browser": false },
  "profile": { "exit_type": "Normal" }
}
EOF
chown -R "$AGENT_USER:$AGENT_USER" "$AGENT_HOME/.config/google-chrome"

# ── 2. chrome-agent wrapper ────────────────────────────────────────────────────
cat > /usr/local/bin/chrome-agent << 'WRAPPER'
#!/bin/bash
# Launches Chrome with CDP on :9222 and AT-SPI2 accessibility enabled.
exec google-chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins='*' \
  --force-renderer-accessibility \
  --no-sandbox \
  --user-data-dir="${CHROME_PROFILE:-$HOME/.config/chrome-agent-profile}" \
  "$@"
WRAPPER
chmod +x /usr/local/bin/chrome-agent

# ── 3. KDE autostart entry ────────────────────────────────────────────────────
# Chrome starts automatically on login so the agent always has a browser ready.
mkdir -p "$AGENT_HOME/.config/autostart"
cat > "$AGENT_HOME/.config/autostart/chrome-agent.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Chrome Agent
Exec=/usr/local/bin/chrome-agent --no-first-run
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Start Chrome with CDP enabled for Tin OS agent
EOF
chown "$AGENT_USER:$AGENT_USER" "$AGENT_HOME/.config/autostart/chrome-agent.desktop"

# ── 4. fstab: Chrome cache in tmpfs ──────────────────────────────────────────
# Uses RAM for Chrome cache — no SSD wear, fast cold starts.
grep -q "chrome-agent-profile" /etc/fstab || \
  echo "tmpfs $AGENT_HOME/.config/chrome-agent-profile/Default/Cache  tmpfs defaults,noatime,size=512M 0 0" \
  >> /etc/fstab

echo ""
echo "✅ Chrome installed and wired for agent use."
echo ""
echo "Next steps:"
echo "  1. Reboot (or log out and back in) — Chrome will autostart on login"
echo "  2. Verify CDP is up: curl -s http://localhost:9222/json/version"
echo "  3. Start MCP server: cd ~/tinagent-os && uv run mcp_server.py"
echo "  4. Add to your MCP config:"
echo '     { "mcpServers": { "tinagent": { "url": "http://<machine-ip>:8765/sse" } } }'
