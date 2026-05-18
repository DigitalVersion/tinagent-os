# TinAgentOS

**The best environment for humans and AI agents to share a machine — equally.**

Boot once. Both you and your agent have full access to the same desktop:
you via keyboard and mouse, the agent via MCP.
When you're tired, the agent works. When the agent is done, you take over.
No scheduling. No handoff ceremony. Just a machine that's always ready for whoever needs it.

---

## Why this exists

Most "computer use" setups treat agents as second-class citizens — sandboxed, screenshot-dependent, burning tokens just to see what's on screen.

TinAgentOS flips the model:

- **Accessibility-first** — the agent reads the UI as structured data (AT-SPI2), not pixels. No screenshot → no token flood → no context overflow.
- **Human-ready** — same KDE Plasma desktop you already know. Sit down and use it normally.
- **Self-hosted** — your hardware, your data, no cloud dependency.
- **Token-efficient by design** — `screen://accessibility` costs a fraction of a screenshot. Use it first, screenshot only when structure isn't enough.

---

## Tech stack

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent (any)                        │
│         Claude · GPT · local model · your code          │
└──────────────────────┬──────────────────────────────────┘
                       │  MCP over SSE (HTTP)
┌──────────────────────▼──────────────────────────────────┐
│               TinAgentOS MCP Server                      │
│                                                          │
│  🔧 Tools (30)     📦 Resources (10)    💬 Prompts (4)  │
└──┬──────────┬────────────┬──────────────┬───────────────┘
   │          │            │              │
   ▼          ▼            ▼              ▼
Chrome      ydotool      grim +        subprocess
CDP :9222   Wayland      AT-SPI2       + pathlib
(browser)   (input)      (screen)      (system)
                                          │
                                       PipeWire
                                    virtual audio
                                      (audio)
│
└── KDE Plasma 6 · Wayland · Kubuntu 24.04 LTS
```

### Why each piece was chosen

| Component | Role | Why |
|-----------|------|-----|
| **KDE Plasma + Wayland** | Desktop | Best accessibility (AT-SPI2) support on Linux. Wayland = no X11 hacks |
| **dbus-broker** | IPC | Replaces dbus-daemon. Faster, more reliable, better for headless agents |
| **ydotool** | Keyboard/mouse | Works on Wayland (xdotool doesn't). Controls input at kernel level via uinput |
| **wl-clipboard** | Clipboard | `wl-copy`/`wl-paste` — Wayland-native. `type_text` pastes via clipboard, not key-by-key (safe for Unicode/Vietnamese) |
| **Chrome CDP** | Browser | Full programmatic control: click, type, screenshot, JS eval, file upload — no Playwright overhead |
| **AT-SPI2 + pydbus** | Screen reading | Reads UI state as structured data — far cheaper than screenshot+OCR for most tasks |
| **PipeWire virtual audio** | Audio | Virtual speaker/mic loopback: agent can play TTS, record output, without physical hardware |
| **grim** | Screenshots | Wayland-native screen capture. Faster than scrot on Wayland |
| **RustDesk** | Remote access | Self-hostable remote desktop. Human can take over or observe the agent |
| **watchdog** | Reliability | Hardware watchdog: machine auto-reboots if agent crashes everything |

---

## MCP primitives

### 🔧 Tools — agent *does* things

```python
# Browser (Chrome CDP)
browser_navigate(url)          # go to URL
browser_click(selector)        # click DOM element
browser_type(selector, text)   # type into input
browser_screenshot()           # capture tab → base64 PNG
browser_eval(js)               # run JavaScript
browser_get_text(selector)     # extract visible text
browser_upload_file(sel, path) # set file input
browser_new_tab(url)           # open tab
browser_close_tab(target_id)   # close tab

# Input (ydotool + wl-clipboard)
input_type_text(text)          # paste via clipboard (unicode-safe)
input_key_press(keys)          # ctrl+c, Return, alt+F4 ...
input_mouse_click(x, y)        # click at coordinates
input_mouse_move(x, y)         # move cursor
input_scroll(x, y, direction)  # scroll
clipboard_get()                # read clipboard
clipboard_set(text)            # write clipboard

# Screen (grim + AT-SPI2)
screen_screenshot()            # full desktop PNG
screen_screenshot_region(...)  # cropped region
screen_get_accessibility_tree()# structured UI state (JSON)
screen_find_element(label)     # find by accessible name
screen_get_active_window()     # focused window info

# System
system_run(command)            # shell command
system_read_file(path)         # read file
system_write_file(path, text)  # write file
system_list_dir(path)          # list directory
system_launch_app(app)         # open application
system_kill_process(name)      # kill by name

# Audio (PipeWire)
audio_play(file_path)          # play via virtual speaker
audio_record(duration, path)   # record from virtual mic
audio_tts(text)                # text-to-speech
```

### 📦 Resources — agent *reads* state

```
screen://current               # live desktop screenshot
screen://accessibility         # AT-SPI UI tree (JSON)
screen://active-window         # focused window
browser://tabs                 # open tabs list
browser://current-url          # active tab URL
browser://page-source          # current page HTML
system://status                # CPU / RAM / disk / uptime
system://processes             # top processes
system://clipboard             # clipboard content
system://env                   # environment variables
```

### 💬 Prompts — reusable task templates

```
web_task(goal, url?)           # browser-based tasks
ui_task(description)           # desktop UI tasks
research_task(topic, format?)  # multi-source research
file_task(instruction, dir?)   # filesystem tasks
```

---

## Getting started

### Option A — Fresh install (recommended)

1. Download the latest TinAgentOS ISO *(coming soon — v0.1 build in progress)*
2. Flash to USB → boot → create your user account
3. Done. The MCP server starts automatically on login.

### Option B — Bootstrap on existing Kubuntu 24.04

```bash
wget https://raw.githubusercontent.com/DigitalVersion/tinagent-os/main/install/bootstrap.sh
sudo AGENT_USER=$USER bash bootstrap.sh
# reboot
```

### Connect your agent

Add to your MCP config:

```json
{
  "mcpServers": {
    "tinagent": {
      "url": "http://<machine-ip>:8765/sse"
    }
  }
}
```

That's it. No cloud account. No API key for the OS itself. No special agent runtime.
The machine is now a shared workspace — use it yourself or let your agent use it, interchangeably.

---

## Config reference

After bootstrap, edit `~/.config/agentos/config.json`:

```json
{
  "brain": {
    "provider": "openrouter",
    "model": "anthropic/claude-sonnet-4-20250514",
    "api_key": "YOUR_OPENROUTER_KEY"
  },
  "mcp_port": 8765,
  "cdp_port": 9222,
  "screen": { "width": 1920, "height": 1080, "scale": 1.0 },
  "state_db": "~/agent-workspace/state.db",
  "downloads_dir": "~/agent-downloads",
  "workspace_dir": "~/agent-workspace",
  "retry": { "max": 3, "delay_sec": 2 },
  "chrome_profile": "~/.config/chrome-agent-profile"
}
```

Chrome runtime command (auto-started by bootstrap):
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --force-renderer-accessibility \
  --no-sandbox \
  --user-data-dir=~/.config/chrome-agent-profile
```

---

## Repo structure

```
tinagent-os/
├── mcp_server.py        # Entry point — SSE MCP server
├── pyproject.toml
│
├── tools/               # @mcp.tool() — agent actions
│   ├── browser.py       # Chrome CDP (9 tools)
│   ├── input.py         # ydotool + clipboard (7 tools)
│   ├── screen.py        # grim + AT-SPI (5 tools)
│   ├── system.py        # subprocess + pathlib (6 tools)
│   └── audio.py         # PipeWire (3 tools)
│
├── resources/           # @mcp.resource() — live state
│   ├── screen.py        # screen://...
│   ├── browser.py       # browser://...
│   └── system.py        # system://...
│
├── prompts/             # @mcp.prompt() — task templates
│   └── tasks.py
│
└── install/
    └── bootstrap.sh     # Full system setup script
```

---

## Token efficiency

Screenshots are expensive. One 1080p PNG ≈ 1,000–2,000 tokens. A page of 10 interactions = context blown.

TinAgentOS prioritizes structured data over pixels:

| Task | ❌ Expensive | ✅ Efficient |
|------|-------------|-------------|
| Read page content | `browser_screenshot()` → OCR | `browser_get_text()` or `browser://page-source` |
| Find a button | screenshot + vision | `screen_find_element("Submit")` → coordinates |
| Check app state | `screen_screenshot()` | `screen://accessibility` → JSON tree |
| Read clipboard | screenshot | `system://clipboard` |

**Rule of thumb:** reach for `screen://accessibility` first. Use screenshots only when visual layout matters (images, charts, captchas).

---

## Contributing

The skeleton is done. Every tool has a docstring explaining exactly what to use — just implement and PR.

**Good first issues:**
- `tools/input.py` — `ydotool` subprocess calls (easiest)
- `tools/system.py` — `subprocess` + `pathlib` (easiest)
- `tools/browser.py` — CDP via `websockets`
- `tools/screen.py` — `grim` + `pydbus` AT-SPI tree

See [CONTRIBUTING.md](CONTRIBUTING.md) for implementation notes.

---

## License

MIT — build something cool.
