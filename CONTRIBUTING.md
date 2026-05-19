# Contributing to TinAgentOS

Thanks for contributing! Each tool file is self-contained — pick one, implement the stubs, send a PR.

## How to pick up a stub

1. Find a function with `raise NotImplementedError`
2. Read the docstring — it tells you exactly what to use
3. Implement it
4. Test on a real Kubuntu machine (or the TinAgentOS ISO)
5. PR with: what you implemented + how you tested

## Setup for development

```bash
git clone https://github.com/DigitalVersion/tinagent-os
cd tinagent-os
uv run mcp_server.py
```

Requirements: Kubuntu 24.04, KDE Plasma Wayland, Chrome running on port 9222.

## Tool implementation notes

### browser.py
- CDP websocket endpoint: `ws://localhost:9222`
- Use `websockets` lib or `pychrome`
- Test: `curl http://localhost:9222/json/version`

### input.py
- `type_text`: always use `wl-copy '{text}' && ydotool key ctrl+v` — NOT `ydotool type`
- `key_press`: `ydotool key ctrl+c` etc.
- Socket: `YDOTOOL_SOCKET=/run/ydotoold.socket`

### screen.py
- Screenshot: `grim /tmp/screen.png` (Wayland) or `scrot` fallback
- Accessibility: `pydbus` → `org.a11y.Bus` → AT-SPI2

### system.py
- Keep it simple: `subprocess.run(cmd, shell=True, capture_output=True)`
- No sandboxing in v0.1 — add allowlist in v0.2

### audio.py
- Virtual sink name: `virtual-speaker`
- Play: `paplay --device=virtual-speaker file.wav`
- Record: `pw-record --target=virtual-mic output.wav`

## PR checklist

- [ ] Implements at least one stub fully
- [ ] Docstring unchanged (or improved)
- [ ] No new dependencies without updating `pyproject.toml`
- [ ] Tested on Kubuntu 24.04 Wayland

---

## Building the ISO

The GitHub Actions workflow (`build-iso.yml`) handles everything automatically on tag push.
This section is for people who want to build locally, or who need to debug a CI failure.

### Quick overview

```
Download Kubuntu ISO
  → mount + rsync all files except filesystem.squashfs
  → unsquashfs into squashfs-root/
  → chroot + bootstrap.sh (SKIP_BROWSER=1)
  → clean apt cache + remove SSH host keys
  → mksquashfs -comp zstd
  → xorriso → bootable ISO
```

### Gotcha 1 — mksquashfs hangs at 0% forever (proc/kcore)

**Symptom:** `mksquashfs` prints a few lines then stops. Output file grows to ~200 MB then
freezes. No progress. No error. You wait 20 minutes, still 0%.

**Cause:** `/proc`, `/sys`, `/dev`, `/dev/pts` are still bind-mounted from the chroot step.
`mksquashfs` enters `/proc` and starts reading `/proc/kcore` — a virtual file that maps
kernel memory and appears infinite. It will never finish.

**Fix:** Unmount **all** virtual filesystems before `mksquashfs`. Order matters — pts before dev:

```bash
sudo umount -lf "$ROOT/dev/pts"
sudo umount -lf "$ROOT/dev"
sudo umount -lf "$ROOT/sys"
sudo umount -lf "$ROOT/proc"

# Verify nothing is left
sudo mount | grep squashfs-root  # must print nothing
```

Also always pass `-e boot proc sys dev run tmp` to `mksquashfs` as a safety net.

### Gotcha 2 — xorriso: squashfs must be < 4 GiB

**Symptom:** `xorriso` exits with `File is too large` or silently produces a broken ISO.

**Cause:** xorriso 1.5.6 hard-limits squashfs to 4,294,967,295 bytes. The flag
`--allow-limited-size` is **not supported** in `-as mkisofs` mode despite appearing in docs.

**How to debug:**
```bash
SIZE=$(stat -c "%s" filesystem.squashfs)
echo "$SIZE bytes = $(echo "scale=2; $SIZE/1073741824" | bc) GiB"
# Must be < 4294967296
```

**How to shrink:**
```bash
# In chroot BEFORE mksquashfs — saves ~150 MB compressed:
rm -rf "$ROOT/var/cache/apt/archives"/*.deb
rm -rf "$ROOT/var/lib/apt/lists"/*
mkdir -p "$ROOT/var/lib/apt/lists/partial"
```

Removing apt cache + lists alone cut the squashfs from 4.5 GiB to 3.8 GiB in our build.
If still over, also remove `/usr/share/doc` (~100 MB) and locale data you don't need.

### Gotcha 3 — compression: use zstd, not xz or gzip

| Codec | Compress time | Decompress | Squashfs size |
|-------|--------------|-----------|---------------|
| xz    | 8–12 hours   | slow      | smallest      |
| gzip  | ~15 min      | fast      | **4.5 GiB** (over limit) |
| zstd  | ~10 min      | fast      | ~3.8 GiB ✅  |

xz will seem to work but finishes in ~10 hours on typical hardware — far too slow for CI.
gzip is fast but produces a larger squashfs that exceeds the 4 GiB limit on a full Kubuntu base.
**Use zstd.**

```bash
sudo mksquashfs "$ROOT" filesystem.squashfs \
  -comp zstd \
  -e boot proc sys dev run tmp \
  -noappend
```

### Gotcha 4 — EFI boot params must come from the original ISO

**Symptom:** ISO boots on BIOS/legacy but not UEFI. Or xorriso errors about missing EFI image.

**Cause:** EFI boot parameters (sector offsets, partition type GUIDs) are specific to each
Kubuntu release. You cannot guess them — they change between point releases.

**How to extract them:**
```bash
xorriso -indev kubuntu.iso -report_el_torito as_mkisofs
```

For **Kubuntu 24.04.4** the EFI partition is at sectors 9357424–9367583:
```bash
sudo dd if=kubuntu.iso bs=512 skip=9357424 count=10160 of=efi.img
```

Then pass `efi.img` to xorriso via `-append_partition 2 ... efi.img`. If you switch to a
different Kubuntu version, re-run `report_el_torito` and update the offsets.

### Gotcha 5 — Chrome cannot be in the ISO

Google Chrome's Terms of Service prohibit including it in redistributable OS images.

**Solution used here:** `SKIP_BROWSER=1` in the chroot step. The ISO ships without Chrome.
After first boot, users run:
```bash
sudo bash ~/setup-browser.sh
```
This downloads Chrome directly from Google (user consent = permitted), installs it, and
wires the CDP wrapper + KDE autostart entry.

`bootstrap.sh` respects `SKIP_BROWSER=1` — it skips the Chrome block entirely.

### Gotcha 6 — Snap Chromium breaks AT-SPI2

AT-SPI2 (accessibility tree) is TinAgentOS's core feature for `screen_get_accessibility_tree()`.
It works by connecting to the `org.a11y.Bus` dbus interface.

Snap confinement blocks dbus interface calls outside the snap sandbox. Snapped Chromium
therefore cannot be read via AT-SPI2. Every `screen_get_accessibility_tree()` call on a
snap Chromium window returns empty or errors.

**Chrome deb** has no such restriction — dbus access works normally.

If you need a fully open-source browser, Chromium **built from source** (not snap) also works.
The snap is the problem, not Chromium itself.

### Gotcha 7 — Kubuntu 24.04 is Plasma 5, not Plasma 6

Plasma 6 shipped with **Kubuntu 24.10** (October 2024).
Kubuntu 24.04 LTS = **KDE Plasma 5.27 LTS**.

This matters for:
- `kwriteconfig5` (not `kwriteconfig6`) in firstrun.sh
- Some KDE config file paths differ between 5 and 6
- QML API differences if you're writing KDE extensions

### Gotcha 8 — SSH host keys must be removed before packaging

If you don't remove SSH host keys from the squashfs, every machine that boots from your
ISO will have the **same SSH host key** — a serious security problem.

```bash
# In the "clean chroot" step, before mksquashfs:
sudo rm -f "$ROOT/etc/ssh/ssh_host_"*
```

`tinagent-sshkeys.service` (installed by bootstrap.sh) regenerates them on first boot via
`ssh-keygen -A`, gated by `ConditionPathExists=!/etc/ssh/ssh_host_rsa_key`.

### Gotcha 9 — GitHub Actions: free disk space first

ubuntu-latest runners have ~14 GB free. The build needs ~20 GB. Without cleanup, the
mksquashfs step fails with "No space left on device" mid-pack (worst possible moment).

Pre-installed toolchains to remove (~10 GB total):
```bash
sudo rm -rf \
  /usr/share/dotnet /usr/local/lib/android /opt/ghc \
  /opt/hostedtoolcache/CodeQL /usr/local/share/boost \
  /usr/lib/jvm /usr/lib/mono /usr/share/swift \
  /usr/local/.ghcup /usr/share/haskell
sudo apt-get clean
docker image prune -af 2>/dev/null || true
```

Do this **before** downloading the Kubuntu ISO.

### Local build checklist

```bash
# 1. Free space (if on CI)
# 2. Download + cache Kubuntu ISO
# 3. Mount ISO, rsync everything except filesystem.squashfs, unmount
# 4. unsquashfs → squashfs-root/
# 5. Extract EFI img via dd (before deleting ISO)
# 6. Delete ISO to free space
# 7. Mount bind: proc sys dev dev/pts into squashfs-root
# 8. chroot + bootstrap.sh (SKIP_BROWSER=1, DEBIAN_FRONTEND=noninteractive)
# 9. UNMOUNT ALL: dev/pts → dev → sys → proc (in that order)
# 10. Verify: `mount | grep squashfs-root` prints nothing
# 11. Clean: rm apt archives, apt lists, ssh host keys
# 12. mksquashfs -comp zstd -e boot proc sys dev run tmp
# 13. Check size < 4 GiB
# 14. xorriso (MBR from grub-pc-bin + EFI from extracted img)
```
