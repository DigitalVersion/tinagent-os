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
| **wl-clipboard** | Clipboard | `wl-copy`/`wl-paste` — Wayland-native. `type_text` pastes via clipboard, not key-by-key (safe for Unicode/emoji) |
| **Chromium CDP** | Browser | Full programmatic control: click, type, screenshot, JS eval, file upload — no Playwright overhead. Chromium = open source, redistributable |
| **AT-SPI2 + pydbus** | Screen reading | Reads UI state as structured data — far cheaper than screenshot+OCR for most tasks |
| **PipeWire virtual audio** | Audio | Virtual speaker/mic loopback: agent can play TTS, record output, without physical hardware |
| **grim** | Screenshots | Wayland-native screen capture. Faster than scrot on Wayland |
| **watchdog** | Reliability | Hardware watchdog: machine auto-reboots if agent crashes everything |
| **uv** | Python runtime | Fast, isolated Python env. No pip, no venv ceremony |

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

### Option A — ISO (v0.1)

1. Download `tinagent-os-0.1.iso` from [Releases](https://github.com/DigitalVersion/tinagent-os/releases)
2. Flash to USB: `dd if=tinagent-os-0.1.iso of=/dev/sdX bs=4M status=progress`
3. Boot → autologin as `tintin` → first-boot setup runs automatically
4. Fill in your API key: `~/.config/agentos/config.json`
5. Start the MCP server: `uv run mcp_server.py`

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

## What bootstrap.sh configures

Everything is automated. After running bootstrap, your machine has:

### Never sleep, never lock

```
/etc/systemd/logind.conf.d/tinagent-nosleep.conf
  HandleLidSwitch=ignore          # close lid → nothing happens
  IdleAction=ignore               # idle → nothing happens

/etc/systemd/sleep.conf.d/tinagent-nosleep.conf
  AllowSuspend=no
  AllowHibernation=no
```

KDE-level lock/screensaver disabled on first login via `~/.tinagent-firstrun.sh`.

### Autologin (SDDM)

```
/etc/sddm.conf.d/autologin.conf
  User=<AGENT_USER>
  Session=plasmawayland
```

### Accessibility (AT-SPI2)

```
/etc/profile.d/tinagent-accessibility.sh
  QT_ACCESSIBILITY=1
  QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
  GTK_MODULES=gail:atk-bridge
  GNOME_ACCESSIBILITY=1
  YDOTOOL_SOCKET=/run/ydotoold.socket
```

Enables AT-SPI2 system-wide so `screen_get_accessibility_tree()` works from session start.

### ydotool (Wayland input daemon)

```
/etc/udev/rules.d/80-ydotool.rules     → uinput device permissions
/etc/systemd/system/ydotoold.service   → starts ydotoold on boot
```

`ydotoold` runs as root, exposes socket at `/run/ydotoold.socket` with group `input` access.

### PipeWire virtual audio

```
/etc/pipewire/pipewire.conf.d/10-virtual-audio.conf
```

Creates:
- `virtual-speaker` (Audio/Sink) — agent plays audio here
- `virtual-mic` (Audio/Source/Virtual) — loopback from speaker
- loopback module connecting them

No physical audio hardware required. `audio_play()` and `audio_record()` work out of the box.

### Hardware watchdog

```
/etc/watchdog.conf
  watchdog-timeout = 60
  interval = 10

/etc/sysctl.conf
  kernel.panic = 10
  kernel.panic_on_oops = 1
```

Machine auto-reboots within 70 seconds if the agent hangs everything.

### polkit rules

```
/etc/polkit-1/rules.d/49-tinagent.rules
```

Members of the `input` group (which includes `AGENT_USER`) can manage login sessions and network without a password prompt.

### tmpfs mounts

```
/etc/fstab
  tmpfs /tmp                           size=2G
  tmpfs ~/.cache/google-chrome         size=1G
```

Chrome cache in RAM — no SSD wear, fast cold starts.

### Chrome cleanup cron

```
/etc/cron.d/tinagent-cleanup
  0 */12 * * *  pkill -9 -f chrome.*renderer
```

Kills orphaned Chrome renderer processes every 12 hours.

### Journal limits

```
/etc/systemd/journald.conf.d/tinagent.conf
  SystemMaxUse=500M
  MaxRetentionSec=1month
```

### NTP

```
/etc/systemd/timesyncd.conf.d/tinagent.conf
  NTP=time.google.com
  FallbackNTP=pool.ntp.org
```

---

## Agent config reference

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
  "chrome_profile": "~/.config/chromium-agent-profile"
}
```

Start Chromium with CDP enabled (run once, leave running):

```bash
chromium-agent   # wrapper installed by bootstrap.sh
```

Then start the MCP server:

```bash
cd ~/tinagent-os
uv run mcp_server.py
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
