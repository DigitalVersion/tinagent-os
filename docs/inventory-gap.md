# Inventory gap: live Tin prototype vs this repo

This document keeps the repository honest about what exists in the live Tin stack
and what is still missing from `tinagent-os`.

## Live prototype pieces not yet packaged here

| Live piece | Current live role | Status in this repo |
| --- | --- | --- |
| Tin dashboard / PWA | Fleet home screen, terminal cards, cockpit UI | Missing |
| Tin Flask API | Shell/session API, feed, vitals, transcripts, launch helpers | Missing |
| WTerm bridge | Default browser view into tmux sessions | Missing |
| tmux session model | Durable process/session substrate | Not installed/configured yet |
| Shell registry | Create/delete/revive shell rows and tmux sessions | Missing |
| Termbridge fallback | Mobile typing fallback when WTerm is not enough | Missing |
| SSH / Mosh attach doors | Native-client fallback into the same tmux session | Partially documented only |
| Pi Web on `:2024` | Chat with an AI agent through a web UI | Missing |
| OpenCode Web on `:2023` | Free/default AI worker web UI | Missing |
| Tin quest / session notes | Card title and current-step declaration | Missing |
| Worker orchestration | Start, rescue, signal done/escalate for AI workers | Missing |
| Job/evidence ledger | Durable proof that work finished | Missing |
| Tailscale serve + nginx | Tailnet-only stable web entry | Partially installed only |
| CDP pool | Multiple logged-in browser slots for web work | Not included |

## Repo pieces that are not yet live Tin product behavior

| Repo piece | Reality check |
| --- | --- |
| MCP server on `:8765` | A skeleton substrate, not the current user-facing Tin workflow |
| MCP tools/resources | Many functions are still `NotImplementedError` stubs |
| Wayland-first ydotool path | Useful substrate, but the live dashboard mostly uses tmux/terminal paths today |
| AT-SPI2 accessibility tree | Planned body/screen-reading layer, not the current Tin control path |
| PipeWire virtual audio | Installed substrate idea; not yet central to Tin dashboard/chat |
| Hardware watchdog | Needs real validation; do not market as reliable product behavior yet |
| ISO workflow | Build lane exists, but the full install-and-talk product is not complete yet |
| RustDesk | Useful rescue lane; optional, not core Tin OS |

## Retired ideas not to reintroduce as core

| Retired piece | Reason |
| --- | --- |
| Watchtower | Predecessor experiment, removed |
| ttyd | Trialed and reverted |
| Old head/headless shell model | Superseded by WTerm-only alive/dead session model |
| Per-shell systemd head units | Superseded; caused respawn/kill complexity |
| socat shell exposure | Superseded by safer tailnet/Tailscale serve patterns |
| Termbridge as primary terminal | Now fallback / mobile typing helper, not primary head |

## Product gap that matters most

The dashboard must grow from “terminal launchpad” into the Tin OS home screen.

Required first-class buttons:

1. **Start OpenCode Web** — free/no-account first-value path.
2. **Start Pi Web** — richer chat-to-agent path, with honest setup status.
3. **Open Terminal** — raw tmux/WTerm/SSH/Mosh power path.
4. **Health Check** — live machine readiness and missing setup.
5. **Setup Model / Provider** — only when a runtime needs it.

Until those exist, Tin OS should be described as the path toward the live prototype,
not a finished conversational OS image.
