# TinAgentOS MCP Server

> Turn any Kubuntu machine into an MCP endpoint for AI agents.

Built on KDE Plasma + Wayland. Exposes desktop control as [MCP](https://modelcontextprotocol.io) tools, resources, and prompts so any AI agent can see and control the machine remotely.

## What's included

| Type | Count | Description |
|------|-------|-------------|
| 🔧 Tools | 24 | Browser (CDP), input (ydotool), screen, system, audio |
| 📦 Resources | 10 | Live state: screen, browser tabs, clipboard, system health |
| 💬 Prompts | 4 | Task templates: web, UI, research, file |

## Quick start

### 1. Install the OS

Flash the TinAgentOS ISO (Kubuntu 24.04 base) onto your machine.
After boot, run:

```bash
sudo bash ~/bootstrap_agentdistro.sh
tailscale up --auth-key=tskey-...
```

### 2. Start the MCP server

```bash
uv run mcp_server.py
# MCP SSE endpoint: http://localhost:8765
```

### 3. Connect your agent

```json
{
  "mcpServers": {
    "tinagent": {
      "url": "http://<machine-ip>:8765/sse"
    }
  }
}
```

## Architecture

```
AI Agent (Claude / GPT / any)
    │
    └── MCP SSE (HTTP :8765)
            │
    ┌───────┴────────────────────────────┐
    │          TinAgentOS MCP Server     │
    │                                    │
    │  tools/browser.py  → CDP :9222     │
    │  tools/input.py    → ydotool       │
    │  tools/screen.py   → grim + AT-SPI │
    │  tools/system.py   → subprocess    │
    │  tools/audio.py    → PipeWire      │
    └────────────────────────────────────┘
            │
    Kubuntu 24.04 + KDE Plasma (Wayland)
```

## Contributing

This is a skeleton — stubs are ready, implementations welcome!

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to pick up a tool and send a PR.

**Good first issues:**
- `tools/browser.py` — implement CDP via websockets
- `tools/input.py` — implement ydotool subprocess calls
- `tools/screen.py` — implement grim screenshot + AT-SPI tree
- `tools/system.py` — implement subprocess + pathlib

## License

MIT
