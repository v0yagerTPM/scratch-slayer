"""Level maps for Scratch Slayer.

HOW A LEVEL IS STORED
=====================
Every level is a GRID OF LETTERS: a Python list of strings, one string per ROW, top row first.
Each letter is one SQUARE of the map. This is exactly the same shape as the Scratch lists
"level 1 map" ... "level 6 map": build.py copies each list of strings straight into a Scratch
list (one string = one list item), and the Engine's 'load level' block reads it back letter by
letter. So whatever grid this file produces IS the level the game plays.

COORDINATES: a square is (column, row), both counting from 0.
  column = how far along the row (0 = the left end of the string)
  row    = which string in the list (0 = the TOP row)
So map_rows[row][column] is the letter on a square. Notice the order: row first, then column.
The game uses the same numbers ("player x" 3.5 = the middle of column 3, "player y" = the row).
In Scratch the lists count from 1 instead, so row 0, column 0 is item 1, letter 1.

HOW THE MAPS ARE MADE
  Levels 1-3   typed out in full below. What you see is exactly what you play. The column
               ruler above each map and the row numbers on the right help you find a square.
  Levels 4-6   too big to type comfortably (36 to 40 squares wide), so they are DRAWN with the
               Grid "drawing kit" class: fill rectangles, carve rooms, then place things.

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
# LEVEL 1: THE OUTPOST (20 x 20). Monsters: imps.
# =================================================================================================
#   rows 1-5    the start room (P at column 1, row 2, the shotgun N just below), then a door
#               (D at column 5, row 2) into the north hall
#   row 6       a wall of 2s with one door (column 12)
#   rows 7-11   the middle hall: the imp pack, two barrels (E), crates (3 and 4)
#   row 12      a wall with one door (column 15)
#   rows 13-18  the bottom room. The exit X is in the LEFT wall (column 0, row 16).
#               Bottom right: a secret wall S (column 15, row 18) hides a closet with shells (A)
#               and a health pack (H).
LEVEL_1_MAP = [
    #          1111111111     <- column numbers (tens)
    #01234567890123456789     <- column numbers (ones)
    "11111111111111111111",    # row 0
    "100001000000000000I1",    # row 1
    "1P000D000000M0000001",    # row 2
    "10000100020000200001",    # row 3
    "10N0010000000000M001",    # row 4
    "11111100000000000001",    # row 5
    "122222222222D2222221",    # row 6
    "10000030000000000001",    # row 7
    "100M003000M0E000M001",    # row 8
    "10000000000400400001",    # row 9
    "10H000300000000M0E01",    # row 10
    "10000030A00000000001",    # row 11
    "111111111111111D1111",    # row 12
    "100000I0000000000001",    # row 13
    "100M0002200000000H01",    # row 14
    "10000M00000022000001",    # row 15
    "X0000000000000002221",    # row 16
    "100022000M0000020A01",    # row 17
    "10000000000000ASH001",    # row 18
    "11111111111111111111",    # row 19
]
# =================================================================================================
# LEVEL 2: THE PROCESSING PLANT (24 x 24). Monsters: spitters. One key: red.
# =================================================================================================
#   rows 1-7    north rooms, split by a wall of 7s at column 15. The RED door R (column 15,
#               row 4) leads to the north-east room, which has the exit X in its top wall
#               (column 19, row 0). Top left: a secret wall S (column 3, row 1) hides a closet.
#   row 8       a wall with one door (column 12)
#   rows 9-16   the middle: a west room with the red key K (column 2, row 10), its door at
#               column 8, row 12, and a big east hall with the chaingun Q (column 12, row 10)
#   row 17      a wall with one door (column 16)
#   rows 18-22  the bottom: the player starts in the west room (P at column 2, row 20)
# The route: bottom -> middle -> red key -> north -> red door -> exit.
LEVEL_2_MAP = [
    #          11111111112222     <- column numbers (tens)
    #012345678901234567890123     <- column numbers (ones)
    "5555555555555555555X5555",    # row 0
    "5H0S00000000000700000005",    # row 1
    "50A7V0000000000700V00005",    # row 2
    "577000600060000700000005",    # row 3
    "50000000E0000H0R00000V05",    # row 4
    "500000600060V00700000005",    # row 5
    "50I000000000000700000005",    # row 6
    "500000000000000700000005",    # row 7
    "577777777777D77777777775",    # row 8
    "500000007000000000000005",    # row 9
    "50K00V00700HQ00000V00005",    # row 10
    "500000007000600000060005",    # row 11
    "50000000D000000V0E000005",    # row 12
    "500V00A0700000000000H005",    # row 13
    "5000000070006000H0060005",    # row 14
    "5000000070V0000000000V05",    # row 15
    "500000007000000000000005",    # row 16
    "5777777777777777D7777775",    # row 17
    "50000000500000000000V005",    # row 18
    "500000005000600006000005",    # row 19
    "50P00000D00000V000000005",    # row 20
    "500000005000600E06000A05",    # row 21
    "500000005000000000V0I005",    # row 22
    "555555555555555555555555",    # row 23
]
# =================================================================================================
# LEVEL 3: THE FORTRESS (28 x 28). Monsters: golems, and the WARDEN (boss). Keys: red and blue.
# =================================================================================================
#   rows 1-11   three wings side by side, split by walls at columns 9 and 18:
#               west wing (red key K) | inner keep (blue key J) | east wing (the warden W)
#   row 12      a wall with three doors: a plain door D into the west wing, the RED door R
#               into the keep, and the BLUE door B into the east wing
#   rows 13-20  the courtyard, with pillars (4) and a central block (9)
#   row 21      a wall with three doors into the side rooms
#   rows 22-26  the side rooms. The player starts in the middle one (P at column 13, row 25).
# The exit X (column 27, row 3) is in a closet sealed by a SKULL DOOR Z (column 25, row 3).
# Only the warden's skull key opens it, so the boss must fall first.
# The keep's top-right corner has a secret wall S (column 15, row 1) hiding shells and health.
LEVEL_3_MAP = [
    #          111111111122222222     <- column numbers (tens)
    #0123456789012345678901234567     <- column numbers (ones)
    "8888888888888888888888888888",    # row 0
    "8I0000000900000SAH90H0000008",    # row 1
    "80G00000090G0J00999000000998",    # row 2
    "800000000900000000900G000Z0X",    # row 3
    "8008880009004004009000000998",    # row 4
    "8000000G09000000009000000008",    # row 5
    "80K0000009000000G09999999008",    # row 6
    "8000000009000000009000000008",    # row 7
    "80800080090040040090000E0A08",    # row 8
    "8000G08009000G000090G0000008",    # row 9
    "8000000A09000000H09000000W08",    # row 10
    "8000000009000000009000000008",    # row 11
    "8999D99999999R99999999B99998",    # row 12
    "8H000000A00000000000000000A8",    # row 13
    "800G000000000000G000GE000008",    # row 14
    "8000040000000000000000400008",    # row 15
    "8000000000400990040000000008",    # row 16
    "8000000000000990000000000008",    # row 17
    "8000040000000000000000400008",    # row 18
    "80000000G00E000000000000G008",    # row 19
    "8000000000000000000A00000008",    # row 20
    "8888D88888888D88888888D88888",    # row 21
    "8000000008000000008000000008",    # row 22
    "80H00000080I0000008000000H08",    # row 23
    "800G00000800000000800000G008",    # row 24
    "800000A008000P0000800I000008",    # row 25
    "8000000008000000008000000008",    # row 26
    "8888888888888888888888888888",    # row 27
]

# =================================================================================================
# THE Grid DRAWING KIT (used for the big levels 4-6)
# =================================================================================================
class Grid:
    """A tiny drawing kit for big maps: start solid or hollow, then carve rooms and add walls.

    Typing a 40 x 40 map by hand is slow and easy to get wrong, so levels 4-6 are DRAWN with
    rectangles instead, a bit like a paint program:
        drawing = Grid(36, "2")            a 36 x 36 map: an outside wall of "2", floor inside
        drawing = Grid(38, "7", fill="7")  a 38 x 38 map that is SOLID wall 7 (dig caves into it)
        drawing.fill(left, top, right, bottom, "5")
                                           fill the rectangle from square (left, top) to square
                                           (right, bottom) with "5". Both corners are included.
                                           A rectangle one square wide is a wall; filling with
                                           "0" carves out a room.
        drawing.put(column, row, "D")      put one letter on one square (doors, the exit, secrets)
        drawing.things("M", [(5, 30), ...])
                                           put a thing on each (column, row) square in the list.
                                           It must land on empty floor (see things() below).
        drawing.rows()                     the finished map, as a list of strings
    Order matters: later drawing covers earlier drawing, so draw walls first, then cut doors
    into them, and add things last.
    """
    def __init__(self, size, border, fill="0"):
        # size   = width AND height (these maps are square)
        # border = the letter for the outside wall
        # fill   = what everything inside starts as: "0" (open floor) or a wall (solid rock)
        self.size = size
        # A list of rows, each a list of letters. Lists (not strings) because Python can change
        # one item of a list, but can't change one letter inside a string.
        self.squares = [[fill] * size for _ in range(size)]
        # The outside wall: the top row, the bottom row, the left column and the right column.
        last = size - 1
        for position in range(size):
            self.squares[0][position] = self.squares[last][position] = border
            self.squares[position][0] = self.squares[position][last] = border

    def put(self, column, row, letter):
        """One letter on one square."""
        self.squares[row][column] = letter

    def fill(self, left, top, right, bottom, letter):
        """Every square from (left, top) to (right, bottom), corners included. The + 1 is there
        because Python's range() stops just BEFORE its end number: range(3, 6) is 3, 4, 5."""
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                self.squares[row][column] = letter

    def things(self, letter, squares):
        """Put a thing (a monster, pickup, key, barrel, the player...) on every (column, row) in
        squares. Each square must still be empty floor, so a typo can't hide a monster inside a
        wall or drop two things on one square."""
        for column, row in squares:
            already_there = self.squares[row][column]
            check(already_there == "0",
                  f"can't put '{letter}' at {where(column, row)}: there is already a "
                  f"'{already_there}' there. Things need an empty floor square (0).")
            self.squares[row][column] = letter

    def rows(self):
        """The finished map: each row of letters glued into one string."""
        return ["".join(letters) for letters in self.squares]


# =================================================================================================
# LEVELS 4-6, drawn with Grid. Each function draws one level and returns its rows.
# Read them top to bottom: walls and rooms first, then doors, then pillars, then things.
# =================================================================================================
def _draw_level_4():
    """THE FOUNDRY (36 x 36): a loading bay, a huge pillared furnace hall full of chargers,
    two side corridors, and three north rooms. Red key in the north-west, exit in the north-east.

    Layout, top to bottom:
      rows 1-7    three north rooms (walls at columns 11 and 24), the red key K in the west one
      row 8       a wall with two plain doors and the RED door at column 32
      rows 9-26   west corridor | furnace hall | east corridor (walls at columns 6 and 29)
      row 27      a wall with two doors
      rows 28-34  the loading bay, where the player starts (P at column 18, row 33)
    The exit X is in the top wall at column 30, in the north-east room behind the red door.
    """
    drawing = Grid(36, "2")
    drawing.fill(1, 27, 34, 27, "5"); drawing.put(8, 27, "D"); drawing.put(27, 27, "D")   # bay / hall wall
    drawing.fill(6, 9, 6, 26, "5"); drawing.put(6, 18, "D")                               # hall / west corridor
    drawing.fill(29, 9, 29, 26, "5"); drawing.put(29, 14, "D")                            # hall / east corridor
    drawing.fill(1, 8, 34, 8, "5")                                                        # wall below the north rooms,
    drawing.put(3, 8, "D"); drawing.put(17, 8, "D"); drawing.put(32, 8, "R")              # with its three doors
    drawing.fill(11, 1, 11, 7, "5"); drawing.fill(24, 1, 24, 7, "5")                      # walls between them
    drawing.put(30, 0, "X")                                                               # the exit, in the top wall
    for column in (10, 24):                                                               # furnace pillars,
        for row in (12, 17, 22):                                                          # each one 2 x 2
            drawing.fill(column, row, column + 1, row + 1, "4")
    for row in (12, 22):
        drawing.fill(17, row, 18, row + 1, "4")
    # The middle pillar is HOLLOW: a 3 x 3 block, its center carved back to floor, with a secret
    # wall S on its north side. The center square gets rockets (U) a few lines down.
    drawing.fill(16, 16, 18, 18, "4"); drawing.put(17, 17, "0"); drawing.put(17, 16, "S")
    drawing.fill(14, 31, 15, 32, "5"); drawing.fill(21, 31, 22, 32, "5")                  # bay crates
    drawing.fill(3, 3, 4, 4, "5"); drawing.fill(29, 3, 30, 4, "5")                        # cover in the
    drawing.fill(15, 3, 15, 5, "4"); drawing.fill(20, 3, 20, 5, "4")                      # north rooms
    # THINGS: the letter first, then the (column, row) squares it goes on.
    drawing.things("P", [(18, 33)])                                                       # player start
    drawing.things("U", [(17, 17)])                                                       # rockets in the hollow pillar
    drawing.things("C", [(13, 15), (21, 15), (13, 20), (21, 20), (8, 11), (27, 24), (19, 10)])   # chargers
    drawing.things("M", [(5, 30), (30, 30), (26, 33), (3, 20)])                           # imps
    drawing.things("V", [(2, 12), (4, 24), (32, 12), (32, 23), (27, 5)])                  # spitters
    drawing.things("G", [(7, 4), (21, 2), (33, 2)])                                       # golems
    drawing.things("K", [(2, 2)]); drawing.things("L", [(17, 2)])                         # red key, rocket launcher
    drawing.things("H", [(2, 33), (33, 33), (9, 2), (33, 18), (2, 15)])                   # health
    drawing.things("A", [(16, 30), (12, 2), (31, 25)])                                    # shells
    drawing.things("I", [(10, 33), (28, 10), (4, 10), (25, 26)])                          # bullets
    drawing.things("U", [(22, 6), (8, 25)])                                               # rockets
    drawing.things("E", [(12, 25), (23, 10), (31, 30), (2, 26), (26, 2)])                 # barrels
    return drawing.rows()


def _draw_level_5():
    """THE SUNKEN VAULTS (38 x 38): solid rock with caverns carved out, joined by narrow
    tunnels. Red key north-west, blue key north, exit east behind the blue door. Dark!

    This one works the OTHER way round from level 4: the Grid starts completely SOLID (fill="7")
    and the caves and tunnels are carved out of it with floor ("0"), like digging.
    """
    drawing = Grid(38, "7", fill="7")
    # Each cave is a rectangle: (left, top, right, bottom).
    caves = {"start": (2, 28, 9, 35), "west": (2, 13, 12, 23), "south": (15, 26, 24, 35),
             "vault": (16, 11, 27, 22), "southeast": (29, 24, 35, 35), "east": (29, 2, 35, 20),
             "northwest": (2, 2, 13, 9), "north": (16, 2, 26, 7)}
    for left, top, right, bottom in caves.values():
        drawing.fill(left, top, right, bottom, "0")                                       # dig the cave out
        for corner_column, corner_row in ((left, top), (right, top), (left, bottom), (right, bottom)):
            drawing.put(corner_column, corner_row, "3")                                   # round the corners off
    # Tunnels one square wide join the caves.
    for column, top, bottom in ((5, 24, 27), (7, 10, 12), (20, 23, 25), (21, 8, 10)):     # up-and-down tunnels
        drawing.fill(column, top, column, bottom, "0")
    for row, left, right in ((31, 10, 14), (17, 13, 15), (30, 25, 28), (14, 28, 28)):     # left-and-right tunnels
        drawing.fill(left, row, right, row, "0")
    # The red door blocks the tunnel to the north cave, the blue door blocks the tunnel to the
    # east cave, and the exit is in the east wall of the east cave.
    drawing.put(21, 9, "R"); drawing.put(28, 14, "B"); drawing.put(36, 5, "X")
    for column, row in ((19, 14), (24, 14), (19, 19), (24, 19)):                          # vault pillars
        drawing.fill(column, row, column + 1, row + 1, "9")
    drawing.fill(6, 17, 7, 18, "3"); drawing.fill(32, 9, 33, 10, "9"); drawing.fill(19, 30, 20, 31, "3")   # rocks for cover
    # A one-square closet dug into the rock above the south-east cave, behind a secret wall.
    drawing.put(32, 23, "S")
    drawing.put(32, 22, "0")
    drawing.things("P", [(5, 33)])                                                        # player start
    drawing.things("F", [(4, 15), (10, 21), (22, 33), (17, 12), (26, 21), (33, 30), (31, 6), (24, 4)])   # wraiths
    drawing.things("V", [(11, 15), (26, 12), (34, 26), (20, 3)])                          # spitters
    drawing.things("G", [(22, 17), (3, 6), (33, 16)])                                     # golems
    drawing.things("M", [(8, 33), (16, 28), (11, 4)])                                     # imps
    drawing.things("K", [(3, 3)]); drawing.things("J", [(25, 3)])                         # red key, blue key
    drawing.things("H", [(32, 22), (3, 22), (23, 28), (34, 33), (17, 21), (34, 3)])       # health (first: the closet)
    drawing.things("A", [(11, 14), (16, 34), (8, 8)])                                     # shells
    drawing.things("I", [(2, 30), (25, 12), (30, 25), (12, 3)])                           # bullets
    drawing.things("U", [(34, 35), (17, 6), (4, 20)])                                     # rockets
    drawing.things("E", [(22, 13), (21, 21), (18, 33)])                                   # barrels
    return drawing.rows()


def _draw_level_6():
    """THE CORE (40 x 40): a ring corridor around four wings, and the Colossus's arena in the
    middle. Red key west, blue key east (behind the red door), the arena's blue door is in the
    south wing, and the exit closet is sealed by a skull door in the arena's north wall.

    The route a player has to take: start at the bottom of the ring -> red key in the west wing
    -> red door into the east wing -> blue key -> blue door from the south wing into the arena
    -> beat the Colossus for the skull key -> skull door -> exit.
    """
    drawing = Grid(40, "8")
    # Everything from (5, 5) to (34, 34) starts solid. The 4 squares left open all the way
    # around it (between it and the outside wall) become the RING corridor.
    drawing.fill(5, 5, 34, 34, "9")                                   # solid core, then carve it
    drawing.fill(6, 6, 17, 10, "0"); drawing.fill(23, 6, 33, 10, "0") # two north rooms
    drawing.fill(6, 13, 10, 27, "0"); drawing.fill(29, 13, 33, 27, "0")   # west + east wings
    drawing.fill(8, 29, 31, 33, "0")                                  # south wing
    # The arena: a 16 x 16 block of wall 4, then its inside carved out, leaving a 1-square wall.
    drawing.fill(12, 12, 27, 27, "4"); drawing.fill(13, 13, 26, 26, "0")
    # Doors from the ring into each part. The east wing's door is the RED one.
    drawing.put(11, 5, "D"); drawing.put(28, 5, "D"); drawing.put(5, 20, "D")
    drawing.put(34, 20, "R"); drawing.put(20, 34, "D")
    # (20, 27) is a square of the arena's own wall: clearing it makes the gap behind the blue door.
    drawing.put(20, 28, "B"); drawing.put(20, 27, "0")                # blue door into the arena
    drawing.put(20, 12, "Z"); drawing.put(20, 11, "0"); drawing.put(20, 10, "X")   # skull door -> exit closet
    for column, row in ((15, 15), (23, 15), (15, 23), (23, 23)):      # arena pillars
        drawing.fill(column, row, column + 1, row + 1, "9")
    drawing.fill(19, 8, 21, 9, "9")                                   # keep the closet walled off
    drawing.put(5, 31, "S"); drawing.put(6, 31, "0")                  # secret closet off the ring
    drawing.fill(12, 30, 13, 31, "4"); drawing.fill(26, 30, 27, 31, "4")   # cover in the south wing
    drawing.things("P", [(20, 37)])                                   # player start (bottom of the ring)
    drawing.things("T", [(20, 18)])                                   # the Colossus, in the arena
    drawing.things("C", [(30, 2), (9, 37), (20, 31), (31, 37), (31, 20)])   # chargers
    drawing.things("F", [(2, 10), (37, 28), (14, 8), (25, 8), (8, 24)])     # wraiths
    drawing.things("G", [(2, 30), (37, 10), (10, 31)])                      # golems
    drawing.things("V", [(8, 15), (32, 15), (29, 31), (16, 2)])             # spitters
    drawing.things("M", [(9, 2), (2, 20), (37, 20)])                        # imps
    drawing.things("K", [(7, 20)]); drawing.things("J", [(32, 26)])         # red key, blue key
    drawing.things("H", [(6, 31), (14, 14), (25, 25), (2, 2), (37, 37), (31, 9), (9, 27)])   # health (first: closet)
    drawing.things("A", [(14, 25), (8, 9), (33, 13)])                       # shells
    drawing.things("I", [(25, 14), (2, 37), (37, 2), (16, 32)])             # bullets
    drawing.things("U", [(13, 20), (26, 20), (24, 32), (6, 6)])             # rockets
    drawing.things("E", [(18, 22), (22, 22), (2, 15), (37, 25), (10, 9)])   # barrels
    return drawing.rows()


LEVEL_4_MAP, LEVEL_5_MAP, LEVEL_6_MAP = _draw_level_4(), _draw_level_5(), _draw_level_6()


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
    dict(name="The Outpost", rows=LEVEL_1_MAP, angle=0, ceil=(0, 10), floor=(7, 45), secret_look="2"),
    dict(name="The Processing Plant", rows=LEVEL_2_MAP, angle=0, ceil=(50, 30), floor=(35, 30), secret_look="7"),
    dict(name="The Fortress", rows=LEVEL_3_MAP, angle=270, ceil=(95, 45), floor=(2, 40), secret_look="9"),
    dict(name="The Foundry", rows=LEVEL_4_MAP, angle=270, ceil=(5, 40), floor=(8, 35), secret_look="4"),
    dict(name="The Sunken Vaults", rows=LEVEL_5_MAP, angle=270, ceil=(55, 20), floor=(50, 25), secret_look="7"),
    dict(name="The Core", rows=LEVEL_6_MAP, angle=270, ceil=(98, 60), floor=(0, 50), secret_look="9"),
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
