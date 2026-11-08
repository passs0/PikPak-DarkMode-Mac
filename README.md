<h1 align="center">PikPak-DarkMode-Mac</h1>

<p align="center">
  <strong>Seamless Adaptive Dark Mode for PikPak on macOS</strong><br/>
  Automatic real-time system theme tracking, zero startup white flashes, and lossless media preservation for the official PikPak desktop app.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/macOS-Apple%20Silicon%20%26%20Intel-black?logo=apple" alt="macOS" />
  <img src="https://img.shields.io/badge/target-PikPak%20Desktop-007AFF" alt="Target" />
  <img src="https://img.shields.io/badge/engine-Electron%20%7C%20Dark%20Reader-blue" alt="Engine" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" /></a>
</p>

---

> [!NOTE]
> **AI-Generated Tool Disclosure**
> **PikPak-DarkMode-Mac** is an AI-generated configuration and patching utility created with **Antigravity** (Google DeepMind) that brings true system-adaptive Dark Mode, instant dark chrome injection, and automated Electron ASAR integrity signing to the official macOS PikPak desktop application.

---

## ✨ Features

- **🌓 System-Adaptive**: Automatically follows your macOS Appearance setting (Light vs. Dark mode). Switches seamlessly in real time when macOS toggles between light and dark (e.g. at sunset/sunrise or in System Settings) without restarting the app.
- **⚡ Zero White Flashes**: Injects instant dark background styles (`#181a1b`) into the window chrome and initial HTML loading screens to prevent any startup flash.
- **🖼️ Media Preservation**: Smartly preserves natural colors for videos, images, avatars, and file thumbnails.
- **🛡️ Auto Integrity & Signing**: Automatically recalculates the `ElectronAsarIntegrity` SHA-256 header hash in `Info.plist` and re-signs the application bundle using `codesign`.
- **📦 Single-File Standalone**: Runs as a self-contained executable with embedded Dark Reader. No secondary folders, clone directories, or local dependencies needed.

---

## 🚀 Quick Install & Run (One-Liner)

Install the standalone command directly to your `~/bin/` folder (no repo folder required):

```bash
mkdir -p ~/bin && curl -fsSL https://raw.githubusercontent.com/passs0/PikPak-DarkMode-Mac/main/patch-pikpak-darkmode -o ~/bin/patch-pikpak-darkmode && chmod +x ~/bin/patch-pikpak-darkmode
```

Then patch PikPak anytime simply by running:

```bash
patch-pikpak-darkmode --force --launch
```

---

## 🛠️ Command-Line Options

| Flag | Description |
| :--- | :--- |
| `--launch`, `-l` | Automatically relaunch PikPak after patching finishes |
| `--force`, `-f` | Close any running PikPak process without prompting |
| `--app <path>` | Specify a custom path (defaults to `/Applications/PikPak.app`) |

---

## 🔄 After Official PikPak Updates

When PikPak auto-updates or is reinstalled, the official installer overwrites `app.asar`. Simply re-run:

```bash
patch-pikpak-darkmode --force --launch
```

---

## ⏪ Restoring the Original App

The patcher automatically creates permanent backups of the original vendor files (`app.asar.original` and `Info.plist.original`) before making any modifications. 

To revert to the untouched official version at any time:

```bash
cp -X /Applications/PikPak.app/Contents/Resources/app.asar.original /Applications/PikPak.app/Contents/Resources/app.asar
cp -X /Applications/PikPak.app/Contents/Info.plist.original /Applications/PikPak.app/Contents/Info.plist
xattr -cr /Applications/PikPak.app
codesign --force --deep --sign - /Applications/PikPak.app
```

---

## 📁 Repository Structure

- [`patch-pikpak-darkmode`](patch-pikpak-darkmode) — Standalone, single-file zero-dependency executable that extracts, patches, hashes, and re-signs `PikPak.app`.
- [`patch_pikpak.py`](patch_pikpak.py) — Python source implementation of the ASAR unpacker, Dark Reader CSS injector, and integrity calculator.
- [`patch.sh`](patch.sh) — Shell wrapper helper.

---

## 🙏 Credits & Acknowledgments

- Powered by [Dark Reader](https://github.com/darkreader/darkreader) (MIT License) for real-time intelligent color inversion.
- Powered by [@electron/asar](https://github.com/electron/asar) for archive inspection and extraction.

---

## ⚠️ Disclaimer

This is an independent community project and is **not** affiliated with, maintained by, or endorsed by PIKCLOUD PTE. LTD. or PikPak. All trademarks belong to their respective owners.

---

## 📄 License

Released under the [MIT License](LICENSE).
