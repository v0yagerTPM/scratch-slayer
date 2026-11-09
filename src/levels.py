"""Level maps for Scratch Slayer.

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
from collections import deque

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

L2 = [
    "555555555555555555555X55"[:0] + "5" * 19 + "X" + "5" * 4,
    "5" + "0" * 14 + "7" + "0" * 7 + "5",
    "5000M" + "0" * 10 + "7" + "00M0000" + "5",
    "5" + "00000" + "6" + "000" + "6" + "0000" + "7" + "0" * 7 + "5",
    "5" + "0" * 12 + "H" + "0" + "R" + "00000" + "M" + "0" + "5",
    "5" + "00000" + "6" + "000" + "6" + "0M00" + "7" + "0" * 7 + "5",
    "5" + "0A" + "0" * 12 + "7" + "0" * 7 + "5",
    "5" + "0" * 14 + "7" + "0" * 7 + "5",
    "5" + "7" * 11 + "D" + "7" * 10 + "5",
    "5" + "0" * 7 + "7" + "0" * 14 + "5",
    "5" + "0K00M00" + "7" + "000000000M0000" + "5",
    "5" + "0" * 7 + "7" + "000" + "6" + "000000" + "6" + "000" + "5",
    "5" + "0" * 7 + "D" + "000000M0000000" + "5",
    "5" + "00M00A0" + "7" + "0" * 14 + "5",
    "5" + "0" * 7 + "7" + "000" + "6" + "000" + "H" + "00" + "6" + "000" + "5",
    "5" + "0" * 7 + "7" + "0M" + "0" * 10 + "M" + "0" + "5",
    "5" + "0" * 7 + "7" + "0" * 14 + "5",
    "5" + "7" * 15 + "D" + "7" * 6 + "5",
    "5" + "0" * 7 + "5" + "0" * 11 + "M00" + "5",
    "5" + "0" * 7 + "5" + "000" + "6" + "0000" + "6" + "00000" + "5",
    "5" + "0P00000" + "D" + "00000M" + "0" * 8 + "5",
    "5" + "0" * 7 + "5" + "000" + "6" + "0000" + "6" + "000" + "A" + "0" + "5",
    "5" + "0" * 7 + "5" + "0" * 9 + "M" + "0000" + "5",
    "5" * 24,
]


def _build_l3():
    W = H = 28
    g = [["0"] * W for _ in range(H)]
    def put(x, y, ch): g[y][x] = ch
    for i in range(W):
        put(i, 0, "8"); put(i, H - 1, "8"); put(0, i, "8"); put(W - 1, i, "8")
    for x in range(1, 27):
        put(x, 12, "9"); put(x, 21, "8")
    for y in range(1, 12):
        put(9, y, "9"); put(18, y, "9")
    for y in range(22, 27):
        put(9, y, "8"); put(18, y, "8")
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
            assert g[y][x] == "0", (ch, x, y)
            put(x, y, ch)
    return ["".join(r) for r in g]

L3 = _build_l3()


def _edit(rows, changes, swap=None):
    """Place letters at (x, y) squares, and optionally swap one letter for another everywhere."""
    grid = [list(r) for r in rows]
    if swap:
        grid = [[swap.get(ch, ch) for ch in r] for r in grid]
    for (x, y), ch in changes.items():
        grid[y][x] = ch
    return ["".join(r) for r in grid]

# Level 1 - imps. A secret closet in the bottom-right room, two barrels near the imp pack in the hall.
L1 = _edit(L1, {(16, 16): "2", (17, 16): "2", (18, 16): "2", (15, 17): "2", (17, 17): "A",
                (15, 18): "S", (16, 18): "H", (12, 8): "E", (17, 10): "E"})
# Level 2 - spitters. A secret closet in the north room, barrels near spitter groups, extra health.
L2 = _edit(L2, {(1, 1): "H", (3, 1): "S", (2, 2): "A", (3, 2): "7", (1, 3): "7", (2, 3): "7",
                (8, 4): "E", (17, 12): "E", (15, 21): "E", (11, 10): "H", (20, 13): "H"}, swap={"M": "V"})
# Level 3 - golems, and the warden boss guarding the exit wing. A secret closet in the keep.
L3 = _edit(L3, {(15, 1): "S", (16, 1): "A", (17, 1): "H", (16, 2): "9", (17, 2): "9",
                (25, 10): "W", (21, 14): "E", (11, 19): "E", (23, 8): "E", (8, 13): "A", (19, 20): "A"},
           swap={"M": "G"})

# Weapons + bullets for the pistol start: the shotgun waits in level 1's first room,
# the chaingun in level 2. Some shell boxes become bullet boxes.
L1 = _edit(L1, {(2, 4): "N", (18, 1): "I", (6, 13): "I"})
L2 = _edit(L2, {(12, 10): "Q", (2, 6): "I", (20, 22): "I"})
# Level 3: the exit switch now sits in a closet sealed by a SKULL DOOR (Z).
# Only the Warden's skull key opens it, so the boss must fall first.
L3 = _edit(L3, {(25, 2): "9", (26, 2): "9", (25, 3): "Z", (25, 4): "9", (26, 4): "9",
                (11, 23): "I", (21, 25): "I", (1, 1): "I"})


class Grid:
    """A tiny drawing kit for big maps: start solid or hollow, then carve rooms and add walls."""
    def __init__(self, size, border, fill="0"):
        self.size = size
        self.g = [[fill] * size for _ in range(size)]
        for i in range(size):
            self.g[0][i] = self.g[size - 1][i] = self.g[i][0] = self.g[i][size - 1] = border
    def put(self, x, y, ch):
        self.g[y][x] = ch
    def fill(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.g[y][x] = ch
    def things(self, ch, cells):
        for x, y in cells:
            assert self.g[y][x] == "0", (ch, x, y, self.g[y][x])
            self.g[y][x] = ch
    def rows(self):
        return ["".join(r) for r in self.g]


def _build_l4():
    """THE FOUNDRY (36 x 36): a loading bay, a huge pillared furnace hall full of chargers,
    two side corridors, and three north rooms. Red key in the north-west, exit in the north-east."""
    m = Grid(36, "2")
    m.fill(1, 27, 34, 27, "5"); m.put(8, 27, "D"); m.put(27, 27, "D")          # bay / hall wall
    m.fill(6, 9, 6, 26, "5"); m.put(6, 18, "D")                                   # hall / west corridor
    m.fill(29, 9, 29, 26, "5"); m.put(29, 14, "D")                                # hall / east corridor
    m.fill(1, 8, 34, 8, "5"); m.put(3, 8, "D"); m.put(17, 8, "D"); m.put(32, 8, "R")  # north rooms
    m.fill(11, 1, 11, 7, "5"); m.fill(24, 1, 24, 7, "5")
    m.put(30, 0, "X")
    for x in (10, 24):                                                            # furnace pillars
        for y in (12, 17, 22):
            m.fill(x, y, x + 1, y + 1, "4")
    for y in (12, 22):
        m.fill(17, y, 18, y + 1, "4")
    m.fill(16, 16, 18, 18, "4"); m.put(17, 17, "0"); m.put(17, 16, "S")           # hollow pillar
    m.fill(14, 31, 15, 32, "5"); m.fill(21, 31, 22, 32, "5")                      # bay crates
    m.fill(3, 3, 4, 4, "5"); m.fill(29, 3, 30, 4, "5"); m.fill(15, 3, 15, 5, "4"); m.fill(20, 3, 20, 5, "4")
    m.things("P", [(18, 33)])
    m.things("U", [(17, 17)])
    m.things("C", [(13, 15), (21, 15), (13, 20), (21, 20), (8, 11), (27, 24), (19, 10)])
    m.things("M", [(5, 30), (30, 30), (26, 33), (3, 20)])
    m.things("V", [(2, 12), (4, 24), (32, 12), (32, 23), (27, 5)])
    m.things("G", [(7, 4), (21, 2), (33, 2)])
    m.things("K", [(2, 2)]); m.things("L", [(17, 2)])
    m.things("H", [(2, 33), (33, 33), (9, 2), (33, 18), (2, 15)])
    m.things("A", [(16, 30), (12, 2), (31, 25)])
    m.things("I", [(10, 33), (28, 10), (4, 10), (25, 26)])
    m.things("U", [(22, 6), (8, 25)])
    m.things("E", [(12, 25), (23, 10), (31, 30), (2, 26), (26, 2)])
    return m.rows()


def _build_l5():
    """THE SUNKEN VAULTS (38 x 38): solid rock with caverns carved out, joined by narrow
    tunnels. Red key north-west, blue key north, exit east behind the blue door. Dark!"""
    m = Grid(38, "7", fill="7")
    caves = {"start": (2, 28, 9, 35), "west": (2, 13, 12, 23), "south": (15, 26, 24, 35),
             "vault": (16, 11, 27, 22), "southeast": (29, 24, 35, 35), "east": (29, 2, 35, 20),
             "northwest": (2, 2, 13, 9), "north": (16, 2, 26, 7)}
    for x0, y0, x1, y1 in caves.values():
        m.fill(x0, y0, x1, y1, "0")
        for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):      # knock the corners in: cave-like
            m.put(cx, cy, "3")
    for x, y0, y1 in ((5, 24, 27), (7, 10, 12), (20, 23, 25), (21, 8, 10)):      # vertical tunnels
        m.fill(x, y0, x, y1, "0")
    for y, x0, x1 in ((31, 10, 14), (17, 13, 15), (30, 25, 28), (14, 28, 28)):    # horizontal tunnels
        m.fill(x0, y, x1, y, "0")
    m.put(21, 9, "R"); m.put(28, 14, "B"); m.put(36, 5, "X")
    for x, y in ((19, 14), (24, 14), (19, 19), (24, 19)):                          # vault pillars
        m.fill(x, y, x + 1, y + 1, "9")
    m.fill(6, 17, 7, 18, "3"); m.fill(32, 9, 33, 10, "9"); m.fill(19, 30, 20, 31, "3")
    m.put(32, 23, "S")                                                             # secret closet
    m.put(32, 22, "0")
    m.things("P", [(5, 33)])
    m.things("F", [(4, 15), (10, 21), (22, 33), (17, 12), (26, 21), (33, 30), (31, 6), (24, 4)])
    m.things("V", [(11, 15), (26, 12), (34, 26), (20, 3)])
    m.things("G", [(22, 17), (3, 6), (33, 16)])
    m.things("M", [(8, 33), (16, 28), (11, 4)])
    m.things("K", [(3, 3)]); m.things("J", [(25, 3)])
    m.things("H", [(32, 22), (3, 22), (23, 28), (34, 33), (17, 21), (34, 3)])
    m.things("A", [(11, 14), (16, 34), (8, 8)])
    m.things("I", [(2, 30), (25, 12), (30, 25), (12, 3)])
    m.things("U", [(34, 35), (17, 6), (4, 20)])
    m.things("E", [(22, 13), (21, 21), (18, 33)])
    return m.rows()


def _build_l6():
    """THE CORE (40 x 40): a ring corridor around four wings, and the Colossus's arena in the
    middle. Red key west, blue key east (behind the red door), the arena's blue door is in the
    south wing, and the exit closet is sealed by a skull door in the arena's north wall."""
    m = Grid(40, "8")
    m.fill(5, 5, 34, 34, "9")                                     # solid core, then carve it
    m.fill(6, 6, 17, 10, "0"); m.fill(23, 6, 33, 10, "0")         # two north rooms
    m.fill(6, 13, 10, 27, "0"); m.fill(29, 13, 33, 27, "0")       # west + east wings
    m.fill(8, 29, 31, 33, "0")                                    # south wing
    m.fill(12, 12, 27, 27, "4"); m.fill(13, 13, 26, 26, "0")      # the arena
    m.put(11, 5, "D"); m.put(28, 5, "D"); m.put(5, 20, "D"); m.put(34, 20, "R"); m.put(20, 34, "D")
    m.put(20, 28, "B"); m.put(20, 27, "0")                        # blue door into the arena
    m.put(20, 12, "Z"); m.put(20, 11, "0"); m.put(20, 10, "X")    # skull door -> exit closet
    for x, y in ((15, 15), (23, 15), (15, 23), (23, 23)):         # arena pillars
        m.fill(x, y, x + 1, y + 1, "9")
    m.fill(19, 8, 21, 9, "9")                                      # keep the closet walled off
    m.put(5, 31, "S"); m.put(6, 31, "0")                          # secret closet off the ring
    m.fill(12, 30, 13, 31, "4"); m.fill(26, 30, 27, 31, "4")
    m.things("P", [(20, 37)])
    m.things("T", [(20, 18)])
    m.things("C", [(30, 2), (9, 37), (20, 31), (31, 37), (31, 20)])
    m.things("F", [(2, 10), (37, 28), (14, 8), (25, 8), (8, 24)])
    m.things("G", [(2, 30), (37, 10), (10, 31)])
    m.things("V", [(8, 15), (32, 15), (29, 31), (16, 2)])
    m.things("M", [(9, 2), (2, 20), (37, 20)])
    m.things("K", [(7, 20)]); m.things("J", [(32, 26)])
    m.things("H", [(6, 31), (14, 14), (25, 25), (2, 2), (37, 37), (31, 9), (9, 27)])
    m.things("A", [(14, 25), (8, 9), (33, 13)])
    m.things("I", [(25, 14), (2, 37), (37, 2), (16, 32)])
    m.things("U", [(13, 20), (26, 20), (24, 32), (6, 6)])
    m.things("E", [(18, 22), (22, 22), (2, 15), (37, 25), (10, 9)])
    return m.rows()


L4, L5, L6 = _build_l4(), _build_l5(), _build_l6()

LEVELS = [
    dict(name="The Outpost", rows=L1, angle=0, ceil=(0, 10), floor=(7, 45), secret_look="2"),
    dict(name="The Processing Plant", rows=L2, angle=0, ceil=(50, 30), floor=(35, 30), secret_look="7"),
    dict(name="The Fortress", rows=L3, angle=270, ceil=(95, 45), floor=(2, 40), secret_look="9"),
    dict(name="The Foundry", rows=L4, angle=270, ceil=(5, 40), floor=(8, 35), secret_look="4"),
    dict(name="The Sunken Vaults", rows=L5, angle=270, ceil=(55, 20), floor=(50, 25), secret_look="7"),
    dict(name="The Core", rows=L6, angle=270, ceil=(98, 60), floor=(0, 50), secret_look="9"),
]

WALL_CH = set("123456789DRBXSZ")
MONSTER_CH = set("MVGWCFT")
BOSS_CH = set("WT")
PICKUP_CH = set("HAIUNQL")
FLOOR_CH = set("0PKJ") | PICKUP_CH | MONSTER_CH


def _reach(rows, start, ok):
    H, W = len(rows), len(rows[0])
    reach, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in reach and rows[n[1]][n[0]] in ok:
                reach.add(n); q.append(n)
    return reach


def validate(lv):
    """Checks a map the way a careful player would: everything that matters must be reachable
    WITHOUT opening secret walls or blowing up barrels; pickups may hide behind secrets."""
    rows = lv["rows"]
    H, W = len(rows), len(rows[0])
    assert all(len(r) == W for r in rows), [len(r) for r in rows]
    assert set("".join(rows)) <= WALL_CH | FLOOR_CH | {"E"}, set("".join(rows)) - WALL_CH - FLOOR_CH
    edge = "123456789X"
    for x in range(W):
        assert rows[0][x] in edge and rows[-1][x] in edge
    for y in range(H):
        assert rows[y][0] in edge and rows[y][-1] in edge
    starts = [(x, y) for y in range(H) for x in range(W) if rows[y][x] == "P"]
    assert len(starts) == 1
    keys = set()
    while True:
        ok = (FLOOR_CH | {"D"} | ({"R"} if "K" in keys else set()) | ({"B"} if "J" in keys else set())
              | ({"Z"} if "boss" in keys else set()))
        reach = _reach(rows, starts[0], ok)
        found = {rows[y][x] for x, y in reach} & {"K", "J"}
        if {rows[y][x] for x, y in reach} & BOSS_CH:
            found.add("boss")      # beating a reachable boss drops the skull key
        if found <= keys:
            break
        keys |= found
    with_secrets = _reach(rows, starts[0], ok | {"S"})
    for y in range(H):
        for x in range(W):
            ch = rows[y][x]
            if ch in MONSTER_CH | {"K", "J"}:
                assert (x, y) in reach, f"{lv['name']}: {ch} at {x},{y} unreachable"
            if ch in PICKUP_CH:
                assert (x, y) in with_secrets, f"{lv['name']}: {ch} at {x},{y} unreachable"
            if ch == "S":
                assert any((x + dx, y + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
                    f"{lv['name']}: secret at {x},{y} can't be reached"
            if ch == "E":
                assert any((x + dx, y + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    exits = [(x, y) for y in range(H) for x in range(W) if rows[y][x] == "X"]
    assert len(exits) == 1
    ex, ey = exits[0]
    assert any((ex + dx, ey + dy) in reach for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), "exit unreachable"
    c = "".join(rows)
    bosses = sum(c.count(b) for b in BOSS_CH)
    assert bosses <= 1, "only one boss per level"
    if "Z" in c:
        assert bosses == 1, "a skull door needs a boss to drop the skull key"
        locked = _reach(rows, starts[0], ok - {"Z"})
        assert not any((ex + dx, ey + dy) in locked for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
            f"{lv['name']}: the exit can be reached without the skull door"
    return dict(size=f"{W}x{H}", **{k: c.count(k) for k in "MVGWCFTHAIUNQLKJESZ"})


if __name__ == "__main__":
    for lv in LEVELS:
        print(lv["name"], validate(lv))
