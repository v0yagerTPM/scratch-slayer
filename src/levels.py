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

The easiest way to draw a map is the map editor: open docs/map-editor.html in a web browser.
You paint squares with the mouse, it checks the map as you go, and it saves the file. (It is
made by src/map_editor.py, and its map checker is a JavaScript copy of validate() below.)
Or edit a map in any plain text editor (Notepad, TextEdit in plain text mode, VS Code). Use a
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
  ?      mystery item: a random health pack or box of ammo, picked when the map loads
         (secret closets use these, so their loot is different each time)
  K      red key         J  blue key
  E      exploding barrel
"""
import math
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
        # LEVEL 1, MAP A: FRONT GATE (28 x 28). 17 imps. No keys. Route: about 63 squares.
        #   rows 22-26  the approach, outside the walls: the player starts at the bottom (P at 13, 25)
        #               facing the gate, between two sandbag walls (3). Two imps, a barrel.
        #   row 21      the outer wall with the main gate (D at 13, 21)
        #   rows 16-20  the gatehouse: a hall in the middle (columns 10-17) and two guard rooms,
        #               west and east, with doors at (9, 18) and (18, 18). The WEST room has the
        #               shotgun N (2, 17) and the only door on into the courtyard (4, 15). The east
        #               room is a side trip: a secret wall S (24, 19) hides shells and health.
        #   rows 6-14   the courtyard: crates (2), sandbags (3), a red monument (4) in the middle,
        #               two barrels and six imps
        #   row 5       the command post's front wall, with ONE door, on the far east side (23, 5)
        #   rows 1-4    the command post: east office -> door (19, 3) -> the hall with the exit X
        #               (13, 0) in its top wall. A door (8, 3) leads on to the west office (health).
        dict(name="Front Gate", rows=load_map(1, "A"), goal="Reach the command post", tint="#5a2a10",
             angle=270, ceil=(0, 10), floor=(7, 45), secret_look="5",
             max_ray_steps=40, light_falloff=4.5, sprite_darkness=0, par_seconds=90),
        # LEVEL 1, MAP B: BARRACKS (30 x 26). 18 imps, indoors and darker. No keys. Route: about 69.
        #   The building has a corridor down the middle (columns 14-15) and a long corridor across
        #   (rows 12-13), but the walls block the short ways:
        #   rows 15-24  the player starts at the south end of the middle corridor (P at 14, 23).
        #               West: the mess hall with its tables (2), door (13, 19), and a pantry behind
        #               a secret wall S (3, 23). East: the armory with the shotgun N (24, 23), door
        #               (16, 21), and a bunk room above it (door 22, 20). The armory side is a dead
        #               end: the way on is through the mess hall's far door (2, 14).
        #   rows 12-13  the cross corridor. It joins the north half of the middle corridor and the
        #               north-east bunk room (door 23, 11).
        #   rows 6-10   bunk rooms full of beds (2), west (door 13, 8, from the middle corridor) and
        #               east (door 23, 11)
        #   rows 1-4    the commander's office in the middle with the exit X (14, 0), between two
        #               small rooms. Only the north-east room has a door into it (20, 3): go
        #               corridor -> north-east bunk room -> door (25, 5) -> door (20, 3).
        dict(name="Barracks", rows=load_map(1, "B"), goal="Find the commander's office", tint="#24304a",
             angle=270, ceil=(60, 12), floor=(33, 22), secret_look="9",
             max_ray_steps=40, light_falloff=5.5, sprite_darkness=1, par_seconds=105),
        # LEVEL 1, MAP C: MOTOR POOL (30 x 28). 18 imps, out in the open (sky-blue ceiling, grey
        # asphalt floor). No keys. Route: about 61 squares.
        #   rows 21-26  the player starts in the entry lane (P at 14, 25). Its doors lead west into
        #               the workshop (shotgun N at 2, 22, door 10, 23) and east into the office
        #               (door 19, 23), where a secret wall S (26, 25) hides shells and health.
        #   row 20      the workshop's door (5, 20) is the only way out into the yard
        #   rows 7-19   the yard: trucks (6), a jeep (2), a tank (9) and, in the south-east corner,
        #               a fenced fuel depot full of barrels (E) with an opening on its west side
        #   rows 1-5    four garage bays. Only bay 1 opens to the yard (3, 6); then bay 1 -> bay 2
        #               (door 7, 4) -> bay 3 (14, 3) -> bay 4 (22, 2), which has the exit X (26, 0).
        dict(name="Motor Pool", rows=load_map(1, "C"), goal="Get into the last garage", tint="#34452a",
             angle=270, ceil=(58, 35), floor=(0, 0), secret_look="5",
             max_ray_steps=40, light_falloff=4.0, sprite_darkness=0, par_seconds=90),
    ]),

    dict(name="The Processing Plant", episode=1, best_weapon=3,
         card=dict(enemy="SPITTER", lines=["Spits acid from far away. Strafe", "with A and D to dodge it."], boss=None),
         card_monster=2, card_boss=0, maps=[
        # LEVEL 2, MAP A: PUMP STATION (32 x 30). 14 spitters, 11 imps. Key: red. Route: about 77.
        #   rows 21-28  the intake room, where the player starts (P at 5, 26), and the boiler room
        #               to the east (door 11, 25) with the chaingun Q (18, 27)
        #   row 20      a wall with one door (5, 20) up into the pump hall
        #   rows 8-19   the pump hall: eight pumps (5), 2 x 2, in two rows. East wall (column 23)
        #               with three doors into the pipe gallery, which a long pipe (6) splits into two
        #               lanes, with one gap (27, 18).
        #   row 7       the north wall: a door (5, 7) to the storage room, the RED door (16, 7) to the
        #               control room, and a door (27, 7) from the gallery to the tank room
        #   rows 1-6    storage (a secret wall S at 4, 1 hides health and shells) | the control room
        #               with the exit X (16, 0) | the tank room with the red key K (26, 4)
        #   Route: intake -> pump hall -> gallery -> tank room (key) -> back -> red door -> exit.
        dict(name="Pump Station", rows=load_map(2, "A"), goal="Find the red key, then the exit", tint="#1f5a14",
             angle=270, ceil=(50, 30), floor=(35, 30), secret_look="7",
             max_ray_steps=40, light_falloff=4.5, sprite_darkness=0, par_seconds=105),
        # LEVEL 2, MAP B: ACID VATS (32 x 32). 15 spitters, 10 imps. Key: red. Route: about 74.
        #   A ring corridor two squares wide runs round the outside. Inside it, the vat hall
        #   (columns 4-27, rows 4-27): acid vats (6), some joined into long tanks, with catwalks
        #   between them. Spitters stand on the far catwalks. The red key K (14, 14) is in the
        #   middle. Doors into the hall: west (3, 10), south (15, 28), east (28, 20).
        #   The player starts in the south-west of the ring (P at 5, 29). The ring's north part
        #   (row 1-2, columns 9-22) is sealed: a RED door (8, 1) on its west end, wall on its east.
        #   It has the exit X (16, 0). The chaingun Q (30, 24) is out east, through the east door.
        #   A secret wall S (25, 26) in the hall's south-east corner hides shells and health.
        dict(name="Acid Vats", rows=load_map(2, "B"), goal="Cross the vats for the red key", tint="#3a5a0a",
             angle=0, ceil=(33, 25), floor=(25, 35), secret_look="9",
             max_ray_steps=40, light_falloff=4.8, sprite_darkness=1, par_seconds=105),
        # LEVEL 2, MAP C: FILTER HALLS (22 x 24). 13 spitters, 12 imps. Key: red. Route: about 86.
        #   Four long halls stacked on top of each other: go along one, through the door at its
        #   end, and back along the next one.
        #   rows 19-22  hall 1, with filter columns (3). The player starts at its west end
        #               (P at 2, 21); the door up is at the east end (19, 18).
        #   rows 13-17  hall 2, with filter tanks (6). Two doors up: the key room (10, 12) and hall 3
        #               at the west end (2, 12). A secret wall S (17, 14) hides shells and health.
        #   rows 7-11   hall 3. The key room (red key K at 10, 10) sits in the middle of it, so hall 3
        #               is joined over the top by a corridor one square wide (row 7). The chaingun Q
        #               (20, 11) is at its east end, next to the RED door (19, 6).
        #   rows 1-5    hall 4, with the exit X (13, 0).
        dict(name="Filter Halls", rows=load_map(2, "C"), goal="Zig-zag up to the red door", tint="#14504a",
             angle=0, ceil=(45, 20), floor=(50, 25), secret_look="7",
             max_ray_steps=30, light_falloff=5.0, sprite_darkness=1, par_seconds=120),
    ]),

    dict(name="The Fortress", episode=1, best_weapon=4,
         card=dict(enemy="GOLEM", lines=["Slow, tough, and hits like a truck.", "Lure it next to a barrel."],
                   boss="BOSS: THE WARDEN carries the SKULL KEY to the exit"),
         card_monster=3, card_boss=4, maps=[
        # LEVEL 3, MAP A: GATEHOUSE (34 x 32). 9 golems, 10 spitters, 9 imps, the WARDEN. Keys: red,
        # blue, skull. Route: about 111 squares.
        #   rows 25-30  the barbican, outside the walls: the player starts at the bottom (P at 17, 29).
        #               A secret wall S (4, 26) hides shells and health.
        #   row 24      the outer wall and its gate (17, 24)
        #   rows 16-23  the gate passage (columns 14-20) between the west and east lower wards (doors
        #               13, 20 and 21, 18). The red key K (30, 21) is in the east ward.
        #   row 15      doors up into the middle ward: west (5, 15) and east (28, 15)
        #   rows 8-14   the middle ward, with pillars (4)
        #   row 7       the RED door (5, 7) to the west tower, where the blue key J (3, 3) is, and the
        #               BLUE door (17, 7) to the great hall, where the warden W (17, 3) waits
        #   rows 1-6    west tower | great hall | east tower. The east tower is only reached through
        #               the SKULL door (24, 3), and has the exit X (29, 0).
        dict(name="Gatehouse", rows=load_map(3, "A"), goal="Two keys, then slay the Warden", tint="#5a0f2a",
             angle=270, ceil=(95, 45), floor=(2, 40), secret_look="8",
             max_ray_steps=40, light_falloff=4.5, sprite_darkness=0, par_seconds=165),
        # LEVEL 3, MAP B: THE KEEP (33 x 33). 10 golems, 9 spitters, 8 imps, the WARDEN. Keys: red,
        # blue, skull. Route: about 101 squares.
        #   Three squares, one inside the other: the bailey (a ring 4 squares wide round the outside),
        #   the inner ward (inside the middle wall, columns 6-26), and the keep in the centre.
        #   The player starts at the bottom of the bailey (P at 16, 30). The red key K (30, 2) is in the
        #   bailey's north-east corner; the RED door (5, 10) in the middle wall's west side leads into
        #   the inner ward's west half, which has the blue key J (8, 15). (Walls at column 16 split the
        #   inner ward in two; the east half, through the door at 27, 22, is a side trip.)
        #   The BLUE door (11, 16) opens the keep: the warden W (16, 17). Behind the SKULL door (16, 14)
        #   is a small sanctum with the exit X (16, 11).
        #   A secret wall S (3, 30) in the bailey's south-west corner hides shells and health.
        dict(name="The Keep", rows=load_map(3, "B"), goal="Into the keep, through two doors", tint="#4a1020",
             angle=0, ceil=(5, 30), floor=(8, 30), secret_look="8",
             max_ray_steps=40, light_falloff=4.8, sprite_darkness=1, par_seconds=150),
        # LEVEL 3, MAP C: DUNGEONS (32 x 30). Dark! 9 golems, 9 spitters, 9 imps, the WARDEN. Keys:
        # red, blue, skull. Route: about 95 squares.
        #   rows 1-5    the guardroom where the player starts (P at 3, 3), then four cells. Each cell
        #               has a door on the corridor (row 6); the last one has the red key K (25, 3).
        #   rows 7-8    the upper corridor. Doors down: a plain one (3, 9) into the torture chamber
        #               (a side trip, with pillars) and the RED door (28, 9) into the flooded hall.
        #   rows 10-18  the flooded hall: pools of water (7) and the blue key J (18, 15). (The torture
        #               chamber next to it has no door into it, so the red door can't be skipped.)
        #   row 19      the BLUE door (22, 19) down into the warden's pit
        #   rows 20-28  the pit, with the warden W (16, 26). The exit X (0, 27) is in a small room at
        #               the pit's west end, behind the SKULL door (5, 27). A secret wall S (27, 27)
        #               hides health and shells.
        dict(name="Dungeons", rows=load_map(3, "C"), goal="Down to the Warden's pit", tint="#2a0a1a",
             angle=0, ceil=(75, 10), floor=(8, 25), secret_look="9",
             max_ray_steps=26, light_falloff=6.5, sprite_darkness=4, par_seconds=135),
    ]),

    dict(name="The Foundry", episode=2, best_weapon=4,
         card=dict(enemy="CHARGER", lines=["Lowers its head, then charges.", "Sidestep it and it slams into a wall."],
                   boss=None),
         card_monster=5, card_boss=0, maps=[
        # LEVEL 4, MAP A: FURNACE HALL (36 x 36). 11 chargers, 10 spitters, 9 imps, 6 golems. Key: red.
        # Route: about 113 squares.
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
        # LEVEL 4, MAP B: SLAG PITS (36 x 34). 9 chargers, 9 imps, 8 spitters, 4 golems. Key: red.
        # Route: about 82 squares.
        #   rows 27-32  the crane yard, where the player starts (P at 3, 31). Its only door into the
        #               slag field is in the west (6, 26). A secret wall S (31, 32) hides supplies.
        #   rows 10-25  the slag field: three long strips of molten slag (4) across it, each open at
        #               one end and with one gap, so you zig-zag up through the lanes between them.
        #               Long straight lanes are where chargers charge. The red key K (33, 15) is at the
        #               east end of the second lane.
        #   row 9       doors up: the tool room (8, 9) with the rocket launcher L (3, 3), the pour room
        #               (18, 9) with its furnaces, and the RED door (28, 9) to the exit room
        #   rows 1-8    tool room | pour room | exit room with the exit X (30, 0)
        dict(name="Slag Pits", rows=load_map(4, "B"), goal="Cross the slag for the red key", tint="#7a3a08",
             angle=0, ceil=(8, 50), floor=(4, 45), secret_look="5",
             max_ray_steps=36, light_falloff=4.2, sprite_darkness=1, par_seconds=120),
        # LEVEL 4, MAP C: ROLLING MILL (34 x 36). 9 chargers, 9 imps, 8 spitters, 4 golems. Key: red.
        # Route: about 88 squares.
        #   Three long halls side by side, running north to south:
        #   columns 1-9    the west hall, with storage racks (2). The red key K (3, 3) is at its north
        #                  end. Doors to the mill floor: south (10, 30) and north (10, 8). A secret
        #                  wall S (3, 34) in the south-west corner hides supplies.
        #   columns 11-22  the mill floor, where the player starts (P at 16, 33), with two long lines
        #                  of rollers (9) and crossings between them. The rocket launcher L (16, 19).
        #   columns 24-32  the east hall, with furnaces (4). Its only door is the RED door (23, 10);
        #                  at its top, an office (door 28, 6) with the exit X (33, 2).
        #   Route: mill floor -> west hall (south door) -> north to the key -> north door -> red door.
        dict(name="Rolling Mill", rows=load_map(4, "C"), goal="Down the west hall for the key", tint="#5a3010",
             angle=270, ceil=(10, 30), floor=(6, 30), secret_look="5",
             max_ray_steps=36, light_falloff=4.5, sprite_darkness=2, par_seconds=120),
    ]),

    dict(name="The Sunken Vaults", episode=2, best_weapon=5,
         card=dict(enemy="WRAITH", lines=["Almost invisible from far away,", "and it blinks sideways. Stay sharp."],
                   boss=None),
         card_monster=6, card_boss=0, maps=[
        # LEVEL 5, MAP A: FLOODED CAVES (38 x 38). Dark! 15 wraiths, 6 golems, 5 spitters, 4 imps,
        # 4 chargers. Keys: red, blue. Route: about 125 squares.
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
        # LEVEL 5, MAP B: THE CISTERN (36 x 36). Dark. 10 wraiths, 8 spitters, 6 imps, 6 chargers,
        # 4 golems. Keys: red, blue. Route: about 109 squares.
        #   A walkway three squares wide runs round a flooded hall (water = wall 7). In the water:
        #   four small islands and a big one in the middle, joined by causeways one square wide.
        #   The player starts in the walkway's south-west corner (P at 2, 34). The red key K (10, 26)
        #   is on the south-west island (causeway from the walkway at row 25). The middle island's
        #   causeway to the north-east island has the RED door (22, 13); the blue key J (25, 9) is
        #   there. The pump room in the walkway's north-east corner is behind the BLUE door (28, 2)
        #   and has the exit X (33, 0). Spitters on the islands shoot across the water.
        #   A secret wall S (2, 31) in the walkway's south-west corner hides supplies.
        dict(name="The Cistern", rows=load_map(5, "B"), goal="Island to island, two keys", tint="#0f2a4a",
             angle=270, ceil=(60, 25), floor=(55, 20), secret_look="9",
             max_ray_steps=30, light_falloff=6.0, sprite_darkness=4, par_seconds=150),
        # LEVEL 5, MAP C: BONE TUNNELS (38 x 36). Very dark. 10 wraiths, 7 imps, 7 spitters,
        # 6 chargers, 4 golems. Keys: red, blue. Route: about 114 squares.
        #   Solid bone-white rock (1) with burial chambers dug out of it, joined by tunnels one
        #   square wide; piles of bones (8) in the chambers.
        #   The player starts in the south-west chamber (P at 4, 32). The tunnel east leads to the
        #   crypt with the red key K (21, 31); beyond it, the deep crypt is a side trip (a secret
        #   wall S at 31, 33 hides supplies). From the crypt, north to the great ossuary, whose east
        #   tunnel has the RED door (22, 18) to the bone chapel with the blue key J (32, 17).
        #   Then west: the west ossuary, north up a long tunnel to the north-west tomb, and the BLUE
        #   door (12, 6) into the last tomb with the exit X (19, 1).
        dict(name="Bone Tunnels", rows=load_map(5, "C"), goal="Through the crypts, two keys", tint="#3a3a2a",
             angle=0, ceil=(10, 10), floor=(12, 15), secret_look="1",
             max_ray_steps=26, light_falloff=7.0, sprite_darkness=5, par_seconds=165),
    ]),

    dict(name="The Core", episode=2, best_weapon=5,
         card=dict(enemy="THE COLOSSUS", lines=["Huge, armored, and it gets angrier.", "At half health it calls for help."],
                   boss="FINAL BOSS: the exit is sealed until it falls"),
         card_monster=7, card_boss=0, maps=[
        # LEVEL 6, MAP A: THE RING (40 x 40). 37 monsters of every kind and the COLOSSUS (boss).
        # Keys: red, blue, skull. Route: about 173 squares.
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
        # LEVEL 6, MAP B: REACTOR (40 x 40). 37 monsters and the COLOSSUS. Keys: red, blue, skull.
        # Route: about 143 squares.
        #   rows 30-38  the turbine hall, with four turbines (5). The player starts in the middle
        #               (P at 19, 37). A secret wall S (35, 37) hides supplies.
        #   row 29      three doors up: the west wing (5, 29), the RED door (34, 29) to the east wing,
        #               and the BLUE door (19, 29) to the reactor chamber
        #   rows 8-28   west wing (cooling pumps; the red key K at 3, 27) | the reactor chamber, with
        #               the core (4) in the middle and the colossus T (19, 23) | east wing (coolant
        #               tanks, 7; the blue key J at 33, 16)
        #   rows 1-7    the north hall, reached from both wings (doors 5, 7 and 34, 7), and in its
        #               middle the control room, only through the SKULL door (19, 8) from the
        #               chamber. The exit X (19, 0).
        dict(name="Reactor", rows=load_map(6, "B"), goal="Shut the reactor down", tint="#5a0a0a",
             angle=270, ceil=(0, 55), floor=(95, 40), secret_look="9",
             max_ray_steps=36, light_falloff=4.5, sprite_darkness=2, par_seconds=210),
        # LEVEL 6, MAP C: THE SPIRE (30 x 30). 30 monsters and the COLOSSUS. Keys: red, blue, skull.
        # Route: about 103 squares.
        #   Rings inside rings. The outer path runs round the outside; the player starts at its
        #   bottom (P at 15, 27). The red key K (1, 12) is on the west side; the RED door (15, 4) at
        #   the top leads in to the inner path. The blue key J (23, 20) is on the inner path's east
        #   side; the BLUE door (15, 21) at its bottom opens the centre, where the colossus T (15, 16)
        #   waits. The SKULL door (15, 11) at the top of the centre opens a small sanctum with the
        #   exit X (13, 10). A secret wall S (2, 2) in the north-west corner hides health.
        dict(name="The Spire", rows=load_map(6, "C"), goal="Spiral in to the Colossus", tint="#3a0a4a",
             angle=270, ceil=(85, 50), floor=(90, 35), secret_look="8",
             max_ray_steps=32, light_falloff=4.4, sprite_darkness=2, par_seconds=150),
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
PICKUP_LETTERS = set("HAIUNQL?")          # health, ammo, weapons and mystery items
KEY_LETTERS = set("KJ")                   # red key, blue key
FLOOR_LETTERS = set("0P") | KEY_LETTERS | PICKUP_LETTERS | MONSTER_LETTERS   # things stand on floor
EDGE_LETTERS = set("123456789X")          # what the outside edge may be made of
# E (a barrel) is in none of these groups: it's solid until it explodes, so the checks treat it
# as something that blocks the way.

# One step right, left, down and up, as (column change, row change).
NEIGHBOR_STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))

# No monster may start closer to the player than this, counting squares walked (doors open).
SAFE_START_DISTANCE = 6


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


def walking_distances(map_rows, start, walkable_letters):
    """Like reachable_squares(), but also counts the steps: {square: squares walked from start}."""
    map_height, map_width = len(map_rows), len(map_rows[0])
    steps, to_do = {start: 0}, deque([start])
    while to_do:
        column, row = to_do.popleft()
        for column_step, row_step in NEIGHBOR_STEPS:
            neighbor_column, neighbor_row = column + column_step, row + row_step
            neighbor = (neighbor_column, neighbor_row)
            if (0 <= neighbor_column < map_width and 0 <= neighbor_row < map_height
                    and neighbor not in steps
                    and map_rows[neighbor_row][neighbor_column] in walkable_letters):
                steps[neighbor] = steps[(column, row)] + 1
                to_do.append(neighbor)
    return steps


def next_to(column, row, squares):
    """True if any of the 4 squares beside (column, row) is in the set 'squares'."""
    return any((column + column_step, row + row_step) in squares for column_step, row_step in NEIGHBOR_STEPS)


def play_through(map_rows, start, door_that_never_opens=None):
    """PLAY THE LEVEL, ROUGHLY: work out what a player could reach, the way they would really
    play it. At first only plain doors (D) open. Each pass flood-fills from the start:
      - found the red key K? Next pass, red doors R count as open too.
      - found the blue key J? Then blue doors B open.
      - reached a boss? Beating it drops the skull key, so skull doors Z open.
    Keep going until a pass finds nothing new. Returns the squares reached (without secret walls)
    and the letters that were walkable in the end.
    'door_that_never_opens' (R, B or Z) stays shut whatever keys are found: check 9 uses it to
    ask "could you finish without this door?"."""
    keys_found = set()
    while True:
        walkable = FLOOR_LETTERS | {"D"}
        if "K" in keys_found:
            walkable = walkable | {"R"}
        if "J" in keys_found:
            walkable = walkable | {"B"}
        if "boss" in keys_found:
            walkable = walkable | {"Z"}
        walkable = walkable - {door_that_never_opens}
        reachable = reachable_squares(map_rows, start, walkable)
        letters_reached = {map_rows[row][column] for column, row in reachable}
        found_this_pass = letters_reached & KEY_LETTERS
        if letters_reached & BOSS_LETTERS:
            found_this_pass.add("boss")          # beating a reachable boss drops the skull key
        if found_this_pass <= keys_found:        # nothing new this pass (a subset): stop
            return reachable, walkable
        keys_found |= found_this_pass            # add the new keys and try again


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

    # PLAY THE LEVEL, ROUGHLY (see play_through() above): everything a player can get to, picking
    # up keys and beating the boss on the way, without secret walls.
    reachable, walkable = play_through(map_rows, start)
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

    # CHECK 9: every key must be NEEDED. Play the level again with the key's door shut for good:
    # if the exit can still be reached, players can walk round that door and the key is pointless.
    for key_letter, door_letter, color in (("K", "R", "red"), ("J", "B", "blue")):
        if key_letter in whole_map_text:
            reachable_with_door_shut, _ = play_through(map_rows, start, door_that_never_opens=door_letter)
            check(not next_to(exit_column, exit_row, reachable_with_door_shut),
                  f"{name}: the exit can be reached without going through a {color} door ({door_letter}), so "
                  f"the {color} key ({key_letter}) isn't needed. Close the other way round, or remove the key.")

    # CHECK 10: no monster starts right next to the player. Count the squares walked from the
    # start (every door open): a monster closer than SAFE_START_DISTANCE would attack before the
    # player has had a chance to look around.
    steps_from_start = walking_distances(map_rows, start, FLOOR_LETTERS | set("DRBZ"))
    for column, row, letter in every_square:
        if letter in MONSTER_LETTERS and (column, row) in steps_from_start:
            check(steps_from_start[(column, row)] >= SAFE_START_DISTANCE,
                  f"{name}: the '{letter}' at {where(column, row)} is only {steps_from_start[(column, row)]} squares' walk "
                  f"from the player start. Monsters must start at least {SAFE_START_DISTANCE} squares away.")

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
    A mystery item (?) counts as the average of what it can turn into.
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

    def ammo_damage_of(letter):
        if letter == "?":    # a mystery item: on average, the average of what it can turn into
            return math.fsum(ammo_damage_of(choice) for choice in config.MYSTERY_ITEMS) / len(config.MYSTERY_ITEMS)
        if letter not in config.AMMO_PICKUPS:
            return 0
        ammo_name, amount = config.AMMO_PICKUPS[letter]
        return damage_per_ammo[ammo_name] * config.scratch_round(amount * pickup_percent / 100)
    health_pack = config.scratch_round(config.HEALTH_PACK * pickup_percent / 100)
    # math.fsum() adds up without the tiny rounding errors of plain sum(), so a total like 365.5 is
    # exactly 365.5 on every version of Python (and in the map editor's JavaScript copy).
    ammo_damage = math.fsum(ammo_damage_of(letter) for letter in pickups_on_map)
    health = round(health_pack * (pickups_on_map.count("H") + pickups_on_map.count("?")
                                  * config.MYSTERY_ITEMS.count("H") / len(config.MYSTERY_ITEMS)))
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
