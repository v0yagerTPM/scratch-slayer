"""Level maps for Scratch Slayer.

WHERE THE MAPS ARE
==================
Each level's map is a plain text file in the src/maps folder:
    src/maps/level 1 map.txt   ...   src/maps/level 6 map.txt
One line of the file = one ROW of the map, top row first. Each letter is one SQUARE.

These are EXACTLY the files Scratch makes when you right-click the list "level 1 map" on the
stage and choose "export", and the files it reads with "import". (Scratch names an exported
list after the list, which is where the file names come from.) So a map can travel both ways:
  - from Scratch into this project: export the list, put the file in src/maps (replacing the
    old one, same name), then run npm test. The build checks the map and puts it in the game.
  - from this project into Scratch: import the file into the list in the Scratch editor.
That's why the files hold nothing but map rows: no comments or notes, because Scratch would
import every line, notes included, as a row of the map. The notes about each level's layout
are in this file instead, next to the level's settings further down.

Edit a map in any plain text editor (Notepad, TextEdit in plain text mode, VS Code). Use a
monospace font such as Consolas or Courier so the columns line up; most code editors show the
column number at the bottom, which helps find a square.

HOW A MAP IS USED
=================
load_map() reads a file into a Python list of strings, one string per row. build.py copies
that list straight into the Scratch list "level N map" (one string = one list item), and the
Engine's 'load level' block reads it back letter by letter. So the file IS the level.

COORDINATES: a square is (column, row), both counting from 0.
  column = how far along the row (0 = the first letter of the line)
  row    = which line of the file (0 = the TOP line)
So map_rows[row][column] is the letter on a square. Notice the order: row first, then column.
The game uses the same numbers ("player x" 3.5 = the middle of column 3, "player y" = the row).
Scratch lists and text editors count from 1 instead: row 0, column 0 is line 1, letter 1.

At the bottom, validate() plays detective: it checks every map can really be finished.
build.py runs validate() on every level each time it builds, so a broken map stops the build
with a message saying what is wrong and where. Run this file on its own
(python3 src/levels.py) to check the maps and print what is in each one.

LEGEND (one character per grid cell)
  0      empty floor
  1-9    walls (each digit is a different wall color)
  D      door            (press E)
  R / B  red / blue door (needs the matching key)
  X      exit switch     (press E to finish the level)
  S      secret wall     (looks like a wall, press E to open)
  P      player start
  Z      skull door      (opens with the skull key the level's BOSS drops)
  M  imp      V  spitter      G  golem      W  warden (boss)
  C  charger  F  wraith       T  colossus (boss)
  H      health pack     A  box of shells   I  bullets   U  rockets
  N      shotgun         Q  chaingun        L  rocket launcher
  K      red key         J  blue key
  E      exploding barrel
"""
import os
# deque = a "double-ended queue": a list you can quickly take items off the FRONT of.
# The flood fill in reachable_squares() below uses it as a to-do list of squares to visit.
from collections import deque


class LevelError(Exception):
    """A problem with a map. The message says which level, what is wrong, and where."""


def where(column, row):
    """A square's position, in Python numbers and in Scratch list numbers."""
    return f"column {column}, row {row} (in Scratch: item {row + 1} of the list, letter {column + 1})"


def check(condition, message):
    """Stop with a LevelError and the message if the condition is not true."""
    if not condition:
        raise LevelError(message)


# =================================================================================================
# READING A MAP FILE
# =================================================================================================
# The maps folder, found from where this file is, so it works whichever folder you run from.
MAPS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps")


def map_file_path(level_number):
    """src/maps/level 1 map.txt, src/maps/level 2 map.txt ..."""
    return os.path.join(MAPS_FOLDER, f"level {level_number} map.txt")


def load_map(level_number):
    """Read one map file and return its rows: a list of strings, top row first.

    Line endings: Windows ends each line with two characters (carriage return + new line),
    Mac and Linux with one (new line). splitlines() understands both, so a file exported from
    Scratch on any computer works. A file may or may not end with a final line break; blank
    lines at the very end are ignored. Everything else is kept exactly as it is, so a stray
    space or tab becomes an 'unknown letter' that validate() points out.
    """
    path = map_file_path(level_number)
    check(os.path.exists(path), f"level {level_number}: the map file is missing. Expected {path}")
    with open(path, encoding="utf-8-sig") as map_file:   # utf-8-sig also skips the invisible
        map_rows = map_file.read().splitlines()          # marker some Windows editors add
    while map_rows and map_rows[-1].strip() == "":       # drop blank lines at the end
        map_rows.pop()
    check(map_rows, f"level {level_number}: the map file {path} is empty.")
    return map_rows


# =================================================================================================
# THE LEVEL LIST: each level's map plus a few settings. build.py reads this.
# =================================================================================================
# For each level:
#   name         used in this file's messages (the level cards' names are drawn in assets6.py)
#   rows         the map, read from its file (becomes the Scratch list "level N map")
#   angle        the direction the player faces at the start, in degrees:
#                0 = right (along the row), 90 = down, 180 = left, 270 = up (toward row 0)
#                -> the Scratch list "level start angles"
#   ceil, floor  (hue, saturation) on Scratch's pen color scale (0-100):
#                0 red, 8 orange, 15 yellow, 33 green, 50 cyan, 63 blue, 75 purple, 90 pink.
#                Saturation 0 = grey, 100 = full color.
#                -> "level ceiling hues" / "level ceiling saturations" / "level floor ..."
#   secret_look  which wall digit the secret walls (S) look like on this level, so they blend in
#                -> "level secret wall looks"
# Other per-level settings (how far rays travel, darkness, par times...) are tables at the top
# of build.py, and the level cards are in assets6.py.
#
# Above each level: a plan of its map, so you can find your way around the text file.
# Positions are (column, row), counting from 0 like the rest of this file.
LEVELS = [
    # LEVEL 1: THE OUTPOST (20 x 20). Monsters: imps.
    #   rows 1-5    the start room (P at 1, 2, the shotgun N just below), then a door (D at 5, 2)
    #               into the north hall
    #   row 6       a wall of 2s with one door (column 12)
    #   rows 7-11   the middle hall: the imp pack, two barrels (E), crates (3 and 4)
    #   row 12      a wall with one door (column 15)
    #   rows 13-18  the bottom room. The exit X is in the LEFT wall (0, 16). Bottom right: a
    #               secret wall S (15, 18) hides a closet with shells (A) and health (H).
    dict(name="The Outpost", rows=load_map(1), angle=0, ceil=(0, 10), floor=(7, 45), secret_look="2"),

    # LEVEL 2: THE PROCESSING PLANT (24 x 24). Monsters: spitters. One key: red.
    #   rows 1-7    north rooms, split by a wall of 7s at column 15. The RED door R (15, 4) leads
    #               to the north-east room, which has the exit X in its top wall (19, 0).
    #               Top left: a secret wall S (3, 1) hides a closet.
    #   row 8       a wall with one door (column 12)
    #   rows 9-16   a west room with the red key K (2, 10) and its door at (8, 12), and a big
    #               east hall with the chaingun Q (12, 10)
    #   row 17      a wall with one door (column 16)
    #   rows 18-22  the bottom: the player starts in the west room (P at 2, 20)
    #   Route: bottom -> middle -> red key -> north -> red door -> exit.
    dict(name="The Processing Plant", rows=load_map(2), angle=0, ceil=(50, 30), floor=(35, 30), secret_look="7"),

    # LEVEL 3: THE FORTRESS (28 x 28). Monsters: golems, and the WARDEN (boss). Keys: red, blue.
    #   rows 1-11   three wings side by side, split by walls at columns 9 and 18:
    #               west wing (red key K) | inner keep (blue key J) | east wing (the warden W)
    #   row 12      a wall with three doors: plain D into the west wing, RED R into the keep,
    #               BLUE B into the east wing
    #   rows 13-20  the courtyard, with pillars (4) and a central block (9)
    #   row 21      a wall with three doors into the side rooms
    #   rows 22-26  the side rooms; the player starts in the middle one (P at 13, 25)
    #   The exit X (27, 3) is in a closet sealed by a SKULL DOOR Z (25, 3): only the warden's
    #   skull key opens it. A secret wall S (15, 1) in the keep hides shells and health.
    dict(name="The Fortress", rows=load_map(3), angle=270, ceil=(95, 45), floor=(2, 40), secret_look="9"),

    # LEVEL 4: THE FOUNDRY (36 x 36). Chargers, plus imps, spitters and golems. One key: red.
    #   rows 1-7    three north rooms (walls at columns 11 and 24); the red key K (2, 2) and the
    #               rocket launcher L (17, 2) are up here
    #   row 8       a wall with two plain doors and the RED door (32, 8)
    #   rows 9-26   west corridor | the furnace hall with 2 x 2 pillars | east corridor
    #               (walls at columns 6 and 29). The middle pillar is hollow: a secret wall S
    #               (17, 16) hides rockets inside it.
    #   row 27      a wall with two doors
    #   rows 28-34  the loading bay, where the player starts (P at 18, 33)
    #   The exit X (30, 0) is in the top wall of the north-east room, behind the red door.
    dict(name="The Foundry", rows=load_map(4), angle=270, ceil=(5, 40), floor=(8, 35), secret_look="4"),

    # LEVEL 5: THE SUNKEN VAULTS (38 x 38). Wraiths, plus the others. Keys: red, blue. Dark!
    #   Solid rock (7) with caves dug out of it, joined by tunnels one square wide. Cave corners
    #   are rounded off with wall 3.
    #   The player starts in the south-west cave (P at 5, 33). The red key K (3, 3) is in the
    #   north-west cave; the RED door (21, 9) blocks the tunnel to the north cave with the blue
    #   key J (25, 3); the BLUE door (28, 14) blocks the tunnel from the middle vault to the east
    #   cave, which has the exit X (36, 5) in its east wall.
    #   A secret wall S (32, 23) above the south-east cave hides a health pack.
    dict(name="The Sunken Vaults", rows=load_map(5), angle=270, ceil=(55, 20), floor=(50, 25), secret_look="7"),

    # LEVEL 6: THE CORE (40 x 40). Everything, and the COLOSSUS (boss). Keys: red, blue.
    #   A ring corridor 4 squares wide runs all the way round the outside. Inside it: two north
    #   rooms, a west wing, an east wing, a south wing, and the arena in the middle.
    #   Route: start at the bottom of the ring (P at 20, 37) -> red key K (7, 20) in the west wing
    #   -> RED door (34, 20) into the east wing -> blue key J (32, 26) -> BLUE door (20, 28) from
    #   the south wing into the arena -> beat the colossus T (20, 18) for the skull key ->
    #   SKULL door Z (20, 12) in the arena's north wall -> the exit X (20, 10).
    #   A secret wall S (5, 31) off the ring hides a health pack.
    dict(name="The Core", rows=load_map(6), angle=270, ceil=(98, 60), floor=(0, 50), secret_look="9"),
]


# =================================================================================================
# CHECKING THAT EVERY LEVEL CAN BE FINISHED
# =================================================================================================
# Groups of letters (sets), so the checks below can ask "is this letter a wall?" in one go.
WALL_LETTERS = set("123456789DRBXSZ")     # anything you can't simply walk through (doors included)
MONSTER_LETTERS = set("MVGWCFT")
BOSS_LETTERS = set("WT")                  # the warden and the colossus
PICKUP_LETTERS = set("HAIUNQL")           # health, ammo and weapons
KEY_LETTERS = set("KJ")                   # red key, blue key
FLOOR_LETTERS = set("0P") | KEY_LETTERS | PICKUP_LETTERS | MONSTER_LETTERS   # things stand on floor
EDGE_LETTERS = set("123456789X")          # what the outside edge may be made of
# E (a barrel) is in none of these groups: it's solid until it explodes, so the checks treat it
# as something that blocks the way.

# One step right, left, down and up, as (column change, row change).
NEIGHBOR_STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def reachable_squares(map_rows, start, walkable_letters):
    """FLOOD FILL: every square you can walk to from 'start', stepping up, down, left or right,
    moving only onto squares whose letter is in 'walkable_letters'. Returns a set of
    (column, row) squares.

    It works like spilling paint at the start square:
      1. The start square is painted, and goes on the to-do list.
      2. Take the next square off the to-do list and look at its 4 neighbors.
      3. Any neighbor that is inside the map, walkable and not painted yet gets painted and
         added to the to-do list.
      4. Repeat until the to-do list is empty: the paint has spread everywhere it can.
    This is called "breadth-first search". Paint bucket tools in drawing programs fill shapes
    the same way.
    """
    map_height, map_width = len(map_rows), len(map_rows[0])
    painted, to_do = {start}, deque([start])
    while to_do:
        column, row = to_do.popleft()
        for column_step, row_step in NEIGHBOR_STEPS:
            neighbor_column, neighbor_row = column + column_step, row + row_step
            neighbor = (neighbor_column, neighbor_row)
            if (0 <= neighbor_column < map_width and 0 <= neighbor_row < map_height
                    and neighbor not in painted
                    and map_rows[neighbor_row][neighbor_column] in walkable_letters):
                painted.add(neighbor)
                to_do.append(neighbor)
    return painted


def next_to(column, row, squares):
    """True if any of the 4 squares beside (column, row) is in the set 'squares'."""
    return any((column + column_step, row + row_step) in squares for column_step, row_step in NEIGHBOR_STEPS)


def validate(level):
    """Checks a map the way a careful player would: everything that matters must be reachable
    WITHOUT opening secret walls or blowing up barrels; pickups may hide behind secrets.

    If a check fails, it stops with a LevelError whose message names the level, says what is
    wrong, and gives the square. build.py calls this for every level, so a broken map stops
    the build. If everything passes, it returns a count of each letter.
    """
    name, map_rows = level["name"], level["rows"]
    map_height, map_width = len(map_rows), len(map_rows[0])

    # CHECK 1: every row is as long as the first one (the map is a proper rectangle).
    for row, row_text in enumerate(map_rows):
        check(len(row_text) == map_width,
              f"{name}: row {row} has {len(row_text)} letters but row 0 has {map_width}. "
              "Every row must be the same length.")

    # A list of every square and its letter, so the checks below can go through them all.
    every_square = [(column, row, map_rows[row][column])
                    for row in range(map_height) for column in range(map_width)]

    # CHECK 2: no unknown letters (only walls, floor things and barrels are allowed).
    for column, row, letter in every_square:
        check(letter in WALL_LETTERS | FLOOR_LETTERS | {"E"},
              f"{name}: unknown letter '{letter}' at {where(column, row)}. "
              "See the LEGEND at the top of levels.py for the letters you can use.")

    # CHECK 3: the outside edge is all wall (or the exit switch), so nobody can walk off the map
    # and rays always hit something.
    for column, row, letter in every_square:
        on_edge = row in (0, map_height - 1) or column in (0, map_width - 1)
        check(not on_edge or letter in EDGE_LETTERS,
              f"{name}: the outside edge must be wall, but there is a '{letter}' at {where(column, row)}.")

    # CHECK 4: exactly one player start.
    starts = [(column, row) for column, row, letter in every_square if letter == "P"]
    check(len(starts) == 1,
          f"{name}: there must be exactly one player start P, but there are {len(starts)}"
          + (": " + "; ".join(where(column, row) for column, row in starts) if starts else "."))
    start = starts[0]

    # PLAY THE LEVEL, ROUGHLY: work out what a player could reach, the way they would really
    # play it. At first only plain doors (D) open. Each pass flood-fills from the start:
    #   - found the red key K? Next pass, red doors R count as open too.
    #   - found the blue key J? Then blue doors B open.
    #   - reached a boss? Beating it drops the skull key, so skull doors Z open.
    # Keep going until a pass finds nothing new. 'reachable' is then everything the player can
    # get to without secret walls.
    keys_found = set()
    while True:
        walkable = FLOOR_LETTERS | {"D"}
        if "K" in keys_found:
            walkable = walkable | {"R"}
        if "J" in keys_found:
            walkable = walkable | {"B"}
        if "boss" in keys_found:
            walkable = walkable | {"Z"}
        reachable = reachable_squares(map_rows, start, walkable)
        letters_reached = {map_rows[row][column] for column, row in reachable}
        found_this_pass = letters_reached & KEY_LETTERS
        if letters_reached & BOSS_LETTERS:
            found_this_pass.add("boss")          # beating a reachable boss drops the skull key
        if found_this_pass <= keys_found:        # nothing new this pass (a subset): stop
            break
        keys_found |= found_this_pass            # add the new keys and try again
    # The same, but with secret walls opened too. Bonus pickups are allowed to hide in there.
    reachable_with_secrets = reachable_squares(map_rows, start, walkable | {"S"})

    # CHECK 5: look at every square of the map.
    for column, row, letter in every_square:
        # Monsters and keys must be reachable WITHOUT secrets (you need them to finish).
        if letter in MONSTER_LETTERS | KEY_LETTERS:
            check((column, row) in reachable,
                  f"{name}: the '{letter}' at {where(column, row)} can't be reached. Monsters and "
                  "keys must be reachable without secret walls or blowing up barrels.")
        # Pickups just have to be reachable somehow, secrets included.
        if letter in PICKUP_LETTERS:
            check((column, row) in reachable_with_secrets,
                  f"{name}: the '{letter}' at {where(column, row)} can't be reached, even through secret walls.")
        # A secret wall must touch a reachable square, or nobody could ever press E on it.
        if letter == "S":
            check(next_to(column, row, reachable),
                  f"{name}: the secret wall at {where(column, row)} has no reachable floor next to it.")
        # Same for barrels: you have to be able to get near one to shoot it.
        if letter == "E":
            check(next_to(column, row, reachable),
                  f"{name}: the barrel at {where(column, row)} has no reachable floor next to it.")

    # CHECK 6: at most one boss (there is only one boss health bar).
    bosses = [(column, row) for column, row, letter in every_square if letter in BOSS_LETTERS]
    check(len(bosses) <= 1,
          f"{name}: only one boss per level, but there are {len(bosses)}: "
          + "; ".join(where(column, row) for column, row in bosses))

    # A skull door needs a boss to drop the skull key. (Checked before the exit, because a
    # missing boss would also make the exit unreachable, and this message explains why.)
    whole_map_text = "".join(map_rows)        # the whole map as one long string, handy for counting
    if "Z" in whole_map_text:
        check(len(bosses) == 1, f"{name}: a skull door (Z) needs a boss (W or T) to drop the skull key.")

    # CHECK 7: exactly one exit switch, and a reachable square right next to it (the switch is
    # in a wall, so you stand beside it and press E).
    exits = [(column, row) for column, row, letter in every_square if letter == "X"]
    check(len(exits) == 1, f"{name}: there must be exactly one exit switch X, but there are {len(exits)}.")
    exit_column, exit_row = exits[0]
    check(next_to(exit_column, exit_row, reachable),
          f"{name}: the exit switch at {where(exit_column, exit_row)} can't be reached. Check the "
          "keys come before their doors, and that floor touches the switch.")

    # CHECK 8: the skull door must really GUARD the exit. Flood-fill again with every door open
    # EXCEPT the skull door: if the exit can still be reached, players could walk around the
    # boss fight, so the skull door is in the wrong place.
    if "Z" in whole_map_text:
        reachable_without_skull_door = reachable_squares(map_rows, start, walkable - {"Z"})
        check(not next_to(exit_column, exit_row, reachable_without_skull_door),
              f"{name}: the exit can be reached without going through the skull door, so players "
              "could skip the boss. Put the Z in the only way into the exit.")

    # Everything passed: report the map's size and how many of each letter it has.
    return dict(size=f"{map_width}x{map_height}",
                **{letter: whole_map_text.count(letter) for letter in "MVGWCFTHAIUNQLKJESZ"})


# Running this file directly (python3 src/levels.py) checks every level and prints its contents.
# (When build.py imports this file instead, this part is skipped.)
if __name__ == "__main__":
    import sys
    try:
        for level in LEVELS:
            print(level["name"], validate(level))
    except LevelError as problem:
        print("MAP PROBLEM:", problem)
        sys.exit(1)
