# Tin OS product philosophy

Tin OS should describe and ship the real workflow, not an over-polished fantasy.

## Core idea

A Tin OS machine should be useful immediately after installation:

```text
Install Tin OS
  -> connect to the internet
  -> open http://tin.local or http://<LAN-IP>:2024
  -> talk to the machine
  -> launch a free default AI worker when needed
```

The first experience must not be “read docs, open a terminal, learn commands, log
into five services.”

## Dashboard first

The Tin dashboard is guaranteed to exist on a Tin OS install. It is the home
screen, not just a terminal list.

It should expose three layers:

1. **Talk to the OS** — the main chat/control surface.
2. **Launch AI workers** — one-click buttons for agent runtimes.
3. **Open raw terminals** — fallback / power-user access through tmux, WTerm,
   SSH, or Mosh.

The raw terminal remains important, but it should not be the first thing a new
owner has to understand.

## Free default path

Tin OS needs one AI path that works for a fresh user without paid keys or account
ceremony.

OpenCode Web is the best default candidate because it can now be used without an
account in the target flow. Therefore the dashboard should include a first-class:

```text
Start OpenCode Web
```

button.

The button should:

1. install or verify the OpenCode runtime,
2. start the local OpenCode Web service,
3. health-check the service,
4. open it in the browser,
5. show status on the dashboard.

This is the “try Tin OS now” lane.

## Power-user path

Pi Web should also be first-class, but it may require an already configured model,
API provider, or runtime. Therefore it should appear as:

```text
Start Pi Web
```

with honest setup states:

- ready,
- needs provider/API setup,
- missing runtime,
- service unhealthy.

Pi Web is the richer chat-to-agent lane; OpenCode Web is the no-friction default
lane.

## Truthful defaults

Tin OS should label every capability honestly:

- **Built-in now** — works immediately in this install.
- **Needs setup** — runtime exists but requires model/API/login/configuration.
- **Power user** — terminal or manual workflow.
- **Planned** — not installed yet.

Do not hide missing setup behind marketing language.

## Product principle

> If a fresh user cannot press a button and see something intelligent happen, the
> OS has not reached first-value yet.

OpenCode Web is the first-value button. Pi Web is the next-level conversation
button. Terminals are the escape hatch and power-user layer.
