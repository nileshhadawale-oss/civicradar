"""Generate the CivicRadar "Pin + Ripple" icon set from the approved source art.

Source of truth: assets/icon-source-pin-ripple.png — the approved, AI-generated
"Pin + Ripple" artwork (a white map pin over cyan radar ripples on an indigo
#6366f1 rounded square, on a white page background).

This script derives the full PWA icon set from that single source so the icons
stay reproducible:

  1. Crop the source to a tight square around the indigo rounded card.
  2. Remove the exterior white page background (flood fill from the corners) so
     full-bleed icons have clean transparent corners.
  3. Downscale with LANCZOS for crisp anti-aliasing.

Outputs (assets/):
  icon-192.png            192x192  full-bleed (transparent rounded corners)
  icon-512.png            512x512  full-bleed
  icon-maskable-512.png   512x512  art @~80% on solid indigo (Android safe-zone)
  apple-touch-icon.png    180x180  full-bleed
  favicon-32.png          32x32

If the source art is missing, the script aborts without touching existing icons.
"""
import os
import sys
from PIL import Image, ImageChops, ImageDraw

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
SOURCE = os.path.join(ASSETS, "icon-source-pin-ripple.png")

# Brand indigo (#6366f1). Used as the documented maskable background; the actual
# fill color is sampled from the source so the maskable card is seamless.
BRAND_INDIGO = (99, 102, 241)


def find_card_bbox(rgb):
    """Bounding box of the indigo card (everything that isn't the white page)."""
    white = Image.new("RGB", rgb.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, white).convert("L")
    mask = diff.point(lambda p: 255 if p > 18 else 0)
    return mask.getbbox()


def square_bbox(bbox, size, pad_frac=0.0):
    """Expand a bbox to a centered square (optionally padded), clamped to image."""
    l, t, r, b = bbox
    w, h = r - l, b - t
    side = max(w, h)
    side = int(side * (1 + pad_frac))
    cx, cy = (l + r) / 2, (t + b) / 2
    half = side / 2
    L = int(round(cx - half)); T = int(round(cy - half))
    R = L + side; B = T + side
    iw, ih = size
    # Shift back inside the image if we ran past an edge.
    if L < 0: R -= L; L = 0
    if T < 0: B -= T; T = 0
    if R > iw: L -= (R - iw); R = iw
    if B > ih: T -= (B - ih); B = ih
    return (max(L, 0), max(T, 0), min(R, iw), min(B, ih))


def remove_page_background(card_rgb):
    """Return RGBA of the card with the exterior white page made transparent.

    Flood-fills inward from each corner so only background white connected to the
    border is removed — the white pin (interior) is preserved.
    """
    SENT = (255, 0, 255)  # sentinel: a color that cannot occur in the artwork
    work = card_rgb.copy()
    w, h = work.size
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(work, xy, SENT, thresh=72)

    out = card_rgb.convert("RGBA")
    src_px = work.load()
    out_px = out.load()
    for y in range(h):
        for x in range(w):
            if src_px[x, y] == SENT:
                r, g, b, _ = out_px[x, y]
                out_px[x, y] = (r, g, b, 0)
    return out


def sample_card_indigo(card_rgb):
    """Median-ish indigo sampled from a clean strip near the top of the card."""
    w, h = card_rgb.size
    px = card_rgb.load()
    ys = range(int(h * 0.10), int(h * 0.18))
    xs = range(int(w * 0.30), int(w * 0.70))
    rs = gs = bs = n = 0
    for y in ys:
        for x in xs:
            r, g, b = px[x, y][:3]
            # Skip anything too light (stray ripple/pin antialiasing).
            if min(r, g, b) > 200:
                continue
            rs += r; gs += g; bs += b; n += 1
    if not n:
        return BRAND_INDIGO
    return (rs // n, gs // n, bs // n)


def downscale(img, size):
    return img.resize((size, size), Image.LANCZOS)


def main():
    if not os.path.isfile(SOURCE):
        print("ERROR: source art not found:", SOURCE, file=sys.stderr)
        return 1

    src = Image.open(SOURCE).convert("RGB")
    bbox = find_card_bbox(src)
    if not bbox:
        print("ERROR: could not locate the icon card in the source.", file=sys.stderr)
        return 1

    sq = square_bbox(bbox, src.size)
    card = src.crop(sq)                       # tight square crop of the indigo card

    indigo = sample_card_indigo(card)
    bleed = remove_page_background(card)       # transparent page corners (full-bleed)

    def save(img, name):
        path = os.path.join(ASSETS, name)
        img.save(path, "PNG")
        print("wrote", path, img.size)

    save(downscale(bleed, 192), "icon-192.png")
    save(downscale(bleed, 512), "icon-512.png")
    save(downscale(bleed, 180), "apple-touch-icon.png")
    save(downscale(bleed, 32), "favicon-32.png")

    # Maskable: solid indigo background with the art scaled to ~80% (safe zone),
    # so Android's circular/rounded crop never clips the pin. The bg uses the
    # color sampled from the card so the rounded edge is seamless.
    M = 512
    mask = Image.new("RGBA", (M, M), indigo + (255,))
    inner = downscale(bleed, int(M * 0.80))
    off = (M - inner.width) // 2
    mask.alpha_composite(inner, (off, off))
    save(mask, "icon-maskable-512.png")

    print("source indigo sampled as", indigo, "(brand #6366f1 =", BRAND_INDIGO, ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
