#!/usr/bin/env python3
"""make.fun bounty entry: Sum up 23 November's world news in one image.

The program draws a 1024x1024 newspaper front page for Monday
23 November 2026, entirely with code (Python standard library only:
no network, no fonts, no image files).  It writes the result to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png when set).

Stories (all first reported, or with their key development, on
23 Nov 2026, verified from news search):
  1. COP31 climate talks collapse: the UN summit ends with no deal
     after the EU and others reject any pact without language on a
     fossil-fuel phase-out. (The Hindu + 6 outlets, Al Jazeera.)
  2. NATO holds an emergency North Atlantic Council meeting today
     in Brussels over Russian missiles in Poland; Polish prosecutors
     confirmed on Sunday that all three objects were Russian Kh-101
     cruise missiles. (NATO / Polish prosecutors via AP, Reuters.)
  3. Tankers ablaze in the Strait of Hormuz: two more tankers caught
     fire on Sunday after hitting naval mines; shipping attacks are
     at their highest level since the war began. (AP, UKMTO, IRNA.)
  4. Democrats win their largest House majority since 1992,
     claiming a 258th seat in North Carolina. (Al Jazeera.)
  5. Asian markets tumble on AI-bubble fears: the Kospi falls more
     than 3% on Monday; Taiwan shares are down 17.5% in a week and
     its regulator bans short-selling at or below the flat price
     from today. (Al Jazeera, Dawn/IQAir, SimpleLife.)
  Also noted: 128 states agree to pursue international rules on
  killer robots by 2028 (UN conference).

Determinism: fixed palette, fixed layout, fixed zlib level, no clock,
no randomness, no I/O besides the single output file, so two runs
write byte-identical files.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 226)   # cream newsprint
INK = (18, 18, 18)        # near-black ink
RED = (192, 57, 43)       # masthead red
WHITE = (255, 255, 255)
TINT = (233, 225, 205)    # icon box tint
GOLD = (232, 178, 60)     # highlight gold
NAVY = (27, 35, 64)       # deep navy
TEAL = (16, 58, 72)       # hero night sky
TEAL_DARK = (11, 42, 54)  # hero ground strip
SEA = (52, 112, 180)      # globe ocean
LAND = (84, 148, 88)      # globe land
SMOKE = (196, 196, 190)   # smoke grey
FLAME = (255, 176, 32)    # flame orange
STEEL = (46, 95, 163)     # chart blue

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 integers, one per row; bit 4 (16) is the leftmost pixel.
_FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '"': (10, 10, 0, 0, 0, 0, 0),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "$": (4, 15, 20, 14, 5, 30, 4),
    "#": (10, 10, 31, 10, 31, 10, 10),
    "*": (0, 4, 21, 14, 21, 4, 0),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "_": (0, 0, 0, 0, 0, 0, 31),
}


class Page:
    """A plain RGB canvas with a few drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        self.px[:] = bytes(color) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.w)
        y1 = min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def frame(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, x, y, length, color, t=1):
        self.rect(x, y, length, t, color)

    def vline(self, x, y, length, color, t=1):
        self.rect(x, y, t, length, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line with a square brush of side t."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r_outer, r_inner, color, bg):
        """A hollow ring: outer disc in color, inner disc in bg."""
        self.disc(cx, cy, r_outer, color)
        self.disc(cx, cy, r_inner, bg)

    # ------------------------------------------------------------ text
    def text_width(self, s, scale):
        s = s.upper()
        return max(0, len(s) * 6 * scale - scale)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = _FONT.get(ch, _FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (16 >> col):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        return self.text(cx - self.text_width(s, scale) // 2, y, s, scale, color)

    def text_right(self, rx, y, s, scale, color):
        return self.text(rx - self.text_width(s, scale), y, s, scale, color)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns a list of lines."""
        words = s.upper().split(" ")
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def encode_png(page):
    """Encode the page as a deterministic PNG (RGB, filter 0)."""
    raw = bytearray()
    row_bytes = page.w * 3
    for y in range(page.h):
        raw.append(0)
        raw += page.px[y * row_bytes:(y + 1) * row_bytes]
    ihdr = struct.pack(">IIBBBBB", page.w, page.h, 8, 2, 0, 0, 0)

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


# ---------------------------------------------------------------- layout
def masthead(p):
    p.frame(8, 8, W - 16, H - 16, INK, 3)
    p.frame(16, 16, W - 32, H - 32, INK, 1)
    p.text_center(W // 2, 34, "THE WORLD TODAY", 7, INK)
    p.rect(32, 132, W - 64, 6, RED)
    p.text(32, 152, "MONDAY, 23 NOVEMBER 2026", 3, INK)
    p.text_right(W - 32, 152, "FIVE STORIES - ONE DAY", 3, RED)
    p.hline(32, 182, W - 64, INK, 2)


def hero(p):
    """A cracked globe under a night sky, with a NO DEAL stamp."""
    x0, y0, x1, y1 = 32, 196, W - 32, 446
    p.rect(x0, y0, x1 - x0, y1 - y0, TEAL)
    # A few fixed stars.
    for sx, sy in ((120, 220), (200, 252), (520, 214), (600, 240),
                   (880, 214), (940, 262), (760, 206), (60, 300)):
        p.rect(sx, sy, 3, 3, WHITE)
    # Dark ground strip.
    p.rect(x0, y1 - 26, x1 - x0, 26, TEAL_DARK)
    # The globe, centre-left.
    gx, gy, gr = 330, 325, 92
    p.disc(gx, gy, gr, SEA)
    for lx, ly, lr in ((300, 300, 26), (360, 340, 20), (315, 360, 16),
                       (375, 295, 12)):
        p.disc(lx, ly, lr, LAND)
    # The crack: a jagged line across the globe, with two branches.
    crack = [(255, 245), (295, 280), (278, 315), (320, 340),
             (305, 375), (350, 405)]
    for (ax, ay), (bx, by) in zip(crack, crack[1:]):
        p.line(ax, ay, bx, by, INK, 5)
    p.line(295, 280, 330, 265, INK, 4)
    p.line(330, 265, 360, 275, INK, 4)
    p.line(320, 340, 355, 330, INK, 3)
    # Smoke rising from the crack (kept inside the panel).
    for sx, sy, sr in ((290, 224, 13), (330, 211, 10), (368, 226, 9)):
        p.disc(sx, sy, sr, SMOKE)
    # NO DEAL stamp, right side.
    p.rect(690, 280, 240, 84, RED)
    p.frame(690, 280, 240, 84, WHITE, 3)
    p.text_center(810, 302, "NO DEAL", 5, WHITE)
    p.frame(x0, y0, x1 - x0, y1 - y0, INK, 2)
    # Headline band.
    p.rect(x0, y1, x1 - x0, 108, INK)
    p.text_center(W // 2, y1 + 14, "COP31 COLLAPSES", 6, WHITE)
    p.text_center(W // 2, y1 + 62,
                  "CLIMATE TALKS FAIL - NO DEAL ON FOSSIL FUELS",
                  2, WHITE)
    p.text_center(W // 2, y1 + 84,
                  "ALSO: 128 STATES AGREE KILLER-ROBOT RULES BY 2028",
                  2, GOLD)


# ------------------------------------------------------------ story icons
def icon_nato(p, x, y):
    """Compass star in a ring: the alliance meets."""
    cx, cy = x + 55, y + 55
    p.disc(cx, cy, 46, INK)
    p.disc(cx, cy, 40, TINT)
    for dx, dy in ((0, -38), (0, 38), (-38, 0), (38, 0)):
        p.line(cx, cy, cx + dx, cy + dy, INK, 5)
    for dx, dy in ((-24, -24), (24, -24), (-24, 24), (24, 24)):
        p.line(cx, cy, cx + dx, cy + dy, INK, 4)
    p.disc(cx, cy, 7, RED)


def icon_tanker(p, x, y):
    """A tanker with flames above the funnel: Hormuz ablaze."""
    # Water.
    p.hline(x + 6, y + 88, 98, STEEL, 3)
    p.hline(x + 6, y + 96, 98, STEEL, 3)
    # Flames above the funnel.
    p.disc(x + 34, y + 40, 6, FLAME)
    p.disc(x + 26, y + 44, 4, FLAME)
    p.disc(x + 42, y + 44, 4, FLAME)
    # Funnel, cargo, bridge, hull.
    p.rect(x + 28, y + 48, 12, 14, RED)
    p.rect(x + 46, y + 50, 10, 12, STEEL)
    p.rect(x + 58, y + 54, 10, 8, STEEL)
    p.rect(x + 70, y + 40, 18, 22, INK)
    p.rect(x + 74, y + 46, 10, 6, WHITE)
    p.rect(x + 8, y + 62, 92, 18, INK)


def icon_capitol(p, x, y):
    """A domed capitol: the House majority."""
    # Dome (upper half of a disc) with a flag.
    p.disc(x + 55, y + 46, 20, INK)
    p.rect(x + 33, y + 46, 44, 22, TINT)
    p.vline(x + 55, y + 12, 16, INK, 3)
    p.rect(x + 58, y + 12, 16, 9, RED)
    # Entablature, columns, base, steps.
    p.rect(x + 18, y + 46, 74, 6, INK)
    for px in (26, 51, 76):
        p.vline(x + px, y + 52, 32, INK, 5)
    p.rect(x + 14, y + 84, 82, 6, INK)
    p.rect(x + 10, y + 90, 90, 5, INK)


def icon_chart_down(p, x, y):
    """Falling bars with a down arrow: markets tumble."""
    p.hline(x + 10, y + 90, 90, INK, 3)
    p.vline(x + 10, y + 20, 70, INK, 3)
    p.rect(x + 22, y + 34, 16, 56, STEEL)
    p.rect(x + 44, y + 50, 16, 40, STEEL)
    p.rect(x + 66, y + 66, 16, 24, STEEL)
    p.line(x + 20, y + 28, x + 92, y + 74, RED, 4)
    p.line(x + 92, y + 74, x + 78, y + 72, RED, 4)
    p.line(x + 92, y + 74, x + 88, y + 60, RED, 4)


def story(p, x, y, w, kicker, headline, sub, icon):
    p.rect(x, y, w, 3, RED)
    p.rect(x, y + 10, 110, 110, TINT)
    p.frame(x, y + 10, 110, 110, INK, 1)
    icon(p, x, y + 10)
    tx = x + 124
    tw = w - 124
    p.text(tx, y + 12, kicker, 2, RED)
    ly = y + 36
    for line in p.wrap(headline, 3, tw)[:3]:
        p.text(tx, ly, line, 3, INK)
        ly += 22
    for line in p.wrap(sub, 2, tw)[:2]:
        p.text(tx, ly + 2, line, 2, INK)
        ly += 15


def grid(p):
    p.text(32, 566, "THE REST OF THE DAY", 3, INK)
    p.hline(32, 594, W - 64, INK, 2)
    stories = [
        ("BRUSSELS", "NATO MEETS TODAY OVER MISSILES IN POLAND",
         "PROSECUTORS: ALL THREE WERE RUSSIAN KH-101S",
         icon_nato),
        ("HORMUZ", "TANKERS ABLAZE IN THE STRAIT OF HORMUZ",
         "TWO MORE HIT MINES SUNDAY; ATTACKS AT RECORD LEVEL",
         icon_tanker),
        ("WASHINGTON", "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992",
         "258TH SEAT CALLED IN NORTH CAROLINA",
         icon_capitol),
        ("MARKETS", "ASIAN MARKETS TUMBLE ON AI-BUBBLE FEARS",
         "KOSPI -3%; TAIWAN -17.5% IN A WEEK",
         icon_chart_down),
    ]
    positions = [(32, 606), (528, 606), (32, 796), (528, 796)]
    for (sx, sy), (kicker, headline, sub, icon) in zip(positions, stories):
        story(p, sx, sy, 464, kicker, headline, sub, icon)


def footer(p):
    p.hline(32, 978, W - 64, INK, 2)
    p.text_center(W // 2, 988,
                  "SOURCES: THE HINDU, AL JAZEERA, AP, REUTERS - 23 NOV 2026",
                  2, INK)


def build():
    p = Page(W, H, PAPER)
    masthead(p)
    hero(p)
    grid(p)
    footer(p)
    return p


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
