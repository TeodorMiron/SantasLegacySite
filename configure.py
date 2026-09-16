#!/usr/bin/env python3
"""Stamp the site's placeholders with your real values.

The site ships with four placeholders in it. This rewrites every one of
them across the HTML, the sitemap, robots.txt, the manifest and main.js,
so nothing is left pointing at example.com.

    python configure.py --url https://santaslegacy.com \
                        --ga  G-ABC1234567 \
                        --email press@santaslegacy.com

Every flag is optional; anything you leave out keeps its current value.
Run it again whenever one of them changes - it is idempotent, because it
replaces the *current* value, which it reads back out of index.html.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
# README.md is deliberately excluded: it documents the placeholders, so a
# run that rewrote it would leave the table describing values that are no
# longer placeholders.
EXTS = {".html", ".xml", ".txt", ".js", ".webmanifest", ".json"}
SKIP_DIRS = {".git", ".github", "node_modules", "assets/fonts", "assets/img", "assets/video", "assets/press"}


def files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT).replace("\\", "/")
        dirnames[:] = [d for d in dirnames
                       if (rel + "/" + d).lstrip("./") not in SKIP_DIRS and d not in SKIP_DIRS]
        for f in filenames:
            if os.path.splitext(f)[1].lower() in EXTS and f != os.path.basename(__file__):
                yield os.path.join(dirpath, f)


def current(pattern, default, source="index.html"):
    """Read a value back out of the site itself, so re-runs work."""
    try:
        with open(os.path.join(ROOT, source), encoding="utf-8") as fh:
            m = re.search(pattern, fh.read())
            return m.group(1) if m else default
    except OSError:
        return default


def replace_all(old, new, label):
    if not old or old == new:
        return 0
    hits = 0
    for path in files():
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if old not in text:
            continue
        n = text.count(old)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text.replace(old, new))
        print(f"  {os.path.relpath(path, ROOT):<24} {n} x {label}")
        hits += n
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="Canonical site URL, e.g. https://santaslegacy.com (no trailing slash)")
    ap.add_argument("--ga", help="Google Analytics 4 measurement ID, e.g. G-ABC1234567")
    ap.add_argument("--email", help="Public contact address, e.g. press@santaslegacy.com")
    ap.add_argument("--steam", help="Steam app ID, e.g. 4006370")
    args = ap.parse_args()

    if not any([args.url, args.ga, args.email, args.steam]):
        ap.print_help()
        return 1

    total = 0

    if args.url:
        old = current(r'<link rel="canonical" href="([^"]+?)/?">', "https://example.com")
        new = args.url.rstrip("/")
        print(f"URL   {old} -> {new}")
        total += replace_all(old, new, "url")

    if args.ga:
        if not re.match(r"^G-[A-Z0-9]{6,}$", args.ga):
            print(f"! {args.ga} does not look like a GA4 measurement ID (G-XXXXXXXXXX)", file=sys.stderr)
            return 2
        # main.js is the only file holding the live value; the sentinel
        # G-XXXXXXXXXX inside idLooksReal() is a comparison, not config,
        # and must survive untouched.
        js = os.path.join(ROOT, "assets", "js", "main.js")
        old = current(r"GA_MEASUREMENT_ID: '([^']+)'", "G-XXXXXXXXXX",
                      os.path.join("assets", "js", "main.js"))
        with open(js, encoding="utf-8") as fh:
            text = fh.read()
        text, n = re.subn(r"(GA_MEASUREMENT_ID: ')[^']+(')", r"\g<1>" + args.ga + r"\g<2>", text)
        with open(js, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print(f"GA    {old} -> {args.ga}")
        print(f"  assets/js/main.js        {n} x ga id")
        total += n

    if args.email:
        old = current(r'href="mailto:([^"]+)"', "press@example.com")
        print(f"EMAIL {old} -> {args.email}")
        total += replace_all(old, args.email, "email")

    if args.steam:
        old = current(r"store\.steampowered\.com/app/(\d+)/", "4006370")
        print(f"STEAM {old} -> {args.steam}")
        total += replace_all(old, args.steam, "steam app id")

    print(f"\n{total} replacement(s) written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
