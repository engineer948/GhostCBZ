# GhostCBZ 👻

A blazingly fast, distraction-free, and privacy-focused comic book reader (`.cbz`, `.zip`) built with Python and Tkinter. Engineered to operate entirely in-memory with zero temporary disk writes.

---

## 📸 Screenshots
<p align="center">
  <img src="screenshot.png" alt="GhostCBZ Main Interface" width="850">
</p>

> *Place your app screenshot in the root directory named `screenshot.png` to display it above.*

---

## ⚡ Engineering Philosophy (Why GhostCBZ?)
Traditional comic readers extract archive files into the operating system's temporary directory (`/tmp` or `%TEMP%`). This design causes excessive Disk I/O, degrades SSD health over time, and leaves unencrypted files behind if the application crashes.

**GhostCBZ operates 100% in-memory:**
- **In-Memory Decompression:** Reads `.cbz` and `.zip` archives directly into RAM using Python's `io.BytesIO`.
- **Zero Disk Footprint:** No files are extracted to your drive during reading.
- **Hardware-Friendly:** Eliminates storage read/write latency for instantaneous page turns.
- **True Incognito Mode:** Toggling the history switch immediately erases `reader_history.json` from disk and volatile memory.
- **Air-Gapped & Secure:** Contains zero networking sockets, tracking, or telemetry.

---

## ✨ Features
- **In-Memory Rendering:** Zero temp files created on your disk.
- **Dynamic Dual-Page Mode:** On-the-fly image concatenation for seamless Manga spreads (`M` key).
- **High-Contrast Night Mode:** Inverts image colors on the fly for night-time reading (`N` key).
- **Interactive Lens Magnifier:** Inspect small text or fine art panels by holding `Right Click`.
- **UI Toggles:** Instantly enable/disable hotkeys or reading history directly from the top bar.
- **Resume Dashboard:** Quick-access list to resume reading recently opened volumes.

---

## 🎮 Shortcuts & Controls

| Action | Shortcut / Mouse Gesture |
| :--- | :--- |
| **Next Page** | `Right Arrow`, `D`, `Space`, or `Click Right Half` |
| **Previous Page** | `Left Arrow`, `A`, or `Click Left Half` |
| **Dual-Page Spread** | `M` |
| **Inverted Night Mode** | `N` |
| **Magnifier Loupe** | `Right Click` (Hold & Drag over image) |
| **Toggle Fullscreen** | `F` or `F11` |
| **Exit Fullscreen** | `ESC` |
| **Toggle Shortcuts** | UI Button (`⚡ Shortcuts: ON/OFF`) |
| **Toggle History** | UI Button (`🕒 History: ON/OFF`) |

---

## 📦 How to Build the AppImage (Fedora / RHEL)

Run the following commands to package GhostCBZ into a standalone `.AppImage` binary:

```bash
# 1. Prepare directory and files
mkdir -p GhostCBZ.AppDir/usr/bin
cp ghostcbz.py GhostCBZ.AppDir/usr/bin/
cp path/to/your_icon.png GhostCBZ.AppDir/ghostcbz.png

# 2. Create Desktop Entry
cat << 'EOF' > GhostCBZ.AppDir/ghostcbz.desktop
[Desktop Entry]
Name=GhostCBZ
Exec=AppRun
Icon=ghostcbz
Type=Application
Categories=Graphics;Viewer;
EOF

# 3. Create Launcher Script
cat << 'EOF' > GhostCBZ.AppDir/AppRun
#!/bin/sh
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
exec python3 "$HERE/usr/bin/ghostcbz.py" "$@"
EOF
chmod +x GhostCBZ.AppDir/AppRun

# 4. Build the AppImage
curl -L -O https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
ARCH=x86_64 ./appimagetool-x86_64.AppImage GhostCBZ.AppDir GhostCBZ-x86_64.AppImage
