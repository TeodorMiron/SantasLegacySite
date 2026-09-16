"""Build the website's image set from the game's marketing captures.

Every source is a lossless PNG shot from the Unity editor; the web needs
a WebP for browsers that take it and a progressive JPEG for the rest, at
two widths (gallery + thumbnail). Re-runnable: it overwrites in place.
"""
import os
from PIL import Image, ImageDraw

SRC = r"D:\Santa'sLegacy"
OUT = r"D:\SantasLegacy-Website\assets\img"

# slug, source path
SHOTS = [
    ("village-operation",   "Screenshots/steam/01_run_the_operation.png"),
    ("elf-inspector",       "Screenshots/steam/02_manage_the_elves.png"),
    ("skill-tree",          "Screenshots/steam/05_make_decisions.png"),
    ("blizzard",            "Screenshots/steam/04_christmas_under_pressure.png"),
    ("reindeer-team",       "Screenshots/steam/03_make_the_gifts.png"),
    ("build-menu",          "Screenshots/07_build_menu.png"),
    ("legacy-prestige",     "Screenshots/09_legacy_prestige.png"),
    ("year-end",            "Screenshots/13_year_result.png"),
    ("sleigh-tree",         "Screenshots/03_sleigh_tree.png"),
    ("village-top",         "Screenshots/05_village_top.png"),
    ("christmas-orders",    "Screenshots/ui/28_christmas_orders.png"),
    ("tree-closeup",        "Screenshots/04_tree_closeup.png"),
]

MINIGAMES = [
    ("mg-cookie-bake",      "Screenshots/14_minigame_cookie_bake.png"),
    ("mg-gift-wrap",        "Screenshots/15_minigame_gift_wrap.png"),
    ("mg-naughty-nice",     "Screenshots/16_minigame_naughty_nice.png"),
    ("mg-reindeer-rhythm",  "Screenshots/17_minigame_reindeer_rhythm.png"),
    ("mg-sleigh-dash",      "Screenshots/18_minigame_sleigh_dash.png"),
    ("mg-pack-sleigh",      "Screenshots/19_minigame_pack_sleigh.png"),
    ("mg-mailroom",         "Screenshots/20_minigame_mailroom.png"),
]

JPEG = dict(quality=82, optimize=True, progressive=True, subsampling=1)
WEBP = dict(quality=80, method=6)


def resized(im, width):
    if im.width <= width:
        return im.copy()
    h = round(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


def emit(im, path_noext, width, jpeg=JPEG, webp=WEBP):
    r = resized(im.convert("RGB"), width)
    r.save(path_noext + ".jpg", "JPEG", **jpeg)
    r.save(path_noext + ".webp", "WEBP", **webp)
    return r.size, os.path.getsize(path_noext + ".jpg"), os.path.getsize(path_noext + ".webp")


def build_set(items, folder_full, folder_thumb, full_w=1600, thumb_w=760):
    total = 0
    for slug, rel in items:
        src = os.path.join(SRC, rel)
        with Image.open(src) as im:
            size, j, w = emit(im, os.path.join(folder_full, slug), full_w)
            _, tj, tw = emit(im, os.path.join(folder_thumb, slug), thumb_w)
        total += j + w + tj + tw
        print(f"  {slug:20} {size[0]}x{size[1]}  jpg {j//1024:4}K  webp {w//1024:4}K  thumb {tw//1024:3}K")
    return total


def star(draw, cx, cy, r_out, r_in, fill, points=5, rot=-90):
    import math
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill)


def build_icon(size, path):
    """A gold star on the game's night-sky navy, with a snow drift.

    Drawn at 8x and downsampled - Pillow has no polygon antialiasing. The
    drift is composited through the rounded-rect mask so it cannot square
    off the bottom corners.
    """
    s = size * 8
    radius = int(s * 0.22)
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=255)

    im = Image.new("RGBA", (s, s), (19, 36, 58, 255))
    d = ImageDraw.Draw(im)
    star(d, s * 0.5, s * 0.40, s * 0.30, s * 0.125, (245, 192, 74, 255))

    drift = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    dd = ImageDraw.Draw(drift)
    dd.rectangle([0, int(s * 0.80), s - 1, s - 1], fill=(240, 246, 252, 255))
    dd.ellipse([int(-s * 0.10), int(s * 0.66), int(s * 0.58), int(s * 0.95)], fill=(240, 246, 252, 255))
    dd.ellipse([int(s * 0.44), int(s * 0.71), int(s * 1.10), int(s * 0.98)], fill=(240, 246, 252, 255))
    im.alpha_composite(drift)
    im.putalpha(mask)

    im = im.resize((size, size), Image.LANCZOS)
    im.save(path, "PNG", optimize=True)
    print(f"  {os.path.basename(path):24} {size}x{size}  {os.path.getsize(path)//1024}K")


def main():
    os.makedirs(os.path.join(OUT, "shots"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "thumbs"), exist_ok=True)
    full = os.path.join(OUT, "shots")
    thumb = os.path.join(OUT, "thumbs")

    print("Hero:")
    with Image.open(os.path.join(SRC, "Screenshots/01_village_hero.png")) as im:
        for w in (2400, 1600, 1000):
            size, j, wb = emit(im, os.path.join(OUT, f"hero-{w}"), w)
            print(f"  hero-{w:<15} {size[0]}x{size[1]}  jpg {j//1024:4}K  webp {wb//1024:4}K")

    print("Screenshots:")
    a = build_set(SHOTS, full, thumb)
    print("Minigames:")
    b = build_set(MINIGAMES, full, thumb)

    print("Video poster:")
    with Image.open(os.path.join(SRC, "Recordings/SantasLegacy_Trailer_poster.png")) as im:
        size, j, wb = emit(im, os.path.join(OUT, "trailer-poster"), 1280)
        print(f"  trailer-poster        {size[0]}x{size[1]}  jpg {j//1024:4}K  webp {wb//1024:4}K")

    print("Update banner:")
    with Image.open(os.path.join(SRC, "Screenshots/steam_header_1600x900.png")) as im:
        size, j, wb = emit(im, os.path.join(OUT, "winter-update"), 1200)
        print(f"  winter-update         {size[0]}x{size[1]}  jpg {j//1024:4}K  webp {wb//1024:4}K")

    # Open Graph / Twitter card: 1200x630, cropped from the trailer's title card
    print("Social card:")
    with Image.open(os.path.join(SRC, "Recordings/SantasLegacy_Trailer_poster.png")) as im:
        im = im.convert("RGB")
        target = 1200 / 630
        w, h = im.size
        if w / h > target:            # too wide - crop the sides
            nw = int(h * target)
            im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:                          # too tall - crop bottom-weighted
            nh = int(w / target)
            top = int((h - nh) * 0.35)
            im = im.crop((0, top, w, top + nh))
        im = im.resize((1200, 630), Image.LANCZOS)
        im.save(os.path.join(OUT, "og-image.jpg"), "JPEG", **JPEG)
        print(f"  og-image.jpg          1200x630  {os.path.getsize(os.path.join(OUT,'og-image.jpg'))//1024}K")

    print("Icons:")
    for sz, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"),
                     (512, "icon-512.png"), (32, "favicon-32.png"), (16, "favicon-16.png")]:
        build_icon(sz, os.path.join(OUT, name))

    print(f"\nscreenshots total: {(a+b)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
