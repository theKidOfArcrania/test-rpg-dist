# Tilesets

This directory holds tileset PNGs consumed by the world renderer.

## Layout convention

Each tileset is a single horizontal strip (or grid) of equal-size
tiles. The renderer reads tiles by atlas index where:

    atlas_index = tile_id - 1   (TileId 0 = "empty", never drawn)

`columns * tile_size_px` defines the strip width; `rows * tile_size_px`
the height. The loader is configured per-file in `src/world/tileset.rs`.

## terrain.png

The default world tileset. 32×32 px tiles, 8 columns, 1 row.

| Atlas idx | TileId | Name        | Solid? |
|-----------|--------|-------------|--------|
| 0         | 1      | grass       | no     |
| 1         | 2      | stone wall  | yes    |
| 2         | 3      | water       | yes    |
| 3         | 4      | path / dirt | no     |
| 4         | 5      | tree        | yes    |
| 5         | 6      | wood floor  | no     |
| 6         | 7      | cobble      | no     |
| 7         | 8      | (debug)     | no     |

`tile_color` and `tile_solid` in `src/world/map.rs` are the source of
truth for the id↔solidity mapping; `tile_color` is now only used as a
fallback when the texture fails to load.

The current `terrain.png` is a procedurally-generated placeholder
(see `generate_placeholder.py`). Swap it for any 256×32 PNG following
the table above. To use a different art pack with different tile
indices, either rearrange the source image or extend `Tileset` with
a `tile_id -> atlas_index` remap table.

## Replacing with real art

Drop the new PNG in as `terrain.png` (matching the columns / tile_size
the loader expects, currently 8 columns × 32 px). If the dimensions
differ, update the constants in `src/world/tileset.rs::load_default`.

If the tileset goes missing or fails to load, the renderer falls back
to the original flat-color tile palette so the game stays playable.
