#!/usr/bin/env python3
"""
PikPak Adaptive Dark Mode Patcher for macOS
Automatically extracts, patches, repacks, updates integrity hash,
and re-signs PikPak for macOS.
"""

import os
import sys
import shutil
import tempfile
import subprocess
import re
import argparse

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
APP_DEFAULT_PATH = "/Applications/PikPak.app"

# Ensure common paths (like Homebrew) are in PATH
for p in ["/opt/homebrew/bin", "/usr/local/bin"]:
    if p not in os.environ.get("PATH", "").split(":"):
        os.environ["PATH"] = p + ":" + os.environ.get("PATH", "")

def run_cmd(cmd, cwd=None, check=True):
    res = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"\n[ERROR] Command failed with exit code {res.returncode}:")
        print(f"Command: {cmd}")
        if res.stdout:
            print(f"STDOUT:\n{res.stdout}")
        if res.stderr:
            print(f"STDERR:\n{res.stderr}")
        sys.exit(res.returncode)
    return res

def check_dependencies():
    node_res = run_cmd("which node", check=False)
    if node_res.returncode != 0:
        print("[ERROR] 'node' is required but not found in PATH.")
        print("Please install Node.js (e.g. 'brew install node').")
        sys.exit(1)
    
    asar_bin = os.path.join(SCRIPT_DIR, "node_modules", ".bin", "asar")
    if not os.path.exists(asar_bin):
        asar_res = run_cmd("which asar", check=False)
        if asar_res.returncode != 0:
            print("[INFO] Local asar not found, checking npx...")
            npx_res = run_cmd("which npx", check=False)
            if npx_res.returncode != 0:
                print("[ERROR] Neither 'asar' nor 'npx' was found.")
                sys.exit(1)

def get_asar_cmd():
    asar_mjs = os.path.join(SCRIPT_DIR, "node_modules", "@electron/asar", "bin", "asar.mjs")
    if os.path.exists(asar_mjs):
        return f'node "{asar_mjs}"'
    return "npx --yes @electron/asar"

def is_pikpak_running(app_path):
    proc_name = os.path.basename(app_path).replace(".app", "")
    res = run_cmd(f'pgrep -f "{app_path}"', check=False)
    return res.returncode == 0

def kill_pikpak(app_path):
    print("[*] Terminating running PikPak instances...")
    run_cmd(f'pkill -f "{app_path}"', check=False)
    # Give it a moment to release file locks
    import time
    time.sleep(1)

def compute_asar_header_hash(asar_path):
    local_asar_lib = os.path.join(SCRIPT_DIR, "node_modules", "@electron/asar", "lib", "asar.js")
    node_script = """
    import crypto from "node:crypto";
    import { pathToFileURL } from "node:url";
    const asarLibPath = process.argv[1];
    const targetAsar = process.argv[2];
    let getRawHeader;
    try {
        const mod = await import(pathToFileURL(asarLibPath).href);
        getRawHeader = mod.getRawHeader;
    } catch(e) {
        const mod = await import("@electron/asar");
        getRawHeader = mod.getRawHeader;
    }
    const raw = getRawHeader(targetAsar);
    const hash = crypto.createHash("sha256").update(raw.headerString || raw).digest("hex");
    console.log(hash);
    """
    res = run_cmd(["node", "--input-type=module", "-e", node_script, local_asar_lib, asar_path])
    return res.stdout.strip()

def patch_renderer_html(index_html_path):
    with open(index_html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Dark loading styles in <style>
    dark_css = """
      @media (prefers-color-scheme: dark) {
        html, body {
          background-color: #181a1b !important;
          color: #e8e6e3 !important;
        }
        #initial-loading svg path[fill="#E1E5EB"] {
          fill: #2a2e33 !important;
        }
      }
    """
    if "@media (prefers-color-scheme: dark)" not in content:
        if "</style>" in content:
            content = content.replace("</style>", dark_css + "\n    </style>", 1)

    # 2. DarkReader script injection
    dr_script = """<script src="./darkreader.js"></script><script>
(function() {
  function initAdaptiveDark() {
    var dr = window.DarkReader;
    if (!dr && typeof require === "function") {
      try { dr = require("./darkreader.js"); } catch(e) {}
    }
    if (!dr) {
      console.warn("[AdaptiveDark] DarkReader not loaded");
      return;
    }
    try {
      if (typeof dr.setFetchMethod === "function") {
        dr.setFetchMethod(window.fetch);
      }
      dr.auto({
        brightness: 100,
        contrast: 92,
        sepia: 0
      }, {
        css: `
          html, body {
            background-color: #181a1b !important;
          }
          img, video, canvas, svg image {
            filter: none !important;
          }
          #initial-loading svg {
            filter: none !important;
          }
          .el-dialog, .el-popper, .el-dropdown-menu, .el-message-box {
            background-color: #212426 !important;
            border-color: #383d40 !important;
          }
          ::-webkit-scrollbar-thumb {
            background-color: rgba(255, 255, 255, 0.2) !important;
          }
          ::-webkit-scrollbar-thumb:hover {
            background-color: rgba(255, 255, 255, 0.35) !important;
          }
          ::-webkit-scrollbar-track {
            background-color: transparent !important;
          }
        `
      });
      console.log("[AdaptiveDark] DarkReader auto initialized successfully");
    } catch(err) {
      console.error("[AdaptiveDark] Init error:", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAdaptiveDark);
  } else {
    initAdaptiveDark();
  }
})();
</script>"""

    if "darkreader.js" not in content:
        if "<title>PikPak</title>" in content:
            content = content.replace("<title>PikPak</title>", "<title>PikPak</title>" + dr_script, 1)
        elif "</head>" in content:
            content = content.replace("</head>", dr_script + "</head>", 1)

    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(content)

def patch_loading_html(loading_html_path):
    if not os.path.exists(loading_html_path):
        return
    with open(loading_html_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "@media (prefers-color-scheme: dark)" not in content and "</style>" in content:
        dark_loading_style = """
    @media (prefers-color-scheme: dark) {
      #app {
        background: #181a1b !important;
      }
    }
    """
        content = content.replace("</style>", dark_loading_style + "</style>", 1)
        with open(loading_html_path, "w", encoding="utf-8") as f:
            f.write(content)

def patch_main_process(main_index_path):
    with open(main_index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace hardcoded white background color with adaptive check
    content = re.sub(
        r'backgroundColor:\s*["\']#(?:fff|ffffff)["\']',
        'backgroundColor:(require("electron").nativeTheme?.shouldUseDarkColors?"#181a1b":"#ffffff")',
        content
    )

    # 2. Append runtime theme sync block if not present
    marker = "/* PIKPAK_ADAPTIVE_DARK_MODE */"
    if marker not in content:
        runtime_block = (
            "\n" + marker + "\n"
            ";(()=>{\n"
            "  try {\n"
            '    const { nativeTheme, BrowserWindow } = require("electron");\n'
            "    if (nativeTheme) {\n"
            '      nativeTheme.themeSource = "system";\n'
            '      nativeTheme.on("updated", () => {\n'
            "        try {\n"
            "          BrowserWindow.getAllWindows().forEach(w => {\n"
            "            try {\n"
            "              if (!w.isDestroyed()) {\n"
            '                w.setBackgroundColor(nativeTheme.shouldUseDarkColors ? "#181a1b" : "#ffffff");\n'
            "              }\n"
            "            } catch(e) {}\n"
            "          });\n"
            "        } catch(e) {}\n"
            "      });\n"
            "    }\n"
            "  } catch(e) {}\n"
            "})();\n"
        )
        content += runtime_block

    with open(main_index_path, "w", encoding="utf-8") as f:
        f.write(content)

def update_info_plist_hash(plist_path, new_hash):
    with open(plist_path, "r", encoding="utf-8") as f:
        plist_content = f.read()

    # Match the SHA256 string inside ElectronAsarIntegrity
    pattern = r'(<key>Resources/app\.asar</key>\s*<dict>\s*<key>algorithm</key>\s*<string>SHA256</string>\s*<key>hash</key>\s*<string>)[a-fA-F0-9]{64}(</string>)'
    if re.search(pattern, plist_content):
        updated_content = re.sub(pattern, rf'\g<1>{new_hash}\g<2>', plist_content)
    else:
        # Fallback to direct replacement if format slightly varies
        m = re.search(r'<key>hash</key>\s*<string>([a-fA-F0-9]{64})</string>', plist_content)
        if m:
            old_hash = m.group(1)
            updated_content = plist_content.replace(old_hash, new_hash, 1)
        else:
            raise RuntimeError("Could not locate ElectronAsarIntegrity hash in Info.plist")

    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

def main():
    parser = argparse.ArgumentParser(description="PikPak Adaptive Dark Mode Patcher for macOS")
    parser.add_argument("--app", default=APP_DEFAULT_PATH, help=f"Path to PikPak.app (default: {APP_DEFAULT_PATH})")
    parser.add_argument("--launch", "-l", action="store_true", help="Launch PikPak after patching")
    parser.add_argument("--force", "-f", action="store_true", help="Do not prompt before closing PikPak")
    args = parser.parse_args()

    app_path = os.path.abspath(args.app)
    if not os.path.exists(app_path):
        print(f"[ERROR] PikPak.app not found at: {app_path}")
        sys.exit(1)

    contents_dir = os.path.join(app_path, "Contents")
    resources_dir = os.path.join(contents_dir, "Resources")
    app_asar_path = os.path.join(resources_dir, "app.asar")
    info_plist_path = os.path.join(contents_dir, "Info.plist")

    if not os.path.exists(app_asar_path) or not os.path.exists(info_plist_path):
        print(f"[ERROR] Invalid app bundle structure at: {app_path}")
        sys.exit(1)

    check_dependencies()
    asar_cmd = get_asar_cmd()

    # Check if app is running
    if is_pikpak_running(app_path):
        if not args.force:
            print("[!] PikPak is currently running.")
            confirm = input("    Close PikPak to continue patching? [y/N]: ").strip().lower()
            if confirm not in ["y", "yes"]:
                print("Aborted.")
                sys.exit(0)
        kill_pikpak(app_path)

    print(f"[*] Starting adaptive dark mode patch for: {app_path}")

    # Backups
    original_asar_backup = os.path.join(resources_dir, "app.asar.original")
    if not os.path.exists(original_asar_backup):
        print("[*] Creating permanent original backup (app.asar.original)...")
        run_cmd(f'cp -X "{app_asar_path}" "{original_asar_backup}"')

    original_plist_backup = os.path.join(contents_dir, "Info.plist.original")
    if not os.path.exists(original_plist_backup):
        print("[*] Creating permanent original backup (Info.plist.original)...")
        run_cmd(f'cp -X "{info_plist_path}" "{original_plist_backup}"')

    # Create temporary workspace
    with tempfile.TemporaryDirectory(prefix="pikpak_patch_") as tmp_dir:
        extracted_dir = os.path.join(tmp_dir, "extracted")
        new_asar_path = os.path.join(tmp_dir, "new_app.asar")

        print("[*] Extracting app.asar...")
        run_cmd(f'{asar_cmd} extract "{app_asar_path}" "{extracted_dir}"')

        # 1. Copy darkreader.js
        dr_source = os.path.join(SCRIPT_DIR, "darkreader.js")
        if not os.path.exists(dr_source):
            nm_dr = os.path.join(SCRIPT_DIR, "node_modules", "darkreader", "darkreader.js")
            if os.path.exists(nm_dr):
                with open(nm_dr, "r", encoding="utf-8") as f:
                    c = f.read()
                if "window.DarkReader = exports;" not in c:
                    target = 'Object.defineProperty(exports, "__esModule", {value: true});'
                    c = c.replace(target, target + '\n    if (typeof window !== "undefined") { window.DarkReader = exports; }')
                with open(dr_source, "w", encoding="utf-8") as f:
                    f.write(c)
            else:
                print(f"[ERROR] darkreader.js not found in {SCRIPT_DIR} or {nm_dr}")
                sys.exit(1)

        renderer_dir = os.path.join(extracted_dir, "dist", "renderer-process")
        dr_dest = os.path.join(renderer_dir, "darkreader.js")
        shutil.copy2(dr_source, dr_dest)

        # 2. Patch renderer index.html
        index_html = os.path.join(renderer_dir, "index.html")
        if os.path.exists(index_html):
            print("[*] Patching renderer index.html...")
            patch_renderer_html(index_html)
        else:
            print("[WARNING] dist/renderer-process/index.html not found!")

        # 3. Patch loading.html
        loading_html = os.path.join(renderer_dir, "static", "loading.html")
        patch_loading_html(loading_html)

        # 4. Patch main-process
        main_index = os.path.join(extracted_dir, "dist", "main-process", "index.js")
        if os.path.exists(main_index):
            print("[*] Patching main-process index.js...")
            patch_main_process(main_index)
        else:
            print("[WARNING] dist/main-process/index.js not found!")

        # 5. Repack ASAR
        print("[*] Repacking app.asar (unpacking native binaries)...")
        run_cmd(f'{asar_cmd} pack "{extracted_dir}" "{new_asar_path}" --unpack "*.{{node,dylib}}"')

        # 6. Compute new ASAR raw header hash
        print("[*] Calculating new ASAR header SHA256 integrity hash...")
        new_hash = compute_asar_header_hash(new_asar_path)
        print(f"    New Hash: {new_hash}")

        # 7. Update Info.plist
        print("[*] Updating ElectronAsarIntegrity in Info.plist...")
        update_info_plist_hash(info_plist_path, new_hash)

        # 8. Copy new app.asar into app bundle
        print("[*] Installing patched app.asar...")
        run_cmd(f'cp -X "{new_asar_path}" "{app_asar_path}"')

    # 9. Clear quarantine and re-sign
    print("[*] Clearing quarantine attributes...")
    run_cmd(f'xattr -cr "{app_path}"')

    print("[*] Re-signing app bundle (ad-hoc codesign)...")
    run_cmd(f'codesign --force --deep --sign - "{app_path}"')

    print("[*] Verifying signature...")
    run_cmd(f'codesign -v "{app_path}"')

    print("\n[SUCCESS] PikPak has been successfully patched with Adaptive Dark Mode!")
    print("          It will now seamlessly adapt to your macOS Light and Dark appearance.")

    if args.launch:
        print("[*] Launching PikPak...")
        run_cmd(f'open -a "{app_path}"')

if __name__ == "__main__":
    main()
