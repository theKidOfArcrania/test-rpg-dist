#!/usr/bin/env python3
"""Pre-render placeholder pixel art for slime / boss-slime / npc /
pickup into data/tilesets/sprites.png.

The player frames at the top of the sheet are hand-authored and
left untouched. This script paints the remaining entity rows with
recognizable-but-rough placeholder art so the new
no-fallback render path always has something to draw. Replace any
of the painted cells with real art at any time; this script only
overwrites the cells it explicitly targets.

Layout (24x24 cells, sheet is 16 cols x 16 rows):
  row 0       : Player (already authored - skipped)
  rows 1..2   : Player reserved (untouched)
  row 3       : Slime               cols 0..7  -> 8 frames
  rows 4..5   : Boss slime 2x2       (TL, TR / BL, BR sub-sprites,
                                      8 frames per quadrant)
  row 6       : NPC                  cols 0..7  -> 8 frames
  row 7       : Per-item pickup icons - one cell each, no facing.
                  cell 0  heal_potion  (red flask)
                  cell 1  mana_potion  (blue flask)
                  cell 2  rusty_sword  (vertical gray sword)
                  cell 3  leather_vest (brown tunic torso)
  row 8       : Projectiles / VFX.
                  cell 0  spark        (radiant cross, 1 frame)

Per-row 8-frame layout (rows 0..6): [down0,down1, left0,left1, up0,up1, right0,right1]

Run with:   python3 data/tilesets/generate_sprites.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

SHEET = Path(__file__).parent / "sprites.png"
TILE = 24
COLS = 16

# --- helpers ---------------------------------------------------------------


def cell_origin(col: int, row: int) -> tuple[int, int]:
    return col * TILE, row * TILE


def clear_cell(img: Image.Image, col: int, row: int) -> None:
    x, y = cell_origin(col, row)
    for dy in range(TILE):
        for dx in range(TILE):
            img.putpixel((x + dx, y + dy), (0, 0, 0, 0))


def paint_pixels(
    img: Image.Image,
    col: int,
    row: int,
    pixels: list[tuple[int, int, tuple[int, int, int, int]]],
) -> None:
    """Stamp explicit pixels into a cell. Coordinates are local (0..TILE)."""
    x, y = cell_origin(col, row)
    for dx, dy, color in pixels:
        if 0 <= dx < TILE and 0 <= dy < TILE:
            img.putpixel((x + dx, y + dy), color)


# --- shape primitives ------------------------------------------------------


def filled_oval(
    img: Image.Image,
    col: int,
    row: int,
    bbox: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
) -> None:
    """Draw a filled, outlined ellipse anchored to a single cell."""
    x, y = cell_origin(col, row)
    x0, y0, x1, y1 = bbox
    draw = ImageDraw.Draw(img)
    draw.ellipse([x + x0, y + y0, x + x1, y + y1], fill=fill, outline=outline)


def two_eyes(
    img: Image.Image,
    col: int,
    row: int,
    eye_positions: list[tuple[int, int]],
    color: tuple[int, int, int, int] = (10, 10, 10, 255),
) -> None:
    for ex, ey in eye_positions:
        paint_pixels(img, col, row, [(ex, ey, color), (ex + 1, ey, color)])


# --- slime -----------------------------------------------------------------

SLIME_BODY = (90, 200, 110, 255)
SLIME_OUTLINE = (30, 70, 35, 255)
BOSS_BODY = (180, 60, 110, 255)
BOSS_OUTLINE = (60, 15, 35, 255)
NPC_BODY = (100, 140, 220, 255)
NPC_OUTLINE = (25, 35, 80, 255)
NPC_HAT = (40, 70, 140, 255)
PICKUP_BODY = (240, 215, 80, 255)
PICKUP_OUTLINE = (90, 65, 10, 255)
PICKUP_ACCENT = (255, 250, 220, 255)


def paint_slime(img: Image.Image, row: int) -> None:
    """8 slime frames in one row.

    Slime is symmetric so all 4 directions share the same blob;
    we just toggle the eye height to fake a hop between the two
    frames per direction.
    """
    eye_layouts = {
        "rest": [(8, 12), (14, 12)],
        "blink": [(8, 13), (14, 13)],
    }
    for col in range(8):
        clear_cell(img, col, row)
        # Body: rounded blob, slightly squashed on the "step" frame.
        squashed = (col % 2 == 1)
        if squashed:
            bbox = (3, 8, 20, 21)
        else:
            bbox = (3, 7, 20, 21)
        filled_oval(img, col, row, bbox, SLIME_BODY, SLIME_OUTLINE)
        # Highlight stripe (gives it a wet-sheen).
        x, y = cell_origin(col, row)
        for hx in range(7, 12):
            img.putpixel((x + hx, y + 9), (190, 240, 200, 255))
        # Eyes alternate per frame.
        layout = eye_layouts["rest"] if not squashed else eye_layouts["blink"]
        two_eyes(img, col, row, layout)


def paint_npc(img: Image.Image, row: int) -> None:
    """8 NPC frames - a tunic-wearing figure facing each direction."""
    # Frame index -> facing
    facings = ["down", "down", "left", "left", "up", "up", "right", "right"]
    for col in range(8):
        clear_cell(img, col, row)
        facing = facings[col]
        bob = 1 if (col % 2 == 1) else 0
        x, y = cell_origin(col, row)
        # Hat (top 4 rows of head, slightly wider than face).
        for hy in range(4 + bob, 8 + bob):
            for hx in range(7, 17):
                img.putpixel((x + hx, y + hy), NPC_HAT)
        # Head (face).
        for hy in range(8 + bob, 12 + bob):
            for hx in range(8, 16):
                img.putpixel((x + hx, y + hy), (250, 220, 190, 255))
        # Tunic body.
        for by in range(12 + bob, 21 + bob):
            for bx in range(6, 18):
                img.putpixel((x + bx, y + by), NPC_BODY)
        # Outline (left + right sides + bottom).
        for by in range(4 + bob, 21 + bob):
            img.putpixel((x + 6, y + by), NPC_OUTLINE)
            img.putpixel((x + 17, y + by), NPC_OUTLINE)
        for bx in range(6, 18):
            img.putpixel((x + bx, y + 21 + bob), NPC_OUTLINE)
        # Eyes per facing.
        eye = (10, 10, 10, 255)
        if facing == "down":
            paint_pixels(img, col, row,
                         [(10, 10 + bob, eye), (13, 10 + bob, eye)])
        elif facing == "up":
            # Back of head - no eyes visible.
            pass
        elif facing == "left":
            paint_pixels(img, col, row, [(9, 10 + bob, eye)])
        elif facing == "right":
            paint_pixels(img, col, row, [(14, 10 + bob, eye)])


def paint_pickups(img: Image.Image, row: int) -> None:
    """Per-item pickup icons. Row 7 cell layout:

      cell 0 (tile 113): heal_potion  - red flask
      cell 1 (tile 114): mana_potion  - blue flask
      cell 2 (tile 115): rusty_sword  - vertical gray sword
      cell 3 (tile 116): leather_vest - brown tunic torso

    The remaining cells (4..15) stay transparent until more
    items ship; cell 0 ALSO doubles as the generic "pickup"
    fallback because data/sprites/pickup.json points at tile 113
    via inheriting whatever lives in the heal-potion slot - the
    generic 'pickup' spec is only resolved when an item omits
    its own sprite_id, which the shipped catalog never does.
    """
    for col in range(8):
        clear_cell(img, col, row)
    paint_potion(img, col=0, row=row, body=(220, 60, 70, 255), highlight=(255, 180, 190, 255))
    paint_potion(img, col=1, row=row, body=(70, 100, 220, 255), highlight=(180, 200, 255, 255))
    paint_sword(img, col=2, row=row)
    paint_vest(img, col=3, row=row)


def paint_potion(img, col, row, body, highlight):
    """Round-bottomed flask: cork on top, neck, bulbous body with
    a sheen highlight."""
    x, y = cell_origin(col, row)
    cork = (130, 80, 30, 255)
    glass_outline = (30, 25, 20, 255)
    # Cork (top 2 rows of the bottle).
    for cy in (5, 6):
        for cx in range(10, 14):
            img.putpixel((x + cx, y + cy), cork)
    # Neck.
    for ny in (7, 8):
        for nx in range(10, 14):
            img.putpixel((x + nx, y + ny), body)
        img.putpixel((x + 9, y + ny), glass_outline)
        img.putpixel((x + 14, y + ny), glass_outline)
    # Round body (rows 9..19).
    body_rows = [
        (8, 16),  # y=9 widening
        (7, 17),  # y=10
        (6, 18),  # y=11
        (6, 18),  # y=12
        (6, 18),  # y=13
        (6, 18),  # y=14
        (6, 18),  # y=15
        (6, 18),  # y=16
        (7, 17),  # y=17
        (8, 16),  # y=18
        (10, 14),  # y=19 base
    ]
    for i, (lo, hi) in enumerate(body_rows):
        py = 9 + i
        for px in range(lo + 1, hi):
            img.putpixel((x + px, y + py), body)
        # Outline edges.
        img.putpixel((x + lo, y + py), glass_outline)
        img.putpixel((x + hi, y + py), glass_outline)
    # Sheen highlight (left side of the bulb).
    for hy in (11, 12, 13):
        img.putpixel((x + 8, y + hy), highlight)


def paint_sword(img, col, row):
    """Vertical sword: brown grip + crossguard + steel blade with
    a tip highlight."""
    x, y = cell_origin(col, row)
    grip = (100, 60, 25, 255)
    grip_outline = (40, 25, 10, 255)
    guard = (180, 150, 60, 255)
    guard_outline = (90, 70, 20, 255)
    blade = (200, 200, 215, 255)
    blade_edge = (90, 95, 110, 255)
    blade_tip = (250, 250, 255, 255)
    # Grip (rows 16..21).
    for gy in range(16, 22):
        for gx in range(11, 13):
            img.putpixel((x + gx, y + gy), grip)
        img.putpixel((x + 10, y + gy), grip_outline)
        img.putpixel((x + 13, y + gy), grip_outline)
    # Pommel (row 22).
    for gx in range(10, 14):
        img.putpixel((x + gx, y + 22), grip_outline)
    # Crossguard (row 15).
    for gx in range(8, 16):
        img.putpixel((x + gx, y + 14), guard_outline)
        img.putpixel((x + gx, y + 15), guard)
        img.putpixel((x + gx, y + 16), guard_outline)
    img.putpixel((x + 7, y + 15), guard_outline)
    img.putpixel((x + 16, y + 15), guard_outline)
    # Blade (rows 4..14).
    for by in range(5, 14):
        for bx in range(11, 13):
            img.putpixel((x + bx, y + by), blade)
        img.putpixel((x + 10, y + by), blade_edge)
        img.putpixel((x + 13, y + by), blade_edge)
    # Tip (row 4) tapered.
    img.putpixel((x + 11, y + 4), blade_tip)
    img.putpixel((x + 12, y + 4), blade_tip)
    img.putpixel((x + 11, y + 3), blade_edge)
    img.putpixel((x + 12, y + 3), blade_edge)


def paint_vest(img, col, row):
    """Sleeveless leather torso: V-neck + lacing down the front."""
    x, y = cell_origin(col, row)
    leather = (140, 90, 50, 255)
    leather_dark = (80, 50, 25, 255)
    lace = (250, 230, 180, 255)
    # Shoulders (rows 6..7).
    for sy in (6, 7):
        for sx in range(7, 17):
            img.putpixel((x + sx, y + sy), leather)
    # V-neck collar carved into top center.
    img.putpixel((x + 11, y + 6), leather_dark)
    img.putpixel((x + 12, y + 6), leather_dark)
    img.putpixel((x + 10, y + 7), leather_dark)
    img.putpixel((x + 11, y + 7), leather_dark)
    img.putpixel((x + 12, y + 7), leather_dark)
    img.putpixel((x + 13, y + 7), leather_dark)
    # Body (rows 8..19).
    for by in range(8, 20):
        for bx in range(7, 17):
            img.putpixel((x + bx, y + by), leather)
    # Outline.
    for by in range(6, 20):
        img.putpixel((x + 6, y + by), leather_dark)
        img.putpixel((x + 17, y + by), leather_dark)
    for bx in range(7, 17):
        img.putpixel((x + bx, y + 20), leather_dark)
    # Lacing (every other pixel down the center).
    for ly in (10, 12, 14, 16, 18):
        img.putpixel((x + 11, y + ly), lace)
        img.putpixel((x + 12, y + ly), lace)
    # Side seams (subtle vertical line).
    for sy in range(9, 19):
        img.putpixel((x + 9, y + sy), leather_dark)
        img.putpixel((x + 14, y + sy), leather_dark)


# --- boss slime (2x2) ------------------------------------------------------


def paint_boss(img: Image.Image, row_top: int) -> None:
    """Boss slime is a 2x2 SpriteGroup. Each of the four sub-sprites
    has its own 8-frame strip:

      sub-sprite TL: row_top   cols 0..7
      sub-sprite TR: row_top   cols 8..15
      sub-sprite BL: row_top+1 cols 0..7
      sub-sprite BR: row_top+1 cols 8..15

    For a given frame index `f`, the four cells form one logical
    48x48 boss image. We render the boss into a temporary 48x48
    canvas then copy each 24x24 quadrant to the corresponding cell.
    """
    for f in range(8):
        canvas = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        # Body bbox - squash on odd frames.
        if f % 2 == 1:
            body = (4, 14, 43, 44)
        else:
            body = (4, 12, 43, 44)
        draw.ellipse(body, fill=BOSS_BODY, outline=BOSS_OUTLINE)
        # Spike crest (4 spikes across the top).
        for sx in (12, 22, 32, 18):
            draw.polygon(
                [(sx - 2, 14), (sx + 2, 14), (sx, 8)],
                fill=BOSS_BODY,
                outline=BOSS_OUTLINE,
            )
        # Highlight sheen.
        for hx in range(14, 28):
            canvas.putpixel((hx, 18), (255, 180, 200, 255))
        # Eyes (red/orange for menace).
        for ex, ey in [(16, 24), (30, 24)]:
            for dx in range(3):
                for dy in range(3):
                    canvas.putpixel((ex + dx, ey + dy), (250, 80, 30, 255))
            canvas.putpixel((ex + 1, ey + 1), (10, 10, 10, 255))
        # Mouth.
        for mx in range(20, 27):
            canvas.putpixel((mx, 32), (10, 10, 10, 255))
        canvas.putpixel((20, 31), (10, 10, 10, 255))
        canvas.putpixel((26, 31), (10, 10, 10, 255))

        # Slice into four quadrants.
        # TL quadrant -> cell (col=f, row=row_top)
        # TR quadrant -> cell (col=f+8, row=row_top)
        # BL quadrant -> cell (col=f, row=row_top+1)
        # BR quadrant -> cell (col=f+8, row=row_top+1)
        positions = [
            ((0, 0, 24, 24), (f, row_top)),       # TL
            ((24, 0, 48, 24), (f + 8, row_top)),  # TR
            ((0, 24, 24, 48), (f, row_top + 1)),  # BL
            ((24, 24, 48, 48), (f + 8, row_top + 1)),  # BR
        ]
        for src_box, (col, row) in positions:
            clear_cell(img, col, row)
            quad = canvas.crop(src_box)
            ox, oy = cell_origin(col, row)
            img.paste(quad, (ox, oy), quad)


def paint_spark(img: Image.Image, row: int, col: int) -> None:
    """Spark spell projectile - small radiant cross with a hot
    inner core. Centered in its 24x24 cell, ~12 px overall.
    Single-frame; animation can be authored in sprites.tsj
    later if a flicker is desired.
    """
    clear_cell(img, col, row)
    x, y = cell_origin(col, row)
    cx, cy = 12, 12
    halo = (140, 200, 255, 140)   # soft outer glow
    rim = (210, 230, 255, 220)
    body = (255, 255, 255, 255)   # hot core
    # Outer cross (4-pixel arms).
    for d in range(-5, 6):
        img.putpixel((x + cx + d, y + cy), halo)
        img.putpixel((x + cx, y + cy + d), halo)
    # Inner cross (rim).
    for d in range(-3, 4):
        img.putpixel((x + cx + d, y + cy), rim)
        img.putpixel((x + cx, y + cy + d), rim)
    # Diagonal sparks.
    for d in (-2, -1, 1, 2):
        img.putpixel((x + cx + d, y + cy + d), halo)
        img.putpixel((x + cx + d, y + cy - d), halo)
    # White-hot core.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            img.putpixel((x + cx + dx, y + cy + dy), body)


def paint_door(img: Image.Image, row: int, col: int) -> None:
    """Generic interactable door - a wooden plank arch with iron
    bands and a small handle. Single 24x24 frame; renders the
    same in all four facings (Interactables don't have a facing
    of their own, just a sprite_id pointed at this tile)."""
    clear_cell(img, col, row)
    x, y = cell_origin(col, row)
    plank = (110, 70, 30, 255)
    plank_dark = (60, 35, 12, 255)
    plank_hl = (160, 110, 60, 255)
    iron = (60, 60, 70, 255)
    iron_hl = (130, 130, 150, 255)
    handle = (220, 200, 60, 255)
    # Door body (rows 4..22, cols 5..18) - tall arched plank.
    for by in range(4, 23):
        for bx in range(5, 19):
            img.putpixel((x + bx, y + by), plank)
    # Vertical plank seams (every 3 cols).
    for sx in (8, 11, 14):
        for sy in range(5, 22):
            img.putpixel((x + sx, y + sy), plank_dark)
    # Soft highlight stripe on the leftmost plank.
    for hy in range(5, 22):
        img.putpixel((x + 6, y + hy), plank_hl)
    # Iron horizontal bands (top + bottom).
    for ix in range(5, 19):
        img.putpixel((x + ix, y + 6), iron)
        img.putpixel((x + ix, y + 7), iron_hl)
        img.putpixel((x + ix, y + 19), iron)
        img.putpixel((x + ix, y + 20), iron_hl)
    # Iron studs at the band ends.
    for sy in (6, 19):
        img.putpixel((x + 5, y + sy), iron_hl)
        img.putpixel((x + 18, y + sy), iron_hl)
    # Frame outline.
    for fy in range(4, 23):
        img.putpixel((x + 4, y + fy), plank_dark)
        img.putpixel((x + 19, y + fy), plank_dark)
    for fx in range(4, 20):
        img.putpixel((x + fx, y + 3), plank_dark)
        img.putpixel((x + fx, y + 22), plank_dark)
    # Handle (small brass nub on the right side).
    img.putpixel((x + 16, y + 13), handle)
    img.putpixel((x + 17, y + 13), handle)
    img.putpixel((x + 16, y + 14), handle)
    img.putpixel((x + 17, y + 14), handle)


# --- entry -----------------------------------------------------------------


def main() -> None:
    img = Image.open(SHEET).convert("RGBA")
    paint_slime(img, row=3)
    paint_boss(img, row_top=4)
    paint_npc(img, row=6)
    paint_pickups(img, row=7)
    paint_spark(img, row=8, col=0)
    paint_door(img, row=8, col=1)
    img.save(SHEET)
    print(f"wrote {SHEET}")


if __name__ == "__main__":
    main()
