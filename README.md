# Scratch Slayer

A Doom-style first-person shooter that runs in **Scratch 3**. It is a raycaster, the same
technique Wolfenstein 3D used in 1992, and it has 6 levels, 5 weapons, 7 monster types and
two bosses, plus an options menu.

The game is **generated from Python**. You don't edit it by dragging blocks. You edit the
Python files in `src/`, run the build, and get a fresh `scratch-slayer.sb3` that you open in
Scratch. This is what makes version control possible: the Python is plain text that git can
track line by line, while an `.sb3` file is a zip that git can only store as one big blob.

> **Important:** the Python source is the "source of truth". If you change blocks inside the
> Scratch editor, those changes are **overwritten** the next time you build. Make changes in
> `src/` (or ask Claude Code to), then rebuild.

## Quick start

You need **Python 3** (nothing else is needed for building) and, for the tests, **Node.js 18
or newer**.

```bash
# build the game -> dist/scratch-slayer.sb3
python3 src/build.py dist/scratch-slayer.sb3      # on Windows: python src\build.py dist\scratch-slayer.sb3

# or, with Node installed:
npm install        # once: installs the headless Scratch VM used by the tests
npm run build
npm test           # builds, then plays the game headlessly and checks the results
npm run compare    # checks the game you build is identical to main's (for refactors)
```

Then open Scratch (scratch.mit.edu → Create, or the Scratch desktop app) and use
**File → Load from your computer** to open `dist/scratch-slayer.sb3`.

Check that every level is still valid after editing a map:

```bash
python3 src/levels.py
```

### Using a map made in Scratch

The maps live in `src/maps/` as plain text files, in exactly the format Scratch uses to
export and import lists. To bring a student's map into the project:

1. In Scratch, show the list (for example "level 1 map"), right-click it on the stage and
   choose **export**. Scratch saves `level 1 map.txt`.
2. Put that file in `src/maps/`, replacing the old one with the same name.
3. Run `npm test`. The build checks the map; if something is wrong (a missing exit, a key
   behind its own door...) it says what and where. Then open the new `dist/scratch-slayer.sb3`.

To go the other way, right-click the list in Scratch, choose **import** and pick a file from
`src/maps/`. Edit maps in a plain text editor with a monospace font. Don't add notes to the
files: Scratch would import every line, notes included, as a row of the map.

## What's where

| Path | What it is |
|---|---|
| `src/build.py` | Puts the game together from `src/game/` and saves the `.sb3`. Run it to build. |
| `src/game/` | The game, one file per part: `config.py` (settings tables), `stage.py`, `guide.py` (the Stage guide), `engine/` (game loop, weapons, options, level loading, movement, raycaster), `monster.py`, `pickups.py`, `hud.py`, the title, card, death and victory screens, the options menu and music. |
| `src/sb3lib.py` | A small compiler: Python functions that become Scratch blocks, written out as `project.json` inside the `.sb3`. |
| `src/sb3extra.py` | More block helpers (mouse, sound, list and pen blocks). |
| `src/maps/` | The six level maps as text files (`level 1 map.txt` ...), one row per line. Same format as Scratch's list export. |
| `src/levels.py` | Loads the maps, adds each level's settings, and `validate()`, which checks every level can be finished and explains any problem it finds. |
| `tests/test_levels.py` | Tests for the map checker: broken maps it must catch. |
| `src/assets*.py` | All the art (hand-written SVG) and sound (synthesized WAV), one file per round of features. Nothing is downloaded from the internet. |
| `tests/harness.js` | Runs the `.sb3` in a headless Scratch VM, presses keys, and checks variables. |
| `tests/plans/*.json` | Test scripts: which keys to press for how many frames, and what should be true afterwards. |
| `tests/render.js` | Turns test snapshots into PNG screenshots. |
| `docs/project-page.md` | The Instructions and Notes & Credits text for the Scratch project page. |
| `dist/` | Build output (ignored by git). |
