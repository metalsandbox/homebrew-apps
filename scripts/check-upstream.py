#!/usr/bin/env python3
"""Check Valve's stable bootstrapper; verify before writing a candidate update.

Uses only Python's standard library and macOS system tools. Never runs Steam.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import tarfile
import tempfile
import zipfile
import urllib.request

BASE = "https://client-update.steamstatic.com/"
ROOT = pathlib.Path(__file__).resolve().parents[1]
CASK = ROOT / "Casks/steam-arm64.rb"
REQUIREMENT = "=anchor apple generic and certificate leaf[subject.OU] = MXGJJ98X76"


def parse_manifest(text):
    tokens = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"|([{}])', text)
    tokens = [a if not b else b for a, b in tokens]
    index = 0

    def obj(nested=False):
        nonlocal index
        result = {}
        while index < len(tokens):
            key = tokens[index]
            index += 1
            if key == "}":
                if not nested:
                    raise ValueError("Unexpected closing brace")
                return result
            if key == "{" or index == len(tokens):
                raise ValueError("Malformed manifest")
            value = tokens[index]
            index += 1
            if value == "}":
                raise ValueError("Missing value")
            if key in result:
                raise ValueError("Duplicate key: " + key)
            result[key] = obj(True) if value == "{" else value
        if nested:
            raise ValueError("Unclosed block")
        return result

    data = obj()["osx"]
    # Do not accidentally select the nested steamchina package.
    package = data["appdmg_osx"]
    version, filename, digest = data["version"], package["file"], package["sha2"]
    if not re.fullmatch(r"[0-9]+", version):
        raise ValueError("Invalid version")
    if not re.fullmatch(r"appdmg_osx\.zip\.[0-9a-f]{40}", filename):
        raise ValueError("Unexpected package path")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("Invalid SHA-256")
    return {"version": version, "file": filename, "sha256": digest}


def download(url, destination):
    with urllib.request.urlopen(url, timeout=120) as source, open(destination, "wb") as target:
        while chunk := source.read(1024 * 1024):
            target.write(chunk)


def verify(info, archive, stage):
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != info["sha256"]:
        raise ValueError("SHA-256 mismatch")
    with zipfile.ZipFile(archive) as bundle:
        expected = {"SteamMacBootstrapper.tar.gz", "SteamMacBootstrapper.version"}
        if set(bundle.namelist()) != expected or len(bundle.namelist()) != 2:
            raise ValueError("Unexpected ZIP layout")
    # unzip accepts Valve's ZIP variant; Apple's ditto does not.
    subprocess.run(["/usr/bin/unzip", "-q", str(archive), "-d", str(stage)], check=True)
    with tarfile.open(stage / "SteamMacBootstrapper.tar.gz", "r:gz") as bundle:
        for member in bundle:
            destination = (stage / member.name).resolve()
            if stage.resolve() not in destination.parents:
                raise ValueError("Unsafe TAR path")
            if not (member.isfile() or member.isdir() or member.issym() or member.islnk()):
                raise ValueError("Unexpected TAR entry type")
            if member.issym() or member.islnk():
                base = destination.parent if member.issym() else stage
                target = (base / member.linkname).resolve()
                if stage.resolve() not in target.parents:
                    raise ValueError("Unsafe TAR link")
    subprocess.run(["/usr/bin/tar", "-xzf", str(stage / "SteamMacBootstrapper.tar.gz"),
                    "-C", str(stage)], check=True)
    app = stage / "Steam.app"
    subprocess.run(["/usr/bin/lipo", "-verify_arch", "arm64",
                    str(app / "Contents/MacOS/steam_osx")], check=True)
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", "-R",
                    REQUIREMENT, str(app)], check=True)
    subprocess.run(["/usr/sbin/spctl", "--assess", "--type", "execute", str(app)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Verify and update Cask if the package changed")
    parser.add_argument("--verify", action="store_true", help="Download and verify even if unchanged (macOS)")
    args = parser.parse_args()
    with urllib.request.urlopen(BASE + "steam_client_osx", timeout=60) as response:
        info = parse_manifest(response.read().decode("utf-8"))
    old = CASK.read_text()
    unchanged = BASE + info["file"] in old and 'sha256 "' + info["sha256"] + '"' in old
    print(json.dumps({**info, "changed": not unchanged}, indent=2))
    if not args.verify and (not args.write or unchanged):
        return
    with tempfile.TemporaryDirectory(prefix="steam-arm64-") as temporary:
        temp = pathlib.Path(temporary)
        archive, stage = temp / "steam.zip", temp / "stage"
        stage.mkdir()
        download(BASE + info["file"], archive)
        verify(info, archive, stage)
    if args.write and not unchanged:
        new, versions = re.subn(r'  version "[^"]+"', '  version "' + info["version"] + '"', old, count=1)
        new, hashes = re.subn(r'  sha256 "[^"]+"', '  sha256 "' + info["sha256"] + '"', new, count=1)
        new, urls = re.subn(r'https://client-update\.steamstatic\.com/appdmg_osx\.zip\.[0-9a-f]+',
                           BASE + info["file"], new, count=1)
        if (versions, hashes, urls) != (1, 1, 1):
            raise ValueError("Cask format changed; refusing automatic edit")
        pending = CASK.with_suffix(".rb.tmp")
        pending.write_text(new)
        pending.replace(CASK)


if __name__ == "__main__":
    main()
