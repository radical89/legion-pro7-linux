# Lenovo Legion Pro 7 Gen 10 (16IAX10H) — Linux Compatibility Tracker

> **AI Authorship Notice:** This document was researched and written entirely by [Claude](https://claude.ai) (Anthropic), an AI assistant, on 2026-05-04. All hardware was scanned live from the machine using shell commands (`inxi`, `lspci`, `dmesg`, `journalctl`, `nvidia-smi`, `bluetoothctl`, etc.). Compatibility findings were researched via web search against upstream kernel mailing lists, GitHub issues, CachyOS forums, and Arch Linux resources. The human owner reviewed and approved the content but did not write it. Please verify any fix instructions independently before applying them — AI can make mistakes.

---

## Machine Specifications

| Field | Value |
|---|---|
| **Model** | Lenovo Legion Pro 7 Gen 10 16IAX10H |
| **Product code** | 83F5 |
| **Board** | LNVNB161216 |
| **BIOS** | Q7CN77WW (2026-02-11) |
| **CPU** | Intel Core Ultra 9 275HX (Arrow Lake-HX, 24c/24t, no HT, 5.4 GHz boost) |
| **dGPU** | NVIDIA GeForce RTX 5080 Max-Q / Mobile (Blackwell GB203M, 16 GB GDDR7) |
| **iGPU** | Intel Arc Xe2-LPG (Arrow Lake-S integrated) |
| **NPU** | Intel Arrow Lake NPU |
| **RAM** | 32 GB DDR5 |
| **Storage** | 2× Samsung PM9C1a 1 TB NVMe (DRAM-less) |
| **Display (internal)** | 2560×1600 @ 240 Hz |
| **Display (external)** | LG ULTRAWIDE 3440×1440 @ 60 Hz |
| **WiFi** | Intel BE200 (Wi-Fi 7, 802.11be, 320 MHz) |
| **Ethernet** | Intel I226-V (2.5 GbE) |
| **Bluetooth** | Intel BE200 (BT 5.4, USB) |
| **Audio codec** | Realtek ALC287 |
| **Speaker amps** | 2× Awinic AW88399 (I2C 0x34, 0x35) |
| **Touchpad** | ELAN06FA:00 (I2C HID) |
| **Webcam (internal)** | Bison Integrated Camera (USB) |
| **Battery** | SMP L24M4PC1, 99.9 Wh design |

**OS tested:** CachyOS (Arch-based, rolling), kernel 7.0.3-1-cachyos (x86_64_v3, PREEMPT, clang 22.1.3), KDE Plasma 6.6.4, Wayland.

---

## Issue Status at a Glance

| # | Component | Severity | Status |
|---|---|---|---|
| 1 | [Internal speakers (AW88399 amps)](#1-internal-speakers--aw88399-amplifier-firmware-missing) | High | **Broken — community fix available** |
| 2 | [Keyboard RGB backlight](#2-keyboard-rgb-backlight--not-controllable-via-kernel) | Medium | **Broken — third-party fix available** |
| 3 | [Fan control / DYTC power profiles](#3-fan-control--dytc-power-profiles-unavailable) | Medium | **Unavailable — no upstream fix** |
| 4 | [NVIDIA RTX 5080 driver stability](#4-nvidia-rtx-5080-mobile--driver-595x-instability) | Medium | **Working but unstable — monitor** |
| 5 | [Wi-Fi 7 suspend/resume](#5-wi-fi-7-be200--suspendresume-connection-drop) | Low | **Known risk — workaround exists** |
| 6 | [Intel Arc iGPU driver (xe vs i915)](#6-intel-arc-xe2-igpu--i915-vs-xe-driver) | Low | **Working suboptimally — upgrade available** |
| 7 | [BIOS updates on Linux](#7-bios-updates-on-linux) | Low | **Possible — tooling available** |

---

## Issues with Available Fixes

### 1. Internal Speakers — AW88399 Amplifier Firmware Missing

**Status:** Broken. Community fix exists. Not yet upstream.

**Symptoms from `dmesg`/`journalctl`:**
```
aw88399-hda i2c-AWDZ8399:00-aw88399-hda.0: Direct firmware load for aw88399_acf.bin failed with error -2
aw88399-hda i2c-AWDZ8399:00-aw88399-hda.0: request [aw88399_acf.bin] failed!
aw88399-hda i2c-AWDZ8399:00-aw88399-hda.0: Chip initialization failed: -2
aw88399-hda i2c-AWDZ8399:00-aw88399-hda.0: probe with driver aw88399-hda failed with error -2
```
(Repeated twice — once per amplifier chip at I2C 0x34 and 0x35.)

Also present:
```
snd_hda_codec_alc269 hdaudioC1D0: ALC287: SKU not ready 0x411111f0
```

**What's broken:** The laptop uses two Awinic AW88399 smart amplifier chips as woofer drivers. The kernel driver (`aw88399-hda`) loads but cannot find `aw88399_acf.bin`, which is the amplifier's acoustic calibration/configuration firmware. Without it, both chips fail to probe and the woofers produce no output. Only the tweeters (driven directly by the ALC287 codec) are active, resulting in thin, tinny audio at low volume. The ALC287 SKU error is a separate issue where the codec's pin configuration isn't read correctly from the hardware straps; it doesn't block headphone or HDMI audio.

**What works:** Headphone jack, HDMI/DisplayPort audio, NVIDIA HDMI audio, microphone.

**Affected models (confirmed):**
- Legion Pro 7i Gen 10 (16IAX10H) — Intel variant (this machine)
- Legion Pro 7 Gen 10 (16AFR10H) — AMD variant
- Legion 5i Gen 9 (16IRX9)
- Legion Y9000P (IAX10H)

**Why it isn't fixed upstream:** `aw88399_acf.bin` is proprietary Awinic firmware. It must be extracted from the Windows driver package. Additionally, a kernel patch to `patch_realtek.c` is required to wire the ALC287 codec to the AW88399 amplifiers for the SSID `17aa:3906`. Neither the firmware nor the patch has been accepted into linux-firmware or the mainline kernel as of 2026-05-04.

**Community fix:**
> **[nadimkobeissi/16iax10h-linux-sound-saga](https://github.com/nadimkobeissi/16iax10h-linux-sound-saga)**
>
> This is the primary community fix repository. It was funded by a $2,000 USD community bounty (organised by Nadim Kobeissi, with Alderon Games contributing $1,000). The engineering was done by Lyapsus/Yakov Till (~95% of the work).
>
> The fix involves:
> 1. Installing the extracted `aw88399_acf.bin` firmware to `/lib/firmware/`
> 2. Applying a kernel patch to the audio subsystem (targets Linux 7.0 and 6.19.11)
> 3. Enabling `CONFIG_SND_HDA_SCODEC_AW88399=m` and `CONFIG_SND_SOC_AW88399=m`
> 4. Rebuilding the kernel and initramfs
> 5. Rebuilding NVIDIA DKMS modules against the new kernel
>
> Full instructions are in that repo's README.

**Tracking:**
- [CachyOS issue #687](https://github.com/CachyOS/linux-cachyos/issues/687) — "Internal speakers tinny sound (aw88399 quirk needed)"
- [CachyOS issue #707](https://github.com/CachyOS/linux-cachyos/issues/707) — "Add audio support (AW88399) for Legion Pro 7i Gen 10" (closed as duplicate of #618)
- [CachyOS issue #618](https://github.com/CachyOS/linux-cachyos/issues/618) — Central tracking issue for upstream integration
- [CachyOS forum thread](https://discuss.cachyos.org/t/new-fix-for-lenovo-legion-pro-7i-16iax10h-with-alc3306-codec/18889)

---

### 2. Keyboard RGB Backlight — Not Controllable via Kernel

**Status:** Broken via standard kernel interface. Third-party fixes available.

**Symptoms:**
```
ideapad_acpi VPC2004:00: Unknown keyboard type: 1
ideapad_acpi VPC2004:00: Keyboard backlight control not available
```

No `/sys/class/leds/kbd_backlight` entry is created. The Legion Gen 10 uses an ITE 8258 Spectrum keyboard controller (USB ID `048d:c197`) for per-key RGB. This is not supported by `ideapad_acpi` and requires a dedicated driver.

**What works:** Fn lock (`platform::fnlock` LED present). Standard keyboard input fully functional.

**Fix option 1 — LenovoLegionLinux (recommended):**
> **[johnfanv2/LenovoLegionLinux](https://github.com/johnfanv2/LenovoLegionLinux)**
>
> A kernel DKMS module that provides fan control, battery conservation, keyboard backlight, and power mode switching for Lenovo Legion laptops. Confirmed working on the 16IAX10H with `force=1` (see [issue #385](https://github.com/johnfanv2/LenovoLegionLinux/issues/385)). A non-critical IO-Port LED initialisation error is present but doesn't affect functionality. Available on the AUR as `lenovolegiontoolkit` or via the project's install script.

**Fix option 2 — legion-spectrum-control:**
> **[alstergee/legion-spectrum-control](https://github.com/alstergee/legion-spectrum-control)**
>
> A CLI + web UI tool (served at `localhost:5555`) for per-key RGB customisation on Legion Gen 10. Supports rainbow wave, colour pulse, static zones, and hardware monitoring integration. Targets the ITE 8258 controller directly.

---

## Issues to Monitor (No Upstream Fix Yet)

### 3. Fan Control / DYTC Power Profiles Unavailable

**Status:** Unavailable. No upstream fix as of 2026-05-04.

**Symptom:**
```
ideapad_acpi VPC2004:00: DYTC interface is not available
```

Lenovo's Dynamic Thermal Control (DYTC) interface — which backs the Performance / Balanced / Quiet mode switching in Lenovo Vantage on Windows — is not accessible to Linux. This means TDP limits and fan curves cannot be adjusted via the standard ACPI interface. The system operates in a fixed mode (likely Balanced) with no way to switch to Performance or Quiet profiles from the OS.

**Partial workarounds:**
- `power-profiles-daemon` (installed by default in most distros) offers `performance`, `balanced`, and `power-saver` profiles via the CPU scaling governor and EPP hints, but does not touch TDP or fan curves.
- `LenovoLegionLinux` (see above) exposes fan control and may partially restore power profile switching even without DYTC.
- `throttled` / `thinkfan` are not applicable to this platform.

**Watch:** upstream `ideapad_acpi` development and any Lenovo firmware updates that may expose the DYTC interface correctly.

---

### 4. NVIDIA RTX 5080 Mobile — Driver 595.x Instability

**Status:** GPU is functional (nvidia-smi, CUDA 13.2 confirmed). Driver has reported instability.

**Current driver:** `595.71.05` (open kernel module, `linux-cachyos-nvidia-open 7.0.3-1`)

**What works:** GPU detection, CUDA, PRIME render offload (`prime-run`), HDMI audio, basic 3D.

**Known issues:**
- [CachyOS issue #771](https://github.com/CachyOS/linux-cachyos/issues/771): games like Elden Ring freeze on loading or revert to the loading screen in a loop. Workaround reported: downgrade NVIDIA packages to archived versions.
- Sporadic illegal memory accesses (XID 13) reported in tensor operations using `cuTensorMapEncodeTiled()` on Blackwell hardware in the 595.x series.
- NVIDIA open driver 595.x is still relatively new for RTX 50 series (Blackwell). The 570.x series was the first consumer Blackwell driver; 595.x is the next generation.

**Note on Nouveau:** Nouveau has no support for Blackwell (RTX 50 series) as of this writing. The NVIDIA open kernel module is the only viable driver.

**Watch:** CachyOS issue #771, CachyOS forum, and NVIDIA driver release notes for the 600.x series.

---

### 5. Wi-Fi 7 (BE200) — Suspend/Resume Connection Drop

**Status:** Wi-Fi loads and operates correctly during normal use. Suspend/resume is a known risk.

**Current state:** `iwlwifi` loaded firmware `gl-c0-fm-c0-c101.ucode` successfully at boot. 6 GHz band enabled (region AU). Interface `wlan0` is UP. Not yet tested across a suspend/resume cycle on this machine.

**Known Linux-wide issue:** Across Ubuntu, Mint, Arch, and other distributions, the Intel BE200 is widely reported to lose its connection after the system resumes from suspend. The card is detected but does not reassociate. Workaround when it occurs:

```bash
# Add to /etc/systemd/system/wifi-resume.service
[Unit]
Description=Restart NetworkManager after resume
After=suspend.target hibernate.target hybrid-sleep.target

[Service]
Type=oneshot
ExecStart=/bin/systemctl restart NetworkManager

[Install]
WantedBy=suspend.target hibernate.target hybrid-sleep.target
```

**Additional note:** 320 MHz channel width has caused random system freezes on some kernels (reported on 6.15.x Arch). Not confirmed on kernel 7.0.3.

**Watch:** `iwlwifi` firmware updates via `linux-firmware` package, and the 320 MHz freeze reports if connecting to a Wi-Fi 7 access point with 320 MHz channels.

---

### 6. Intel Arc Xe2 iGPU — i915 vs xe Driver

**Status:** Working. Suboptimal driver in use.

**Current state:** The iGPU (Intel Arc Xe2-LPG) is driven by the `i915` driver. It is loading Meteor Lake firmware (`mtl_dmc.bin`, `mtl_guc_70.bin`, etc.) — this is intentional because Arrow Lake shares the same display/media IP blocks as Meteor Lake. Both displays are functional.

**The case for switching to `xe`:**
The `xe` kernel driver is Intel's modern replacement for `i915`, designed from the ground up for Xe-architecture GPUs. Benchmarks on Meteor Lake (the same IP as Arrow Lake's iGPU) show 20–50% compute uplift and double-digit gains in general graphics tasks versus `i915`. It enables GuC and HuC by default, improving hardware-accelerated video decode/encode (VA-API). `xe` is the driver that will receive future development; `i915` is in maintenance mode for new hardware.

**How to switch (test carefully):**
```bash
# Add to kernel parameters (e.g. in /etc/kernel/cmdline or GRUB):
i915.force_probe=!0x7d55 xe.force_probe=0x7d55
```
Replace `0x7d55` with the actual PCI device ID from `lspci -nn | grep VGA | grep Intel`.

**Known risk:** A small number of legacy OpenGL applications perform marginally worse on `xe` due to `i915`'s optimised paths for older code. Display tearing has been reported by some users. If issues arise, add `xe.enable_psr=0` to kernel parameters.

**Watch:** `xe` driver stability reports for Arrow Lake in CachyOS and Arch forums.

---

### 7. BIOS Updates on Linux

**Status:** Possible via community tooling.

Lenovo distributes BIOS updates as Windows `.exe` files. On Linux, `fwupd` covers many Lenovo models via the LVFS (Linux Vendor Firmware Service), but coverage for the 16IAX10H Gen 10 has been incomplete.

A Notebookcheck article from April 2025 noted that a BIOS update for the Legion Pro 7i Gen 10 addressed an important NVIDIA feature — users without Windows access may have missed this.

**Tooling:**
> **[nadimkobeissi/lenovo-bios-fwupd](https://github.com/nadimkobeissi/lenovo-bios-fwupd)** — Extracts firmware from Lenovo BIOS `.exe` files and packages it for `fwupdmgr` installation without requiring Windows. From the same author as the audio fix.

**Action:** Check `fwupdmgr get-updates` periodically. If the current BIOS (Q7CN77WW) is not the latest, use the above tool or a Windows VM/WinPE USB to apply it.

---

## What Works Correctly

The following was confirmed working on this machine via live hardware scan and boot log review:

| Component | Driver / Notes |
|---|---|
| CPU (Core Ultra 9 275HX) | Hybrid core scheduling mature in kernel 7.x. S0ix suspend fixed in 6.15+. NPU via `intel_vpu`. |
| NVIDIA RTX 5080 Mobile | `nvidia` open module 595.71.05. CUDA 13.2. `prime-run` for PRIME offload. |
| Intel Arc iGPU | `i915`, OpenGL 4.6 (Mesa 26.0.6), Vulkan 1.4.341. Both displays output. |
| Intel Arrow Lake NPU | `intel_vpu`, exposed as `/dev/accel/accel0`. OpenVINO 2026.x compatible. |
| RAM (32 GB DDR5) | Healthy, DIMM temps 39–41 °C at idle. 30 GB ZRAM swap. |
| NVMe storage (×2 PM9C1a) | `nvme` driver. DRAM-less design means lower random-write burst, no Linux bugs. |
| Ethernet (Intel I226-V) | `igc` driver. Works when cable connected. |
| Bluetooth (BE200) | `btusb`, firmware `ibt-0291-0291.sfi`, hci0 powered on, no errors. |
| Touchpad (ELAN06FA:00) | I2C HID multitouch. |
| Webcam — internal (Bison) | `uvcvideo`. |
| Webcam — external (Logitech C922) | `uvcvideo` + `snd-usb-audio`. |
| Headphone jack | ALC287 Analog, PipeWire 1.6.4. |
| HDMI audio | Both NVIDIA HDMI and Intel PCH HDMI. LG ULTRAWIDE detected by name. |
| Thunderbolt 4 | `thunderbolt` driver, no errors. |
| Display backlight | `intel_backlight` present and writable. |
| Suspend (S3/deep) | Default sleep state is `deep` (S3). NVMe simple-suspend quirk applied. |
| Fn lock key | `platform::fnlock` LED. |
| Battery | 98.2% capacity health. upower reporting correctly. |

---

## Related Projects & Resources

### Audio Fix
- **[nadimkobeissi/16iax10h-linux-sound-saga](https://github.com/nadimkobeissi/16iax10h-linux-sound-saga)** — The primary community audio fix. Contains firmware, kernel patches, and full install instructions.

### Hardware Control (fans, LEDs, power modes)
- **[johnfanv2/LenovoLegionLinux](https://github.com/johnfanv2/LenovoLegionLinux)** — DKMS kernel module for fan control, keyboard backlight, battery conservation, and power mode switching. Works on 16IAX10H with `force=1` ([issue #385](https://github.com/johnfanv2/LenovoLegionLinux/issues/385)).
- **[alstergee/legion-spectrum-control](https://github.com/alstergee/legion-spectrum-control)** — Per-key RGB control for Gen 10 ITE 8258 keyboard controller.

### BIOS Updates
- **[nadimkobeissi/lenovo-bios-fwupd](https://github.com/nadimkobeissi/lenovo-bios-fwupd)** — Apply Lenovo BIOS updates from Linux without Windows.

### General Legion Linux Notes
- **[cszach/linux-on-lenovo-legion](https://github.com/cszach/linux-on-lenovo-legion)** — General Linux setup notes for Lenovo Legion laptops.

### Issue Trackers
- [CachyOS linux-cachyos issues](https://github.com/CachyOS/linux-cachyos/issues) — Search `legion`, `aw88399`, `nvidia 595`
- [ArchWiki — Lenovo Legion 7i](https://wiki.archlinux.org/title/Lenovo_Legion_7i)
- [ArchWiki — NVIDIA](https://wiki.archlinux.org/title/NVIDIA)
- [ArchWiki — Hybrid graphics](https://wiki.archlinux.org/title/Hybrid_graphics)

---

## How This Was Created

This document was produced by Claude (claude-sonnet-4-6, Anthropic) on 2026-05-04 by:

1. Running live hardware scans on the machine (`inxi -Fxz`, `lscpu`, `lspci -v`, `nvidia-smi`, `bluetoothctl`, `dmesg`, `journalctl -b 0 -k`, `sensors`, `aplay -l`, `lsblk`, etc.)
2. Searching the web for each hardware component's Linux compatibility status
3. Reading the upstream GitHub issues and forum threads linked above
4. Correlating boot logs against known error signatures

The human owner of this machine reviewed the content but did not write it. Treat this as a starting point for your own investigation, not ground truth — AI makes mistakes, upstream statuses change, and your hardware revision or BIOS version may behave differently.

**Contributions welcome.** If you have this machine, found something wrong here, or have a fix working, please open an issue or PR.

---

*Last updated: 2026-05-04 | Kernel tested: 7.0.3-1-cachyos | Distro: CachyOS*
