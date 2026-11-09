"""Level maps for Scratch Slayer.

HOW A LEVEL IS STORED
=====================
Every level is a GRID OF LETTERS: a Python list of strings, one string per ROW, top row first.
Each letter is one SQUARE of the map. This is exactly the same shape as the Scratch lists
"level 1 map" ... "level 6 map": build.py copies each list of strings straight into a Scratch
list (one string = one list item), and the Engine's 'load level' block reads it back letter by
letter. So whatever grid this file produces IS the level the game plays.

COORDINATES: a square is written (x, y) = (column, row), both counting from 0.
  x = how far along the row (0 = the left end of the string)
  y = which row (0 = the TOP row, the first string in the list)
So rows[y][x] is the letter at square (x, y). Notice the order: row first, then column.
The game uses the same numbers ("player x" 3.5 = the middle of column 3).

HOW THE MAPS ARE MADE (three different ways, because they were added at different times)
  Level 1        typed out by hand, letter by letter.
  Level 2        typed out with Python string arithmetic ("0" * 14 = fourteen floor squares).
  Level 3        drawn by a small function that starts with an empty floor and places walls.
  Levels 1-3     then PATCHED with _edit() in several rounds (secrets, barrels, weapons, the
                 skull door), as features were added to the game. The final map is the original
                 grid with every patch below it applied, in order from top to bottom.
  Levels 4-6     drawn with the Grid "drawing kit" class: fill rectangles, carve rooms, place things.

At the bottom, validate() plays detective: it checks every map can really be finished.
build.py runs validate() on every level each time it builds, so a broken map stops the build
before it ever reaches Scratch. Run this file on its own (python3 src/levels.py) to check the
maps and print what is in each one.

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
# deque = a "double-ended queue": a list you can quickly take items off the FRONT of.
# The flood fill in _reach() below uses it as a to-do list of squares to look at.
from collections import deque


# =================================================================================================
# LEVEL 1: THE OUTPOST (20 x 20), typed out by hand
# =================================================================================================
# What you see is (almost) what you play: 20 strings of 20 letters. Three rooms stacked top to
# bottom, joined by doors (D). The exit switch X is in the left wall of the bottom room.
# This is only the FIRST draft. Further down, two _edit() calls add a secret closet, barrels,
# the shotgun and bullets. Those patches replace single letters at given (x, y) squares.
L1 = [
    "11111111111111111111",
    "100001000000000000A1",
    "1P000D000000M0000001",
    "10000100020000200001",
    "1000010000000000M001",
    "11111100000000000001",
    "122222222222D2222221",
    "10000030000000000001",
    "100M003000M00000M001",
    "10000000000400400001",
    "10H000300000000M0001",
    "10000030A00000000001",
    "111111111111111D1111",
    "10000000000000000001",
    "100M0002200000000H01",
    "10000M00000022000001",
    "X0000000000000000001",
    "100022000M0000000001",
    "10000000000000A00001",
    "11111111111111111111",
]

# =================================================================================================
# LEVEL 2: THE PROCESSING PLANT (24 x 24), typed out with string arithmetic
# =================================================================================================
# Each row is glued together from pieces with +. In Python, "0" * 14 means fourteen "0"s in a
# row, so "5" + "0" * 14 + "7" is: a wall (5), fourteen floor squares, then a wall (7).
# Every row adds up to 24 letters; validate() would complain if one didn't.
#
# The monsters here are written as M (imps), but they are really spitters: the _edit() call
# for level 2 further down swaps every M for a V. The level was drawn before spitters existed.
#
# Row 0 is the top wall with the exit switch in it. Its first piece, "555...X55"[:0], is a
# leftover from an earlier draft: [:0] cuts a string down to its first 0 letters, which is an
# empty string "", so it adds nothing. The row is really 19 walls, then X, then 4 walls,
# which puts the exit at square (19, 0).
L2 = [
    "555555555555555555555X55"[:0] + "5" * 19 + "X" + "5" * 4,
    "5" + "0" * 14 + "7" + "0" * 7 + "5",
    "5000M" + "0" * 10 + "7" + "00M0000" + "5",
    "5" + "00000" + "6" + "000" + "6" + "0000" + "7" + "0" * 7 + "5",
    "5" + "0" * 12 + "H" + "0" + "R" + "00000" + "M" + "0" + "5",     # the red door R, top-middle
    "5" + "00000" + "6" + "000" + "6" + "0M00" + "7" + "0" * 7 + "5",
    "5" + "0A" + "0" * 12 + "7" + "0" * 7 + "5",
    "5" + "0" * 14 + "7" + "0" * 7 + "5",
    "5" + "7" * 11 + "D" + "7" * 10 + "5",                              # wall across the map, one door
    "5" + "0" * 7 + "7" + "0" * 14 + "5",
    "5" + "0K00M00" + "7" + "000000000M0000" + "5",                     # the red key K, west room
    "5" + "0" * 7 + "7" + "000" + "6" + "000000" + "6" + "000" + "5",
    "5" + "0" * 7 + "D" + "000000M0000000" + "5",
    "5" + "00M00A0" + "7" + "0" * 14 + "5",
    "5" + "0" * 7 + "7" + "000" + "6" + "000" + "H" + "00" + "6" + "000" + "5",
    "5" + "0" * 7 + "7" + "0M" + "0" * 10 + "M" + "0" + "5",
    "5" + "0" * 7 + "7" + "0" * 14 + "5",
    "5" + "7" * 15 + "D" + "7" * 6 + "5",                               # second wall across, one door
    "5" + "0" * 7 + "5" + "0" * 11 + "M00" + "5",
    "5" + "0" * 7 + "5" + "000" + "6" + "0000" + "6" + "00000" + "5",
    "5" + "0P00000" + "D" + "00000M" + "0" * 8 + "5",                   # the player starts at P, bottom-left
    "5" + "0" * 7 + "5" + "000" + "6" + "0000" + "6" + "000" + "A" + "0" + "5",
    "5" + "0" * 7 + "5" + "0" * 9 + "M" + "0000" + "5",
    "5" * 24,                                                           # bottom wall
]


# =================================================================================================
# LEVEL 3: THE FORTRESS (28 x 28), drawn by a function
# =================================================================================================
def _build_l3():
    """Draws level 3 square by square, then turns the drawing into a list of strings.

    Plan of the fortress (rows 0-27, top to bottom):
      rows 1-11   three wings side by side: west wing | inner keep | east wing
                  (split by walls at x = 9 and x = 18)
      row 12      a wall across the map with three doors: a plain door (D) into the west wing,
                  the RED door (R) into the keep, and the BLUE door (B) into the east wing
      rows 13-20  the courtyard, with pillars
      row 21      another wall across, with three doors into the side rooms
      rows 22-26  the side rooms, where the player starts (P at 13, 25)
    The exit X is in the east wall at (27, 3).
    """
    # W and H = width and height of the map in squares.
    W = H = 28
    # g = the grid being drawn: a list of 28 rows, each a list of 28 letters, all floor ("0")
    # to start with. Lists of letters (not strings) are used because Python can change one
    # item of a list, but can't change one letter inside a string.
    g = [["0"] * W for _ in range(H)]
    # put(x, y, ch) = "write letter ch at square (x, y)". Note g[y][x]: row first, then column.
    def put(x, y, ch): g[y][x] = ch
    # The outside wall: the top and bottom rows and the left and right columns, all wall 8.
    for i in range(W):
        put(i, 0, "8"); put(i, H - 1, "8"); put(0, i, "8"); put(W - 1, i, "8")
    # Two long walls across the whole map: row 12 (wall 9) and row 21 (wall 8).
    for x in range(1, 27):
        put(x, 12, "9"); put(x, 21, "8")
    # Two walls running down from the top, splitting the north part into three wings.
    for y in range(1, 12):
        put(9, y, "9"); put(18, y, "9")
    # Two short walls splitting the bottom strip into three side rooms.
    for y in range(22, 27):
        put(9, y, "8"); put(18, y, "8")
    # Doors in those walls (see the plan in the docstring), and the exit switch in the east wall.
    for x, y, ch in [(4, 12, "D"), (13, 12, "R"), (22, 12, "B"), (13, 21, "D"), (4, 21, "D"),
                     (22, 21, "D"), (27, 3, "X")]:
        put(x, y, ch)
    # courtyard pillars and a central block that hides the far side
    for x, y in [(5, 15), (5, 18), (10, 16), (17, 16), (22, 15), (22, 18)]:
        put(x, y, "4")
    for x, y in [(13, 16), (14, 16), (13, 17), (14, 17)]:
        put(x, y, "9")
    # west wing cover, keep pillars, east wing maze wall
    for x, y in [(3, 4), (4, 4), (5, 4), (6, 8), (6, 9), (2, 8)]:
        put(x, y, "8")
    for x, y in [(12, 4), (15, 4), (12, 8), (15, 8)]:
        put(x, y, "4")
    for x in range(19, 25):
        put(x, 6, "9")
    # THINGS ("entities"): each letter, and the list of squares it goes on. As in level 2 the
    # monsters are written as M here and swapped to golems (G) by the level 3 _edit() below.
    ents = {
        "P": [(13, 25)],
        "M": [(3, 14), (8, 19), (20, 14), (24, 19), (16, 14),      # courtyard
              (2, 2), (7, 5), (4, 9),                              # west wing
              (11, 2), (16, 6), (13, 9),                           # inner keep
              (20, 9), (25, 10), (21, 3),                          # east wing
              (3, 24), (24, 24)],                                  # side rooms
        "K": [(2, 6)], "J": [(13, 2)],
        "A": [(11, 23), (7, 10), (6, 25), (21, 25), (26, 13), (25, 8)],
        "H": [(16, 10), (2, 23), (25, 23), (1, 13), (20, 1)],
    }
    for ch, cells in ents.items():
        for x, y in cells:
            # Safety check: a thing may only go on empty floor. If a typo put a monster inside a
            # wall (or on top of another thing), the build stops here and names the square.
            assert g[y][x] == "0", (ch, x, y)
            put(x, y, ch)
    # Turn each row (a list of letters) back into one string: ["1", "0", "0"] -> "100".
    return ["".join(r) for r in g]

L3 = _build_l3()


# =================================================================================================
# PATCHING LEVELS 1-3 WITH _edit()
# =================================================================================================
def _edit(rows, changes, swap=None):
    """Place letters at (x, y) squares, and optionally swap one letter for another everywhere.

    rows     the map to change (a list of strings). It is not changed: a NEW map is returned.
    changes  a dictionary {(x, y): letter}: put this letter on that square.
    swap     optional dictionary {old letter: new letter}, applied to EVERY square first.
             {"M": "V"} turns every imp into a spitter.
    """
    # Strings can't be changed one letter at a time, so split every row into a list of letters.
    grid = [list(r) for r in rows]
    # Swap first, so the single-square changes below are never swapped by accident
    # (that is how level 3 can swap M -> G and still place one W, the warden).
    if swap:
        # swap.get(ch, ch) = "the new letter for ch if there is one, otherwise ch itself".
        grid = [[swap.get(ch, ch) for ch in r] for r in grid]
    for (x, y), ch in changes.items():
        grid[y][x] = ch
    # Glue each row back into a string.
    return ["".join(r) for r in grid]

# Each call below takes the map so far and returns a patched copy, which replaces it
# (L1 = _edit(L1, ...)). They run from top to bottom, so later patches can overwrite earlier
# ones. To find out what is REALLY on a square of levels 1-3, check these patches too.

# ROUND 1: secrets, barrels and the real monster types.
# Level 1 - imps. A secret closet in the bottom-right room, two barrels near the imp pack in the hall.
#   The four "2"s build the closet's walls, S at (15, 18) is its secret door, and the closet holds
#   shells (A) and a health pack (H). E = an exploding barrel.
L1 = _edit(L1, {(16, 16): "2", (17, 16): "2", (18, 16): "2", (15, 17): "2", (17, 17): "A",
                (15, 18): "S", (16, 18): "H", (12, 8): "E", (17, 10): "E"})
# Level 2 - spitters. A secret closet in the north room, barrels near spitter groups, extra health.
#   swap={"M": "V"} turns every M drawn above into a spitter.
L2 = _edit(L2, {(1, 1): "H", (3, 1): "S", (2, 2): "A", (3, 2): "7", (1, 3): "7", (2, 3): "7",
                (8, 4): "E", (17, 12): "E", (15, 21): "E", (11, 10): "H", (20, 13): "H"}, swap={"M": "V"})
# Level 3 - golems, and the warden boss guarding the exit wing. A secret closet in the keep.
#   swap={"M": "G"} turns every M into a golem, then (25, 10) becomes W: the warden boss.
L3 = _edit(L3, {(15, 1): "S", (16, 1): "A", (17, 1): "H", (16, 2): "9", (17, 2): "9",
                (25, 10): "W", (21, 14): "E", (11, 19): "E", (23, 8): "E", (8, 13): "A", (19, 20): "A"},
           swap={"M": "G"})

# ROUND 2: weapons, bullets and the skull door.
# Weapons + bullets for the pistol start: the shotgun waits in level 1's first room,
# the chaingun in level 2. Some shell boxes become bullet boxes.
#   N = shotgun, Q = chaingun, I = a box of bullets (written over some of the A shell boxes).
L1 = _edit(L1, {(2, 4): "N", (18, 1): "I", (6, 13): "I"})
L2 = _edit(L2, {(12, 10): "Q", (2, 6): "I", (20, 22): "I"})
# Level 3: the exit switch now sits in a closet sealed by a SKULL DOOR (Z).
# Only the Warden's skull key opens it, so the boss must fall first.
#   The "9"s wall in the squares around the exit at (27, 3), leaving Z at (25, 3) as the only way in.
L3 = _edit(L3, {(25, 2): "9", (26, 2): "9", (25, 3): "Z", (25, 4): "9", (26, 4): "9",
                (11, 23): "I", (21, 25): "I", (1, 1): "I"})


# =================================================================================================
# THE Grid DRAWING KIT (used for the big levels 4-6)
# =================================================================================================
class Grid:
    """A tiny drawing kit for big maps: start solid or hollow, then carve rooms and add walls.

    Typing a 40 x 40 map by hand is slow and easy to get wrong, so levels 4-6 are DRAWN with
    rectangles instead, a bit like a paint program:
        m = Grid(36, "2")              a 36 x 36 map: an outside wall of "2", floor inside
        m = Grid(38, "7", fill="7")    a 38 x 38 map that is SOLID wall 7 (carve caves into it)
        m.fill(x0, y0, x1, y1, "5")    fill the rectangle from corner (x0, y0) to (x1, y1)
                                       with "5". Both corners are included. A rectangle one
                                       square wide is a wall; filling with "0" carves a room.
        m.put(x, y, "D")               put one letter on one square (doors, the exit, secrets)
        m.things("M", [(5, 30), ...])  put a thing on each square in the list. It must land on
                                       empty floor, or the build stops (see things() below).
        m.rows()                       the finished map, as a list of strings
    Order matters: later drawing covers earlier drawing, so draw walls first, then cut doors
    into them, and add things last.
    """
    def __init__(self, size, border, fill="0"):
        # size   = width AND height (these maps are square)
        # border = the letter for the outside wall
        # fill   = what everything inside starts as: "0" (open floor) or a wall (solid rock)
        self.size = size
        self.g = [[fill] * size for _ in range(size)]
        # The outside wall: row 0, the last row, column 0 and the last column.
        for i in range(size):
            self.g[0][i] = self.g[size - 1][i] = self.g[i][0] = self.g[i][size - 1] = border
    def put(self, x, y, ch):
        """One letter on square (x, y)."""
        self.g[y][x] = ch
    def fill(self, x0, y0, x1, y1, ch):
        """Every square from (x0, y0) to (x1, y1), corners included. The + 1 is there because
        Python's range() stops just BEFORE its end number: range(3, 6) is 3, 4, 5."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.g[y][x] = ch
    def things(self, ch, cells):
        """Put thing ch (a monster, pickup, key, barrel, the player...) on every square in cells.
        Each square must still be empty floor. If it isn't, the build stops and says which
        letter, which square, and what was already there, so mistakes are easy to find."""
        for x, y in cells:
            assert self.g[y][x] == "0", (ch, x, y, self.g[y][x])
            self.g[y][x] = ch
    def rows(self):
        """The finished map: each row of letters glued into one string."""
        return ["".join(r) for r in self.g]


# =================================================================================================
# LEVELS 4-6, drawn with Grid. Each function draws one level and returns its rows.
# Read them top to bottom: walls and rooms first, then doors, then pillars, then things.
# =================================================================================================
def _build_l4():
    """THE FOUNDRY (36 x 36): a loading bay, a huge pillared furnace hall full of chargers,
    two side corridors, and three north rooms. Red key in the north-west, exit in the north-east.

    Layout, top to bottom:
      rows 1-7    three north rooms (walls at x = 11 and x = 24), the red key K in the west one
      row 8       wall with two plain doors and the RED door at (32, 8)
      rows 9-26   west corridor | furnace hall | east corridor (walls at x = 6 and x = 29)
      row 27      wall with two doors
      rows 28-34  the loading bay, where the player starts (P at 18, 33)
    The exit X is in the top wall at (30, 0), in the north-east room behind the red door.
    """
    m = Grid(36, "2")
    m.fill(1, 27, 34, 27, "5"); m.put(8, 27, "D"); m.put(27, 27, "D")          # bay / hall wall
    m.fill(6, 9, 6, 26, "5"); m.put(6, 18, "D")                                   # hall / west corridor
    m.fill(29, 9, 29, 26, "5"); m.put(29, 14, "D")                                # hall / east corridor
    m.fill(1, 8, 34, 8, "5"); m.put(3, 8, "D"); m.put(17, 8, "D"); m.put(32, 8, "R")  # north rooms
    m.fill(11, 1, 11, 7, "5"); m.fill(24, 1, 24, 7, "5")                          # walls between them
    m.put(30, 0, "X")                                                             # the exit, in the top wall
    for x in (10, 24):                                                            # furnace pillars
        for y in (12, 17, 22):
            m.fill(x, y, x + 1, y + 1, "4")                                       # each pillar is 2 x 2
    for y in (12, 22):
        m.fill(17, y, 18, y + 1, "4")
    # The middle pillar is HOLLOW: a 3 x 3 block, its center carved back to floor, with a secret
    # wall S on its north side. The center square gets rockets (U) a few lines down.
    m.fill(16, 16, 18, 18, "4"); m.put(17, 17, "0"); m.put(17, 16, "S")           # hollow pillar
    m.fill(14, 31, 15, 32, "5"); m.fill(21, 31, 22, 32, "5")                      # bay crates
    m.fill(3, 3, 4, 4, "5"); m.fill(29, 3, 30, 4, "5"); m.fill(15, 3, 15, 5, "4"); m.fill(20, 3, 20, 5, "4")
    # THINGS. The first letter is the thing, then the squares it goes on.
    m.things("P", [(18, 33)])                                                     # player start
    m.things("U", [(17, 17)])                                                     # rockets in the hollow pillar
    m.things("C", [(13, 15), (21, 15), (13, 20), (21, 20), (8, 11), (27, 24), (19, 10)])   # chargers
    m.things("M", [(5, 30), (30, 30), (26, 33), (3, 20)])                         # imps
    m.things("V", [(2, 12), (4, 24), (32, 12), (32, 23), (27, 5)])                # spitters
    m.things("G", [(7, 4), (21, 2), (33, 2)])                                     # golems
    m.things("K", [(2, 2)]); m.things("L", [(17, 2)])                             # red key, rocket launcher
    m.things("H", [(2, 33), (33, 33), (9, 2), (33, 18), (2, 15)])                 # health
    m.things("A", [(16, 30), (12, 2), (31, 25)])                                  # shells
    m.things("I", [(10, 33), (28, 10), (4, 10), (25, 26)])                        # bullets
    m.things("U", [(22, 6), (8, 25)])                                             # rockets
    m.things("E", [(12, 25), (23, 10), (31, 30), (2, 26), (26, 2)])               # barrels
    return m.rows()


def _build_l5():
    """THE SUNKEN VAULTS (38 x 38): solid rock with caverns carved out, joined by narrow
    tunnels. Red key north-west, blue key north, exit east behind the blue door. Dark!

    This one works the OTHER way round from level 4: the Grid starts completely SOLID (fill="7")
    and the caves and tunnels are carved out of it with floor ("0"), like digging.
    """
    m = Grid(38, "7", fill="7")
    # Each cave is a rectangle: (left x, top y, right x, bottom y).
    caves = {"start": (2, 28, 9, 35), "west": (2, 13, 12, 23), "south": (15, 26, 24, 35),
             "vault": (16, 11, 27, 22), "southeast": (29, 24, 35, 35), "east": (29, 2, 35, 20),
             "northwest": (2, 2, 13, 9), "north": (16, 2, 26, 7)}
    for x0, y0, x1, y1 in caves.values():
        m.fill(x0, y0, x1, y1, "0")                                   # dig the cave out
        for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):      # knock the corners in: cave-like
            m.put(cx, cy, "3")
    # Tunnels one square wide join the caves. (x, first y, last y) for tunnels running up and
    # down; (y, first x, last x) for tunnels running left and right.
    for x, y0, y1 in ((5, 24, 27), (7, 10, 12), (20, 23, 25), (21, 8, 10)):      # vertical tunnels
        m.fill(x, y0, x, y1, "0")
    for y, x0, x1 in ((31, 10, 14), (17, 13, 15), (30, 25, 28), (14, 28, 28)):    # horizontal tunnels
        m.fill(x0, y, x1, y, "0")
    # The red door blocks the tunnel to the north cave, the blue door blocks the tunnel to the
    # east cave, and the exit is in the east wall of the east cave.
    m.put(21, 9, "R"); m.put(28, 14, "B"); m.put(36, 5, "X")
    for x, y in ((19, 14), (24, 14), (19, 19), (24, 19)):                          # vault pillars
        m.fill(x, y, x + 1, y + 1, "9")
    m.fill(6, 17, 7, 18, "3"); m.fill(32, 9, 33, 10, "9"); m.fill(19, 30, 20, 31, "3")   # rocks for cover
    # A one-square closet dug into the rock above the south-east cave, behind a secret wall.
    m.put(32, 23, "S")                                                             # secret closet
    m.put(32, 22, "0")
    m.things("P", [(5, 33)])                                                       # player start
    m.things("F", [(4, 15), (10, 21), (22, 33), (17, 12), (26, 21), (33, 30), (31, 6), (24, 4)])   # wraiths
    m.things("V", [(11, 15), (26, 12), (34, 26), (20, 3)])                         # spitters
    m.things("G", [(22, 17), (3, 6), (33, 16)])                                    # golems
    m.things("M", [(8, 33), (16, 28), (11, 4)])                                    # imps
    m.things("K", [(3, 3)]); m.things("J", [(25, 3)])                              # red key, blue key
    m.things("H", [(32, 22), (3, 22), (23, 28), (34, 33), (17, 21), (34, 3)])      # health (first one: the closet)
    m.things("A", [(11, 14), (16, 34), (8, 8)])                                    # shells
    m.things("I", [(2, 30), (25, 12), (30, 25), (12, 3)])                          # bullets
    m.things("U", [(34, 35), (17, 6), (4, 20)])                                    # rockets
    m.things("E", [(22, 13), (21, 21), (18, 33)])                                  # barrels
    return m.rows()


def _build_l6():
    """THE CORE (40 x 40): a ring corridor around four wings, and the Colossus's arena in the
    middle. Red key west, blue key east (behind the red door), the arena's blue door is in the
    south wing, and the exit closet is sealed by a skull door in the arena's north wall.

    The route a player has to take: start at the bottom of the ring -> red key in the west wing
    -> red door into the east wing -> blue key -> blue door from the south wing into the arena
    -> beat the Colossus for the skull key -> skull door -> exit.
    """
    m = Grid(40, "8")
    # Everything from (5, 5) to (34, 34) starts solid. The 4 squares left open around it
    # (between the outside wall and this block) become the RING corridor.
    m.fill(5, 5, 34, 34, "9")                                     # solid core, then carve it
    m.fill(6, 6, 17, 10, "0"); m.fill(23, 6, 33, 10, "0")         # two north rooms
    m.fill(6, 13, 10, 27, "0"); m.fill(29, 13, 33, 27, "0")       # west + east wings
    m.fill(8, 29, 31, 33, "0")                                    # south wing
    # The arena: a 16 x 16 block of wall 4, then its inside carved out, leaving a 1-square wall.
    m.fill(12, 12, 27, 27, "4"); m.fill(13, 13, 26, 26, "0")      # the arena
    # Doors from the ring into each wing. The east wing's door is the RED one.
    m.put(11, 5, "D"); m.put(28, 5, "D"); m.put(5, 20, "D"); m.put(34, 20, "R"); m.put(20, 34, "D")
    # (20, 27) is a square of the arena's own wall: clearing it makes the gap behind the blue door.
    m.put(20, 28, "B"); m.put(20, 27, "0")                        # blue door into the arena
    m.put(20, 12, "Z"); m.put(20, 11, "0"); m.put(20, 10, "X")    # skull door -> exit closet
    for x, y in ((15, 15), (23, 15), (15, 23), (23, 23)):         # arena pillars
        m.fill(x, y, x + 1, y + 1, "9")
    m.fill(19, 8, 21, 9, "9")                                      # keep the closet walled off
    m.put(5, 31, "S"); m.put(6, 31, "0")                          # secret closet off the ring
    m.fill(12, 30, 13, 31, "4"); m.fill(26, 30, 27, 31, "4")      # cover in the south wing
    m.things("P", [(20, 37)])                                     # player start (bottom of the ring)
    m.things("T", [(20, 18)])                                     # the Colossus, in the arena
    m.things("C", [(30, 2), (9, 37), (20, 31), (31, 37), (31, 20)])   # chargers
    m.things("F", [(2, 10), (37, 28), (14, 8), (25, 8), (8, 24)])     # wraiths
    m.things("G", [(2, 30), (37, 10), (10, 31)])                      # golems
    m.things("V", [(8, 15), (32, 15), (29, 31), (16, 2)])             # spitters
    m.things("M", [(9, 2), (2, 20), (37, 20)])                        # imps
    m.things("K", [(7, 20)]); m.things("J", [(32, 26)])               # red key, blue key
    m.things("H", [(6, 31), (14, 14), (25, 25), (2, 2), (37, 37), (31, 9), (9, 27)])   # health (first: closet)
    m.things("A", [(14, 25), (8, 9), (33, 13)])                       # shells
    m.things("I", [(25, 14), (2, 37), (37, 2), (16, 32)])             # bullets
    m.things("U", [(13, 20), (26, 20), (24, 32), (6, 6)])             # rockets
    m.things("E", [(18, 22), (22, 22), (2, 15), (37, 25), (10, 9)])   # barrels
    return m.rows()


L4, L5, L6 = _build_l4(), _build_l5(), _build_l6()


# =================================================================================================
# THE LEVEL LIST: the maps plus a few settings each. build.py reads this.
# =================================================================================================
# For each level:
#   name         used in this file's messages (the level cards' names are drawn in assets6.py)
#   rows         the map (becomes the Scratch list "level N map")
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
LEVELS = [
    dict(name="The Outpost", rows=L1, angle=0, ceil=(0, 10), floor=(7, 45), secret_look="2"),
    dict(name="The Processing Plant", rows=L2, angle=0, ceil=(50, 30), floor=(35, 30), secret_look="7"),
    dict(name="The Fortress", rows=L3, angle=270, ceil=(95, 45), floor=(2, 40), secret_look="9"),
    dict(name="The Foundry", rows=L4, angle=270, ceil=(5, 40), floor=(8, 35), secret_look="4"),
    dict(name="The Sunken Vaults", rows=L5, angle=270, ceil=(55, 20), floor=(50, 25), secret_look="7"),
    dict(name="The Core", rows=L6, angle=270, ceil=(98, 60), floor=(0, 50), secret_look="9"),
]


# =================================================================================================
# CHECKING THAT EVERY LEVEL CAN BE FINISHED
# =================================================================================================
# Groups of letters (sets), so the checks below can ask "is this letter a wall?" in one go.
WALL_CH = set("123456789DRBXSZ")       # anything you can't simply walk through (doors included)
MONSTER_CH = set("MVGWCFT")
BOSS_CH = set("WT")                    # the warden and the colossus
PICKUP_CH = set("HAIUNQL")             # health, ammo and weapons
FLOOR_CH = set("0PKJ") | PICKUP_CH | MONSTER_CH   # squares you can walk on: things stand on floor
# E (a barrel) is in neither group: it's solid until it explodes, so the checks treat it as
# something that blocks the way.


def _reach(rows, start, ok):
    """FLOOD FILL: every square you can walk to from 'start', stepping up, down, left or right,
    moving only onto squares whose letter is in 'ok'. Returns them as a set of (x, y) squares.

    It works like spilling paint at the start square:
      1. The start square is painted, and goes on the to-do list (q, a queue).
      2. Take the next square off the to-do list and look at its 4 neighbors.
      3. Any neighbor that is inside the map, walkable ('ok') and not painted yet gets painted
         and added to the to-do list.
      4. Repeat until the to-do list is empty: the paint has spread everywhere it can.
    This is called "breadth-first search". Paint bucket tools in drawing programs fill shapes
    the same way.
    """
    H, W = len(rows), len(rows[0])
    reach, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        # The 4 neighbors: one step right, left, down and up.
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in reach and rows[n[1]][n[0]] in ok:
                reach.add(n); q.append(n)
    return reach


def validate(lv):
    """Checks a map the way a careful player would: everything that matters must be reachable
    WITHOUT opening secret walls or blowing up barrels; pickups may hide behind secrets.

    Each check is an 'assert': if it isn't true, Python stops with an AssertionError (and, for
    most checks, a message saying what's wrong). build.py calls this for every level, so a
    broken map stops the build. If everything passes, it returns a count of each letter.
    """
    rows = lv["rows"]
    H, W = len(rows), len(rows[0])
    # CHECK 1: every row is as long as the first one (the map is a proper rectangle).
    assert all(len(r) == W for r in rows), [len(r) for r in rows]
    # CHECK 2: no unknown letters (only walls, floor things and barrels are allowed).
    assert set("".join(rows)) <= WALL_CH | FLOOR_CH | {"E"}, set("".join(rows)) - WALL_CH - FLOOR_CH
    # CHECK 3: the outside edge is all wall (or the exit switch), so nobody can walk off the map
    # and rays always hit something.
    edge = "123456789X"
    for x in range(W):
        assert rows[0][x] in edge and rows[-1][x] in edge
    for y in range(H):
        assert rows[y][0] in edge and rows[y][-1] in edge
    # CHECK 4: exactly one player start.
    starts = [(x, y) for y in range(H) for x in range(W) if rows[y][x] == "P"]
    assert len(starts) == 1

    # PLAY THE LEVEL, ROUGHLY: work out what a player could reach, the way they would really
    # play it. At first only plain doors (D) open. Each pass flood-fills from the start:
    #   - found the red key K? Next pass, red doors R count as open too.
    #   - found the blue key J? Then blue doors B open.
    #   - reached a boss? Beating it drops the skull key, so skull doors Z open.
    # Keep going until a pass finds nothing new. 'reach' is then everything the player can get to.
    keys = set()
    while True:
        ok = (FLOOR_CH | {"D"} | ({"R"} if "K" in keys else set()) | ({"B"} if "J" in keys else set())
              | ({"Z"} if "boss" in keys else set()))
        reach = _reach(rows, starts[0], ok)
        found = {rows[y][x] for x, y in reach} & {"K", "J"}
        if {rows[y][x] for x, y in reach} & BOSS_CH:
            found.add("boss")      # beating a reachable boss drops the skull key
        if found <= keys:          # nothing new this pass (found is a subset of keys): stop
            break
        keys |= found              # add the new keys and try again
    # The same, but with secret walls opened too. Bonus pickups are allowed to hide in there.
    with_secrets = _reach(rows, starts[0], ok | {"S"})

    # CHECK 5: look at every square of the map.
    for y in range(H):
        for x in range(W):
            ch = rows[y][x]
            # Monsters and keys must be reachable WITHOUT secrets (you need them to finish).
            if ch in MONSTER_CH | {"K", "J"}:
                assert (x, y) in reach, f"{lv['name']}: {ch} at {x},{y} unreachable"
            # Pickups just have to be reachable somehow, secrets included.
            if ch in PICKUP_CH:
                assert (x, y) in with_secrets, f"{lv['name']}: {ch} at {x},{y} unreachable"
            # A secret wall must touch a reachable square, or nobody could ever press E on it.
            if ch == "S":
                assert any((x + dx, y + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
                    f"{lv['name']}: secret at {x},{y} can't be reached"
            # Same for barrels: you have to be able to get near one to shoot it.
            if ch == "E":
                assert any((x + dx, y + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    # CHECK 6: exactly one exit switch, and a reachable square right next to it (the switch is
    # in a wall, so you stand beside it and press E).
    exits = [(x, y) for y in range(H) for x in range(W) if rows[y][x] == "X"]
    assert len(exits) == 1
    ex, ey = exits[0]
    assert any((ex + dx, ey + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), "exit unreachable"
    # CHECK 7: at most one boss (there is only one boss health bar).
    c = "".join(rows)          # the whole map as one long string, handy for counting letters
    bosses = sum(c.count(b) for b in BOSS_CH)
    assert bosses <= 1, "only one boss per level"
    # CHECK 8: a skull door needs a boss to drop the skull key, and it must really GUARD the
    # exit. Flood-fill again with every door open EXCEPT the skull door: if the exit can still
    # be reached, players could walk around the boss fight, so the skull door is in the wrong place.
    if "Z" in c:
        assert bosses == 1, "a skull door needs a boss to drop the skull key"
        locked = _reach(rows, starts[0], ok - {"Z"})
        assert not any((ex + dx, ey + dy) in locked for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
            f"{lv['name']}: the exit can be reached without the skull door"
    # Everything passed: report the map's size and how many of each letter it has.
    return dict(size=f"{W}x{H}", **{k: c.count(k) for k in "MVGWCFTHAIUNQLKJESZ"})


# Running this file directly (python3 src/levels.py) checks every level and prints its contents.
# (When build.py imports this file instead, this part is skipped.)
if __name__ == "__main__":
    for lv in LEVELS:
        print(lv["name"], validate(lv))
