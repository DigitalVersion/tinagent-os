# Contributing to Tin OS (`tinagent-os`)

Thanks for contributing. The current goal of this repo is to turn the live Tin
prototype into an installable, truthful operating environment.

## Current priority

Do **not** assume the repo is already the full product. Today it is mostly the OS
substrate: Kubuntu bootstrap, ISO workflow, Chrome/CDP setup, and an MCP server
skeleton.

Highest-value contributions:

1. Implement the MCP tools/resources that are still stubs.
2. Add a local Tin web door on `:2024` so the owner can open a browser and chat
   with the machine.
3. Add first-boot owner setup: network, model/API provider, tailnet, health check.
4. Add safe privileged-action approval instead of blind root execution.
5. Keep docs accurate about what is built vs planned.

## Development setup

```bash
git clone https://github.com/DigitalVersion/tinagent-os
cd tinagent-os
uv run mcp_server.py
```

Recommended test machine: Kubuntu 24.04, KDE Plasma Wayland, Chrome running on
port `9222` through `install/setup-browser.sh`.

## Implementing a stub

1. Find a function with `raise NotImplementedError`.
2. Read the docstring and this file's notes.
3. Implement the smallest working version.
4. Test on a real Wayland session where possible.
5. Update docs if the user-visible behavior changes.

## Tool implementation notes

### `tools/browser.py`

- CDP endpoint: `http://localhost:9222/json/version` and websocket targets under
  `http://localhost:9222/json`.
- Use `websockets`, raw CDP, or a small CDP helper. Avoid heavyweight browser
  frameworks unless needed.
- Test: `curl http://localhost:9222/json/version`.

### `tools/input.py`

- `type_text`: prefer `wl-copy` followed by paste shortcut. Do **not** type long
  Unicode text key-by-key through `ydotool`.
- `key_press`: use `ydotool key ...`.
- Socket: `YDOTOOL_SOCKET=/run/ydotoold.socket`.

### `tools/screen.py`

- Screenshot: `grim` on Wayland.
- Accessibility: AT-SPI2 through dbus (`org.a11y.Bus`).
- Prefer structured accessibility data before screenshots.

### `tools/system.py`

- Keep v0 simple but not reckless.
- If adding `system_run`, include timeout, captured output, and clear errors.
- Do not silently run destructive commands. This repo needs an approval broker
  before it becomes a real OS product.

### `tools/audio.py`

- Virtual sink/source names from bootstrap:
  - `virtual-speaker`
  - `virtual-mic`
- Play: `paplay` or `pw-play`.
- Record: `pw-record`.
- TTS engine is not decided yet; keep it pluggable.

## Documentation rule

Every public claim must be one of:

- **Built:** code exists in this repo and was tested.
- **Prototype:** exists in the external/live Tin stack but is not packaged here yet.
- **Planned:** product direction only.

Do not market planned features as built.

---

## Building the ISO

The GitHub Actions workflow (`build-iso.yml`) handles the ISO build on tag push or
manual workflow dispatch. This section is for local debugging.

### Quick overview

```text
Download Kubuntu ISO
  -> mount + rsync all files except filesystem.squashfs
  -> unsquashfs into squashfs-root/
  -> chroot + bootstrap.sh (SKIP_BROWSER=1)
  -> clean apt cache + remove SSH host keys
  -> mksquashfs -comp zstd
  -> xorriso -> bootable ISO
```

### Gotcha 1 — `mksquashfs` hangs at 0% forever (`/proc/kcore`)

Unmount **all** virtual filesystems before `mksquashfs`. Order matters:

```bash
sudo umount -lf "$ROOT/dev/pts"
sudo umount -lf "$ROOT/dev"
sudo umount -lf "$ROOT/sys"
sudo umount -lf "$ROOT/proc"
sudo mount | grep squashfs-root  # must print nothing
```

Also pass `-e boot proc sys dev run tmp` to `mksquashfs`.

### Gotcha 2 — squashfs must be < 4 GiB

`xorriso` rejects large squashfs files. Check before building the final ISO:

```bash
SIZE=$(stat -c "%s" filesystem.squashfs)
echo "$SIZE bytes"
```

Shrink by removing apt caches/lists and unused docs/locales.

### Gotcha 3 — use zstd compression

`xz` is too slow for CI. `gzip` can exceed the 4 GiB limit. Use:

```bash
sudo mksquashfs "$ROOT" filesystem.squashfs \
  -comp zstd \
  -e boot proc sys dev run tmp \
  -noappend
```

### Gotcha 4 — EFI boot params come from the original ISO

Do not guess EFI offsets. Extract them with:

```bash
xorriso -indev kubuntu.iso -report_el_torito as_mkisofs
```

For Kubuntu 24.04.4 the existing workflow uses:

```bash
sudo dd if=kubuntu.iso bs=512 skip=9357424 count=10160 of=efi.img
```

Re-check if the Kubuntu ISO version changes.

### Gotcha 5 — Chrome cannot be bundled

Google Chrome is not redistributable inside OS images. The ISO should ship
without Chrome. Users run:

```bash
sudo bash ~/setup-browser.sh
```

This downloads Chrome directly from Google after first boot.

### Gotcha 6 — Snap Chromium breaks AT-SPI2

Snap confinement blocks the dbus accessibility interfaces Tin relies on. Use the
Chrome `.deb` installer or a non-snap Chromium build.

### Gotcha 7 — Kubuntu 24.04 is Plasma 5

Kubuntu 24.04 LTS ships KDE Plasma 5.27, not Plasma 6. Use `kwriteconfig5` and
Plasma 5-compatible paths.

### Gotcha 8 — remove SSH host keys before packaging

Do not bake shared SSH host keys into the ISO:

```bash
sudo rm -f "$ROOT/etc/ssh/ssh_host_"*
```

Regenerate on first boot.

### Gotcha 9 — GitHub Actions disk space

`ubuntu-latest` runners need cleanup before the ISO build. The workflow removes
large preinstalled toolchains before download/extraction.

## PR checklist

- [ ] Does not claim planned features as built.
- [ ] Implements or documents one concrete behavior.
- [ ] Updates README/docs when user-visible behavior changes.
- [ ] Tested on Kubuntu 24.04 Wayland, or clearly states why not.
- [ ] No secrets, API keys, private hostnames, or tailnet-only URLs committed.
