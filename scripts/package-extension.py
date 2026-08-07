"""Validate and zip extension/ into an upload for the Chrome Web Store.

The store rejects an upload for reasons it reports slowly and vaguely — a queued
submission can come back a day later over a description that is eleven characters
too long. Every check here is one of those: cheap to verify locally, expensive to
discover after upload.

The one that is not merely bureaucratic is the localhost check. README.md tells
you to add `http://127.0.0.1/*` to the manifest to test against a dev server and
to remove it before packaging; shipping that pattern hands every extension user a
content script pointed at their own machine.

Run:  venv/bin/python scripts/package-extension.py
Out:  dist/clearbg-extension-<version>.zip
"""
import json
import pathlib
import re
import struct
import sys
import zipfile

SRC = pathlib.Path("extension")
OUT = pathlib.Path("dist")
# Everything else in extension/ ships. README.md is for us, not for users, and
# dotfiles/editor droppings would only pad the upload.
EXCLUDE = {"README.md"}
DESC_MAX = 132  # store limit; the manifest field is truncated in the listing above it
NAME_MAX = 75


def png_size(path):
    """Real pixel dimensions from the IHDR chunk, without decoding the image."""
    return struct.unpack(">II", path.read_bytes()[16:24])


def check(manifest):
    """Return a list of problems that would fail or embarrass an upload."""
    problems = []

    if len(manifest["description"]) > DESC_MAX:
        problems.append(f"description is {len(manifest['description'])} chars, max {DESC_MAX}")
    if len(manifest["name"]) > NAME_MAX:
        problems.append(f"name is {len(manifest['name'])} chars, max {NAME_MAX}")

    version = manifest["version"]
    parts = version.split(".")
    if len(parts) > 4 or not all(p.isdigit() and int(p) <= 65535 for p in parts):
        problems.append(f"version {version!r} must be 1-4 dot-separated integers, each <= 65535")

    # A declared icon whose real size differs is rendered by the browser anyway,
    # blurrily — and the 128 is reused as the store listing icon, where the size
    # must be exact.
    for size, rel in manifest.get("icons", {}).items():
        path = SRC / rel
        if not path.exists():
            problems.append(f"icons: {rel} is declared but missing")
        elif png_size(path) != (int(size), int(size)):
            w, h = png_size(path)
            problems.append(f"icons: {rel} is declared {size}x{size} but is {w}x{h}")

    referenced = [manifest["background"]["service_worker"], manifest["options_ui"]["page"]]
    referenced += [js for cs in manifest.get("content_scripts", []) for js in cs["js"]]
    for rel in referenced:
        if not (SRC / rel).exists():
            problems.append(f"manifest references {rel}, which does not exist")

    dev = re.findall(r"\S*(?:localhost|127\.0\.0\.1)\S*", json.dumps(manifest))
    if dev:
        problems.append(f"dev-only host pattern left in manifest: {', '.join(sorted(set(dev)))}")

    return problems


def main():
    manifest = json.loads((SRC / "manifest.json").read_text())

    problems = check(manifest)
    if problems:
        print("Not packaged:")
        for p in problems:
            print(f"  - {p}")
        return 1

    files = sorted(
        p for p in SRC.rglob("*")
        if p.is_file() and p.name not in EXCLUDE and not p.name.startswith(".")
    )

    OUT.mkdir(exist_ok=True)
    dst = OUT / f"clearbg-extension-{manifest['version']}.zip"
    # Paths are stored relative to extension/ — the store requires manifest.json
    # at the root of the zip, not inside a folder.
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, path.relative_to(SRC))
            print(f"  {path.relative_to(SRC)!s:24} {path.stat().st_size // 1024:4} KB")

    print(f"\n{manifest['name']} {manifest['version']} -> {dst} ({dst.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
