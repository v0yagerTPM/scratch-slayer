# CLAUDE.md: Scratch Slayer

A Doom-style raycasting shooter for Scratch 3, **generated from Python**. The owner is a
middle school technology teacher; students read and remix the generated Scratch blocks, so
the blocks must stay readable.

## Golden rules

- **The Python in `src/` is the source of truth.** Never hand-edit the `.sb3`. Edits made in the
  Scratch editor are lost on the next build; if the teacher made some, port them into `src/`.
- **Descriptive variable names, always.** Never single letters, in Python or in Scratch
  (`monster x`, `wall stripe height`, not `x`, `h`). This applies to loop variables too.
  The one deliberate exception is the `V("variable name")` reporter helper, used over 1,000 times.
- **Comment generously.** Use `note("text", block)` to attach a comment to a block and
  `comment="..."` on `script(...)` for a script header. Write for a 12-year-old: what it does
  and why. Doom/Wolfenstein history is welcome where it explains a technique.
- **Keep the Stage guide comments current.** `GUIDE` in `game/guide.py` (map letters, monster and
  weapon tables, options, how to add a level) is what students read first. Update it with
  every feature.
- After every change: `npm test` (it builds first). For a map change also run `python3 src/levels.py`.
- **Refactors must not change the game.** For any change that shouldn't affect what students see
  (renaming, moving code), `npm run compare` must say IDENTICAL. The build is deterministic, so
  any difference it lists is real.
- **Always ship a fresh `.sb3`.** After every significant code update, rebuild
  `dist/scratch-slayer.sb3` (`npm test` or `npm run build` does it) and commit it in the same commit
  as the change, so the downloadable game on GitHub always matches the source. Don't restore the
  old `.sb3` even when only its zip timestamps changed.

## Commands

```bash
python3 src/build.py dist/scratch-slayer.sb3   # build (stdlib only)
npm test                                        # build + all headless test plans
npm test -- full-game                           # one plan
node tests/harness.js dist/scratch-slayer.sb3 tests/plans/sprint.json tests/out/sprint
node tests/render.js tests/out/sprint <snap names...>   # snapshots -> PNG (needs sharp)
python3 src/levels.py                           # validate all maps
python3 tests/test_levels.py                    # map checker tests (npm test runs them too)
npm run compare                                 # is the built project identical to main's? (-- <ref> for another)
```

## Architecture

- `sb3lib.py`: `Project`, `Target` (sprite or stage), `script(hat, *blocks, comment=, canvas_x=)`,
  `Def(name, warp=True)` for custom blocks, `call(name, warp=True)` (warp must match the `Def`), and expression helpers (`add`, `mul`,
  `eq`, `and_`, `ifelse`, `until`, `repeat`, `setv`, `chg`, `V("var")`, `item(n, "list")`,
  `join`, `costume(default, plug)`, pen blocks such as `pen_down()`/`pen_up()`). `note()` attaches block
  comments. Layout of blocks on the canvas is estimated automatically. The file header explains
  how nested Python calls become project.json blocks.
- `sb3extra.py`: extra helpers (mouse_x/y/down, tan_, set_volume, play_named, etc.).
- `build.py`: the entry point. It imports the `game/` modules **in order** (importing one adds its
  sprite and scripts to the project), runs the sanity checks (unique names, etc.) and saves the
  `.sb3`. The import order is the creation order, so it decides block IDs and layering: put a new
  module where it belongs in the game, and expect `npm run compare` to report a change if you move one.
- `game/`: the game, one module per part. `config.py` has the tables (`MONSTER_TYPES`, `WEAPON_TYPES`,
  `WALLS`, `AMMO`, `DIFFICULTIES`; per-level settings live in `levels.py`), broadcast and state
  names, and shared helpers (`V`, `hurt_player`, `add_sound`, `map_letter_at`); every module does
  `from sb3extra import *` and `from game.config import *`, and imports anything else explicitly from
  the module that defines it. `stage.py` (project, Stage variables and lists), `guide.py` (the
  Stage guide), `engine/` (`sprite`, `main_loop`, `weapons`, `options_input`, `level_loader`,
  `movement`, `raycaster`), `screen_placement.py` (helpers for things in the 3D world), then
  `monster`, `pickups`, `barrels`, `projectiles`, `hud` (weapon, crosshair, HUD, arms panel, boss
  bar, messages, results screen, digits), `title_screen`, `level_cards`, `death_screen`,
  `victory_screen`, `options_screen` (Options Panel and Widgets) and `music`. Each sprite's Python
  handle is its name in snake_case (`engine`, `options_widgets`); give a sprite a sound with
  `add_sound(sprite, name, sounds_function)`.
- `maps/level N map.txt`: the six maps, one row per line, nothing else. Same format and file name as
  Scratch's list export/import (right-click the list "level N map"), so a student's exported map can
  be dropped in as-is. Never add comments or a ruler to these files: Scratch would import them as rows.
- `levels.py`: `load_map()` reads the files into lists of strings (`map_rows[row][column]`), and
  `LEVELS` has **one record per level with everything about it**: map, episode, start angle, colors,
  secret look, draw distance, darkness, level-select weapon, par time, card text and card monsters,
  plus a written plan of the map. `stage.py` turns the records into Scratch lists and
  `pictures/level_cards.py` draws the cards from them. Adding a level in Python = one map file + one
  record (tested by building a 7-level copy and playing level 7). `validate()` raises
  `LevelError` with a message naming the level and square. It checks reachability, keys, and that
  a skull door (`Z`) really gates the exit behind the boss.
- `pictures/`: every costume and backdrop as hand-written SVG, **by subject**: `drawing` (svg(),
  `text_label`, `full_screen`, gradients), `lettering` (the block-letter font `LETTERS` and digit
  glyphs; `block_text(..., font=)` takes a variant, e.g. `OPTIONS_LETTERS`), `monsters`, `weapons`,
  `pickups`, `world` (barrels, explosions, projectiles), `hud` (panels, arms, boss bars, `MESSAGES`,
  digits), `title_screen`, `level_cards` (`CARDS`), `death_screen` (`KILLERS`), `victory_screen`,
  `options_menu`, `tally_screen`.
- `sounds/`: every sound as synthesized WAV: `synth` (`RATE`, `make_wav`, `smooth_samples`,
  `note_frequency`), `weapons`, `monsters`, `world`, `screens`, `music`. Put new art or sound in the
  file for its subject, defined once (never patch another file's data after the fact). No external
  images or sounds (keeps it copyright-safe). Game code refers to them by full name, e.g.
  `pictures.monsters.IMP_WALK1`, `sounds.weapons.pistol`.

## Game loop (Engine main script)

One frame = input → movement/sprint → shooting → plain broadcasts in a fixed order:
`update monsters and objects` → `draw HUD` → `draw HUD numbers`, plus the raycaster drawing
with the pen. The level flow (title → card → melt → play → complete/died → next) is in the
Engine's green-flag script. After the exit, `work out level stats` + `count up level stats` run the
tally screen. 'level time' adds the timer difference each frame; closing the options menu resets
'time at last frame' so pauses don't count.

**Difficulty** (stage var `difficulty`, lists `difficulty ...`) scales monster health when a clone
starts (`full health`) and every hit on the player: always damage the player with `hurt_player()`
in `game/config.py`, never `chg("health", ...)` directly.

## Scratch quirks learned the hard way

- **Broadcast-and-wait costs at least one frame.** The main loop uses plain broadcasts; their
  receivers run later in the same tick, in the order the broadcasts were sent.
- **A loop inside a script that is re-broadcast every frame gets restarted** before it can
  finish. Put loops in warp custom blocks (`Def(...)`, which defaults to warp=True), which
  finish in one go (e.g. `launch new shots`, `check rocket hits`).
- **Warp blocks yield after about 500 ms**, so keep them lean (big map loads are fine).
- **`key pressed` can't detect Shift, Ctrl or Esc.** That's why sprint is Q and pause is P.
- **`=` is case-insensitive** (`"m" = "M"`), so map letters can't use case to mean different things.
- **Every sprite needs at least one costume** (the Music sprite has a 1x1 "speaker").
- **Variable names must be unique** between the Stage and every sprite's local variables
  (`build.py` checks this). Shared state goes on the Stage.
- **Don't put boolean (hexagon) blocks in number slots.** Set a variable with an `if` instead.
- Switching to a costume name that doesn't exist silently does nothing, so check names.
- Scratch's clone limit is 300. The game currently uses about 105.
- Front/back layering is "last `go to front` wins". Sprites that must stay on top (options
  menu, digits) call `front()` every frame after the others.
- **Clones run in layer order, so clones that all `go to front` in one broadcast swap places
  every frame.** If one must stay under its siblings (the options row highlight), give it its
  own broadcast sent earlier: threads of an earlier plain broadcast always run first.

## Map letters (see `levels.py` docstring and the Stage guide; the maps are in `src/maps/`)

Walls `1-9`; doors `D`, red `R`, blue `B`, skull `Z`; exit switch `X`; secret wall `S`.
Things: `P` player, monsters `M` imp, `V` spitter, `G` golem, `W` warden (boss), `C` charger,
`F` wraith, `T` colossus (boss); pickups `H` health, `A` shells, `I` bullets, `U` rockets,
`N` shotgun, `Q` chaingun, `L` rocket launcher, `K` red key, `J` blue key; `E` barrel.
A boss automatically carries the skull key (item type 5).

## Tests

`tests/harness.js` loads the `.sb3` into scratch-vm with a fake renderer and a fake clock, and
steps it frame by frame. A plan is a JSON list of steps:

| key | meaning |
|---|---|
| `frames` | how many frames to run this step |
| `keys` | keys held down: `"space"`, `"up arrow"`, `"w"`, `"1"` ... |
| `set` | set stage variables first (aliases: `px`, `py`, `ang`, `HEALTH`, `state`, ...) |
| `setList` | replace stage lists, e.g. `{"weapons owned": [1,1,1,1,1]}` |
| `hit` | `{"type": 7, "damage": 31}`: the first live monster of that type takes a hit |
| `setMonsterType` | set local variables on every clone of a monster type |
| `toBossKey` | move the player onto the boss's skull key |
| `mouse` | `{"x":..,"y":..,"down":true}` in stage coordinates |
| `log` / `snap` | print state / save a snapshot (render with `tests/render.js`) |
| `dumpMonsters` | print every monster (or one type) |
| `expectMonsters` | `{"type": 1, "monster health": 2}`: every clone of that monster type must have these local values |
| `expect` | assertions: `{"current weapon": 3, "list:ammo counts": [48,7,0], "health": {"lt": 100}}` |

The harness exits non-zero if any `expect` fails or the VM logs an error. Add a plan (or
steps with `expect`) for every new feature.
