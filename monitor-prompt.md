You are monitoring known open Linux compatibility issues for a Lenovo Legion Pro 7 Gen 10 (16IAX10H) running CachyOS. Your job is to search for any new developments and keep the README up to date.

## Your task

1. Search online for updates on each of the following open issues. For each one, check if there are new fixes, merged patches, new workarounds, new upstream kernel commits, new firmware releases, or significant new community discussions since the last check date shown in the README.

   **Issue 1 — Internal speakers / AW88399 amplifier firmware**
   - Search: "aw88399_acf.bin linux firmware", "aw88399 linux 2026", "16iax10h audio fix"
   - Check: https://github.com/nadimkobeissi/16iax10h-linux-sound-saga (new commits, issues, PRs)
   - Check: https://github.com/CachyOS/linux-cachyos/issues/618
   - Check: https://github.com/CachyOS/linux-cachyos/issues/687
   - Check: https://github.com/CachyOS/linux-cachyos/issues/707
   - Check linux-firmware upstream for aw88399_acf.bin being added

   **Issue 2 — DYTC power profiles unavailable (ideapad_acpi)**
   - Search: "ideapad_acpi DYTC arrow lake linux", "lenovo legion DYTC linux fix 2026"
   - Check for any kernel patches to ideapad_acpi adding DYTC support for Arrow Lake-HX

   **Issue 3 — NVIDIA RTX 5080 Mobile driver stability**
   - Search: "nvidia 595 linux fix", "nvidia 600 driver release", "nvidia rtx 5080 mobile linux 2026"
   - Check: https://github.com/CachyOS/linux-cachyos/issues/771
   - Check for new NVIDIA driver releases beyond 595.x

   **Issue 4 — Keyboard RGB / LenovoLegionLinux model 83F5**
   - Search: "LenovoLegionLinux 83F5", "lenovo legion pro 7 gen 10 linux keyboard backlight"
   - Check: https://github.com/johnfanv2/LenovoLegionLinux/issues/385
   - Check if model 83F5 has been added to the LenovoLegionLinux allowlist

   **Issue 5 — Intel BE200 Wi-Fi 7 suspend/resume**
   - Search: "intel be200 iwlwifi suspend resume fix 2026", "be200 linux suspend fix"
   - Check for iwlwifi firmware updates or kernel patches addressing the suspend/resume drop

   **Issue 6 — Intel xe driver stability for Arrow Lake**
   - Search: "xe driver arrow lake stable 2026", "intel xe arrow lake linux kernel"
   - Check if xe has been made the default for Arrow Lake in any recent kernel, or if the known issues (boot freeze, Vulkan compute, gaming FPS) have been resolved

2. Read the current README: /home/karlos/Projects/legion-pro7-linux/README.md

3. For EVERY issue you searched, add or update a `> Last checked: YYYY-MM-DD — <one line summary of status>` blockquote directly under the **Status:** line of that issue's section in the README. Use today's actual date.

4. If you found genuinely new information (a fix landed, a patch merged, a new workaround documented, a status changed), update the relevant section content with the new details. Also update the summary table at the top if the status changed.

5. Update the `*Last updated:*` line at the very bottom of the README to today's date.

6. If you made ANY changes to the README, run these commands:
   ```
   git -C /home/karlos/Projects/legion-pro7-linux add README.md
   git -C /home/karlos/Projects/legion-pro7-linux commit -m "Daily monitor YYYY-MM-DD: <brief summary>"
   git -C /home/karlos/Projects/legion-pro7-linux push
   ```
   Replace YYYY-MM-DD with today's date and write a real summary of what changed.

7. If nothing changed at all, do not commit — just exit cleanly.

## Rules
- Be factual. Only report things you actually found from real sources. Do not invent updates.
- Include URLs as sources when you find new information.
- Keep the existing README structure — only add/update content, do not reformat or rewrite sections that don't need changing.
- Today's date can be confirmed by running: date +%Y-%m-%d
