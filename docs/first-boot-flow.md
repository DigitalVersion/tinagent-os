# Tin OS first-boot flow

## Product promise

A new owner should be able to put a Tin OS machine on a trusted network, open a
browser, and reach useful AI without learning terminal commands first.

```text
Power on
  -> connect Ethernet or Wi-Fi
  -> open the displayed LAN address
  -> press Start OpenCode Web
  -> begin working
```

## What the repository implements now

On an existing Debian/Ubuntu/Kubuntu machine:

```bash
sudo AGENT_USER="$USER" bash install/install-tin.sh
bash install/install-ai-apps.sh
```

The first command installs a boot-persistent Tin service and prints:

```text
LAN:      http://192.168.x.x:8080
Tailnet:  http://100.x.x.x:8080   # when Tailscale is present
Local:    http://127.0.0.1:8080
```

The second command installs OpenCode and optionally Pi Web. The dashboard then
provides first-class start buttons for both applications.

## First conversation/work session

The owner can choose:

- **Start OpenCode Web** — free/default first-value AI lane.
- **Start Pi Web** — configured-provider project/workspace lane.
- **Create tmux session** — persistent power-user process lane.

Tin shows live running/idle state and recent tmux output in the browser.

## Safety boundary

The submission runtime should be used only on a trusted LAN or private tailnet.
It intentionally does not expose arbitrary shell commands through HTTP. Session
startup is restricted to an explicit allowlist.

## Still required for the appliance/ISO experience

- A released ISO that has booted and passed the complete field gate.
- QR code and address rendered on the physical first-boot screen.
- `tin.local` discovery without manually reading an IP address.
- Owner account/authentication and privileged-action approval.
- Bundled WTerm browser terminal.
- Update, backup, restore, and factory reset.

The ISO workflow remains **experimental** until those claims are verified on a
clean machine.
