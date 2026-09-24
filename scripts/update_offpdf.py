#!/usr/bin/env python3
"""Update the OffPDF cask from the latest published GitHub release."""

import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path


CASK = Path(__file__).resolve().parents[1] / "Casks" / "offpdf.rb"
RELEASE_API = "https://api.github.com/repos/McanKul/offpdf/releases/latest"


def fetch(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "homebrew-apps-offpdf-updater",
        },
    )
    return urllib.request.urlopen(request, timeout=60)


def main():
    with fetch(RELEASE_API) as response:
        release = json.load(response)

    tag = release["tag_name"]
    match = re.fullmatch(r"v(\d+\.\d+\.\d+)", tag)
    if not match or release.get("draft") or release.get("prerelease"):
        raise ValueError(f"Unexpected latest release tag: {tag}")
    version = match.group(1)

    content = CASK.read_text()
    old_version = re.search(r'^  version "([^"]+)"$', content, re.MULTILINE)
    old_hash = re.search(r'^  sha256 "([a-f0-9]{64})"$', content, re.MULTILINE)
    if not old_version or not old_hash:
        raise ValueError("Cannot find the cask version and SHA-256")
    if tuple(map(int, version.split("."))) < tuple(map(int, old_version.group(1).split("."))):
        raise ValueError(f"Latest release {version} is older than cask {old_version.group(1)}")
    if old_version.group(1) == version:
        print(f"OffPDF {version} is already current")
        return

    asset_name = f"OffPDF_{version}_aarch64.dmg"
    assets = [asset for asset in release["assets"] if asset["name"] == asset_name]
    if len(assets) != 1:
        raise ValueError(f"Expected exactly one release asset named {asset_name}")
    asset_url = assets[0]["browser_download_url"]
    expected_url = f"https://github.com/McanKul/offpdf/releases/download/{tag}/{asset_name}"
    if asset_url != expected_url:
        raise ValueError(f"Unexpected asset URL: {asset_url}")

    digest = hashlib.sha256()
    with fetch(asset_url) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)

    updated = content.replace(old_version.group(0), f'  version "{version}"', 1)
    updated = updated.replace(old_hash.group(0), f'  sha256 "{digest.hexdigest()}"', 1)
    CASK.write_text(updated)
    print(f"Updated OffPDF {version}: {digest.hexdigest()}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, ValueError) as error:
        print(f"OffPDF update failed: {error}", file=sys.stderr)
        sys.exit(1)
