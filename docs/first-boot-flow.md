# Tin OS first-boot flow

This document describes the product behavior Tin OS is being built toward.

## Goal

A non-technical owner should be able to install or receive a Tin OS machine, put it
on the network, open a browser, and talk to the OS.

```text
Power on
  -> connect to internet
  -> see local address / QR code
  -> open Tin in a browser
  -> chat with the OS
  -> let Tin inspect, execute, coordinate agents, and ask for approval
```

## Target user-visible flow

### 1. First boot

The machine boots into a locked-down but owner-accessible desktop/session.

A full-screen welcome page shows:

```text
Tin OS is ready.
Open this address on your phone or laptop:

http://tin.local

If that does not work:
http://192.168.x.x:2024

[QR code]
```

### 2. Owner setup

The browser UI asks for:

1. owner account / local password,
2. model or API provider configuration,
3. optional Tailscale/tailnet connection,
4. basic machine name,
5. consent for what Tin may control.

### 3. First conversation

The owner sees a chat UI:

```text
Owner: What can you do on this machine?
Tin: I can inspect system health, manage local files and services, open browser
     tasks, start agent sessions, and ask before privileged actions.
```

The dashboard should also show first-value buttons:

```text
[Start OpenCode Web]   free/default AI worker lane
[Start Pi Web]         richer chat-to-agent lane, may need provider setup
[Open Terminal]        raw tmux/WTerm/SSH/Mosh power path
[Health Check]         inspect readiness and missing setup
```

A good first automatic health report:

- hostname and LAN IP,
- internet connectivity,
- disk/RAM/CPU,
- services running,
- browser-control readiness,
- Tailscale status,
- pending setup items.

### 4. Approval model

Tin may do safe read-only work directly:

- check status,
- read non-secret system info,
- list local services,
- summarize logs.

Tin must ask for approval before:

- deleting files,
- installing packages,
- changing network/auth/security settings,
- sending data outside the machine,
- running privileged/root operations,
- starting paid/external API actions.

### 5. Cockpit

The chat UI should include a cockpit panel:

- live agent sessions,
- active jobs,
- blocked prompts,
- last evidence,
- machine health,
- approval queue.

## Current repo gap

The current repo does not yet implement this full flow. It provides the OS/MCP
substrate and installer work needed to get there.

Implementation still needed:

- web service on `:2024`,
- mDNS/Avahi name `tin.local`,
- QR display on first boot,
- owner setup wizard,
- local chat runtime,
- dashboard start/open buttons for OpenCode Web and Pi Web,
- cockpit panel,
- approval broker,
- durable job/evidence storage.

## Development milestone definition

Tin OS v0 becomes real when this command works on a clean Kubuntu machine:

```bash
sudo AGENT_USER=$USER bash install/bootstrap.sh
```

After reboot, the owner can open:

```text
http://<machine-ip>:2024
```

…and ask Tin:

```text
What is the status of this machine?
```

Tin must answer from live local state, not from a canned demo.
