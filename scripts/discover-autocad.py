#!/usr/bin/env python3
"""Find public Autodesk AutoCAD for Mac DMG links from the Autodesk Community.

Discovery only. Candidate links are NOT verified binary releases.
"""
import argparse
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen

THREAD = "https://forums.autodesk.com/t5/installation-licensing-forum/2027-product-download-links/td-p/14055738"
UA = "Mozilla/5.0 (compatible; homebrew-apps-autocad-discovery/1.0)"
PATH = re.compile(r"^/NetSWDLD/ODIS/prd/(20[0-9]{2})/ACDMAC/[A-Za-z0-9-]+/SFX/(Autodesk_AutoCAD_([0-9]{4}(?:\\.[0-9]+)?)_macOS\\.dmg)$", re.I)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href", "")
        if href:
            self.links.append(href.replace("&amp;", "&"))


def candidate(url):
    p = urlparse(url)
    if p.scheme != "https" or p.hostname != "efulfillment.autodesk.com":
        return None
    if p.username or p.password or p.port or p.query or p.fragment:
        return None
    m = PATH.fullmatch(unquote(p.path))
    if not m or int(m.group(1)) != int(m.group(3).split(".")[0]):
        return None
    return {"version": m.group(3), "url": url}


def discover(html):
    parser = Links()
    parser.feed(html)
    unique = {}
    for href in parser.links:
        item = candidate(href)
        if item:
            unique[item["url"]] = item
    return sorted(unique.values(), key=lambda x: (tuple(int(i) for i in x["version"].split(".")), x["url"]), reverse=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", default=THREAD, help="Public Autodesk forum thread")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable results")
    args = ap.parse_args()
    if not args.url.startswith("https://forums.autodesk.com/"):
        ap.error("Only the official Autodesk Community forum is permitted")
    with urlopen(Request(args.url, headers={"User-Agent": UA}), timeout=25) as r:
        html = r.read(10_000_000).decode("utf-8", "replace")
    data = discover(html)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for item in data:
            print(item["version"], item["url"])
    if not data:
        ap.exit(2, "No matching public Mac AutoCAD DMG links; page may be paginated or changed.\n")


if __name__ == "__main__":
    main()
