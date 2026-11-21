#!/usr/bin/env python3
"""NIMBARA — a travel poster for a place that isn't there.

A floating glass-dune observatory city above a sea of clouds, where the
sun sets twice. Pure Python 3 standard library, no network, deterministic:
the same bytes come out of every run.
"""
import math
import os
import struct
import zlib

W = H = 1024

# ---------------------------------------------------------------- palette
SKY_TOP = (30, 22, 72)        # deep indigo, top of the sky
SKY_MID = (126, 64, 112)      # violet-rose
SKY_HOR = (244, 168, 92)      # amber horizon
SUN1_CORE = (255, 219, 138)   # big low sun, setting
SUN2_CORE = (255, 233, 176)   # small high sun
CLOUD_A = (251, 227, 184)     # pale cream cloud
CLOUD_B = (246, 207, 160)     # peach cloud
CLOUD_C = (232, 180, 143)     # rose cloud
CLOUD_D = (201, 163, 192)     # lavender cloud, lowest
ISLE_TOP = (86, 150, 158)     # glass dune, lit rim
ISLE_BOT = (38, 74, 96)       # glass dune, shadow side
ISLE_UNDER = (26, 50, 70)     # floating underside
SPIRE = (207, 232, 226)       # mirrored spire
SPIRE_SHADE = (120, 168, 178)
GOLD = (255, 205, 110)        # ring and lights
CREAM = (255, 243, 214)       # poster type
INK = (28, 20, 64)           # shadow / birds
FRAME = (255, 243, 214)

buf = bytearray(W * H * 3)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return (int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))


def sky_at(y):
    """Sky colour at row y (before suns and clouds)."""
    if y < 380:
        return mix(SKY_TOP, SKY_MID, y / 380.0)
    t = min(1.0, (y - 380) / 240.0)
    return mix(SKY_MID, SKY_HOR, t)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o] = c[0]
        buf[o + 1] = c[1]
        buf[o + 2] = c[2]


def hline(y, x0, x1, c):
    """Fill a horizontal span on row y (clamped)."""
    if y < 0 or y >= H:
        return
    x0 = max(0, int(x0))
    x1 = min(W - 1, int(x1))
    if x1 < x0:
        return
    o = (y * W + x0) * 3
    n = x1 - x0 + 1
    buf[o:o + 3 * n] = bytes(c) * n


def fill_rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1 + 1)):
        hline(y, x0, x1, c)


def fill_poly(pts, c):
    n = len(pts)
    ys = [p[1] for p in pts]
    for y in range(max(0, min(ys)), min(H - 1, max(ys)) + 1):
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            hline(y, xs[i], xs[i + 1], c)


def fill_ellipse(cx, cy, rx, ry, c):
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        dy = (y - cy) / ry
        dx = rx * math.sqrt(max(0.0, 1.0 - dy * dy))
        hline(y, cx - dx, cx + dx, c)


def fill_ellipse_grad(cx, cy, rx, ry, c_top, c_bot):
    """Ellipse filled with a vertical gradient."""
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        dy = (y - cy) / ry
        dx = rx * math.sqrt(max(0.0, 1.0 - dy * dy))
        t = (y - (cy - ry)) / (2.0 * ry)
        hline(y, cx - dx, cx + dx, mix(c_top, c_bot, t))


def line(x0, y0, x1, y1, c):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        set_px(int(round(lerp(x0, x1, t))), int(round(lerp(y0, y1, t))), c)


def disc(cx, cy, r, c):
    fill_ellipse(cx, cy, r, r, c)


def sun(cx, cy, r, glow, core):
    """A sun with a soft glow blended into the sky behind it."""
    for y in range(max(0, cy - r - glow), min(H, cy + r + glow + 1)):
        for x in range(max(0, cx - r - glow), min(W, cx + r + glow + 1)):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                set_px(x, y, core)
            elif d <= r + glow:
                t = (d - r) / glow
                set_px(x, y, mix(core, sky_at(y), t * t))


# ------------------------------------------------------------------- sky
for y in range(620):
    hline(y, 0, W - 1, sky_at(y))
# sea of cloud below the horizon
for y in range(620, H):
    hline(y, 0, W - 1, mix(SKY_HOR, CLOUD_D, (y - 620) / 404.0))

# two suns: the sun sets twice over Nimbara
sun(648, 552, 92, 150, SUN1_CORE)
sun(322, 318, 44, 90, SUN2_CORE)

# ----------------------------------------------------------------- clouds
# distant cloud bands, rolling toward the horizon
for cx, cy, rx, ry, c in [
        (200, 668, 260, 34, CLOUD_B), (560, 652, 300, 30, CLOUD_A),
        (900, 676, 240, 32, CLOUD_B), (120, 760, 300, 44, CLOUD_C),
        (880, 800, 320, 48, CLOUD_C), (512, 900, 420, 70, CLOUD_D),
        (180, 950, 340, 80, CLOUD_D), (860, 960, 340, 78, CLOUD_D)]:
    fill_ellipse(cx, cy, rx, ry, c)

# ------------------------------------------------------- floating islands
def island(cx, top_y, rx, ry, tip_y, c_top, c_bot, under):
    """A glass dune floating above the clouds: domed top, tapering rock."""
    fill_ellipse_grad(cx, top_y, rx, ry, c_top, c_bot)
    fill_poly([(cx - rx, top_y), (cx + rx, top_y), (cx, tip_y)], under)


# small far islands first
island(148, 792, 150, 52, 892, (96, 152, 158), (44, 78, 98), (30, 54, 74))
island(884, 772, 168, 56, 884, (96, 152, 158), (44, 78, 98), (30, 54, 74))
# the main island, home of the Sunspire
island(512, 700, 330, 108, 918, ISLE_TOP, ISLE_BOT, ISLE_UNDER)

# little spires on the far islands
fill_poly([(128, 792), (140, 792), (134, 716)], SPIRE_SHADE)
fill_poly([(864, 772), (878, 772), (871, 700)], SPIRE_SHADE)
disc(134, 712, 5, GOLD)
disc(871, 696, 5, GOLD)

# ------------------------------------------------------------- the Sunspire
# the landmark: one tall mirrored spire rising from the dune, ringed in gold
fill_poly([(496, 700), (528, 700), (517, 372), (507, 372)], SPIRE)
fill_poly([(507, 372), (517, 372), (513, 700), (508, 700)], SPIRE_SHADE)
# glass dome at the foot of the spire
fill_ellipse(512, 700, 46, 20, SPIRE)
# glowing ring around the spire's upper third
for k in range(160):
    a = 2.0 * math.pi * k / 160.0
    rx, ry = 96, 24
    x = int(512 + rx * math.cos(a))
    y = int(452 + ry * math.sin(a))
    disc(x, y, 3, GOLD)
# star at the tip
for dx, dy in [(0, -14), (0, 14), (-14, 0), (14, 0)]:
    line(512, 366, 512 + dx, 366 + dy, GOLD)
disc(512, 366, 6, (255, 240, 190))

# warm lights along the dune's rim, like windows waking at dusk
for x in (300, 360, 420, 470, 560, 610, 668, 724):
    disc(x, 668 + int(18 * math.sin((x - 512) / 90.0)), 4, GOLD)

# foreground cloud wisps curling past the island's underside
fill_ellipse(300, 940, 260, 46, CLOUD_B)
fill_ellipse(760, 955, 280, 48, CLOUD_B)
fill_ellipse(512, 1000, 420, 60, CLOUD_C)

# ------------------------------------------------------------------- birds
for bx, by, s in [(250, 420, 12), (300, 452, 9), (760, 400, 11),
                  (812, 436, 8), (700, 470, 7)]:
    line(bx - s, by, bx, by - 6, INK)
    line(bx, by - 6, bx + s, by, INK)

# -------------------------------------------------------------------- type
# hand-drawn 5x7 bitmap capitals, scaled up, for the place name
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
}


def draw_text(text, x0, y0, scale, c, shadow=None):
    adv = 6 * scale  # 5 columns + 1 column gap
    if shadow is not None:
        draw_text(text, x0 + 5, y0 + 6, scale, shadow)
    for li, ch in enumerate(text):
        g = GLYPHS[ch]
        for r in range(7):
            for col in range(5):
                if g[r][col] == "1":
                    fill_rect(x0 + li * adv + col * scale, y0 + r * scale,
                              x0 + li * adv + col * scale + scale - 1,
                              y0 + r * scale + scale - 1, c)


NAME = "NIMBARA"
SCALE = 16
name_w = len(NAME) * 6 * SCALE - SCALE
nx = (W - name_w) // 2
ny = 132
draw_text(NAME, nx, ny, SCALE, CREAM, shadow=INK)

# a fine rule under the name, with a diamond at each end
hline(ny + 7 * SCALE + 26, nx, nx + name_w - 1, CREAM)
hline(ny + 7 * SCALE + 29, nx, nx + name_w - 1, CREAM)
for dx, dy in [(0, -7), (0, 7), (-7, 0), (7, 0)]:
    line(nx - 26, ny + 7 * SCALE + 27 + dy, nx - 26 + dx,
         ny + 7 * SCALE + 27, CREAM)
    line(nx + name_w + 25, ny + 7 * SCALE + 27 + dy,
         nx + name_w + 25 + dx, ny + 7 * SCALE + 27, CREAM)

# thin poster frame
for t in range(5):
    hline(28 + t, 28, W - 29, FRAME)
    hline(H - 29 - t, 28, W - 29, FRAME)
    for y in range(28, H - 28):
        set_px(28 + t, y, FRAME)
        set_px(W - 29 - t, y, FRAME)

# --------------------------------------------------------------------- png
def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        o = y * W * 3
        raw += buf[o:o + W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
