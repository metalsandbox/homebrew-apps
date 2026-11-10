#!/usr/bin/env python3
"""Prepare a private, checksum-pinned Homebrew Cask from a user's Autodesk DMG."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys


def run(*args):
    return subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def installer_in_dmg(dmg):
    # hdiutil -plist avoids parsing localized output or assuming /Volumes/Installer.
    result = run("hdiutil", "attach", "-readonly", "-nobrowse", "-plist", str(dmg))
    info = plistlib.loads(result.stdout)
    mounts = [Path(x["mount-point"]) for x in info["system-entities"] if "mount-point" in x]
    try:
        candidates = []
        for mount in mounts:
            for app in mount.rglob("*.app"):
                setup = app / "Contents/Helper/Setup.app/Contents/MacOS/Setup"
                if setup.is_file():
                    candidates.append((mount, setup))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected one Autodesk Setup binary, found {len(candidates)}")
        return str(candidates[0][1].relative_to(candidates[0][0]))
    finally:
        for mount in reversed(mounts):
            run("hdiutil", "detach", str(mount))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def render(dmg, year, setup, checksum):
    # Local file URI is private to this Mac. This cask must not be committed.
    # The vendor Setup performs the install; its side effects are outside Homebrew.
    return f'''# GENERATED LOCALLY — do not commit: contains an absolute user path.
cask "autocad-local" do
  version "{year}"
  sha256 "{checksum}"

  url {json.dumps(dmg.as_uri())}
  name "Autodesk AutoCAD for Mac"
  desc "User-supplied Autodesk installer; requires a valid Autodesk license"
  homepage "https://www.autodesk.com/products/autocad/overview"

  depends_on macos: :ventura

  installer script: {{
    executable: {json.dumps(setup)},
    args:       ["--silent"],
    sudo:       true,
  }}

  # Vendor-wide shared licensing/support files are deliberately left alone.
  # Verify the app path on this Mac before relying on uninstall.
  uninstall delete: "/Applications/Autodesk/AutoCAD {year}/AutoCAD {year}.app"

  livecheck do
    skip "Autodesk downloads require an authenticated account"
  end
end
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dmg", type=Path, required=True, help="DMG downloaded from Autodesk Account")
    parser.add_argument("--year", type=int, required=True, help="AutoCAD release year (e.g. 2027)")
    parser.add_argument("--output", type=Path, default=Path("Casks/autocad-local.rb"))
    args = parser.parse_args()
    dmg = args.dmg.expanduser().resolve(strict=True)
    if sys.platform != "darwin":
        parser.error("Run on macOS: inspecting the official DMG requires hdiutil")
    if not dmg.is_file() or dmg.suffix.lower() != ".dmg":
        parser.error("--dmg must be a local .dmg file")
    if not (2021 <= args.year <= 2100):
        parser.error("--year must be a supported AutoCAD for Mac release year")
    if args.output.exists():
        parser.error(f"Refusing to overwrite {args.output}")
    setup = installer_in_dmg(dmg)
    if f"{args.year}" not in setup:
        parser.error(f"Installer path does not mention release {args.year}: {setup}")
    checksum = digest(dmg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(dmg, args.year, setup, checksum), encoding="utf-8")
    print(f"Generated {args.output}. Keep the source DMG at: {dmg}")
    print("Review generated cask, verify the uninstall path, then run:")
    print(f"  brew install --cask {args.output.resolve()}")


if __name__ == "__main__":
    main()
