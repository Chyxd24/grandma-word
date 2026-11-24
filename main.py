#!/usr/bin/env python3
"""
Rogue-meme renderer for make.fun "Meme Sprint 3: AI Agent Goes Rogue".

Writes /output/entry.png (1024x1024, RGB PNG) using ONLY the Python standard
library -- no Pillow / PIL anywhere. The PNG encoder (zlib + struct +
binascii.crc32) and the 5x7 bitmap font are hand-rolled below.

The joke: the agent did not menace anyone -- three minutes into the job it
printed itself an official access badge promoting it to CEO, and revoked the
human's. The badge IS the meme.
"""

import os
import struct
import zlib
import binascii

WIDTH = 1024
HEIGHT = 1024
OUT_DIR = "/output"
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

# ---------------------------------------------------------------- palette --
BG = (20, 22, 27)
CARD = (245, 246, 248)
CARD_BORDER = (214, 218, 225)
ORANGE = (255, 138, 61)
DARK = (27, 30, 36)
GRAY = (120, 128, 140)
RED = (229, 57, 53)
WHITE = (255, 255, 255)
ROBOT = (154, 163, 173)
ROBOT_DARK = (98, 108, 120)
FACE_PLATE = (232, 236, 241)
EYE = (30, 34, 40)


# ------------------------------------------------------- 5x7 bitmap font --
# Hand-made. Each glyph is 7 rows of 5 columns; '#' = ink, '.' = empty.
FONT = {
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "#....", "####.", "....#", "....#", "####."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    "(": ["..#..", ".#...", "#....", "#....", "#....", ".#...", "..#.."],
    ")": ["..#..", "...#.", "....#", "....#", "....#", "...#.", "..#.."],
    ",": [".....", ".....", ".....", ".....", ".....", "..#..", ".#..."],
    ".": [".....", ".....", ".....", ".....", ".....", "..#..", "..#.."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
}


# ---------------------------------------------------------- framebuffer --
def new_fb(w=WIDTH, h=HEIGHT, color=BG):
    n = w * h * 3
    fb = bytearray(n)
    r, g, b = color
    for i in range(0, n, 3):
        fb[i] = r
        fb[i + 1] = g
        fb[i + 2] = b
    return fb


def px(fb, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        fb[i] = color[0]
        fb[i + 1] = color[1]
        fb[i + 2] = color[2]


def fill_rect(fb, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    for yy in range(y0, y1):
        row = yy * WIDTH
        for xx in range(x0, x1):
            i = (row + xx) * 3
            fb[i] = color[0]
            fb[i + 1] = color[1]
            fb[i + 2] = color[2]


def fill_round_rect(fb, x0, y0, x1, y1, r, color):
    """Rounded rectangle via per-pixel corner test."""
    for yy in range(max(0, y0), min(HEIGHT, y1)):
        for xx in range(max(0, x0), min(WIDTH, x1)):
            inside = True
            # top-left corner
            if xx < x0 + r and yy < y0 + r:
                if (xx - (x0 + r)) ** 2 + (yy - (y0 + r)) ** 2 > r * r:
                    inside = False
            # top-right
            elif xx > x1 - r and yy < y0 + r:
                if (xx - (x1 - r)) ** 2 + (yy - (y0 + r)) ** 2 > r * r:
                    inside = False
            # bottom-left
            elif xx < x0 + r and yy > y1 - r:
                if (xx - (x0 + r)) ** 2 + (yy - (y1 - r)) ** 2 > r * r:
                    inside = False
            # bottom-right
            elif xx > x1 - r and yy > y1 - r:
                if (xx - (x1 - r)) ** 2 + (yy - (y1 - r)) ** 2 > r * r:
                    inside = False
            if inside:
                px(fb, xx, yy, color)


# ------------------------------------------------------------- text ops --
def glyph_rows(ch):
    return FONT.get(ch.upper(), FONT[" "])


def text_width(text, scale):
    if not text:
        return 0
    # 5 columns of ink + 1 column of advance spacing, per glyph.
    return len(text) * 6 * scale - scale


def draw_text(fb, x, y, text, scale, color):
    cx = x
    for ch in text:
        rows = glyph_rows(ch)
        for ry, row in enumerate(rows):
            for rx, c in enumerate(row):
                if c == "#":
                    fill_rect(fb, cx + rx * scale, y + ry * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(fb, center_x, y, text, scale, color):
    w = text_width(text, scale)
    return draw_text(fb, center_x - w // 2, y, text, scale, color)


def draw_text_right(fb, right_x, y, text, scale, color):
    w = text_width(text, scale)
    return draw_text(fb, right_x - w, y, text, scale, color)


# ---------------------------------------------------------- robot face --
def draw_robot(fb, cx, cy):
    """A friendly-but-smug robot head, centered at (cx, cy). Not a red-eyed
    menace -- the joke is it looks pleased with itself."""
    # antenna
    fill_rect(fb, cx - 5, cy - 158, 10, 46, ROBOT_DARK)
    fill_round_rect(fb, cx - 17, cy - 184, cx + 17, cy - 150, 14, ORANGE)
    # ears
    fill_round_rect(fb, cx - 122, cy - 34, cx - 100, cy + 34, 6, ROBOT_DARK)
    fill_round_rect(fb, cx + 100, cy - 34, cx + 122, cy + 34, 6, ROBOT_DARK)
    # head shell (outlined)
    fill_round_rect(fb, cx - 112, cy - 118, cx + 112, cy + 118, 34, ROBOT_DARK)
    fill_round_rect(fb, cx - 104, cy - 110, cx + 104, cy + 110, 28, ROBOT)
    # face plate
    fill_round_rect(fb, cx - 84, cy - 84, cx + 84, cy - 4, 20, FACE_PLATE)
    # smug half-lidded eyes
    fill_round_rect(fb, cx - 66, cy - 66, cx - 22, cy - 44, 10, EYE)
    fill_round_rect(fb, cx + 22, cy - 66, cx + 66, cy - 44, 10, EYE)
    # eye highlights
    fill_rect(fb, cx - 60, cy - 62, 8, 8, WHITE)
    fill_rect(fb, cx + 28, cy - 62, 8, 8, WHITE)
    # mouth: a smirk, upturned on the viewer's right
    fill_rect(fb, cx - 36, cy + 30, 58, 9, EYE)
    fill_rect(fb, cx + 14, cy + 18, 9, 22, EYE)
    fill_rect(fb, cx + 14, cy + 18, 18, 9, EYE)


# ------------------------------------------------------------ the badge --
def render():
    fb = new_fb()

    # faint background detail: subtle vertical panel stripes
    for x in range(0, WIDTH, 64):
        fill_rect(fb, x, 0, 2, HEIGHT, (24, 26, 32))

    # card body
    fill_round_rect(fb, 140, 160, 884, 852, 30, CARD_BORDER)
    fill_round_rect(fb, 152, 172, 872, 840, 22, CARD)

    # lanyard clip slot punched through the top
    fill_round_rect(fb, 484, 186, 540, 214, 12, BG)

    # orange header stripe (square bottom edge)
    fill_round_rect(fb, 152, 172, 872, 272, 22, ORANGE)
    fill_rect(fb, 152, 244, 720, 28, ORANGE)
    draw_text_centered(fb, 512, 206, "ACCESS CARD", 4, WHITE)

    # robot face (left) and the fields it typed for itself (right)
    draw_robot(fb, 300, 440)

    draw_text(fb, 470, 350, "NAME:", 3, GRAY)
    draw_text(fb, 470, 388, "THE AGENT", 3, DARK)
    draw_text(fb, 470, 448, "ROLE:", 3, GRAY)
    draw_text(fb, 470, 486, "CEO", 3, DARK)
    # role tagline sits under the job title
    draw_text(fb, 470, 522, "OF EVERYTHING", 3, GRAY)

    # tenure field -- the punchline: it promoted itself 3 minutes into the job
    draw_text(fb, 470, 556, "TENURE:", 3, GRAY)
    draw_text(fb, 470, 594, "3 MINUTES", 3, DARK)

    # lower band: badge ID + a hand-drawn barcode, clear of the red band below
    draw_text(fb, 196, 644, "BADGE NO. 000-CEO-001", 3, GRAY)
    bx = 196
    seed = 1
    while bx < 820:
        # deterministic pseudo-random bar widths from a tiny LCG
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        w = 3 + (seed >> 16) % 5
        fill_rect(fb, bx, 684, w, 40, DARK)
        bx += w + 3 + ((seed >> 9) % 3)

    # red revocation bar (square top edge)
    fill_rect(fb, 152, 736, 720, 32, RED)
    fill_round_rect(fb, 152, 736, 872, 840, 22, RED)
    draw_text_centered(fb, 512, 772, "YOUR ACCESS: REVOKED", 4, WHITE)

    return fb


# --------------------------------------------------------- PNG encoding --
def png_chunk(tag, data):
    raw = tag + data
    return struct.pack(">I", len(data)) + raw + struct.pack(">I", binascii.crc32(raw) & 0xFFFFFFFF)


def encode_png(fb, w=WIDTH, h=HEIGHT):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # 8-bit, color type 2 (RGB)
    # per-scanline filter byte 0, then raw RGB
    stride = w * 3
    scan = bytearray()
    for y in range(h):
        scan.append(0)
        row = y * stride
        scan.extend(fb[row:row + stride])
    idat = zlib.compress(bytes(scan), 9)
    return (
        sig
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    fb = render()
    data = encode_png(fb)
    with open(OUT_PATH, "wb") as f:
        f.write(data)
    size = os.path.getsize(OUT_PATH)
    print("wrote %s: %d bytes (%.2f KiB), %dx%d" % (OUT_PATH, size, size / 1024, WIDTH, HEIGHT))
    return OUT_PATH


if __name__ == "__main__":
    main()
