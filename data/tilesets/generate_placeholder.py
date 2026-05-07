#!/usr/bin/env python3
"""Generate a minimal placeholder tileset PNG so the textured render
path has something to draw before real Kenney art is dropped in.

Layout: 8 tiles in a single row, 32x32 pixels each, atlas indexed
left-to-right with `atlas_index = tile_id - 1` (TileId 0 is "empty").

Tile order matches src/world/map.rs::tile_color (and the comment block
above it):

    1  grass    (passable)
    2  stone wall (solid)
    3  water    (solid)
    4  path / dirt (passable)
    5  tree     (solid)
    6  wood floor (passable)
    7  cobble / dark stone (passable - decorative)
    8  unknown / magenta debug tile

Each tile has a base color matching the previous draw_rectangle palette
plus a tiny per-tile pixel pattern so they look like art instead of
flat blocks. Real art arrives later by replacing terrain.png with a
properly arranged Kenney pack image (or any other 32x32-tile sheet).
"""

from PIL import Image, ImageDraw

TILE = 32
COLS = 8
W, H = TILE * COLS, TILE

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)


def cell(i):
    return (i * TILE, 0, (i + 1) * TILE - 1, TILE - 1)


def fill(i, color):
    x0, y0, x1, y1 = cell(i)
    d.rectangle([x0, y0, x1, y1], fill=color)


def darker(c, amount=0.7):
    return tuple(int(v * amount) for v in c[:3]) + (c[3],)


def lighter(c, amount=1.25):
    return tuple(min(255, int(v * amount)) for v in c[:3]) + (c[3],)


grass = (87, 140, 76, 255)
fill(0, grass)
for px, py in [(4, 6), (10, 18), (18, 4), (22, 22), (28, 12), (14, 28), (6, 24)]:
    d.point((px, py), fill=darker(grass, 0.7))
    d.point((px + 1, py), fill=darker(grass, 0.7))


stone = (115, 107, 102, 255)
fill(1, stone)
mortar = darker(stone, 0.55)
for y in (10, 21):
    d.line([(TILE * 1, y), (TILE * 2 - 1, y)], fill=mortar)
for x in (TILE * 1 + 8, TILE * 1 + 24):
    d.line([(x, 0), (x, 9)], fill=mortar)
for x in (TILE * 1 + 16,):
    d.line([(x, 11), (x, 20)], fill=mortar)
for x in (TILE * 1 + 8, TILE * 1 + 24):
    d.line([(x, 22), (x, 31)], fill=mortar)


water = (51, 102, 166, 255)
fill(2, water)
wave = lighter(water, 1.4)
for y in (8, 18, 26):
    for x_off in range(2, 30, 8):
        d.line([(TILE * 2 + x_off, y), (TILE * 2 + x_off + 4, y)], fill=wave)


dirt = (158, 143, 102, 255)
fill(3, dirt)
for px, py in [(6, 8), (14, 14), (22, 6), (26, 24), (10, 28), (18, 22)]:
    d.point((TILE * 3 + px, py), fill=darker(dirt, 0.7))
    d.point((TILE * 3 + px + 1, py + 1), fill=darker(dirt, 0.7))


tree_bg = (66, 96, 60, 255)
tree_fg = (46, 92, 48, 255)
trunk = (76, 56, 38, 255)
fill(4, tree_bg)
d.ellipse([TILE * 4 + 5, 3, TILE * 4 + 26, 24], fill=tree_fg)
d.rectangle([TILE * 4 + 14, 22, TILE * 4 + 17, 30], fill=trunk)


wood = (140, 102, 66, 255)
fill(5, wood)
plank_line = darker(wood, 0.65)
for y in (10, 21):
    d.line([(TILE * 5, y), (TILE * 6 - 1, y)], fill=plank_line)
for x in (TILE * 5 + 12, TILE * 5 + 24):
    d.line([(x, 0), (x, 9)], fill=plank_line)
for x in (TILE * 5 + 6, TILE * 5 + 18, TILE * 5 + 28):
    d.line([(x, 11), (x, 20)], fill=plank_line)
for x in (TILE * 5 + 8, TILE * 5 + 22):
    d.line([(x, 22), (x, 31)], fill=plank_line)


cobble = (82, 82, 107, 255)
fill(6, cobble)
crack = darker(cobble, 0.6)
for cx, cy in [(6, 6), (20, 6), (12, 18), (24, 22), (6, 24)]:
    d.ellipse(
        [TILE * 6 + cx - 3, cy - 3, TILE * 6 + cx + 3, cy + 3], outline=crack
    )


fill(7, (255, 0, 255, 255))
for y in range(0, TILE, 4):
    for x in range(0, TILE, 4):
        if ((x // 4) + (y // 4)) % 2 == 0:
            d.rectangle(
                [TILE * 7 + x, y, TILE * 7 + x + 3, y + 3], fill=(0, 0, 0, 255)
            )

img.save("terrain.png")
print(f"wrote terrain.png ({W}x{H}, {COLS} tiles)")
