#!/usr/bin/env bash
# bootstrap.sh — Tin OS full system setup
# Run as root. Works in chroot (ISO build) or on live system.
# Usage: sudo AGENT_USER=tintin bash bootstrap.sh

set -euo pipefail

IN_CHROOT=false
[[ "$(systemctl is-system-running 2>/dev/null || echo 'chroot')" == "chroot" ]] && IN_CHROOT=true

if [[ -z "${AGENT_USER:-}" ]]; then
  read -rp "Agent username (e.g. tintin): " AGENT_USER
fi
AGENT_HOME="/home/$AGENT_USER"
echo ">>> Setting up Tin OS for user: $AGENT_USER (chroot=$IN_CHROOT)"

# ── 1. Locale ─────────────────────────────────────────────────────────────────
echo "LC_ALL=en_US.UTF-8" >> /etc/environment
echo "LANG=en_US.UTF-8"   >> /etc/environment
locale-gen en_US.UTF-8 2>/dev/null || true

# ── 2. Remove bloat ───────────────────────────────────────────────────────────
if ! $IN_CHROOT; then
  snap remove --purge firefox 2>/dev/null || true
  # Chromium snap is kept — it's our browser (open source, redistributable)
fi
DEBIAN_FRONTEND=noninteractive apt-get purge -y \
  plasma-discover update-notifier unattended-upgrades \
  ibus fcitx5 fcitx5-vietnamese 2>/dev/null || true
apt-get autoremove -y

# ── 3. Install packages ───────────────────────────────────────────────────────
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  dbus-broker ydotool wl-clipboard \
  python3-pip python3-venv \
  watchdog openssh-server curl wget

# Browser (optional — skip in ISO builds, user runs setup-browser.sh post-boot)
# Set SKIP_BROWSER=1 to omit Chrome (e.g. GitHub Actions ISO build).
if [[ "${SKIP_BROWSER:-0}" != "1" ]]; then
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    -O /tmp/chrome.deb
  DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/chrome.deb
  rm /tmp/chrome.deb
  # CDP wrapper installed here; also installed by setup-browser.sh post-boot
  cat > /usr/local/bin/chrome-agent << 'WRAPPER'
#!/bin/bash
exec google-chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins='*' \
  --force-renderer-accessibility \
  --no-sandbox \
  --user-data-dir="${CHROME_PROFILE:-$HOME/.config/chrome-agent-profile}" \
  "$@"
WRAPPER
  chmod +x /usr/local/bin/chrome-agent
fi

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# RustDesk
wget -q https://github.com/rustdesk/rustdesk/releases/latest/download/rustdesk-latest-x86_64.deb \
  -O /tmp/rustdesk.deb
DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/rustdesk.deb
rm /tmp/rustdesk.deb

# ── 4. Never sleep / never lock ───────────────────────────────────────────────
mkdir -p /etc/systemd/logind.conf.d /etc/systemd/sleep.conf.d

cat > /etc/systemd/logind.conf.d/tinagent-nosleep.conf << 'EOF'
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
IdleAction=ignore
EOF

cat > /etc/systemd/sleep.conf.d/tinagent-nosleep.conf << 'EOF'
[Sleep]
AllowSuspend=no
AllowHibernation=no
AllowHybridSleep=no
AllowSuspendThenHibernate=no
EOF

# ── 5. SDDM autologin ─────────────────────────────────────────────────────────
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/autologin.conf << EOF
[Autologin]
User=$AGENT_USER
Session=plasmawayland
EOF

# ── 6. Accessibility env ──────────────────────────────────────────────────────
cat > /etc/profile.d/tinagent-accessibility.sh << 'EOF'
export QT_ACCESSIBILITY=1
export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
export GTK_MODULES=gail:atk-bridge
export GNOME_ACCESSIBILITY=1
export YDOTOOL_SOCKET=/run/ydotoold.socket
gsettings set org.gnome.desktop.interface toolkit-accessibility true 2>/dev/null || true
EOF

# ── 7. ydotool udev + service ─────────────────────────────────────────────────
cat > /etc/udev/rules.d/80-ydotool.rules << 'EOF'
KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"
EOF

cat > /etc/systemd/system/ydotoold.service << 'EOF'
[Unit]
After=multi-user.target
[Service]
Type=simple
ExecStart=/usr/bin/ydotoold --socket-path=/run/ydotoold.socket --socket-own=root:input --socket-perm=0660
Restart=always
[Install]
WantedBy=multi-user.target
EOF

# ── 8. Virtual audio (PipeWire) ───────────────────────────────────────────────
mkdir -p /etc/pipewire/pipewire.conf.d
cat > /etc/pipewire/pipewire.conf.d/10-virtual-audio.conf << 'EOF'
context.modules = [
  { name = libpipewire-module-null-sink
    args = { media.class = "Audio/Sink"
             node.name = "virtual-speaker"
             node.description = "Virtual Speaker" } }
  { name = libpipewire-module-null-sink
    args = { media.class = "Audio/Source/Virtual"
             node.name = "virtual-mic"
             node.description = "Virtual Mic"
             audio.position = [ FL FR ] } }
  { name = libpipewire-module-loopback
    args = { capture.props = { node.target = "virtual-speaker" }
             playback.props = { node.target = "virtual-mic" } } }
]
EOF

# ── 9. Watchdog ───────────────────────────────────────────────────────────────
cat > /etc/watchdog.conf << 'EOF'
watchdog-device = /dev/watchdog
watchdog-timeout = 60
interval = 10
EOF
echo "kernel.panic = 10"        >> /etc/sysctl.conf
echo "kernel.panic_on_oops = 1" >> /etc/sysctl.conf

# ── 10. Journal ───────────────────────────────────────────────────────────────
mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/tinagent.conf << 'EOF'
[Journal]
SystemMaxUse=500M
MaxRetentionSec=1month
ForwardToSyslog=no
EOF

# ── 11. NTP ───────────────────────────────────────────────────────────────────
mkdir -p /etc/systemd/timesyncd.conf.d
cat > /etc/systemd/timesyncd.conf.d/tinagent.conf << 'EOF'
[Time]
NTP=time.google.com
FallbackNTP=pool.ntp.org
EOF

# ── 12. polkit ────────────────────────────────────────────────────────────────
cat > /etc/polkit-1/rules.d/49-tinagent.rules << 'EOF'
polkit.addRule(function(action, subject) {
  if ((action.id.indexOf("org.freedesktop.login1.") === 0 ||
       action.id.indexOf("org.freedesktop.NetworkManager.") === 0) &&
      subject.isInGroup("input")) { return polkit.Result.YES; }
});
EOF

# ── 13. fstab tmpfs ───────────────────────────────────────────────────────────
grep -q "tmpfs /tmp" /etc/fstab || cat >> /etc/fstab << EOF
tmpfs /tmp                                    tmpfs defaults,noatime,size=2G 0 0
tmpfs $AGENT_HOME/.cache/google-chrome        tmpfs defaults,noatime,size=1G 0 0
EOF

# ── 14. Chrome cleanup cron ───────────────────────────────────────────────────
echo "0 */12 * * * $AGENT_USER pkill -9 -f chrome.*renderer" > /etc/cron.d/tinagent-cleanup

# ── 15. User + groups ─────────────────────────────────────────────────────────
id "$AGENT_USER" &>/dev/null || useradd -m -s /bin/bash "$AGENT_USER"
usermod -aG input,sudo "$AGENT_USER"

# ── 16. Agent workspace + config skeleton ────────────────────────────────────
mkdir -p "$AGENT_HOME/agent-workspace" "$AGENT_HOME/agent-downloads"
mkdir -p "$AGENT_HOME/.config/agentos"
cat > "$AGENT_HOME/.config/agentos/config.json" << EOF
{
  "brain": {
    "provider": "openrouter",
    "model": "anthropic/claude-sonnet-4-20250514",
    "api_key": "FILL_IN_YOUR_OPENROUTER_KEY"
  },
  "mcp_port": 8765,
  "cdp_port": 9222,
  "screen": {"width": 1920, "height": 1080, "scale": 1.0},
  "state_db": "$AGENT_HOME/agent-workspace/state.db",
  "downloads_dir": "$AGENT_HOME/agent-downloads",
  "workspace_dir": "$AGENT_HOME/agent-workspace",
  "retry": {"max": 3, "delay_sec": 2},
  "chrome_profile": "$AGENT_HOME/.config/chrome-agent-profile"
}
EOF
chown -R "$AGENT_USER:$AGENT_USER" \
  "$AGENT_HOME/agent-workspace" \
  "$AGENT_HOME/agent-downloads" \
  "$AGENT_HOME/.config/agentos"

# ── 17. firstrun.sh — runs on first login (KDE + MCP server) ─────────────────
cat > "$AGENT_HOME/.tinagent-firstrun.sh" << 'FIRSTRUN'
#!/usr/bin/env bash
# Runs once on first login to apply KDE settings and start MCP server.
# Auto-deleted after run.

kwriteconfig5 --file kscreenlockerrc --group Daemon --key Autolock false
kwriteconfig5 --file kscreenlockerrc --group Daemon --key LockOnResume false
kwriteconfig5 --file powermanagementprofilesrc --group AC --group HandleButtonEvents --key lidAction 0
kwriteconfig5 --file powermanagementprofilesrc --group AC --group HandleButtonEvents --key triggerLidActionWhenExternalMonitorPresent false
kwriteconfig5 --file powermanagementprofilesrc --group Battery --group HandleButtonEvents --key lidAction 0
kwriteconfig5 --file powermanagementprofilesrc --group Battery --group SuspendSession --key suspendType 0
kwriteconfig5 --file powermanagementprofilesrc --group AC --group DPMSControl --key idleTime 0
kwriteconfig5 --file kwalletrc --group Wallet --key Enabled false
kwriteconfig5 --file kdeglobals --group KDE --key AnimationDurationFactor 0
kwriteconfig5 --file plasmanotifyrc --group Notifications --key DoNotDisturb true
kwriteconfig5 --file kwinrc --group Wayland --key OutputScaleOverride 1
echo 'export KWIN_WAYLAND_VIRTUAL_SCREENS=1920x1080' >> ~/.profile

# Self-delete
rm -f ~/.tinagent-firstrun.sh
sed -i '/tinagent-firstrun/d' ~/.profile
FIRSTRUN
chmod +x "$AGENT_HOME/.tinagent-firstrun.sh"
echo 'if [[ -f ~/.tinagent-firstrun.sh ]]; then bash ~/.tinagent-firstrun.sh; fi' >> "$AGENT_HOME/.profile"
chown "$AGENT_USER:$AGENT_USER" "$AGENT_HOME/.tinagent-firstrun.sh" "$AGENT_HOME/.profile"

# ── 18. Enable services (skip start in chroot) ────────────────────────────────
systemctl enable ydotoold          2>/dev/null || true
systemctl enable systemd-timesyncd 2>/dev/null || true
systemctl enable dbus-broker       2>/dev/null || true
systemctl enable ssh               2>/dev/null || true
systemctl enable tailscaled        2>/dev/null || true
if ! $IN_CHROOT; then
  systemctl disable dbus-daemon    2>/dev/null || true
  systemctl daemon-reload
  systemctl start ydotoold ssh tailscaled systemd-timesyncd
  udevadm control --reload-rules && udevadm trigger
  sysctl -p
fi

echo ""
echo "✅ Tin OS bootstrap complete."
echo ""
echo "Next steps:"
echo "  1. Reboot"
echo "  2. Fill api_key in $AGENT_HOME/.config/agentos/config.json"
echo "  3. Start MCP server: uv run mcp_server.py"
