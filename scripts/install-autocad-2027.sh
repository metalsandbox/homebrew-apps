#!/bin/bash
# Install AutoCAD 2027.1 from a public Autodesk CDN link through a locally
# generated, SHA-256-pinned Homebrew Cask. No Autodesk credentials are stored.
set -euo pipefail

URL='https://efulfillment.autodesk.com/NetSWDLD/ODIS/prd/2027/ACDMAC/DA13C2BB-9635-3AD7-9E72-CB16D8C17DB6/SFX/Autodesk_AutoCAD_2027.1_macOS.dmg'
NAME='Autodesk_AutoCAD_2027.1_macOS.dmg'
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="${HOME}/Library/Caches/metalsandbox-autocad"
DMG="${CACHE}/${NAME}"
CASK="${ROOT}/Casks/autocad-local.rb"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo 'Requires macOS.' >&2
  exit 1
fi
if ! command -v brew >/dev/null 2>&1; then
  echo 'Install Homebrew first: https://brew.sh/' >&2
  exit 1
fi
mkdir -p "$CACHE"
if [[ ! -s "$DMG" ]]; then
  echo "Downloading directly from Autodesk (public session-free URL)..."
  curl --fail --location --show-error --retry 3 --connect-timeout 20 \
    --output "${DMG}.partial" "$URL" || {
      rm -f "${DMG}.partial"
      echo 'Public download failed. Download the DMG while logged into Autodesk Account and supply it manually.' >&2
      exit 1
    }
  mv "${DMG}.partial" "$DMG"
fi

# Fail closed on authentication HTML, invalid image data, or corrupt downloads.
hdiutil verify "$DMG" || {
  echo 'Downloaded content is not a valid DMG. Remove it before retrying.' >&2
  exit 1
}

# The Python tool discovers Autodesk Setup dynamically and computes SHA-256.
if [[ -e "$CASK" ]]; then
  echo "Existing generated Cask at $CASK: refusing to overwrite. Review/remove it before retrying." >&2
  exit 1
fi
python3 "$ROOT/scripts/prepare-autocad-cask.py" --dmg "$DMG" --year 2027 --output "$CASK"
echo 'The following Cask was generated from the actual DMG:'
grep -E '^  (version|sha256|url) ' "$CASK"
echo 'Installing through Homebrew; Autodesk may request administrator permission.'
brew install --cask "$CASK"
