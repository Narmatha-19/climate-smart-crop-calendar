"""
Generates the Android launcher icons (mipmap-*dpi/) from the same leaf
design used for the PWA icons (crop-calendar/scripts/generate_pwa_icons.py),
so the installed .apk shows the real app icon instead of Capacitor's
default placeholder. Run once; re-run only if the brand colors change.
"""

import math
import os

from PIL import Image, ImageDraw, ImageChops

RES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "android", "app", "src", "main", "res")

GREEN_DARK = (18, 56, 34)
GREEN_LIGHT = (76, 175, 80)
WHITE = (255, 255, 255)

# Legacy square launcher icon size, and the larger adaptive-icon foreground
# canvas size (which needs extra inset padding - Android's mask crops the
# outer edges), per density bucket.
DENSITIES = {
    "mdpi": (48, 108),
    "hdpi": (72, 162),
    "xhdpi": (96, 216),
    "xxhdpi": (144, 324),
    "xxxhdpi": (192, 432),
}


def draw_leaf_icon(size, maskable=False, corner_radius_ratio=0.22):
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = 0 if maskable else int(s * corner_radius_ratio)
    for y in range(s):
        t = y / s
        r = int(GREEN_DARK[0] + (GREEN_LIGHT[0] - GREEN_DARK[0]) * t)
        g = int(GREEN_DARK[1] + (GREEN_LIGHT[1] - GREEN_DARK[1]) * t)
        b = int(GREEN_DARK[2] + (GREEN_LIGHT[2] - GREEN_DARK[2]) * t)
        draw.line([(0, y), (s, y)], fill=(r, g, b, 255))

    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=255)
    bg = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    bg.paste(img, (0, 0), mask)
    img = bg

    inset = 0.30 if maskable else 0.24
    cx, cy = s / 2, s / 2
    span = s * (1 - 2 * inset)
    r = span * 0.62
    offset = r * 0.78

    circle_a = Image.new("L", (s, s), 0)
    ImageDraw.Draw(circle_a).ellipse([cx - r, cy - offset - r, cx + r, cy - offset + r], fill=255)
    circle_b = Image.new("L", (s, s), 0)
    ImageDraw.Draw(circle_b).ellipse([cx - r, cy + offset - r, cx + r, cy + offset + r], fill=255)
    blade_mask = ImageChops.multiply(circle_a, circle_b)

    leaf = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    leaf.paste(Image.new("RGBA", (s, s), WHITE + (255,)), (0, 0), blade_mask)

    veins = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(veins)
    tip_half_len = math.sqrt(max(r * r - offset * offset, 1))
    vein_w = max(2, int(s * 0.011))
    vdraw.line([(cx - tip_half_len, cy), (cx + tip_half_len, cy)], fill=GREEN_DARK, width=vein_w)
    side_len = (r - offset) * 1.6
    side_w = max(1, int(s * 0.006))
    for t in (-0.32, 0.0, 0.34):
        mx = cx + tip_half_len * t
        for sign in (-1, 1):
            vdraw.line([(mx, cy), (mx + tip_half_len * 0.12, cy + side_len * sign)], fill=GREEN_DARK, width=side_w)
    veins_clipped = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    veins_clipped.paste(veins, (0, 0), blade_mask)
    leaf.alpha_composite(veins_clipped)

    leaf = leaf.rotate(-45, center=(cx, cy), resample=Image.BICUBIC)
    img.alpha_composite(leaf)

    return img.resize((size, size), Image.LANCZOS)


for density, (legacy_size, fg_size) in DENSITIES.items():
    out_dir = os.path.join(RES_DIR, f"mipmap-{density}")
    if not os.path.isdir(out_dir):
        print(f"skip {density}: {out_dir} not found")
        continue

    legacy_icon = draw_leaf_icon(legacy_size, maskable=False)
    legacy_icon.save(os.path.join(out_dir, "ic_launcher.png"))
    legacy_icon.save(os.path.join(out_dir, "ic_launcher_round.png"))

    fg_icon = draw_leaf_icon(fg_size, maskable=True)
    fg_icon.save(os.path.join(out_dir, "ic_launcher_foreground.png"))

    print(f"{density}: wrote ic_launcher.png/ic_launcher_round.png ({legacy_size}px), "
          f"ic_launcher_foreground.png ({fg_size}px)")

print("\nDone.")
