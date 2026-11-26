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

## What it does

- **System-Adaptive:** Follows your macOS Appearance setting in real time without restarting the app.
- **Zero White Flashes:** Injects instant dark background styles (`#181a1b`) into window chrome and initial HTML loading screens.
- **Media Preservation:** Preserves natural colors for videos, images, avatars, and thumbnails via Dark Reader.
- **Auto Integrity & Signing:** Recalculates `ElectronAsarIntegrity` SHA-256 hashes in `Info.plist` and re-signs `PikPak.app` with `codesign`.
- **Single-File Standalone:** Self-contained executable with embedded Dark Reader—no clone directories or local dependencies needed.

## Install

Install the standalone command to `~/bin/` and run it (re-run anytime after PikPak auto-updates):

```zsh
mkdir -p ~/bin && curl -fsSL https://raw.githubusercontent.com/passs0/PikPak-DarkMode-Mac/main/patch-pikpak-darkmode -o ~/bin/patch-pikpak-darkmode && chmod +x ~/bin/patch-pikpak-darkmode
patch-pikpak-darkmode --force --launch
```

| Flag | Description |
| :--- | :--- |
| `--launch`, `-l` | Automatically relaunch PikPak after patching finishes |
| `--force`, `-f` | Close any running PikPak process without prompting |
| `--app <path>` | Specify a custom path (defaults to `/Applications/PikPak.app`) |

## Restore Original App

```zsh
cp -X /Applications/PikPak.app/Contents/Resources/app.asar.original /Applications/PikPak.app/Contents/Resources/app.asar
cp -X /Applications/PikPak.app/Contents/Info.plist.original /Applications/PikPak.app/Contents/Info.plist
xattr -cr /Applications/PikPak.app && codesign --force --deep --sign - /Applications/PikPak.app
```

Built with [Google Antigravity](https://antigravity.google) — 100% AI-written code and docs, steered and tested by hand.

## License

Released under the [MIT License](LICENSE). Powered by [Dark Reader](https://github.com/darkreader/darkreader) and `@electron/asar`. Not affiliated with PikPak.
