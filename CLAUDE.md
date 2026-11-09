# CLAUDE.md: Scratch Slayer

A Doom-style raycasting shooter for Scratch 3, **generated from Python**. The owner is a
middle school technology teacher; students read and remix the generated Scratch blocks, so
the blocks must stay readable.

## Golden rules

- **The Python in `src/` is the source of truth.** Never hand-edit the `.sb3`. Edits made in the
  Scratch editor are lost on the next build; if the teacher made some, port them into `src/`.
- **Descriptive variable names, always.** Never single letters, in Python or in Scratch
  (`monster x`, `wall stripe height`, not `x`, `h`). This applies to loop variables too.
- **Comment generously.** Use `note("text", block)` to attach a comment to a block and
  `comment="..."` on `script(...)` for a script header. Write for a 12-year-old: what it does
  and why. Doom/Wolfenstein history is welcome where it explains a technique.
- **Keep the Stage guide comments current.** `GUIDE` in `build.py` (map letters, monster and
  weapon tables, options, how to add a level) is what students read first. Update it with
  every feature.
- After every change: `npm test` (it builds first). For a map change also run `python3 src/levels.py`.

## Commands

```bash
python3 src/build.py dist/scratch-slayer.sb3   # build (stdlib only)
npm test                                        # build + all headless test plans
npm test -- full-game                           # one plan
node tests/harness.js dist/scratch-slayer.sb3 tests/plans/sprint.json tests/out/sprint
node tests/render.js tests/out/sprint <snap names...>   # snapshots -> PNG (needs sharp)
python3 src/levels.py                           # validate all maps
```

## Architecture

- `sb3lib.py`: `Project`, `Target` (sprite or stage), `script(hat, *blocks, comment=)`,
  `Def(name, warp=True)` for custom blocks, `call(name)`, and expression helpers (`add`, `mul`,
  `eq`, `and_`, `ifelse`, `until`, `repeat`, `setv`, `chg`, `V("var")`, `item(n, "list")`,
  `join`, `costume(default, plug)`, pen blocks). `note()` attaches block comments. Layout of
  blocks on the canvas is estimated automatically.
- `sb3extra.py`: extra helpers (mouse_x/y/down, tan_, set_volume, play_named, etc.).
- `build.py`: top-level config tables (`MONSTER_TYPES`, `WEAPON_TYPES`, `WALLS`, `AMMO`,
  per-level lists), stage variables and lists, then each sprite: Engine (main loop,
  raycaster, input, options menu, level loader), Monster, Pickup, Barrel, Projectile, Weapon,
  Crosshair, HUD, Arms Panel, Boss Bar, Message, Screens, Digits, the title/card/death/victory
  sprites, Options Panel, Options Widgets, Music. Ends with sanity checks (unique names, etc.).
- `levels.py`: maps are lists of strings. Levels 1-3 are hand-drawn plus `_edit()` patches;
  levels 4-6 are drawn with the `Grid` helper. `validate()` checks reachability, keys, and that
  a skull door (`Z`) really gates the exit behind the boss.
- `assets.py` … `assets6.py`: SVG strings and synthesized WAVs, one file per feature round.
  Later files reuse earlier ones. No external images or sounds (keeps it copyright-safe).

## Game loop (Engine main script)

One frame = input → movement/sprint → shooting → plain broadcasts in a fixed order:
`update monsters and objects` → `draw HUD` → `draw HUD numbers`, plus the raycaster drawing
with the pen. The level flow (title → card → melt → play → complete/died → next) is in the
Engine's green-flag script.

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
- Scratch's clone limit is 300. The game currently uses about 100.
- Front/back layering is "last `go to front` wins". Sprites that must stay on top (options
  menu, digits) call `front()` every frame after the others.

## Map letters (see `levels.py` docstring and the Stage guide)

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
| `expect` | assertions: `{"current weapon": 3, "list:ammo counts": [48,7,0], "health": {"lt": 100}}` |

The harness exits non-zero if any `expect` fails or the VM logs an error. Add a plan (or
steps with `expect`) for every new feature.
