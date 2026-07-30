"""Regenerate static/img/thumbs/ — the demo thumbnails on the homepage tool grid.

Every tool card leads with its own result image. Those images already exist for
the tool pages, but at page-hero size (up to 900px, ~2.2 MB across the set) for a
slot that renders about 230px wide. Serving the originals put 2.4 MB on the
landing page, competing with the AI model warm-up for the same bandwidth.

So each one is centre-cropped to the card's 4:3 aspect and fitted to 480×360 —
exactly the pixels the card displays at 2x, rather than pixels `object-cover`
would throw away. That is where the ~71% saving comes from; quality is unchanged
at the size it is actually shown.

Sources come from TOOL_NAV's `demo` / `demo_before` keys, so adding artwork to a
tool there and re-running this is all that is needed. Transparency is preserved
(several cut-out demos rely on it) and the animated GIF becomes an animated WebP.

Run:  venv/bin/python scripts/make-tool-thumbs.py
"""
import os
import pathlib
import subprocess
import sys

import django
from PIL import Image, ImageOps

SRC = pathlib.Path("static/img")
OUT = SRC / "thumbs"
BOX = (480, 360)  # the card slot is aspect-[4/3]; this is the 2x asset
QUALITY = 76
# Crop slightly above centre: these are mostly photos of people and products,
# where the subject sits high and a true centre crop cuts off heads.
CENTERING = (0.5, 0.4)


def thumb_name(path):
    """'img/demo-x.gif' -> 'demo-x.webp'. Mirrors thumb_path() in context_processors."""
    return pathlib.Path(path).stem + ".webp"


def main():
    sys.path.insert(0, ".")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()
    from remover.context_processors import TOOL_NAV

    OUT.mkdir(parents=True, exist_ok=True)
    sources = sorted(
        {t[k].split("/", 1)[1] for t in TOOL_NAV for k in ("demo", "demo_before") if t.get(k)}
    )

    total_in = total_out = 0
    for name in sources:
        src, dst = SRC / name, OUT / thumb_name(name)
        if name.endswith(".gif"):
            # Animated WebP keeps the motion at a fraction of a re-palettised GIF.
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                 "-vf", f"scale={BOX[0]}:{BOX[1]}:force_original_aspect_ratio=increase,"
                        f"crop={BOX[0]}:{BOX[1]}",
                 "-c:v", "libwebp", "-lossless", "0", "-q:v", "70", "-loop", "0", str(dst)],
                check=True,
            )
        else:
            im = Image.open(src)
            has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
            im = im.convert("RGBA" if has_alpha else "RGB")
            # Never upscale: a few sources are already smaller than the box.
            w = min(BOX[0], im.width)
            im = ImageOps.fit(im, (w, round(w * BOX[1] / BOX[0])), Image.LANCZOS,
                              centering=CENTERING)
            im.save(dst, "WEBP", quality=QUALITY, method=6)
        total_in += src.stat().st_size
        total_out += dst.stat().st_size
        print(f"{name:32} {src.stat().st_size // 1024:4} KB -> {dst.name:32} "
              f"{dst.stat().st_size // 1024:3} KB")

    print(f"\n{len(sources)} thumbnails: {total_in / 1024:.0f} KB -> {total_out / 1024:.0f} KB "
          f"({100 - total_out * 100 / total_in:.0f}% smaller)")


if __name__ == "__main__":
    main()
