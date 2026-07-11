# Inventory: public submission snapshot vs live Tin

This document prevents the public repository from claiming more than it ships.

## Packaged in this repository

| Capability | Public implementation |
| --- | --- |
| English-first Tin OS browser home | `tin_os/web/` |
| OpenCode Web detection/start | `/api/modules/opencode/start` |
| Pi Web detection/start | `/api/modules/pi/start` |
| tmux session inventory and recent output | `/api/sessions` |
| Bounded session create/list/stop | `tin_os/server.py` |
| Boot-persistent installation | `install/install-tin.sh` |
| OpenCode/Pi app installation | `install/install-ai-apps.sh` |
| Cold-start runtime smoke test | `scripts/smoke-test.sh` |
| Public-data privacy gate | `scripts/check-no-private-data.sh` |

## Proven in the live Tin prototype but not packaged here yet

| Live capability | Why it remains separate |
| --- | --- |
| Multi-machine federation | Needs generic node discovery and identity configuration |
| WTerm WebSocket PTY bridge | Needs packaging and authentication review |
| Termbridge/SSH/Mosh fallback doors | Power-user transport layer, not first-value path |
| Phone push when an agent waits | Requires owner notification configuration |
| Rich transcript mapping | Must be generalized beyond one agent's private file layout |
| Durable job/evidence/handoff ledger | Must remain independent of the private operating repository |
| Self-healing multi-node deploy ring | Needs product-safe update and rollback design |

## Experimental substrate

- Kubuntu ISO workflow.
- Chrome/CDP desktop automation bootstrap.
- AT-SPI2/ydotool/PipeWire environment configuration.

These are useful foundations but are not represented as release-ready product
features.

## Retired ideas not to reintroduce

- Watchtower predecessor.
- ttyd trial.
- Per-session head/headless systemd lifecycle.
- socat exposure.
- Termbridge as the primary onboarding interface.

## Next packaging milestone

The public snapshot becomes a Tin OS appliance when a clean machine can:

1. boot a released image,
2. show its LAN URL or QR code,
3. open the dashboard,
4. start OpenCode Web without account ceremony,
5. preserve a work session across browser disconnect,
6. request owner approval before privileged actions.
