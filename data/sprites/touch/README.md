# Touch HUD icons

Optional PNG icons rendered on top of the mobile / wasm on-screen buttons.
Each file lives at `data/sprites/touch/<id>.png`. Any missing file falls
back to the button's single-letter label, so the HUD still works without
any icons authored.

Expected filenames (id -> action it represents):

| File              | Action               | Default label |
| ----------------- | -------------------- | ------------- |
| `attack.png`      | melee attack         | `J`           |
| `cast.png`        | cast spell           | `K`           |
| `interact.png`    | confirm (battle)     | `Z`           |
| `spell_cycle.png` | next spell           | `Q`           |
| `menu.png`        | pause menu           | `≡`           |
| `inventory.png`   | inventory drawer     | `I`           |
| `back_x.png`      | universal modal exit | `X`           |

> The overworld layout omits the dedicated `interact` button —
> tap-anywhere-outside-controls fires `Action::Interact` instead.
> Battle mode hides Attack / Cast / SpellCycle (the action menu
> dispatches those) and surfaces a single `interact` button as
> the explicit Confirm affordance.

## Authoring guidance

- **Resolution**: 64x64 or 128x128 PNGs work well. They're drawn inscribed
  into the button hit circle (side ≈ button_radius × √2), so an extra
  pixel of padding helps avoid clipping against the button border.
- **Transparency**: use a transparent background — the dark button disc
  is drawn underneath so the icon only needs the foreground glyph.
- **Color**: light/white glyphs read best against the translucent dark
  button fill. The `back_x` icon gets a slightly larger inset (15%) since
  it sits inside a square plate instead of a circle.
- **Pixel-art look**: if you want hard pixel edges, set the texture
  filter to nearest after loading — currently we apply linear filtering
  so the same icon scales cleanly across phone DPIs.

The asset list is declared in `src/touch_ui.rs::TOUCH_ICON_IDS`; add a
new id there + reference it from a `ButtonRect.icon` field if you add a
new touch button.
