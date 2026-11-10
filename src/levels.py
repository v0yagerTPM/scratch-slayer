"""Level maps for Scratch Slayer.

WHERE THE MAPS ARE
==================
Each level has one or more MAPS to choose from (map A, map B, map C ...). When a level starts,
the game picks one of them at random, so the game plays differently each time. Each map is a
plain text file in the src/maps folder:
    src/maps/level 1 map A.txt   src/maps/level 1 map B.txt   ...   src/maps/level 6 map A.txt
One line of the file = one ROW of the map, top row first. Each letter is one SQUARE.

These are EXACTLY the files Scratch makes when you right-click the list "level 1 map A" on the
stage and choose "export", and the files it reads with "import". (Scratch names an exported
list after the list, which is where the file names come from.) So a map can travel both ways:
  - from Scratch into this project: export the list, put the file in src/maps (replacing the
    old one, same name), then run npm test. The build checks the map and puts it in the game.
  - from this project into Scratch: import the file into the list in the Scratch editor.
That's why the files hold nothing but map rows: no comments or notes, because Scratch would
import every line, notes included, as a row of the map. The notes about each map's layout
are in this file instead, next to the map's settings further down.

Edit a map in any plain text editor (Notepad, TextEdit in plain text mode, VS Code). Use a
monospace font such as Consolas or Courier so the columns line up; most code editors show the
column number at the bottom, which helps find a square.

HOW A MAP IS USED
=================
load_map() reads a file into a Python list of strings, one string per row. game/stage.py copies
that list straight into the Scratch list "level N map A" (one string = one list item), and the
Engine's 'load level' block reads it back letter by letter. So the file IS the map.

COORDINATES: a square is (column, row), both counting from 0.
  column = how far along the row (0 = the first letter of the line)
  row    = which line of the file (0 = the TOP line)
So map_rows[row][column] is the letter on a square. Notice the order: row first, then column.
The game uses the same numbers ("player x" 3.5 = the middle of column 3, "player y" = the row).
Scratch lists and text editors count from 1 instead: row 0, column 0 is line 1, letter 1.

At the bottom, validate() plays detective: it checks every map can really be finished.
The build runs validate() on every level each time (game/config.py), so a broken map stops the build
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

# A level's maps are lettered in order: its first map is map A, the second map B, and so on.
MAP_LETTERS = "ABCDEFGHI"


def map_list_name(level_number, map_letter):
    """The name of a map's Scratch list (and of its file): "level 1 map A"."""
    return f"level {level_number} map {map_letter}"


def map_file_path(level_number, map_letter):
    """src/maps/level 1 map A.txt, src/maps/level 1 map B.txt ..."""
    return os.path.join(MAPS_FOLDER, map_list_name(level_number, map_letter) + ".txt")


def load_map(level_number, map_letter):
    """Read one map file and return its rows: a list of strings, top row first.

    Line endings: Windows ends each line with two characters (carriage return + new line),
    Mac and Linux with one (new line). splitlines() understands both, so a file exported from
    Scratch on any computer works. A file may or may not end with a final line break; blank
    lines at the very end are ignored. Everything else is kept exactly as it is, so a stray
    space or tab becomes an 'unknown letter' that validate() points out.
    """
    name = map_list_name(level_number, map_letter)
    path = map_file_path(level_number, map_letter)
    check(os.path.exists(path), f"{name}: the map file is missing. Expected {path}")
    with open(path, encoding="utf-8-sig") as map_file:   # utf-8-sig also skips the invisible
        map_rows = map_file.read().splitlines()          # marker some Windows editors add
    while map_rows and map_rows[-1].strip() == "":       # drop blank lines at the end
        map_rows.pop()
    check(map_rows, f"{name}: the map file {path} is empty.")
    return map_rows


# =================================================================================================
# THE LEVEL LIST: everything about each level and its maps, in one record per level. The build
# reads this: game/stage.py turns the settings into Scratch lists, and pictures/level_cards.py
# draws the cards.
# =================================================================================================
# For each LEVEL (the same whichever map you get):
#   name         the level's name. The level card shows it in capitals.
#   episode      1 or 2. Each episode has its own music. Finishing the last level of episode 1
#                shows "EPISODE 1 COMPLETE" instead of "LEVEL COMPLETE".
#   best_weapon  starting at this level from the options menu's level select gives you
#                weapons 1 to this one, with some ammo -> "level select best weapon"
#   card         the level intro card's words about the level's new enemy: enemy (the big
#                word), lines (two lines about the enemy), boss (a warning line, or None)
#   card_monster the monster type (1-7, see "monster names") that walks onto the card
#                -> "level intro monster"
#   card_boss    a boss type shown in the card's background, or 0 for none -> "level intro boss"
#   maps         the level's maps: map A first, then B, C ... One is picked when the level starts.
#
# For each MAP of a level:
#   name         the map's own name ("Furnace Hall"). A level with more than one map shows it on
#                the level card, under the level's name, and the heading says LEVEL 1-B.
#   rows         the map, read from its file (becomes the Scratch list "level N map A")
#   goal         the card's goal line ("Find the red key, then the exit"). Each map has its own,
#                because the maps of a level can use different keys.
#   tint         the card's background glow color
#   angle        the direction the player faces at the start, in degrees:
#                0 = right (along the row), 90 = down, 180 = left, 270 = up (toward row 0)
#                -> the Scratch list "map start angles"
#   ceil, floor  (hue, saturation) on Scratch's pen color scale (0-100):
#                0 red, 8 orange, 15 yellow, 33 green, 50 cyan, 63 blue, 75 purple, 90 pink.
#                Saturation 0 = grey, 100 = full color.
#                -> "map ceiling hues" / "map ceiling saturations" / "map floor ..."
#   secret_look  which wall digit the secret walls (S) look like on this map, so they blend in
#                -> "map secret wall looks"
#   max_ray_steps    how many squares a ray may travel before giving up. Big maps need a limit
#                    so the game stays fast; walls that far away are black anyway.
#                    -> "map max ray steps"
#   light_falloff    how quickly walls fade to black with distance (bigger = darker map)
#                    -> "map light falloffs"
#   sprite_darkness  how much monsters and items darken with distance (0 = not at all)
#                    -> "map sprite darkness"
#   par_seconds      the par time on the tally screen: about 3 times as long as simply walking
#                    the shortest route to the exit (keys and boss included), which leaves time
#                    for fighting, rounded to the nearest 15 seconds -> "map par times"
# Colors, darkness and draw distance belong to the map, so one map of a level can be a night
# version of the place, or a flooded one.
#
# ADDING A MAP to a level (in the Python source): save it as src/maps/level 2 map B.txt (the
# next letter), add a record for it at the end of that level's maps, and run npm test.
# ADDING A LEVEL: save its map as src/maps/level 7 map A.txt, add a record at the end of this
# list, and run npm test. Either way the build makes everything else from these records: the
# Scratch lists, the level loader's blocks, the level cards and their headings.
# (To add a map or a level inside Scratch instead, see the Stage guide.)
#
# Above each map: a plan of it, so you can find your way around the text file.
# Positions are (column, row), counting from 0 like the rest of this file.
LEVELS = [
    dict(name="The Outpost", episode=1, best_weapon=2,
         card=dict(enemy="IMP", lines=["Fast and vicious up close.", "Keep your distance and blast it."], boss=None),
         card_monster=1, card_boss=0, maps=[
        # LEVEL 1, MAP A: THREE HALLS (20 x 20). Monsters: imps.
        #   rows 1-5    the start room (P at 1, 2, the shotgun N just below), then a door (D at 5, 2)
        #               into the north hall
        #   row 6       a wall of 2s with one door (column 12)
        #   rows 7-11   the middle hall: the imp pack, two barrels (E), crates (3 and 4)
        #   row 12      a wall with one door (column 15)
        #   rows 13-18  the bottom room. The exit X is in the LEFT wall (0, 16). Bottom right: a
        #               secret wall S (15, 18) hides a closet with shells (A) and health (H).
        dict(name="Three Halls", rows=load_map(1, "A"), goal="Find the exit switch", tint="#5a2a10",
             angle=0, ceil=(0, 10), floor=(7, 45), secret_look="2",
             max_ray_steps=64, light_falloff=4.5, sprite_darkness=0, par_seconds=60),
    ]),

    dict(name="The Processing Plant", episode=1, best_weapon=3,
         card=dict(enemy="SPITTER", lines=["Spits acid from far away. Strafe", "with A and D to dodge it."], boss=None),
         card_monster=2, card_boss=0, maps=[
        # LEVEL 2, MAP A: THE RED DOOR (24 x 24). Monsters: spitters. One key: red.
        #   rows 1-7    north rooms, split by a wall of 7s at column 15. The RED door R (15, 4) leads
        #               to the north-east room, which has the exit X in its top wall (19, 0).
        #               Top left: a secret wall S (3, 1) hides a closet.
        #   row 8       a wall with one door (column 12)
        #   rows 9-16   a west room with the red key K (2, 10) and its door at (8, 12), and a big
        #               east hall with the chaingun Q (12, 10)
        #   row 17      a wall with one door (column 16)
        #   rows 18-22  the bottom: the player starts in the west room (P at 2, 20)
        #   Route: bottom -> middle -> red key -> north -> red door -> exit.
        dict(name="The Red Door", rows=load_map(2, "A"), goal="Find the red key, then the exit", tint="#1f5a14",
             angle=0, ceil=(50, 30), floor=(35, 30), secret_look="7",
             max_ray_steps=64, light_falloff=4.5, sprite_darkness=0, par_seconds=90),
    ]),

    dict(name="The Fortress", episode=1, best_weapon=4,
         card=dict(enemy="GOLEM", lines=["Slow, tough, and hits like a truck.", "Lure it next to a barrel."],
                   boss="BOSS: THE WARDEN carries the SKULL KEY to the exit"),
         card_monster=3, card_boss=4, maps=[
        # LEVEL 3, MAP A: THREE WINGS (28 x 28). Golems and the WARDEN (boss). Keys: red, blue.
        #   rows 1-11   three wings side by side, split by walls at columns 9 and 18:
        #               west wing (red key K) | inner keep (blue key J) | east wing (the warden W)
        #   row 12      a wall with three doors: plain D into the west wing, RED R into the keep,
        #               BLUE B into the east wing
        #   rows 13-20  the courtyard, with pillars (4) and a central block (9)
        #   row 21      a wall with three doors into the side rooms
        #   rows 22-26  the side rooms; the player starts in the middle one (P at 13, 25)
        #   The exit X (27, 3) is in a closet sealed by a SKULL DOOR Z (25, 3): only the warden's
        #   skull key opens it. A secret wall S (15, 1) in the keep hides shells and health.
        dict(name="Three Wings", rows=load_map(3, "A"), goal="Two keys, then slay the Warden", tint="#5a0f2a",
             angle=270, ceil=(95, 45), floor=(2, 40), secret_look="9",
             max_ray_steps=64, light_falloff=4.5, sprite_darkness=0, par_seconds=135),
    ]),

    dict(name="The Foundry", episode=2, best_weapon=4,
         card=dict(enemy="CHARGER", lines=["Lowers its head, then charges.", "Sidestep it and it slams into a wall."],
                   boss=None),
         card_monster=5, card_boss=0, maps=[
        # LEVEL 4, MAP A: FURNACE HALL (36 x 36). Chargers, plus imps, spitters and golems. Key: red.
        #   rows 1-7    three north rooms (walls at columns 11 and 24); the red key K (2, 2) and the
        #               rocket launcher L (17, 2) are up here
        #   row 8       a wall with two plain doors and the RED door (32, 8)
        #   rows 9-26   west corridor | the furnace hall with 2 x 2 pillars | east corridor
        #               (walls at columns 6 and 29). The middle pillar is hollow: a secret wall S
        #               (17, 16) hides rockets inside it.
        #   row 27      a wall with two doors
        #   rows 28-34  the loading bay, where the player starts (P at 18, 33)
        #   The exit X (30, 0) is in the top wall of the north-east room, behind the red door.
        dict(name="Furnace Hall", rows=load_map(4, "A"), goal="Find the red key, then the exit", tint="#6a2a08",
             angle=270, ceil=(5, 40), floor=(8, 35), secret_look="4",
             max_ray_steps=34, light_falloff=4.5, sprite_darkness=2, par_seconds=165),
    ]),

    dict(name="The Sunken Vaults", episode=2, best_weapon=5,
         card=dict(enemy="WRAITH", lines=["Almost invisible from far away,", "and it blinks sideways. Stay sharp."],
                   boss=None),
         card_monster=6, card_boss=0, maps=[
        # LEVEL 5, MAP A: FLOODED CAVES (38 x 38). Wraiths, plus the others. Keys: red, blue. Dark!
        #   Solid rock (7) with caves dug out of it, joined by tunnels one square wide. Cave corners
        #   are rounded off with wall 3.
        #   The player starts in the south-west cave (P at 5, 33). The red key K (3, 3) is in the
        #   north-west cave; the RED door (21, 9) blocks the tunnel to the north cave with the blue
        #   key J (25, 3); the BLUE door (28, 14) blocks the tunnel from the middle vault to the east
        #   cave, which has the exit X (36, 5) in its east wall.
        #   A secret wall S (32, 23) above the south-east cave hides a health pack.
        dict(name="Flooded Caves", rows=load_map(5, "A"), goal="Two keys, deep in the dark", tint="#0f3a4a",
             angle=270, ceil=(55, 20), floor=(50, 25), secret_look="7",
             max_ray_steps=26, light_falloff=6.5, sprite_darkness=5, par_seconds=180),
    ]),

    dict(name="The Core", episode=2, best_weapon=5,
         card=dict(enemy="THE COLOSSUS", lines=["Huge, armored, and it gets angrier.", "At half health it calls for help."],
                   boss="FINAL BOSS: the exit is sealed until it falls"),
         card_monster=7, card_boss=0, maps=[
        # LEVEL 6, MAP A: THE RING (40 x 40). Everything, and the COLOSSUS (boss). Keys: red, blue.
        #   A ring corridor 4 squares wide runs all the way round the outside. Inside it: two north
        #   rooms, a west wing, an east wing, a south wing, and the arena in the middle.
        #   Route: start at the bottom of the ring (P at 20, 37) -> red key K (7, 20) in the west wing
        #   -> RED door (34, 20) into the east wing -> blue key J (32, 26) -> BLUE door (20, 28) from
        #   the south wing into the arena -> beat the colossus T (20, 18) for the skull key ->
        #   SKULL door Z (20, 12) in the arena's north wall -> the exit X (20, 10).
        #   A secret wall S (5, 31) off the ring hides a health pack.
        dict(name="The Ring", rows=load_map(6, "A"), goal="Destroy the Colossus, take its key", tint="#4a0a3a",
             angle=270, ceil=(98, 60), floor=(0, 50), secret_look="9",
             max_ray_steps=36, light_falloff=4.2, sprite_darkness=2, par_seconds=240),
    ]),
]


def every_map():
    """Every map of every level, in order: (level number, map letter, level record, map record).
    Level 1's maps come first (A, B, C ...), then level 2's, and so on. This order is the order of
    the Scratch lists 'map list names', 'map start angles' and the other 'map ...' lists."""
    for level_number, level in enumerate(LEVELS, start=1):
        for map_letter, game_map in zip(MAP_LETTERS, level["maps"]):
            yield level_number, map_letter, level, game_map


def map_title(level_number, map_letter, level, game_map):
    """How messages and the balance report name a map: 'The Outpost, map A (Three Halls)'."""
    return f"{level['name']}, map {map_letter} ({game_map['name']})"


def check_level_list():
    """Every level needs at least one map, and no more maps than there are letters for."""
    for level_number, level in enumerate(LEVELS, start=1):
        check(level["maps"], f"level {level_number} ({level['name']}) has no maps.")
        check(len(level["maps"]) <= len(MAP_LETTERS),
              f"level {level_number} ({level['name']}) has {len(level['maps'])} maps, but there are only "
              f"{len(MAP_LETTERS)} map letters ({MAP_LETTERS}).")


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
    """Checks one map the way a careful player would: everything that matters must be reachable
    WITHOUT opening secret walls or blowing up barrels; pickups may hide behind secrets.
    'level' is a dict with the map's 'rows' and a 'name' for the messages, such as
    "The Outpost, map A (Three Halls)".

    If a check fails, it stops with a LevelError whose message names the map, says what is
    wrong, and gives the square. The build calls this for every map of every level, so a broken
    map stops the build. If everything passes, it returns a count of each letter.
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


# =================================================================================================
# BALANCE REPORT: is there enough ammo and health on a map for its monsters?
# =================================================================================================
def balance(map_rows, config, difficulty_name="normal"):
    """Adds up what a map gives you and what it throws at you, using the game's own tables in
    game/config.py (passed in as 'config'), at one difficulty ("easy", "normal" or "hard"):
      monster health  every monster's hit points added up, scaled by the difficulty's 'monster
                      health' (a colossus also calls 2 chargers)
      ammo damage     how much damage all the ammo on the map can do: a bullet does 1, a shell
                      about 2.5 (the shotgun does 2 or 3), a rocket up to 6 to everything near the
                      blast. Weapons count for the ammo they come with. Only the supplies the
                      difficulty keeps count, and each gives its 'pickup amount'.
      ammo ratio      ammo damage / monster health. Below 1, the map's ammo can't kill
                      everything (you also bring ammo from the last level). The bigger it
                      is, the easier the map.
      health          what the health packs that appear give, added up
    Rounding is done the way the game does it, so these are the game's own numbers. Barrels and
    your fists aren't counted, so the real fight is a bit easier than the numbers."""
    difficulty = next(row for row in config.DIFFICULTIES if row[0] == difficulty_name)
    monster_health_percent, supplies_percent, pickup_percent = difficulty[2], difficulty[3], difficulty[4]
    whole_map_text = "".join(map_rows).upper()

    def monster_health(letter):
        """One monster's starting health at this difficulty (rounded, like the game)."""
        row = next(row for row in config.MONSTER_TYPES if row[0] == letter)
        return config.scratch_round(row[2] * monster_health_percent / 100)
    monster_letters = [row[0] for row in config.MONSTER_TYPES]
    total_health = sum(monster_health(letter) * whole_map_text.count(letter) for letter in monster_letters)
    if "T" in whole_map_text:
        total_health += 2 * monster_health(config.MONSTER_TYPES[config.CHARGER_TYPE - 1][0])

    shotgun = config.WEAPON_TYPES[2]
    damage_per_ammo = {"bullets": 1, "shells": (shotgun[3] + shotgun[4]) / 2,
                       "rockets": config.EXPLOSION_DAMAGE_UP_CLOSE}
    kept = config.supplies_kept(map_rows, supplies_percent)
    pickups_on_map = ([letter for column, row, letter in kept]                          # supplies that appear
                      + [letter for letter in whole_map_text if letter in "NQL"])       # weapons always do
    ammo_damage = sum(damage_per_ammo[config.AMMO_PICKUPS[letter][0]]
                      * config.scratch_round(config.AMMO_PICKUPS[letter][1] * pickup_percent / 100)
                      for letter in pickups_on_map if letter in config.AMMO_PICKUPS)
    health = pickups_on_map.count("H") * config.scratch_round(config.HEALTH_PACK * pickup_percent / 100)
    return dict(monsters=sum(whole_map_text.count(letter) for letter in monster_letters),
                monster_health=total_health, ammo_damage=round(ammo_damage),
                ammo_ratio=round(ammo_damage / total_health, 2) if total_health else None,
                health=health)


# Running this file directly (python3 src/levels.py) checks every map, prints what is in it,
# then prints the balance report. (When the build imports this file instead, this part is skipped.)
if __name__ == "__main__":
    import sys
    try:
        check_level_list()
        for level_number, map_letter, level, game_map in every_map():
            title = map_title(level_number, map_letter, level, game_map)
            print(title, validate(dict(name=title, rows=game_map["rows"])))
    except LevelError as problem:
        print("MAP PROBLEM:", problem)
        sys.exit(1)
    import game.config   # the monster, weapon and pickup tables (imported here, not at the top,
                         # because game/config.py itself imports this file)
    print()
    print("BALANCE REPORT (see balance() above). Ammo ratio = ammo damage / monster health; bigger = easier.")
    difficulty_names = [row[0] for row in game.config.DIFFICULTIES]
    print(f"{'':<50}{'':>9}{'ammo ratio':^24}{'health':^24}")
    print(f"{'map':<50}{'monsters':>9}" + "".join(f"{name:>8}" for name in difficulty_names) * 2)
    for level_number, map_letter, level, game_map in every_map():
        numbers = {name: balance(game_map["rows"], game.config, name) for name in difficulty_names}
        print(f"{map_title(level_number, map_letter, level, game_map):<50}{numbers['normal']['monsters']:>9}"
              + "".join(f"{str(numbers[name]['ammo_ratio']):>8}" for name in difficulty_names)
              + "".join(f"{numbers[name]['health']:>8}" for name in difficulty_names))
