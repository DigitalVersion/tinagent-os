# Contributing to TinAgentOS

Thanks for contributing! Each tool file is self-contained — pick one, implement the stubs, send a PR.

## How to pick up a stub

1. Find a function with `raise NotImplementedError`
2. Read the docstring — it tells you exactly what to use
3. Implement it
4. Test on a real Kubuntu machine (or the TinAgentOS ISO)
5. PR with: what you implemented + how you tested

## Setup for development

```bash
git clone https://github.com/DigitalVersion/tinagent-os
cd tinagent-os
uv run mcp_server.py
```

Requirements: Kubuntu 24.04, KDE Plasma Wayland, Chrome running on port 9222.

## Tool implementation notes

### browser.py
- CDP websocket endpoint: `ws://localhost:9222`
- Use `websockets` lib or `pychrome`
- Test: `curl http://localhost:9222/json/version`

### input.py
- `type_text`: always use `wl-copy '{text}' && ydotool key ctrl+v` — NOT `ydotool type`
- `key_press`: `ydotool key ctrl+c` etc.
- Socket: `YDOTOOL_SOCKET=/run/ydotoold.socket`

### screen.py
- Screenshot: `grim /tmp/screen.png` (Wayland) or `scrot` fallback
- Accessibility: `pydbus` → `org.a11y.Bus` → AT-SPI2

### system.py
- Keep it simple: `subprocess.run(cmd, shell=True, capture_output=True)`
- No sandboxing in v0.1 — add allowlist in v0.2

### audio.py
- Virtual sink name: `virtual-speaker`
- Play: `paplay --device=virtual-speaker file.wav`
- Record: `pw-record --target=virtual-mic output.wav`

## PR checklist

- [ ] Implements at least one stub fully
- [ ] Docstring unchanged (or improved)
- [ ] No new dependencies without updating `pyproject.toml`
- [ ] Tested on Kubuntu 24.04 Wayland
