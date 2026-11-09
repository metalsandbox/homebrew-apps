"""Check the Canon China catalog and verify a newer Canon PRINT disk image."""

import argparse
import hashlib
import html
from pathlib import Path
import plistlib
import re
import subprocess
from tempfile import TemporaryDirectory


CASK = Path(__file__).resolve().parents[1] / "Casks/canon-print.rb"
SUPPORT = "https://www.canon.com.cn/supports/download"
CATALOG = f"{SUPPORT}/sims/list/slist?channel=5&modelCodeJ=6794C&modelNameC=TS8880&query=Canon+PRINT"
DETAIL = f"{SUPPORT}/simsdetail"
VERSION = r"[0-9]+(?:\.[0-9]+)+"
RELEASE = re.compile(
    rf"""<div class="js_item"[^>]*\burl="{re.escape(DETAIL)}/([0-9]{{10}})\.html"\s*>"""
    rf"""\s*<div class="js_title">\s*Canon\s+PRINT\s+v\.?\s*({VERSION})\s*\(Mac\)\s*</div>""",
    re.IGNORECASE,
)
DOWNLOAD = r"https://gdlp01\.c-wss\.com/gds/[0-9]+/[0-9]+/[0-9]+/mCSC-mac-[A-Za-z0-9_.-]+\.dmg"
SIGNATURE = (
    '=anchor apple generic and certificate 1[field.1.2.840.113635.100.6.2.6] exists'
    ' and certificate leaf[field.1.2.840.113635.100.6.1.13] exists'
    ' and certificate leaf[subject.OU] = "XE2XNRRXZ5"'
)


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def curl(url, *args):
    return command(
        "curl", "--fail", "--silent", "--show-error", "--proto", "=https",
        "--retry", "2", "--max-time", "90", *args, url,
    )


def version_key(version):
    return tuple(map(int, version.split(".")))


def releases():
    first_page = curl(CATALOG)
    pagination = re.search(r'class="pagenum3">共([0-9]+)页', first_page)
    if not pagination or not 1 <= int(pagination[1]) <= 10:
        raise ValueError("Unexpected Canon catalog pagination")

    pages = [first_page]
    for page in range(2, int(pagination[1]) + 1):
        pages.append(curl(f"{CATALOG}&pageNo={page}"))
    matches = {
        (version, content_id)
        for page in pages
        for content_id, version in RELEASE.findall(re.sub(r"</?span\b[^>]*>", "", page))
    }
    if not matches:
        raise ValueError("No Canon PRINT Mac release found in the official catalog")
    latest = max((version for version, _ in matches), key=version_key)
    content_ids = {content_id for version, content_id in matches if version == latest}
    if len(content_ids) != 1:
        raise ValueError(f"Multiple Canon releases found for {latest}")
    return latest, content_ids.pop()


def download_url(content_id):
    detail = curl(f"{DETAIL}/{content_id}.html")
    link = re.search(r'<input\b[^>]*\bid="dl_link"\s+value="([^"]+)"', detail)
    if not link:
        raise ValueError("Canon download link is missing")
    redirect = html.unescape(link[1])
    if not re.fullmatch(
        r"https://pdisp01\.c-wss\.com/gdl/WWUFORedirectTarget\.do\?id=[A-Za-z0-9_=-]+&cmp=ASP&lang=ZH",
        redirect,
    ):
        raise ValueError("Unexpected Canon download redirect")
    url = curl(redirect, "--output", "/dev/null", "--write-out", "%{redirect_url}")
    if not re.fullmatch(DOWNLOAD, url):
        raise ValueError("Unexpected Canon DMG URL")
    return url


def verify(dmg, mount, version):
    mount.mkdir()
    command("hdiutil", "attach", "-readonly", "-nobrowse", "-mountpoint", str(mount), str(dmg))
    try:
        app = mount / "Canon Inkjet Smart Connect.app"
        command("codesign", "--verify", "--deep", "--strict", "-R", SIGNATURE, str(app))
        command("spctl", "--assess", "--type", "execute", str(app))
        info = plistlib.loads((app / "Contents/Info.plist").read_bytes())
        if (
            info["CFBundleIdentifier"] != "jp.co.canon.ij.print.portal"
            or info["CFBundleShortVersionString"] != version
            or not re.fullmatch(r"11(?:\.0)*", info["LSMinimumSystemVersion"])
        ):
            raise ValueError("Canon app identity, version, or macOS requirement changed")
        executable = app / "Contents/MacOS" / info["CFBundleExecutable"]
        if not {"arm64", "x86_64"} <= set(command("lipo", "-archs", str(executable)).split()):
            raise ValueError("Canon app no longer supports both Apple Silicon and Intel")
    finally:
        command("hdiutil", "detach", str(mount))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-current", action="store_true", help="Verify the current official DMG without writing")
    args = parser.parse_args()

    source = CASK.read_text(encoding="utf-8")
    current = re.search(rf'^  version "({VERSION})"$', source, re.MULTILINE)[1]
    version, content_id = releases()
    if version_key(version) < version_key(current):
        raise ValueError(f"Canon catalog lists {version}, older than the cask version {current}")
    if args.verify_current and version != current:
        raise ValueError(f"Canon catalog now lists {version}; expected {current}")
    if version == current and not args.verify_current:
        print(f"Canon PRINT {current} is current")
        return

    url = download_url(content_id)
    with TemporaryDirectory(prefix="canon-print-") as directory:
        dmg = Path(directory) / "canon-print.dmg"
        curl(url, "--output", str(dmg))
        with dmg.open("rb") as package:
            sha256 = hashlib.file_digest(package, "sha256").hexdigest()
        verify(dmg, Path(directory) / "volume", version)

    if args.verify_current:
        if f'  url "{url}"' not in source or f'  sha256 "{sha256}"' not in source:
            raise ValueError("Current official DMG URL or SHA-256 differs from the cask")
        print(f"Verified current Canon PRINT {version}")
        return

    for stanza, value in (
        ("version", version),
        ("sha256", sha256),
        ("url", url),
        ("homepage", f"{DETAIL}/{content_id}.html"),
    ):
        source, count = re.subn(rf'^  {stanza} "[^"\n]+"$', f'  {stanza} "{value}"', source, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(f"Expected one {stanza} stanza in {CASK.name}")
    CASK.write_text(source, encoding="utf-8")
    print(f"Verified Canon PRINT {version} and updated {CASK.name}")


if __name__ == "__main__":
    main()
