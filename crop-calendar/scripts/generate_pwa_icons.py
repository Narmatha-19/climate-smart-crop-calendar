"""
Generates the PWA app icons (static/icons/) from the same green/leaf
branding already used in static/css/style.css (--green-700, --green-500),
so the installed app icon matches the in-app sidebar mark instead of
introducing a new, unrelated visual identity. Run once; re-run only if
the brand colors change.
"""

import math
import os

from PIL import Image, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "icons")
os.makedirs(OUT_DIR, exist_ok=True)

GREEN_DARK = (18, 56, 34)     # --green-900
GREEN_LIGHT = (76, 175, 80)   # --green-400
WHITE = (255, 255, 255)


def draw_leaf_icon(size, corner_radius_ratio=0.22, maskable=False):
    scale = 4  # supersample for smooth edges, then downscale
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background: rounded square (or full-bleed square for maskable icons,
    # since Android applies its own adaptive-icon mask on top).
    radius = 0 if maskable else int(s * corner_radius_ratio)
    for y in range(s):
        t = y / s
        r = int(GREEN_DARK[0] + (GREEN_LIGHT[0] - GREEN_DARK[0]) * t)
        g = int(GREEN_DARK[1] + (GREEN_LIGHT[1] - GREEN_DARK[1]) * t)
        b = int(GREEN_DARK[2] + (GREEN_LIGHT[2] - GREEN_DARK[2]) * t)
        draw.line([(0, y), (s, y)], fill=(r, g, b, 255))

    mask = Image.new("L", (s, s), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=255)
    bg = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    bg.paste(img, (0, 0), mask)
    img = bg
    draw = ImageDraw.Draw(img)

    # Leaf blade: the intersection of two overlapping circles (a "vesica"
    # shape) - pointed at both ends, unlike a plain ellipse which reads as
    # a pill/eye rather than a leaf. Before rotation the blade's long axis
    # (tip to tip) is horizontal.
    from PIL import ImageChops

    inset = 0.30 if maskable else 0.24
    cx, cy = s / 2, s / 2
    span = s * (1 - 2 * inset)
    r = span * 0.62
    offset = r * 0.78

    circle_a = Image.new("L", (s, s), 0)
    ImageDraw.Draw(circle_a).ellipse(
        [cx - r, cy - offset - r, cx + r, cy - offset + r], fill=255
    )
    circle_b = Image.new("L", (s, s), 0)
    ImageDraw.Draw(circle_b).ellipse(
        [cx - r, cy + offset - r, cx + r, cy + offset + r], fill=255
    )
    blade_mask = ImageChops.multiply(circle_a, circle_b)

    # White fill for the blade
    leaf = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    leaf.paste(Image.new("RGBA", (s, s), WHITE + (255,)), (0, 0), blade_mask)

    # Veins drawn generously in the blade's natural (horizontal) orientation,
    # then clipped through blade_mask - guarantees nothing spills outside
    # the leaf regardless of the exact vesica geometry above.
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
    draw = ImageDraw.Draw(img)

    return img.resize((size, size), Image.LANCZOS)


sizes = {
    "icon-192.png": (192, False),
    "icon-512.png": (512, False),
    "icon-maskable-512.png": (512, True),
    "apple-touch-icon.png": (180, False),
}

for filename, (size, maskable) in sizes.items():
    icon = draw_leaf_icon(size, maskable=maskable)
    icon.save(os.path.join(OUT_DIR, filename))
    print(f"Saved {filename} ({size}x{size}{', maskable' if maskable else ''})")

print("\nDone:", OUT_DIR)
