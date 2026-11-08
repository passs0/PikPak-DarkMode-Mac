# PikPak Adaptive Dark Mode for macOS

[![macOS](https://img.shields.io/badge/Platform-macOS-blue?logo=apple)](https://www.apple.com/macos/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated patcher that brings true **system-adaptive Dark Mode** to the official PikPak desktop application on macOS.

---

## ✨ Features

- **🌓 System-Adaptive**: Automatically follows your macOS Appearance setting (Light vs. Dark mode). Switches seamlessly in real time when macOS toggles between light and dark (e.g. at sunset/sunrise or in System Settings) without restarting the app.
- **⚡ Zero White Flashes**: Injects instant dark background styles (`#181a1b`) into the window chrome and initial HTML loading screens to prevent any startup flash.
- **🖼 Media Preservation**: Smartly preserves natural colors for videos, images, avatars, and file thumbnails.
- **🛡 Auto Integrity & Signing**: Automatically recalculates the `ElectronAsarIntegrity` SHA-256 header hash in `Info.plist` and re-signs the application bundle using `codesign`.
- **📦 Single-File Standalone**: Runs as a self-contained executable with embedded Dark Reader. No secondary folders, clone directories, or local dependencies needed.

---

## 🚀 Quick Install & Run (One-Liner)

Install the standalone command directly to your `~/bin/` folder (no repo folder required):

```bash
mkdir -p ~/bin && curl -fsSL https://raw.githubusercontent.com/passs0/pikpak-darkmode-mac/main/patch-pikpak-darkmode -o ~/bin/patch-pikpak-darkmode && chmod +x ~/bin/patch-pikpak-darkmode
```

Then patch PikPak anytime simply by running:

```bash
patch-pikpak-darkmode --force --launch
```

---

## 🛠 Command-Line Options

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

## 🤝 Acknowledgements

- Powered by [Dark Reader](https://github.com/darkreader/darkreader) (MIT License) for real-time intelligent color inversion.
- Powered by [@electron/asar](https://github.com/electron/asar) for archive inspection and extraction.

---

## ⚠️ Disclaimer

This is an independent community project and is **not** affiliated with, maintained by, or endorsed by PIKCLOUD PTE. LTD. or PikPak. All trademarks belong to their respective owners.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
