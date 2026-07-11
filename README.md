# Tin OS

**Install it, connect it to the internet, open a local URL, and talk to your computer.**

This repository is the build and bootstrap home for **Tin OS** (repo name: `tinagent-os`):
a conversational operating layer for human + AI work.

The intended first-run experience is simple:

```text
Install Tin OS
  -> connect Ethernet or Wi-Fi
  -> the machine shows: Open http://tin.local
     or http://192.168.x.x:2024
  -> the owner opens it from a phone or laptop
  -> the owner chats with the OS
  -> Tin can inspect the machine, run tasks, coordinate agents,
     and ask for human approval before risky actions
```

Tin OS is not trying to replace the Linux kernel. It is a packaged operating
environment on top of Linux/Kubuntu that makes **conversation the primary control
surface** and AI agents first-class workers on the machine.

---

## Product framing

Organizations are moving from “people using apps” to **people coordinating AI
agents, tools, and machines**. Today that work is scattered across terminals,
browser tabs, project management tools, remote desktops, and chatbots.

Tin OS turns a machine into a local command center:

- **Chat is the desktop** — the owner talks to the machine through a browser.
- **Agents are applications** — coding agents, browser agents, local models, and
  automation workers can be launched, observed, and stopped.
- **Jobs are processes** — long-running work survives tab closes and reconnects.
- **Human approval is the permission system** — destructive or irreversible work
  must ask the owner first.
- **Evidence is the audit log** — work is not “done” until the system records how
  it was verified.

For hackathon / P4 language: **Tin OS is a working Human-AgentOS** — a system for
assigning, governing, executing, and measuring human + AI work.

---

## What exists in this repo today

This repo currently contains the **OS substrate** for Tin OS:

- Kubuntu-based ISO build workflow (`.github/workflows/build-iso.yml`).
- System bootstrap script (`install/bootstrap.sh`) that configures:
  - autologin,
  - no sleep / no lock,
  - Tailscale,
  - SSH,
  - ydotool for Wayland input,
  - AT-SPI2 accessibility environment,
  - PipeWire virtual audio,
  - watchdog and journal limits,
  - Chrome setup hook.
- Post-boot browser setup (`install/setup-browser.sh`) for Chrome + CDP.
- A Python MCP server skeleton (`mcp_server.py`) with modules for:
  - browser control,
  - keyboard/mouse input,
  - screen/accessibility reading,
  - system operations,
  - audio.

### Reality check

This repo is **not yet** the complete Tin OS product.

The following pieces are still to be implemented or integrated here:

- Local Tin web door on `http://tin.local` / `http://<LAN-IP>:2024`.
- Conversational UI bundled into the OS image.
- First-boot wizard for owner account, network, model/API provider, and tailnet.
- Durable job ledger / evidence layer.
- Human approval broker for privileged or risky operations.
- Built-in cockpit showing live agent sessions and machine state.
- Full implementation of all MCP tools/resources; several are still stubs.

The live prototype that inspired this repo uses a working stack of Pi Web, Tin
cockpit, tmux workers, Tailscale, and an ATP/Central Command job ledger. This repo
is the path to make that experience installable and repeatable.

See:

- [`docs/first-boot-flow.md`](docs/first-boot-flow.md) for the target first-boot
  experience: install, connect to the network, open `tin.local` / `:2024`, and
  chat with the OS.
- [`docs/product-philosophy.md`](docs/product-philosophy.md) for the product
  principle: a fresh install must have a free first-value AI path, with OpenCode
  Web as the default candidate.
- [`docs/inventory-gap.md`](docs/inventory-gap.md) for the current gap between
  the live Tin prototype and this installable repo.

---

## Target architecture

```text
Phone / laptop browser
        |
        |  http://tin.local or http://<LAN-IP>:2024
        v
+----------------------------------------------------+
| Tin Web Door                                       |
| - chat with the OS                                 |
| - live cockpit cards                               |
| - owner approval prompts                           |
+-------------------------+--------------------------+
                          |
                          v
+----------------------------------------------------+
| Tin Runtime                                        |
| - local agent session                              |
| - job ledger + evidence                            |
| - worker/session manager                           |
| - permission / approval broker                     |
+------------+----------------+----------------------+
             |                |
             v                v
+---------------------+   +--------------------------+
| MCP / desktop tools |   | OS services              |
| - browser CDP       |   | - Tailscale              |
| - AT-SPI2 UI tree   |   | - SSH                    |
| - ydotool input     |   | - systemd                |
| - screenshots       |   | - watchdog               |
| - audio loopback    |   | - browser autostart      |
+---------------------+   +--------------------------+
             |
             v
       Kubuntu / Linux base
```

---

## Current developer quick start

### Bootstrap an existing Kubuntu machine

```bash
wget https://raw.githubusercontent.com/DigitalVersion/tinagent-os/main/install/bootstrap.sh
sudo AGENT_USER=$USER bash bootstrap.sh
# reboot
```

Then install Chrome for the browser-control layer:

```bash
sudo bash install/setup-browser.sh "$USER"
# reboot or log out/in
curl -s http://localhost:9222/json/version
```

Start the current MCP server skeleton:

```bash
uv run mcp_server.py --host 0.0.0.0 --port 8765
```

Connect an MCP-capable agent to:

```text
http://<machine-ip>:8765/sse
```

That gives an external agent a path to the machine. The future Tin OS default is
stronger: the owner opens `http://tin.local` / `:2024` and chats directly with the
OS.

---

## Building the ISO

The GitHub Actions workflow builds a Kubuntu-based ISO on tag push or manual
workflow dispatch.

```bash
git tag v0.1.0
git push origin v0.1.0
```

Important packaging constraints:

- Chrome is **not bundled** in the ISO because Google Chrome is not redistributable
  inside OS images. Users run `setup-browser.sh` after first boot.
- Kubuntu 24.04 uses **KDE Plasma 5.27**, not Plasma 6.
- The ISO build must keep `filesystem.squashfs` below the xorriso 4 GiB limit.
- SSH host keys must be removed before packaging and regenerated on first boot.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for ISO build gotchas.

---

## MCP primitives planned for the substrate

The MCP layer gives the local agent a body. The target primitives are:

### Browser

- navigate to a URL,
- click/type/read DOM elements,
- capture tab screenshots,
- evaluate JavaScript,
- upload files,
- manage tabs.

### Input

- type text through clipboard paste,
- press keyboard shortcuts,
- click/move mouse,
- scroll,
- read/write clipboard.

### Screen

- full or regional screenshots,
- AT-SPI2 accessibility tree,
- active window metadata,
- find UI elements by accessible label.

### System

- read system status,
- list processes,
- read/write files,
- launch applications,
- run bounded shell commands.

### Audio

- play audio through a virtual speaker,
- record through a virtual microphone,
- provide a TTS hook.

Until these are fully implemented, do not market the MCP server as production-ready.

---

## Roadmap to the real Tin OS experience

### Phase 0 — truthful substrate

- Keep this repo honest about what is built vs planned.
- Build and test the Kubuntu bootstrap path.
- Implement enough MCP tools to inspect and control the local machine.

### Phase 1 — local Tin web door

- Install/run a local conversational UI on port `2024`.
- Show the owner the LAN URL and QR code on first boot.
- Make `http://tin.local` resolve on the LAN where possible.
- Add dashboard buttons for **Start OpenCode Web** and **Start Pi Web** so a new
  owner does not have to know terminal commands first.

### Phase 2 — first-boot owner setup

- Configure owner account.
- Configure internet and optional Tailscale.
- Configure model/API provider.
- Run a machine health check.

### Phase 3 — cockpit + durable work

- Show live agent cards and machine status.
- Keep work alive across browser disconnects.
- Add job/evidence tracking.

### Phase 4 — approval and safety

- Add a privileged broker for root/system actions.
- Require human approval for destructive, irreversible, or external-send actions.
- Add backup, restore, update, and factory reset.

### Phase 5 — Tin Box

- Ship Tin OS preinstalled on a mini PC or dedicated machine.
- User plugs it in, connects to the network, scans the QR code, and starts talking.

---

## Name

- Product name: **Tin OS**
- Repository/package name: `tinagent-os`
- Category language: **Human-AgentOS**

A good one-line description:

> Tin OS turns a connected machine into a conversational command center for human
> and AI work.

---

## License

MIT.
