# Contributing to Tin OS

Tin OS is being extracted from a live private fleet into a safe, installable public
product. Contributions must preserve two rules:

1. **Reality first:** do not claim planned behavior as built.
2. **Private stays private:** never commit fleet domains, node IPs, credentials,
   customer names, transcripts, or private workspace paths.

## Development setup

```bash
git clone https://github.com/DigitalVersion/tinagent-os.git
cd tinagent-os
python3 -m tin_os.server --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080`.

Requirements: Linux, Python 3.11+, tmux. The runtime has no third-party Python
dependencies.

## Required checks

```bash
bash scripts/check-no-private-data.sh
bash scripts/smoke-test.sh
```

Also inspect the UI at desktop and phone widths. A passing syntax check does not
catch overflow, inaccessible controls, or unreadable cards.

## Public claim labels

Use these labels consistently:

- **Built:** code exists in this repository and passed its documented test.
- **Live prototype:** behavior exists in the private/live Tin system but is not
  packaged here yet.
- **Experimental:** build lane exists but has not passed a release gate.
- **Roadmap:** product direction only.

## Code boundaries

- `tin_os/server.py`: standard-library HTTP/API runtime and bounded tmux/module commands.
- `tin_os/web/`: English-first product UI.
- `install/`: machine installation and optional AI app setup.
- `scripts/`: test and privacy gates.
- `docs/`: product rationale and evidence safe for public release.

Do not add a general arbitrary-command HTTP endpoint. Tin currently has no public
internet authentication layer; fixed command surfaces are an intentional safety
boundary.

## Pull request checklist

- [ ] Behavior is categorized as Built, Live prototype, Experimental, or Roadmap.
- [ ] `scripts/check-no-private-data.sh` passes.
- [ ] `scripts/smoke-test.sh` passes.
- [ ] UI was rendered at desktop and phone widths.
- [ ] No secrets, private topology, customer content, or terminal transcripts.
- [ ] README and evidence are updated if user-visible behavior changed.

## ISO lane

`.github/workflows/build-iso.yml` and `install/bootstrap.sh` are experimental
Kubuntu substrate work. Do not call an ISO release-ready until a built artifact has
booted on a clean machine and passed the install/open/start-AI flow.
