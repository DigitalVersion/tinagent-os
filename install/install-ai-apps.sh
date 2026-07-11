#!/usr/bin/env bash
# Install the two browser AI doors surfaced by Tin OS.
set -euo pipefail

if [[ $EUID -eq 0 ]]; then
  echo "Run as the desktop owner, not root: bash install/install-ai-apps.sh"
  exit 1
fi

export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$PATH"

echo ">>> Installing OpenCode (free first-value lane)"
if ! command -v opencode >/dev/null 2>&1; then
  curl -fsSL https://opencode.ai/install | bash
  export PATH="$HOME/.opencode/bin:$PATH"
fi
opencode --version

echo
echo ">>> Installing Pi Web (optional configured-provider lane)"
if command -v npm >/dev/null 2>&1; then
  npm install -g @jmfederico/pi-web
  command -v pi-web-server >/dev/null && pi-web-server --version 2>/dev/null || true
else
  echo "npm is not installed, so Pi Web was skipped."
  echo "Install a current Node.js/npm runtime, then run: npm install -g @jmfederico/pi-web"
fi

echo
echo "✅ AI app installation finished."
echo "Return to Tin OS and press Start OpenCode Web or Start Pi Web."
