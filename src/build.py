"""Builds scratch-slayer.sb3 — a 6-level raycasting shooter made of real Scratch blocks.

Every Scratch variable, list, broadcast and custom block uses a descriptive name, and every
section of every script carries a comment that explains it.
"""
from sb3extra import *
import assets, assets2, assets3, assets4, assets5, assets6
from levels import LEVELS, validate

RAY_COUNT, STRIPE_WIDTH = 80, 6      # 80 rays, each drawn as a 6-px-wide vertical stripe
WALK_SPEED, MONSTER_SPEED, TURN_SPEED = 0.07, 0.025, 4   # per frame, at 30 frames per second
SPRINT_BOOST, SPRINT_DRAIN, STAMINA_REST, STAMINA_REFILL, EXHAUSTED_UNTIL = 1.75, 1.2, 20, 0.6, 40
CENTER_COLUMN = RAY_COUNT // 2 + 1   # list item of the crosshair column
START_BULLETS = 50
MIN_FOV, MAX_FOV = 60, 100

# wall letter, hue, saturation, brightness (Scratch pen 0-100 scales), style
#   style 0 = plain wall, 1 = door, 2 = exit switch (off), 3 = exit switch (on), 4 = secret wall
WALLS = [("1", 0, 0, 72, 0), ("2", 8, 55, 68, 0), ("3", 33, 50, 62, 0), ("4", 0, 70, 66, 0),
         ("5", 45, 18, 62, 0), ("6", 30, 75, 58, 0), ("7", 58, 28, 64, 0),
         ("8", 98, 72, 50, 0), ("9", 75, 22, 50, 0),
         ("D", 10, 30, 58, 1), ("R", 0, 90, 72, 1), ("B", 60, 90, 72, 1),
         ("X", 0, 0, 55, 2), ("Y", 0, 0, 55, 3), ("S", 0, 0, 60, 4), ("Z", 75, 30, 70, 5)]
#   style 5 = skull door: a door frame with two glowing red eyes

# One row per monster type. Each column becomes a Scratch list ("monster health", "monster speed"...),
# so students can rebalance monsters without touching any code.
MONSTER_COLUMNS = ["letters", "names", "health", "speed", "claw damage", "size", "keep distance",
                   "wake distance", "shots per volley", "shot delay", "shot speed", "shot damage",
                   "shot look", "voice pitch", "is boss", "special move"]
MONSTER_TYPES = [
    ["M", "imp",      3,  0.025, 12, 100, 0.9, 7,  0, 0,  0,    0,  "none",   0,    0, "none"],
    ["V", "spitter",  3,  0.02,  6,  95,  4,   9,  1, 75, 0.11, 10, "acid",   60,   0, "none"],
    ["G", "golem",    6,  0.022, 16, 130, 0.9, 7,  0, 0,  0,    0,  "none",   -90,  0, "none"],
    ["W", "warden",   24, 0.02,  16, 165, 2,   10, 3, 55, 0.13, 14, "fire",   -140, 1, "none"],
    ["C", "charger",  5,  0.028, 14, 120, 0.9, 9,  0, 0,  0,    0,  "none",   -40,  0, "charge"],
    ["F", "wraith",   4,  0.034, 10, 100, 0.9, 8,  0, 0,  0,    0,  "none",   120,  0, "blink"],
    ["T", "colossus", 60, 0.018, 25, 210, 2.2, 12, 3, 60, 0.14, 16, "plasma", -200, 1, "rage"],
]
CHARGER_TYPE = 5     # the colossus calls in two of these at half health

# One row per weapon, same idea as the monster table. 'ammo slot' = item number in "ammo counts":
# 0 = needs no ammo, 1 = bullets, 2 = shells, 3 = rockets.
WEAPON_COLUMNS = ["names", "ammo slots", "reload frames", "damage min", "damage max", "ranges", "aim widths"]
WEAPON_TYPES = [
    ["fist",            0, 16, 1, 2, 1.5, 1],
    ["pistol",          1, 14, 1, 1, 999, 1],
    ["shotgun",         2, 26, 2, 3, 999, 1.6],
    ["chaingun",        1, 5,  1, 1, 999, 1],
    ["rocket launcher", 3, 30, 0, 0, 0,   1],
]
AMMO = [("bullets", START_BULLETS, 200), ("shells", 0, 99), ("rockets", 0, 50)]   # name, new-game amount, most you can carry
# Per level: how far rays travel (bigger maps need a limit so the game stays fast), how quickly
# walls fade to black with distance, and how much monsters darken with distance.
LEVEL_MAX_RAY_STEPS = [64, 64, 64, 34, 26, 36]
LEVEL_LIGHT_FALLOFF = [4.5, 4.5, 4.5, 4.5, 6.5, 4.2]
LEVEL_SPRITE_DARKNESS = [0, 0, 0, 2, 5, 2]
LEVEL_SELECT_BEST_WEAPON = [2, 3, 4, 4, 5, 5]   # starting at level N from the options menu gives weapons 1..this

for lv in LEVELS:
    validate(lv)

# ---------------- names used in Scratch ----------------
# broadcasts
CLEAR, SPAWN, UPDATE, DRAW_HUD, DRAW_NUMBERS, FIRE, PUNCH = (
    "clear level", "spawn monsters and objects", "update monsters and objects", "draw HUD",
    "draw HUD numbers", "fire weapon", "punch")
SUMMON, START_MUSIC, APPLY_MUSIC = "summon monsters", "start music", "apply music setting"
DRAW_OPTIONS_PANEL, DRAW_OPTIONS_WIDGETS = "draw options panel", "draw options widgets"
OPTIONS = "options"   # 'screen showing' while the options menu is open
# screens + game states
NONE, TITLE, DIED, COMPLETE, WIN = "none", "title", "died", "level complete", "you win"
PLAYING, EXIT_REACHED, DEAD = "playing", "exit reached", "dead"
INTRO = "intro"   # used for both 'game state' and 'screen showing' while a level card or melt is on screen
SHOW_TITLE, SHOW_CARD = "show title", "show level card"
SHOW_DEATH, SHOW_WIN = "show death screen", "show victory screen"

def V(name): return Var(name)

def map_letter_at(column, row):
    """letter (column + 1) of item (row + 1) of current map — columns and rows count from 0."""
    return letter(add(column, 1), item(add(row, 1), "current map"))

P = Project()
stage = Target(P, "Stage", is_stage=True)
stage.costume("black", assets.BACKDROP, 240, 180)
stage.costume("title sky", assets6.TITLE_SKY, 240, 180)
stage.costume("victory sky", assets5.VICTORY_SKY, 240, 180)

STAGE_VARS = ["player x", "player y", "player angle", "look direction x", "look direction y",
              "camera plane x", "camera plane y", "projection factor", "hurt flash timer",
              "pickup flash timer", "map is showing", "shot fired this frame", "closest target depth",
              "shot target id", "shot range", "target hit id", "gun bob angle", "player is moving",
              "current level", "has red key", "has blue key", "level kills", "level monster count",
              "level item count", "level items collected", "message timer", "ceiling hue",
              "ceiling saturation", "floor hue", "floor saturation", "map width", "map height",
              "minimap square size", "health", "total kills",
              "boss health", "boss max health", "boss is awake", "level secret count", "level secrets found",
              # weapons
              "current weapon", "weapon switch timer", "hit damage", "aim width", "ammo shown",
              # bosses + the skull key
              "has skull key", "boss is dead", "boss death x", "boss death y", "boss name",
              # per-level look
              "max ray steps", "light falloff", "sprite darkness", "camera plane length",
              "options open", "options row", "options from game"]
for name in STAGE_VARS:
    stage.var(name)
stage.var("card is up", 0); stage.var("lightning glow", 0)
stage.var("killer type", 0); stage.var("killer name", "monster")
stage.var("total secrets found", 0); stage.var("total secret count", 0)
stage.var("stamina", 100); stage.var("is exhausted", 0); stage.var("is sprinting", 0)
stage.var("speed boost", 1); stage.var("stamina rest timer", 0)
# OPTIONS: these are NOT reset by the green flag, so your settings stick while the project is open.
stage.var("turn speed", 4); stage.var("mouse steering", 0); stage.var("mouse sensitivity", 5)
stage.var("field of view", 66); stage.var("music is on", 1); stage.var("start level choice", 1)
stage.var("highest level reached", 1)
stage.var("game state", TITLE); stage.var("screen showing", TITLE); stage.var("message name", "")

LEVEL_LISTS = [f"level {i + 1} map" for i in range(len(LEVELS))]
for name, lv in zip(LEVEL_LISTS, LEVELS):
    stage.lst(name, lv["rows"])
stage.lst("level start angles", [lv["angle"] for lv in LEVELS])
stage.lst("level ceiling hues", [lv["ceil"][0] for lv in LEVELS])
stage.lst("level ceiling saturations", [lv["ceil"][1] for lv in LEVELS])
stage.lst("level floor hues", [lv["floor"][0] for lv in LEVELS])
stage.lst("level floor saturations", [lv["floor"][1] for lv in LEVELS])
stage.lst("level secret wall looks", [lv["secret_look"] for lv in LEVELS])
stage.lst("level max ray steps", LEVEL_MAX_RAY_STEPS)
stage.lst("level light falloffs", LEVEL_LIGHT_FALLOFF)
stage.lst("level sprite darkness", LEVEL_SPRITE_DARKNESS)
stage.lst("level select best weapon", LEVEL_SELECT_BEST_WEAPON)
stage.lst("level intro monster", [1, 2, 3, 5, 6, 7])   # monster type shown walking onto each level's card
stage.lst("level intro boss", [0, 0, 4, 0, 0, 0])      # a boss shown in the background of the card (0 = none)
stage.lst("melt offsets", [0] * 24)
for column_number, column in enumerate(MONSTER_COLUMNS):
    stage.lst(f"monster {column}", [row[column_number] for row in MONSTER_TYPES])
for column_number, column in enumerate(WEAPON_COLUMNS):
    stage.lst(f"weapon {column}", [row[column_number] for row in WEAPON_TYPES])
stage.lst("weapons owned", [1, 1, 0, 0, 0])          # 1 = you have it. Item N = weapon slot N.
stage.lst("ammo names", [a[0] for a in AMMO])
stage.lst("ammo counts", [a[1] for a in AMMO])
stage.lst("ammo limits", [a[2] for a in AMMO])
stage.lst("ammo at level start", [a[1] for a in AMMO])
# Where every monster is right now (item N = monster id N). Rockets use these to find what they hit.
stage.lst("monster x positions"); stage.lst("monster y positions"); stage.lst("monster alive flags")
stage.lst("wall letters", [w[0] for w in WALLS]); stage.lst("wall hues", [w[1] for w in WALLS])
stage.lst("wall saturations", [w[2] for w in WALLS]); stage.lst("wall brightnesses", [w[3] for w in WALLS])
stage.lst("wall styles", [w[4] for w in WALLS])
stage.lst("current map"); stage.lst("wall distance per column", [0] * RAY_COUNT)
for name in ["monster start x", "monster start y", "monster start type", "item start x", "item start y",
             "item start type", "barrel start x", "barrel start y",
             "new shot x", "new shot y", "new shot speed x", "new shot speed y", "new shot damage", "new shot look",
             "new shot owner",
             "new explosion x", "new explosion y", "explosion x", "explosion y",
             "squares to clear x", "squares to clear y"]:
    stage.lst(name)
problems_id = stage.lst("map problems")
# HUD number slots: 1 health, 2 ammo for the weapon in your hands, 3-6 level-complete stats,
# 7 total kills (win screen), 8-9 secrets, 10-11 secrets found / in the whole game (win screen),
# 12-15 the options menu: turn speed, mouse sensitivity, field of view, start level
HUD_SLOTS = 15
stage.lst("HUD number values", [0] * HUD_SLOTS)
stage.lst("HUD number x", [-150, 222, 20, 130, 20, 130, 120, 20, 130, 50, 120, 176, 176, 176, 57])
stage.lst("HUD number y", [-158, -158, 30, 30, -15, -15, -78, -60, -60, -112, -112, 80, 20, -10, -70])
stage.lst("HUD number size", [100] * 11 + [70] * 4)
stage.lst("HUD number screen", [NONE, NONE, COMPLETE, COMPLETE, COMPLETE, COMPLETE, WIN, COMPLETE, COMPLETE, WIN, WIN,
                                OPTIONS, OPTIONS, OPTIONS, OPTIONS])

def list_monitor(name, x, y, w, h):
    lid = P.stage_lists[name][0]
    P.monitors.append({"id": lid, "mode": "list", "opcode": "data_listcontents", "params": {"LIST": name},
                       "spriteName": None, "value": [], "width": w, "height": h, "x": x, "y": y,
                       "visible": False})
list_monitor("map problems", 10, 10, 460, 230)
for name in LEVEL_LISTS:
    list_monitor(name, 5, 5, 300, 350)

# ============================================================================================
#                                        STAGE: THE LEVEL GUIDE
# ============================================================================================
GUIDE = [
"""HOW THE LEVELS WORK  (start here!)

Every level is a LIST on the Stage: "level 1 map", "level 2 map" ... "level 6 map".
Each ITEM in the list is one ROW of the map, top row first.
Each LETTER in a row is one SQUARE of the map, left to right.

So a level is just a grid of letters. Example (a tiny 7 x 5 room):
   1111111
   1P0M0A1
   10020X1   <- X sits in the wall: walk up to it and press E
   1000H01
   1111111

When a level starts, the Engine's "load level" block reads this grid
one letter at a time and builds the level from it. The 3D view is
drawn from the grid on every frame, so the grid IS the level.""",

"""THE LETTERS (the map legend)

0      empty floor you can walk on
1 - 9  walls. Each digit is a different wall color (see "wall letters")
D      a door. Face it and press E to open it
R      a RED door. Opens only after you pick up the red key
B      a BLUE door. Opens only after you pick up the blue key
X      the EXIT SWITCH. Put it in a wall. Press E on it to finish the level

Z      a SKULL DOOR. Opens only with the skull key the level's BOSS drops
S      a SECRET WALL. Looks like a normal wall; press E on it to open it

These letters are THINGS. The loader replaces each one with floor (0)
and remembers where it was:
P      where the player starts (exactly one per level)
M      an imp         (claws, level 1)
V      a spitter      (spits acid from a distance, level 2)
G      a golem        (big, tough, hits hard, level 3)
W      the warden     (BOSS: throws 3 fireballs at once)
C      a charger      (winds up, then charges in a straight line, level 4)
F      a wraith       (fades with distance, blinks sideways, level 5)
T      the colossus   (BOSS: plasma, gets angry and calls chargers, level 6)
H      a health pack (+25 health)
A      a box of shells (+8)      I  a box of bullets (+20)
U      a box of rockets (+4)
N      the shotgun   Q  the chaingun   L  the rocket launcher
K      the red key
J      the blue key
E      an exploding barrel. It stays solid until it is shot.

A BOSS (W or T) carries the skull key. Put a Z between the boss and
the exit, and players must beat the boss to leave. Only one boss per
level.

Upper or lower case both work. Scratch treats "m" and "M" as the same.""",

"""WHAT "load level" DOES, STEP BY STEP  (Engine sprite)

1. Empties "current map" and the start lists for monsters and items.
2. Picks the list for "current level" (level 1 map, level 2 map ...).
3. Goes through it ROW by ROW (item 1, item 2 ...) and inside each
   row LETTER by LETTER.
4. For each letter:
     P -> remembers "player x" and "player y", turns it into 0
     a monster letter (any letter in "monster letters") -> adds the
          square to "monster start x / y / type", turns it into 0
     H A K J I U N Q L -> adds it to "item start x / y / type",
          turns it into 0 (a boss also gets a hidden skull key, type 5)
     E -> adds it to "barrel start x / y" and KEEPS the E, so the
          barrel blocks you until it explodes
     S -> counts it as one of the level's secrets
     anything else (walls, doors, 0) is copied unchanged
   It also checks the letter for mistakes (see MAP CHECKER below).
5. Adds the finished row to "current map".
6. Reads the start angle and the ceiling/floor colors for this level.

After that, "start level" broadcasts "spawn monsters and objects".
The Monster, Pickup and Barrel sprites make one CLONE for every
entry in their start lists.

Why copy to "current map" instead of using "level 1 map" directly?
Opening a door changes its letter to 0 in "current map" only.
"level 1 map" is never changed, so retrying a level resets every door.""",

"""SQUARES AND COORDINATES

Inside the code, map columns and rows count from 0 (that makes the
math simpler). Row 0 is item 1 of the list, column 0 is letter 1.

The player and monsters stand anywhere INSIDE a square, so their
positions have decimals: "player x" = 3.5 is the middle of column 3.
floor(player x) gives the column the player is standing in.

Angles: 0 = facing right along a row (toward the end of the row)
        90 = facing DOWN the list (toward higher item numbers)
        180 = facing left,  270 = facing UP the list""",

"""HOW TO EDIT A LEVEL

EASY WAY (small changes):
1. Click the Stage, then the Variables category.
2. Tick the checkbox next to "level 1 map". The list appears on the stage.
3. Click any item to edit that row. Press Enter when done.
4. Untick the box to hide it again, then click the green flag to play.

BETTER WAY (big changes or a whole new map):
1. Show the list (step 2 above).
2. Right-click the list on the stage -> "export". A .txt file downloads.
3. Open it in Notepad (Windows) or TextEdit (Mac).
   Use a monospace font like Consolas or Courier so the grid lines up.
4. Edit the grid. One row per line. Save the file.
5. Right-click the list on the stage -> "import" and pick your file.

RULES FOR A MAP THAT WORKS
- Every row must be the SAME LENGTH.
- The outside edge must be walls (any digit, or X for the exit).
- Exactly ONE P and ONE X.
- Put the X in a wall that touches floor the player can reach.
- Put doors (D, R, B, Z) in a one-square gap between walls,
  otherwise players just walk around them.
- The red key K must be reachable BEFORE the red door R
  (same for J and B), or the level can't be finished.
- Keys, monsters and the exit must be reachable WITHOUT opening a
  secret wall or blowing up a barrel. Hide bonus items behind secrets.
- Put a secret wall S in a wall, with a closed-off closet behind it.
- Big maps (levels 4-6 are 36 to 40 wide) need a limit on how far rays
  travel: item N of "level max ray steps" (about 26-36 for big maps).
  Walls that far away are black anyway, so nobody notices.

MAP CHECKER: when a level starts, the loader checks rows of different
lengths, holes in the outside wall, unknown letters, and a missing P
or X. If it finds a problem, the "map problems" list pops up on the
stage telling you the row and letter number to fix.""",

"""CHANGING THE START DIRECTION AND COLORS

"level start angles"         item N = which way you face on level N
"level ceiling hues"         item N = ceiling color on level N
"level ceiling saturations"  item N = how colorful the ceiling is
"level floor hues"           item N = floor color
"level floor saturations"    item N = how colorful the floor is

Hue uses Scratch's pen color numbers (0 to 100):
  0 red, 8 orange, 15 yellow, 33 green, 50 cyan, 63 blue,
  75 purple, 90 pink
Saturation: 0 = grey, 100 = full color.

WALL COLORS: the lists "wall letters", "wall hues", "wall saturations",
"wall brightnesses" and "wall styles" line up item by item.
Item 2 of each list describes wall letter "2".
To invent a new wall letter (say W), add W to "wall letters" and add
a hue, saturation, brightness and style (0) to the other four lists.
Don't use P M V G W C F T H A I U N Q L K J E or 0 for walls: those
already mean something.

SECRET WALLS (S) copy the look of one wall per level:
"level secret wall looks" item N = which wall digit S looks like on
level N. Secret walls have no dark seams: sharp-eyed players can spot them.""",

"""MONSTER TYPES  (all the numbers live in lists you can edit)

The "monster ..." lists line up item by item. Item 1 = imp, 2 = spitter,
3 = golem, 4 = warden, 5 = charger, 6 = wraith, 7 = colossus.
For example, item 3 of "monster health" is how much damage a golem
can take.

monster letters      the map letter for this monster
monster names        used to pick costumes: "golem walk 1", "golem dead"
monster health       hit points (a pistol shot does 1, a shotgun blast 2-3)
monster speed        squares moved per frame (30 frames = 1 second)
monster claw damage  most health a claw attack takes (half to all of it)
monster size         percent size on screen (100 = imp size)
monster keep distance  stops this close to you (spitters stay back)
monster wake distance  starts chasing when you get this close
monster shots per volley  0 = no ranged attack, 3 = three fireballs
monster shot delay   frames between volleys
monster shot speed   squares per frame the projectile flies
monster shot damage  most damage one projectile does
monster shot look    projectile costume: "acid", "fire" or "plasma"
monster voice pitch  makes the pain/death sounds higher or lower
monster is boss      1 = shows the boss health bar and drops the skull key
monster special move "none", "charge" (charger), "blink" (wraith) or
                     "rage" (colossus). Give an imp "blink" and see!

NEW MONSTER: add one item to the end of EVERY "monster ..." list,
then give the Monster sprite four costumes named
"<name> walk 1", "<name> walk 2", "<name> attack", "<name> dead".
Its letter works in maps right away. (Optional: give the Death Message
sprite a "killed by <name>" costume with a tip for your monster.)""",

"""HOW TO ADD A 7TH LEVEL

1. Variables -> Make a List -> name it "level 7 map" (For all sprites).
   Fill it with your grid (export/import is easiest).
2. Add one item to the END of each of these lists:
   "level start angles", "level ceiling hues", "level ceiling saturations",
   "level floor hues", "level floor saturations", "level secret wall looks",
   "level intro monster" (monster type 1 to 7 shown on the level card),
   "level intro boss" (a boss type, or 0 for none), "level max ray steps",
   "level light falloffs", "level sprite darkness" and
   "level select best weapon".
   The game counts the items in "level start angles" to know how many
   levels there are, so it plays your new level after level 6 by itself.
3. In the Engine sprite, find "define load level". It has THREE blocks
   that say  if current level = 6 then ... "level 6 map".
   Duplicate each one, change 6 to 7, and pick "level 7 map".
4. (Optional) Give it a level card: duplicate the costume "card 6" in the
   Card Background sprite and "heading 6" in the Card Heading sprite,
   rename the copies "card 7" and "heading 7", and change the words.
   Without them, the game shows a "NEXT LEVEL" card instead.""",

"""HOW THE TITLE SCREEN AND LEVEL CARDS ARE ANIMATED

Every animated sprite runs a loop like:
   repeat until <game state is not "title">
       ...move a little...
Each pass of a loop like this waits for the next screen refresh, so one
pass = one frame (30 per second).

Title Logo: falls with gravity ('fall speed' gets 1.3 more negative each
  frame) and bounces: when it hits the floor its speed flips and shrinks
  to 45 percent. After 3 bounces it gently pulses using sin().
Title Monster: one clone per monster in its 'lineup' lists. Each walks in
  from the side, bobs up and down with sin(), and now and then roars.
Title Embers: the original makes clones at random; each clone floats up,
  wobbles sideways with sin() and fades out with the ghost effect.
Stage: random lightning = a brightness effect that fades each frame.

Level cards: the Engine shows the card for about 3 seconds (or until you
press SPACE), then plays a SCREEN MELT. The melt imitates the famous
transition from Doom (1993): the screen is cut into 24 columns that
slide down at slightly different speeds, revealing the level behind.
See 'start melt' and 'draw melt curtain' in the Engine sprite.

Death screen: whatever hurts you sets 'killer type'. When you die, the
monster that did it looms up and gloats, with a tip for beating it.
Victory screen: fireworks are clones too. A rocket clone slows as it
rises (gravity), then makes 14 spark clones that fly apart and fade.""",

"""SPRINT AND STAMINA (hold Q)

Sprint is on Q, easy to reach with your left pinky while using WASD.
(Scratch's 'key pressed' block cannot detect Shift.)
To use a different key, change the 'key q pressed?' block in the
Engine's 'walking' code (search for the SPRINT comment).

stamina          100 = full bar, 0 = empty
speed boost      1 when walking, 1.75 when sprinting
stamina rest timer   counts down after you stop sprinting; the bar
                 only refills once it reaches 0 (a short pause)
is exhausted     1 after you run the bar dry. You can't sprint again
                 until stamina is back up to 40 (the COOLDOWN).

The bar is drawn with the pen at the end of 'draw 3D view'. Its label
and outline are part of the HUD costumes. To tune it, edit the numbers
in the SPRINT blocks: 1.75 = speed boost, 1.2 = stamina drained per
frame, 20 = rest frames before refilling, 0.6 = refilled per frame.""",

"""WEAPONS  (keys 1-5)

The "weapon ..." lists line up item by item, like the monster lists:
item 1 fist, 2 pistol, 3 shotgun, 4 chaingun, 5 rocket launcher.

weapon names          used to pick costumes ("shotgun ready", "shotgun
                      firing") and sounds (the sound named "shotgun")
weapon ammo slots     0 = no ammo needed, otherwise the item number in
                      "ammo counts": 1 bullets, 2 shells, 3 rockets
weapon reload frames  frames between shots (30 frames = 1 second)
weapon damage min/max a hit does a random amount between these
weapon ranges         how far a hit reaches (fists: 1.5 squares)
weapon aim widths     1 = normal, bigger = easier to hit (shotgun spread)

"weapons owned" item N = 1 when you have weapon N.
"ammo counts" / "ammo limits": how much you carry / the most you can.
Rockets aren't instant hits: they fly as Projectile clones and explode
on walls, barrels and monsters, using the same explosion lists as
barrels. Too close and they hurt you too!

Doom (1993) made this number-key weapon scheme famous, and its pistol
start, shotgun pickup and rocket splash damage inspired these.""",

"""OPTIONS MENU  (O on the title screen, P to pause during the game)

turn speed          degrees you turn each frame with the arrow keys
mouse steering      1 = the mouse's distance from the middle of the
                    stage turns you, and clicking shoots. Scratch can't
                    lock the mouse pointer like PC shooters do.
mouse sensitivity   how fast mouse steering turns you
field of view       60 to 100 degrees. The camera plane's length is
                    tan(field of view / 2). Wolfenstein 3D used about 66.
music is on         1 = music plays (N also switches it)
start level choice  level select (only levels you have reached:
                    "highest level reached")

These are NOT reset by the green flag, so settings stick while the
project is open. The menu is drawn by the Options Panel and Options
Widgets sprites; the Engine's 'handle options input' block reads the
keys and the mouse.""",
]
gy = 0
for text in GUIDE:
    guide_height = 60 + 18 * len(text.split("\n"))
    stage.workspace_comment(text, 0, gy, width=560, height=guide_height)
    gy += guide_height + 40

# ============================================================================================
#                                              ENGINE
# ============================================================================================
E = Target(P, "Engine", layer=1, visible=False)
E.costume("dot", assets.TINY, 1, 1)
for nm, fn in (("door", assets2.door), ("switch", assets2.switch), ("locked", assets2.locked),
               ("secret", assets3.secret), ("melt", assets4.melt), ("out of breath", assets5.out_of_breath),
               ("menu click", assets6.menu_click)):
    d, n = fn(); E.sound(nm, d, assets.RATE, n)
ENGINE_VARS = [
    # raycaster
    "ray column", "ray screen position", "ray direction x", "ray direction y", "ray square x", "ray square y",
    "distance between x lines", "distance between y lines", "ray step x", "ray step y",
    "distance to next x line", "distance to next y line", "letter hit", "hit side", "ray steps taken",
    "wall distance", "wall stripe height", "spot along wall", "stripe screen x", "stripe brightness",
    "wall type number", "wall style", "shading band number",
    # movement + input
    "forward input", "strafe input", "move amount x", "move amount y", "next player x", "next player y",
    "wall buffer", "M key was held", "E key was held", "shot cooldown", "exit timer",
    "facing square x", "facing square y", "facing letter",
    # level loading + map editing
    "map row", "map column", "map letter", "row text", "new row text", "row count", "letter position",
    "first row length", "player starts found", "exits found",
    "square to change x", "square to change y", "new letter", "queue position",
    # level intro + melt
    "show intro", "intro start time", "melt column", "column offset", "curtain top", "melt done",
    # minimap
    "minimap letter", "minimap player x", "minimap player y",
    # weapons
    "weapon ammo slot", "weapon to try", "N key was held",
    # options menu
    "screen before options", "up key was held", "down key was held",
    "change direction", "change repeat timer", "mouse row", "mouse was down", "slider fraction", "last options row"]
for name in ENGINE_VARS:
    E.var(name)

def wait_for_space(skip_pause=False):
    blocks = [wait_until(not_(key("space"))), wait_until(key("space")), wait_until(not_(key("space")))]
    return blocks if skip_pause else [wait(0.5)] + blocks

# ---------------------------------------- one frame of play ----------------------------------------
facing_a_door = or_(or_(or_(eq(V("facing letter"), "D"), eq(V("facing letter"), "R")),
                        or_(eq(V("facing letter"), "B"), eq(V("facing letter"), "X"))),
                    eq(V("facing letter"), "Z"))  # S stays secret: no hint
frame = [
    note("EXPLOSIONS + BARREL WRECKAGE from last frame (see the custom block).",
         call("share explosions and clear wreckage")),
    note("SHOT RESULT: if you fired last frame, the monsters worked out which\n"
         "monster or barrel was in the crosshair and stored its id in\n"
         "'shot target id' (barrels are numbered from 1001). Now we pass that\n"
         "on as 'target hit id' so that monster or barrel takes the hit.",
         ifelse(eq(V("shot fired this frame"), 1),
                [setv("target hit id", V("shot target id")), setv("shot fired this frame", 0)],
                [setv("target hit id", 0)])),
    note("TURNING: left/right arrows change the angle you face by 'turn speed'\n"
         "degrees each frame (set it in the options menu). 'update camera' then\n"
         "works out the new look direction.",
         if_(key("left arrow"), chg("player angle", mul(-1, V("turn speed"))))),
    if_(key("right arrow"), chg("player angle", V("turn speed"))),
    note("MOUSE STEERING (turn it on in the options menu): the farther the mouse\n"
         "is from the middle of the stage, the faster you turn. Scratch can't\n"
         "lock the mouse pointer the way PC games do, so this steers instead.\n"
         "The 12-pixel dead zone in the middle stops you drifting.",
         if_(and_(eq(V("mouse steering"), 1), gt(abs_(mouse_x()), 12)),
             chg("player angle", mul(mouse_x(), mul(V("mouse sensitivity"), 0.0035))))),
    call("update camera"),
    note("WALKING: 'forward input' is +1 (up / W), -1 (down / S) or 0.\n"
         "'strafe input' is +1 (D), -1 (A) or 0.",
         setv("forward input", 0)), setv("strafe input", 0),
    if_(or_(key("up arrow"), key("w")), chg("forward input", 1)),
    if_(or_(key("down arrow"), key("s")), chg("forward input", -1)),
    if_(key("a"), chg("strafe input", -1)),
    if_(key("d"), chg("strafe input", 1)),
    note(f"SPRINT (hold Q while moving): Scratch's 'key pressed' block can't see\n"
         f"Shift, so sprint uses Q, next to W. Sprinting multiplies your\n"
         f"speed by {SPRINT_BOOST} and drains 'stamina' ({SPRINT_DRAIN} a frame). When you stop,\n"
         f"stamina waits {STAMINA_REST} frames, then refills {STAMINA_REFILL} a frame.",
         ifelse(and_(and_(key("q"), eq(V("is exhausted"), 0)),
                     and_(gt(V("stamina"), 0), or_(not_(eq(V("forward input"), 0)), not_(eq(V("strafe input"), 0))))),
                [setv("is sprinting", 1), setv("speed boost", SPRINT_BOOST), chg("stamina", -SPRINT_DRAIN),
                 setv("stamina rest timer", STAMINA_REST)],
                [setv("is sprinting", 0), setv("speed boost", 1),
                 ifelse(gt(V("stamina rest timer"), 0), [chg("stamina rest timer", -1)],
                        [chg("stamina", STAMINA_REFILL), if_(gt(V("stamina"), 100), setv("stamina", 100))])])),
    note(f"COOLDOWN: run the bar completely dry and you're out of breath. You\n"
         f"can't sprint again until stamina refills to {EXHAUSTED_UNTIL}.",
         if_(and_(lt(V("stamina"), 0.5), eq(V("is exhausted"), 0)),
             setv("stamina", 0), setv("is exhausted", 1), play("out of breath"),
             if_(lt(V("message timer"), 3), setv("message name", "out of breath"), setv("message timer", 50)))),
    if_(and_(eq(V("is exhausted"), 1), not_(lt(V("stamina"), EXHAUSTED_UNTIL))), setv("is exhausted", 0)),
    note("If a movement key is down, turn the inputs into a step on the map:\n"
         "forward follows the look direction, strafe goes sideways to it.\n"
         "Then 'move player with collision' tries the step without walking into walls.\n"
         "'gun bob angle' makes the shotgun sway while you walk.\n"
         "'speed boost' is 1 when walking and bigger when sprinting.",
         ifelse(or_(not_(eq(V("forward input"), 0)), not_(eq(V("strafe input"), 0))),
                [setv("player is moving", 1),
                 setv("move amount x", mul(sub(mul(V("look direction x"), V("forward input")),
                                               mul(V("look direction y"), V("strafe input"))),
                                           mul(WALK_SPEED, V("speed boost")))),
                 setv("move amount y", mul(add(mul(V("look direction y"), V("forward input")),
                                               mul(V("look direction x"), V("strafe input"))),
                                           mul(WALK_SPEED, V("speed boost")))),
                 call("move player with collision"), chg("gun bob angle", mul(12, V("speed boost")))],
                [setv("player is moving", 0)])),
    note("MINIMAP (M key): 'M key was held' remembers that the key is already\n"
         "down, so holding M toggles the map once instead of flickering on/off\n"
         "every frame.",
         ifelse(key("m"), [if_(eq(V("M key was held"), 0), setv("map is showing", sub(1, V("map is showing"))),
                               setv("M key was held", 1))],
                [setv("M key was held", 0)])),
    note("USE (E key): open a door or flip the exit switch, once per key press.",
         ifelse(key("e"), [if_(eq(V("E key was held"), 0), call("use door or switch"), setv("E key was held", 1))],
                [setv("E key was held", 0)])),
    note("HINT: if you are facing a door or the exit switch, and no other message\n"
         "is busy, show 'Press E ...' at the top of the screen.",
         call("find facing square")),
    if_(and_(lt(V("message timer"), 3), facing_a_door),
        ifelse(eq(V("facing letter"), "X"), [setv("message name", "switch hint")], [setv("message name", "door hint")]),
        setv("message timer", 2)),
    note("WEAPON KEYS 1-5: switch to a weapon you own ('weapons owned' item = 1).\n"
         "'weapon switch timer' lowers the old gun and raises the new one;\n"
         "you can't shoot until it's back up.",
         if_(and_(key("1"), not_(eq(V("current weapon"), 1))), setv("current weapon", 1), setv("weapon switch timer", 8))),
    *[if_(and_(key(str(n)), and_(eq(item(n, "weapons owned"), 1), not_(eq(V("current weapon"), n)))),
          setv("current weapon", n), setv("weapon switch timer", 8)) for n in range(2, 6)],
    note("SHOOTING (space, or click when mouse steering is on): only when the\n"
         "weapon has reloaded ('shot cooldown') and isn't being switched.\n"
         "The monsters check during their update whether they are in the crosshair.",
         if_(and_(or_(key("space"), and_(eq(V("mouse steering"), 1), mouse_down())),
                  and_(lt(V("shot cooldown"), 1), lt(V("weapon switch timer"), 1))),
             call("fire current weapon"))),
    note("PAUSE (P): open the options menu on top of the frozen game.",
         if_(key("p"), call("options menu", warp=False))),
    note("MUSIC (N): switch the music on or off, once per key press.",
         ifelse(key("n"), [if_(eq(V("N key was held"), 0), call("switch music"), setv("N key was held", 1))],
                [setv("N key was held", 0)])),
    note("DRAW THE FRAME: walls first ('draw 3D view' uses the pen), then the\n"
         "monsters and items update and place themselves, then the HUD on top.\n"
         "Plain 'broadcast' (not 'and wait') keeps each frame to ONE screen refresh,\n"
         "so the game runs at 30 frames per second.",
         call("draw 3D view")),
    call("copy numbers to HUD"), bcast(UPDATE), bcast(DRAW_HUD), bcast(DRAW_NUMBERS),
    note("TIMERS + END CHECKS: count down the reload. After the exit switch is\n"
         "flipped, 'exit timer' waits 20 frames so you see the switch turn green.\n"
         "Running out of health ends the level.",
         if_(gt(V("shot cooldown"), 0), chg("shot cooldown", -1))),
    if_(gt(V("weapon switch timer"), 0), chg("weapon switch timer", -1)),
    if_(gt(V("exit timer"), 0), chg("exit timer", -1), if_(lt(V("exit timer"), 1), setv("game state", EXIT_REACHED))),
    if_(lt(V("health"), 1), setv("health", 0), setv("game state", DEAD)),
]

E.script(
    flag(), hide(),
    note("NEW GAME: reset everything that carries over between levels.\n"
         "You start with your fists and the pistol (weapon slots 1 and 2).",
         setv("health", 100)), replace("weapons owned", 3, 0), replace("weapons owned", 4, 0),
    replace("weapons owned", 5, 0), setv("current weapon", 2), setv("weapon switch timer", 0),
    *[replace("ammo counts", i + 1, a[1]) for i, a in enumerate(AMMO)], call("remember ammo at level start"),
    setv("total kills", 0), setv("total secrets found", 0), setv("total secret count", 0), setv("current level", 1), setv("map is showing", 0), setv("M key was held", 0),
    setv("E key was held", 0), setv("shot cooldown", 0), setv("shot fired this frame", 0),
    setv("target hit id", 0), setv("gun bob angle", 0), setv("player is moving", 0),
    hide_list("map problems"), stop_sounds(), pen_clear(),
    note("TITLE SCREEN: load level 1 (ready for later), then tell the title\n"
         "sprites to start their animations, and wait for SPACE. O opens the\n"
         "options menu.",
         setv("game state", TITLE)), setv("screen showing", TITLE), setv("show intro", 1), setv("card is up", 0),
    call("start level", warp=False),
    bcast(SHOW_TITLE), wait_until(not_(key("space"))),
    until(key("space"), if_(key("o"), call("options menu", warp=False))),
    wait_until(not_(key("space"))),
    note("Leaving the title: changing 'game state' ends every title animation\n"
         "loop, and the music stops.",
         setv("game state", INTRO)), stop_sounds(),
    note("LEVEL SELECT: if the options menu picked a later level, start there\n"
         "with the weapons and ammo a player would have found by then.",
         if_(gt(V("start level choice"), 1),
             setv("current level", V("start level choice")), call("give level select weapons"),
             call("start level", warp=False))),
    note("LEVEL LOOP: each pass of 'forever' plays one level (or one retry).",
         forever(
             note("LEVEL START: a new level gets its intro card and the screen melt.\n"
                  "A retry after dying just melts in.",
                  ifelse(eq(V("show intro"), 1), [call("level intro", warp=False)], [call("melt in", warp=False)])),
             note("Start playing (and start the music). 'highest level reached' unlocks\n"
                  "levels in the options menu's level select.",
                  setv("game state", PLAYING)), setv("screen showing", NONE), bcast(START_MUSIC),
             if_(gt(V("current level"), V("highest level reached")), setv("highest level reached", V("current level"))),
             note("PLAY: repeat one frame at a time until you reach the exit or die.\n"
                  "Everything that happens in a frame is inside this loop.",
                  until(or_(eq(V("game state"), EXIT_REACHED), eq(V("game state"), DEAD)), *frame)),
             note("AFTER THE LEVEL:\n"
                  "Died -> show 'YOU DIED', take back this level's kills, refill health,\n"
                  f"give back the ammo you started the level with (at least {START_BULLETS}\n"
                  "bullets), and reload the SAME level.\n"
                  "Exit -> show the stats, go to the next level. After the last level\n"
                  "(the number of items in 'level start angles') show the win screen.",
                  ifelse(eq(V("game state"), DEAD),
                         [setv("screen showing", DIED), call("draw still frame", warp=False),
                          note("Who did it? 'killer type' was set by whatever hurt you last:\n"
                               "a monster type number, 0 for a barrel, -1 for your own rocket.",
                               ifelse(eq(V("killer type"), 0), [setv("killer name", "barrel")],
                                      [ifelse(eq(V("killer type"), -1), [setv("killer name", "rocket")],
                                              [setv("killer name", item(V("killer type"), "monster names"))])])),
                          stop_sounds(), bcast(SHOW_DEATH), *wait_for_space(), stop_sounds(),
                          chg("total kills", mul(-1, V("level kills"))), setv("health", 100),
                          call("restore ammo at level start"),
                          setv("show intro", 0), call("start level", warp=False)],
                         [setv("screen showing", COMPLETE), call("draw still frame", warp=False), *wait_for_space(),
                          chg("total secrets found", V("level secrets found")),
                          chg("total secret count", V("level secret count")),
                          chg("current level", 1),
                          if_(gt(V("current level"), length("level start angles")),
                              note("VICTORY: clear away the level, then let the victory sprites take\n"
                                   "over. The stats appear once their panel has faded in.",
                                   setv("screen showing", INTRO)), bcastw(DRAW_NUMBERS), bcastw(CLEAR), pen_clear(),
                              setv("screen showing", WIN), bcastw(DRAW_HUD), stop_sounds(), bcast(SHOW_WIN), wait(1.6),
                              call("copy numbers to HUD"), bcastw(DRAW_NUMBERS), stop_script()),
                          call("remember ammo at level start"), setv("show intro", 1),
                          call("start level", warp=False)])),
         )),
    comment="MAIN GAME SCRIPT  (read the comments down the left side)\n"
            "Title screen -> then for each level: play frames until you\n"
            "flip the exit switch or die -> results screen -> next level.\n"
            "The level design guide is in the Stage's code area.")

E.script(Def("share explosions and clear wreckage"),
    note("EXPLOSIONS: barrels that blew up last frame put their position in\n"
         "'new explosion x/y'. Copy them to 'explosion x/y' for THIS frame, so\n"
         "every monster and barrel sees the same list while it updates.",
         clear_list("explosion x")), clear_list("explosion y"), setv("queue position", 1),
    repeat(length("new explosion x"),
           addto("explosion x", item(V("queue position"), "new explosion x")),
           addto("explosion y", item(V("queue position"), "new explosion y")), chg("queue position", 1)),
    clear_list("new explosion x"), clear_list("new explosion y"),
    note("BARREL WRECKAGE: each exploded barrel asked for its square to become\n"
         "floor. Only the Engine can change the map, so it does that here.",
         setv("queue position", 1)),
    repeat(length("squares to clear x"),
           setv("square to change x", item(V("queue position"), "squares to clear x")),
           setv("square to change y", item(V("queue position"), "squares to clear y")),
           setv("new letter", 0), call("change map square"), chg("queue position", 1)),
    clear_list("squares to clear x"), clear_list("squares to clear y"),
         comment="SHARE EXPLOSIONS AND CLEAR WRECKAGE: runs at the start of every frame.")

E.script(Def("level intro", warp=False),
         note("Freeze the game and hide the HUD, gun and screens.",
              setv("game state", INTRO)), setv("screen showing", INTRO),
         bcastw(DRAW_HUD), bcastw(DRAW_NUMBERS),
         note("Show the card. The Card Background, Card Heading, Card Monster and\n"
              "Title Embers sprites animate themselves while 'card is up' = 1.",
              setv("card is up", 1)), bcast(SHOW_CARD),
         note("Wait about 3 seconds, or until SPACE (ignored for the first half\n"
              "second so a held key doesn't skip it by accident).",
              setv("intro start time", timer())),
         wait_until(or_(gt(sub(timer(), V("intro start time")), 3.4),
                        and_(key("space"), gt(sub(timer(), V("intro start time")), 0.6)))),
         wait_until(not_(key("space"))),
         note("Card down (the card sprites fade out), then melt into the level.",
              setv("card is up", 0)), call("melt in", warp=False),
         comment="LEVEL INTRO: the level card, then the screen melt.")

E.script(Def("melt in", warp=False),
         setv("game state", INTRO), setv("screen showing", INTRO),
         bcastw(DRAW_HUD), bcastw(DRAW_NUMBERS),
         call("start melt"), play("melt"),
         note("One frame per pass: draw the level, then the curtain on top of it.\n"
              "The curtain's columns slide down a bit more each frame.",
              until(eq(V("melt done"), 1), call("draw 3D view"), call("draw melt curtain"))),
         comment="MELT IN: reveal the level with a Doom-style screen melt.")

E.script(Def("start melt"),
         clear_list("melt offsets"),
         note("Each of the 24 columns gets a starting offset. Negative = a short\n"
              "wait before it starts moving. Each column's wait is close to its\n"
              "neighbor's (within 6), which gives the melt its ragged edge.\n"
              "Doom picked its starting offsets the same way.",
              addto("melt offsets", mul(-1, rnd(0, 15)))),
         setv("melt column", 2),
         repeat(23,
                setv("column offset", add(item(sub(V("melt column"), 1), "melt offsets"), mul(rnd(-1, 1), 6))),
                if_(gt(V("column offset"), 0), setv("column offset", 0)),
                if_(lt(V("column offset"), -36), setv("column offset", -36)),
                addto("melt offsets", V("column offset")), chg("melt column", 1)),
         setv("melt done", 0),
         comment="START MELT: set up the 24 melt columns.")

E.script(Def("draw melt curtain"),
         setv("melt done", 1), setv("melt column", 1), pen_size(21),
         repeat(24,
                note("Move this column down: slowly while waiting (offset below 0),\n"
                     "then faster and faster (each step is 12 percent bigger).",
                     setv("column offset", item(V("melt column"), "melt offsets"))),
                ifelse(lt(V("column offset"), 0), [chg("column offset", 2)],
                       [chg("column offset", add(4, mul(V("column offset"), 0.12)))]),
                replace("melt offsets", V("melt column"), V("column offset")),
                note("Still on screen? Draw the dark curtain from its top edge down to the\n"
                     "bottom, then a dark red rim on top. Round pen ends make it drip.",
                     if_(lt(V("column offset"), 380),
                         setv("melt done", 0),
                         ifelse(lt(V("column offset"), 0), [setv("curtain top", 180)],
                                [setv("curtain top", sub(180, V("column offset")))]),
                         pen_color("#120304"),
                         *line(add(-250, mul(V("melt column"), 20)), V("curtain top"),
                               add(-250, mul(V("melt column"), 20)), -200),
                         pen_color("#6a0c0c"),
                         *line(add(-250, mul(V("melt column"), 20)), V("curtain top"),
                               add(-250, mul(V("melt column"), 20)), sub(V("curtain top"), 2)))),
                chg("melt column", 1)),
         comment="DRAW MELT CURTAIN: one frame of the melt. Sets 'melt done' to 1\nwhen every column has slid off the bottom.")

E.script(Def("start level", warp=False),
         bcastw(CLEAR), call("load level"), bcastw(SPAWN), call("update camera"),
         comment="START LEVEL: delete the old monster and item clones, read the\n"
                 "map with 'load level', make new clones, then aim the camera.")

E.script(Def("draw still frame", warp=False),
         setv("target hit id", 0), setv("shot fired this frame", 0),
         call("draw 3D view"), bcastw(UPDATE), call("copy numbers to HUD"), bcastw(DRAW_HUD), bcastw(DRAW_NUMBERS),
         comment="DRAW STILL FRAME: draws one frame while the game is paused\n"
                 "(title, died, level complete, win). 'broadcast and wait' is fine\n"
                 "here because nothing is moving.")

HUD_SOURCES = ["health", "ammo shown", "level kills", "level monster count", "level items collected",
               "level item count", "total kills", "level secrets found", "level secret count",
               "total secrets found", "total secret count", "turn speed", "mouse sensitivity", "field of view"]
E.script(Def("copy numbers to HUD"),
         note("AMMO SHOWN = the ammo for the weapon in your hands. Fists use none, so\n"
              "it's empty text and the Digits sprite shows nothing.",
              setv("weapon ammo slot", item(V("current weapon"), "weapon ammo slots"))),
         ifelse(eq(V("weapon ammo slot"), 0), [setv("ammo shown", "")],
                [setv("ammo shown", item(V("weapon ammo slot"), "ammo counts"))]),
         *[replace("HUD number values", i + 1, V(v)) for i, v in enumerate(HUD_SOURCES)],
         note("Slot 15 (start level) only shows in the title screen's options menu.",
              ifelse(eq(V("options from game"), 1), [replace("HUD number values", 15, "")],
                     [replace("HUD number values", 15, V("start level choice"))])),
         comment="COPY NUMBERS TO HUD: the Digits sprite draws whatever is in\n'HUD number values'. Slot 1 health, 2 ammo, "
                 "3 level kills,\n4 monsters in level, 5 items collected, 6 items in level,\n7 total kills, "
                 "8 secrets found, 9 secrets in level, 10-11 secrets in the whole game,\n"
                 "12-15 the options menu.")


# ------------------------------------------- weapons -------------------------------------------
E.script(Def("fire current weapon"),
    note("Which ammo does this weapon use? 0 = none (fists), otherwise an item\n"
         "number in 'ammo counts' (1 bullets, 2 shells, 3 rockets).",
         setv("weapon ammo slot", item(V("current weapon"), "weapon ammo slots"))),
    ifelse(or_(eq(V("weapon ammo slot"), 0), gt(item(V("weapon ammo slot"), "ammo counts"), 0)),
           [note("FIRE: spend one round, start the reload, and copy this weapon's numbers\n"
                 "from the 'weapon ...' lists. 'hit damage' is rolled now; the monster\n"
                 "in the crosshair takes it next frame. 'aim width' > 1 = easier to hit\n"
                 "(the shotgun's spread).",
                 if_(gt(V("weapon ammo slot"), 0),
                     replace("ammo counts", V("weapon ammo slot"), sub(item(V("weapon ammo slot"), "ammo counts"), 1)))),
            setv("shot cooldown", item(V("current weapon"), "weapon reload frames")),
            setv("shot fired this frame", 1), setv("closest target depth", 999), setv("shot target id", 0),
            setv("shot range", item(V("current weapon"), "weapon ranges")),
            setv("hit damage", rnd(item(V("current weapon"), "weapon damage min"), item(V("current weapon"), "weapon damage max"))),
            setv("aim width", item(V("current weapon"), "weapon aim widths")),
            note("ROCKETS aren't instant: the launcher adds a rocket to the 'new shot'\n"
                 "lists (owner 0 = you) and the Projectile sprite flies it. Its range\n"
                 "is 0, so nothing is hit instantly.",
                 if_(eq(V("current weapon"), 5),
                     addto("new shot x", add(V("player x"), mul(V("look direction x"), 0.4))),
                     addto("new shot y", add(V("player y"), mul(V("look direction y"), 0.4))),
                     addto("new shot speed x", mul(V("look direction x"), 0.3)),
                     addto("new shot speed y", mul(V("look direction y"), 0.3)),
                     addto("new shot damage", 0), addto("new shot look", "rocket"), addto("new shot owner", 0))),
            ifelse(eq(V("current weapon"), 1), [bcast(PUNCH)], [bcast(FIRE)])],
           [note("OUT OF AMMO: switch to the best weapon that still has some.",
                 call("pick best weapon")),
            setv("message name", "out of ammo"), setv("message timer", 45)]),
    comment="FIRE CURRENT WEAPON: runs when you press SPACE and the weapon is ready.\n"
            "Every weapon works the same way; their differences are just numbers\n"
            "in the 'weapon ...' lists on the Stage (try changing them!).")

E.script(Def("pick best weapon"),
    note("Try slot 5, then 4, 3, 2. The first one you own that has ammo wins.\n"
         "If none do, you're down to your fists (slot 1).",
         setv("current weapon", 1)), setv("weapon to try", 5),
    repeat(4,
           setv("weapon ammo slot", item(V("weapon to try"), "weapon ammo slots")),
           if_(and_(and_(eq(V("current weapon"), 1), eq(item(V("weapon to try"), "weapons owned"), 1)),
                    gt(item(V("weapon ammo slot"), "ammo counts"), 0)),
               setv("current weapon", V("weapon to try"))),
           chg("weapon to try", -1)),
    setv("weapon switch timer", 8),
    comment="PICK BEST WEAPON: like Doom, switch away from an empty gun.")

E.script(Def("remember ammo at level start"),
    *[replace("ammo at level start", i + 1, item(i + 1, "ammo counts")) for i in range(len(AMMO))],
    comment="REMEMBER AMMO AT LEVEL START: so dying gives this level's ammo back.")

E.script(Def("restore ammo at level start"),
    *[replace("ammo counts", i + 1, item(i + 1, "ammo at level start")) for i in range(len(AMMO))],
    if_(lt(item(1, "ammo counts"), START_BULLETS), replace("ammo counts", 1, START_BULLETS)),
    comment="RESTORE AMMO AT LEVEL START: after dying. You always get at least\n"
            f"{START_BULLETS} bullets back so the pistol works.")

E.script(Def("give level select weapons"),
    note("Own every weapon from slot 3 up to 'level select best weapon' for\n"
         "the chosen level, with some ammo for each.",
         setv("weapon to try", 3)),
    repeat(3, if_(not_(gt(V("weapon to try"), item(V("current level"), "level select best weapon"))),
                  replace("weapons owned", V("weapon to try"), 1)),
           chg("weapon to try", 1)),
    replace("ammo counts", 1, 120),
    if_(eq(item(3, "weapons owned"), 1), replace("ammo counts", 2, 24)),
    if_(eq(item(5, "weapons owned"), 1), replace("ammo counts", 3, 8)),
    setv("current weapon", item(V("current level"), "level select best weapon")),
    call("remember ammo at level start"),
    comment="GIVE LEVEL SELECT WEAPONS: starting part-way through the game.")

E.script(Def("switch music"),
    setv("music is on", sub(1, V("music is on"))), bcast(APPLY_MUSIC),
    ifelse(eq(V("music is on"), 1), [setv("message name", "music on")], [setv("message name", "music off")]),
    setv("message timer", 40),
    comment="SWITCH MUSIC: N key. The Music and Prompt Text sprites listen for\n'apply music setting' and set their volume.")

# ------------------------------------------- options menu -------------------------------------------
ROW_Y = assets6.OPTION_ROW_Y
TRACK_LEFT, TRACK_RIGHT = assets6.TRACK_LEFT, assets6.TRACK_RIGHT
def clamp(var, low, high):
    return [if_(lt(V(var), low), setv(var, low)), if_(gt(V(var), high), setv(var, high))]

E.script(Def("options menu", warp=False),
    note("OPEN: remember which screen was showing (the title, or the game if\n"
         "you pressed P), and wait until you let go of the key that opened it.",
         setv("screen before options", V("screen showing"))),
    ifelse(eq(V("screen showing"), NONE), [setv("options from game", 1)], [setv("options from game", 0)]),
    setv("options open", 1), setv("screen showing", OPTIONS), setv("options row", 1),
    setv("mouse was down", 1), setv("change repeat timer", 0), play("menu click"),
    wait_until(not_(or_(key("o"), key("p")))),
    note("ONE MENU FRAME per pass: read the keys and mouse, then redraw.\n"
         "Plain broadcasts run in the order they're sent: panel, then the\n"
         "sliders and switches on top, then the numbers on top of those.",
         until(eq(V("options open"), 0),
               call("handle options input"), call("copy numbers to HUD"),
               bcast(DRAW_OPTIONS_PANEL), bcast(DRAW_OPTIONS_WIDGETS), bcast(DRAW_NUMBERS))),
    note("CLOSE: wait for the key to be let go (so the game doesn't pause again\n"
         "straight away), put the old screen back and hide the menu.",
         wait_until(not_(or_(key("o"), key("p"))))),
    setv("screen showing", V("screen before options")), play("menu click"),
    bcast(DRAW_OPTIONS_PANEL), bcast(DRAW_OPTIONS_WIDGETS), bcast(DRAW_NUMBERS),
    call("update camera"),
    comment="OPTIONS MENU: O on the title screen, P during the game.\n"
            "Runs one menu frame per screen refresh until you close it.")

E.script(Def("handle options input"),
    note("CLOSE with O or P.",
         if_(or_(key("o"), key("p")), setv("options open", 0))),
    setv("last options row", V("options row")),
    note("UP / DOWN (or W / S) pick a row, once per key press. From the game\n"
         "the last row (start level) can't be picked.",
         ifelse(or_(key("up arrow"), key("w")),
                [if_(eq(V("up key was held"), 0), chg("options row", -1)), setv("up key was held", 1)],
                [setv("up key was held", 0)])),
    ifelse(or_(key("down arrow"), key("s")),
           [if_(eq(V("down key was held"), 0), chg("options row", 1)), setv("down key was held", 1)],
           [setv("down key was held", 0)]),
    if_(lt(V("options row"), 1), setv("options row", 1)),
    if_(gt(V("options row"), sub(6, V("options from game"))), setv("options row", sub(6, V("options from game")))),
    note("LEFT / RIGHT (or A / D) change the value. Holding the key repeats the\n"
         "change every 5 frames, like a keyboard does.",
         setv("change direction", 0)),
    if_(or_(key("left arrow"), key("a")), setv("change direction", -1)),
    if_(or_(key("right arrow"), key("d")), setv("change direction", 1)),
    ifelse(eq(V("change direction"), 0), [setv("change repeat timer", 0)],
           [ifelse(gt(V("change repeat timer"), 0), [chg("change repeat timer", -1), setv("change direction", 0)],
                   [setv("change repeat timer", 5)])]),
    if_(not_(eq(V("change direction"), 0)),
        note("Row 1 turn speed, 2 mouse steering (on/off), 3 mouse sensitivity,\n"
             "4 field of view (2 degrees a step), 5 music (on/off), 6 start level.",
             if_(eq(V("options row"), 1), chg("turn speed", V("change direction")))),
        if_(eq(V("options row"), 2), setv("mouse steering", sub(1, V("mouse steering")))),
        if_(eq(V("options row"), 3), chg("mouse sensitivity", V("change direction"))),
        if_(eq(V("options row"), 4), chg("field of view", mul(2, V("change direction")))),
        if_(eq(V("options row"), 5), setv("music is on", sub(1, V("music is on"))), bcast(APPLY_MUSIC)),
        if_(eq(V("options row"), 6), chg("start level choice", V("change direction"))),
        play("menu click")),
    note("MOUSE: hold the button down on a row to pick it. On a slider, the\n"
         "knob jumps to the mouse (so you can drag it). A click on a switch\n"
         "flips it; on the level row, left half = down, right half = up.",
         ifelse(mouse_down(),
                [setv("mouse row", add(round_(div(sub(ROW_Y[0], mouse_y()), 30)), 1)),
                 if_(and_(and_(gt(V("mouse row"), 0), lt(V("mouse row"), sub(7, V("options from game")))),
                          lt(abs_(sub(mouse_y(), sub(ROW_Y[0], mul(sub(V("mouse row"), 1), 30)))), 13)),
                     setv("options row", V("mouse row")),
                     setv("slider fraction", div(sub(mouse_x(), TRACK_LEFT), TRACK_RIGHT - TRACK_LEFT)),
                     if_(lt(V("slider fraction"), 0), setv("slider fraction", 0)),
                     if_(gt(V("slider fraction"), 1), setv("slider fraction", 1)),
                     if_(gt(mouse_x(), TRACK_LEFT - 15),
                         if_(eq(V("mouse row"), 1), setv("turn speed", add(1, round_(mul(9, V("slider fraction")))))),
                         if_(eq(V("mouse row"), 3), setv("mouse sensitivity", add(1, round_(mul(9, V("slider fraction")))))),
                         if_(eq(V("mouse row"), 4), setv("field of view", add(MIN_FOV, mul(2, round_(mul((MAX_FOV - MIN_FOV) / 2, V("slider fraction")))))))),
                     if_(eq(V("mouse was down"), 0),
                         if_(eq(V("mouse row"), 2), setv("mouse steering", sub(1, V("mouse steering")))),
                         if_(eq(V("mouse row"), 5), setv("music is on", sub(1, V("music is on"))), bcast(APPLY_MUSIC)),
                         if_(eq(V("mouse row"), 6),
                             ifelse(lt(mouse_x(), 50), [chg("start level choice", -1)], [chg("start level choice", 1)])),
                         play("menu click"))),
                 setv("mouse was down", 1)],
                [setv("mouse was down", 0)])),
    note("Keep every setting inside its range.",
         *clamp("turn speed", 1, 10)[:1]), *clamp("turn speed", 1, 10)[1:],
    *clamp("mouse sensitivity", 1, 10), *clamp("field of view", MIN_FOV, MAX_FOV),
    if_(lt(V("start level choice"), 1), setv("start level choice", 1)),
    if_(gt(V("start level choice"), V("highest level reached")), setv("start level choice", V("highest level reached"))),
    if_(not_(eq(V("options row"), V("last options row"))), play("menu click")),
    comment="HANDLE OPTIONS INPUT: one frame of the options menu.")

# ------------------------------------------- level loader -------------------------------------------
def from_current_level_list(index, target_var):
    """if current level = 1 then set target to (item index of level 1 map) ... one 'if' per level."""
    return [if_(eq(V("current level"), i + 1), setv(target_var, item(index, name)))
            for i, name in enumerate(LEVEL_LISTS)]

def thing(letter_code, *blocks):
    return if_(eq(V("map letter"), letter_code), *blocks, setv("map letter", 0))

def item_start(type_number):
    return [addto("item start x", V("map column")), addto("item start y", V("map row")),
            addto("item start type", type_number)]

def problem(*parts):
    return addto("map problems", joins(*parts))

row_number, letter_number = add(V("map row"), 1), add(V("map column"), 1)
on_outside_edge = or_(or_(eq(V("map row"), 0), eq(V("map row"), sub(V("row count"), 1))),
                      or_(eq(V("map column"), 0), eq(V("map column"), sub(V("first row length"), 1))))

E.script(
    Def("load level"),
    note("1. CLEAR OUT the last level: empty the map and the start lists,\n"
         "and reset the per-level counters, keys and timers.",
         clear_list("current map")), clear_list("monster start x"), clear_list("monster start y"),
    clear_list("item start x"), clear_list("item start y"), clear_list("item start type"),
    clear_list("map problems"), clear_list("monster start type"),
    clear_list("barrel start x"), clear_list("barrel start y"),
    clear_list("new explosion x"), clear_list("new explosion y"), clear_list("explosion x"), clear_list("explosion y"),
    clear_list("squares to clear x"), clear_list("squares to clear y"),
    clear_list("new shot x"), clear_list("new shot y"), clear_list("new shot speed x"),
    clear_list("new shot speed y"), clear_list("new shot damage"), clear_list("new shot look"),
    clear_list("new shot owner"), setv("killer type", 0),
    setv("boss is awake", 0), setv("boss health", 0), setv("level secret count", 0), setv("level secrets found", 0),
    setv("level kills", 0), setv("level items collected", 0), setv("level monster count", 0),
    setv("has red key", 0), setv("has blue key", 0), setv("hurt flash timer", 0), setv("pickup flash timer", 0),
    setv("has skull key", 0), setv("boss is dead", 0), setv("weapon switch timer", 0),
    setv("exit timer", 0), setv("message timer", 0), setv("shot cooldown", 0),
    setv("stamina", 100), setv("is exhausted", 0), setv("is sprinting", 0), setv("speed boost", 1),
    setv("stamina rest timer", 0),
    setv("player starts found", 0), setv("exits found", 0),
    note("2. PICK THE LEVEL LIST. Scratch can't choose a list by number, so there\n"
         "is one 'if' per level, in THREE places: two here (row count, first row)\n"
         f"and one inside the loop below. To add level {len(LEVELS) + 1}, duplicate all three.",
         if_(eq(V("current level"), 1), setv("row count", length(LEVEL_LISTS[0])))),
    *[if_(eq(V("current level"), i + 1), setv("row count", length(name)))
      for i, name in enumerate(LEVEL_LISTS) if i > 0],
    *from_current_level_list(1, "row text"),
    setv("first row length", strlen(V("row text"))),
    note("3. READ THE MAP ROW BY ROW. 'map row' counts from 0 (row 0 = item 1).",
         setv("map row", 0)),
    repeat(V("row count"),
           note("Get this row's text from the level list.",
                if_(eq(V("current level"), 1), setv("row text", item(add(V("map row"), 1), LEVEL_LISTS[0])))),
           *[if_(eq(V("current level"), i + 1), setv("row text", item(add(V("map row"), 1), name)))
             for i, name in enumerate(LEVEL_LISTS) if i > 0],
           note("MAP CHECK: every row must be as long as the first one.",
                if_(not_(eq(strlen(V("row text")), V("first row length"))),
                    problem("Row ", row_number, " has ", strlen(V("row text")), " letters but row 1 has ",
                            V("first row length"), ". Every row must be the same length."))),
           setv("new row text", ""), setv("map column", 0),
           note("4. LOOK AT EACH LETTER in the row, left to right.",
                repeat(strlen(V("row text")),
                       setv("map letter", letter(add(V("map column"), 1), V("row text"))),
                       note("THINGS: P, the monster letters, H, A, K and J are not walls.\n"
                            "Remember where each one is, then turn its square into floor (0).\n"
                            "Player start -> 'player x/y' (the +0.5 puts you in the middle\n"
                            "of the square).",
                            thing("P", setv("player x", add(V("map column"), 0.5)),
                                  setv("player y", add(V("map row"), 0.5)), chg("player starts found", 1))),
                       note("MONSTERS: if the letter is in 'monster letters', its position in\n"
                            "that list is the monster TYPE (1 imp, 2 spitter, 3 golem, 4 warden,\n"
                            "5 charger, 6 wraith, 7 colossus). A BOSS also gets a skull key\n"
                            "(item 5) on its square: it stays hidden until the boss dies.",
                            if_(gt(itemnum(V("map letter"), "monster letters"), 0),
                                addto("monster start x", V("map column")), addto("monster start y", V("map row")),
                                addto("monster start type", itemnum(V("map letter"), "monster letters")),
                                if_(eq(item(itemnum(V("map letter"), "monster letters"), "monster is boss"), 1),
                                    *item_start(5)),
                                chg("level monster count", 1), setv("map letter", 0))),
                       note("Items -> 'item start x/y/type': 1 health, 2 shells, 3 red key,\n"
                            "4 blue key, (5 skull key), 6 bullets, 7 rockets, 8 shotgun,\n"
                            "9 chaingun, 10 rocket launcher.",
                            thing("H", *item_start(1))),
                       thing("A", *item_start(2)),
                       thing("K", *item_start(3)), thing("J", *item_start(4)),
                       *[thing(ch, *item_start(n)) for ch, n in (("I", 6), ("U", 7), ("N", 8), ("Q", 9), ("L", 10))],
                       note("BARRELS (E) keep their letter, so they block like a wall until they\n"
                            "explode. SECRET WALLS (S) are counted for the results screen.",
                            if_(eq(V("map letter"), "E"), addto("barrel start x", V("map column")),
                                addto("barrel start y", V("map row")))),
                       if_(eq(V("map letter"), "S"), chg("level secret count", 1)),
                       note("MAP CHECKS for this letter: count exits, spot letters the game\n"
                            "doesn't know, and spot holes in the outside wall.",
                            if_(eq(V("map letter"), "X"), chg("exits found", 1))),
                       if_(and_(and_(not_(eq(V("map letter"), 0)), not_(eq(V("map letter"), "E"))),
                                eq(itemnum(V("map letter"), "wall letters"), 0)),
                           problem("Row ", row_number, ", letter ", letter_number, ": \"", V("map letter"),
                                   "\" is not a letter the game knows.")),
                       if_(and_(eq(V("map letter"), 0), on_outside_edge),
                           problem("Row ", row_number, ", letter ", letter_number,
                                   ": the outside edge must be a wall, not floor or a thing.")),
                       note("Add the (possibly changed) letter to the new row and move right.",
                            setv("new row text", join(V("new row text"), V("map letter")))),
                       chg("map column", 1))),
           note("5. The row is finished: add it to 'current map', move down a row.",
                addto("current map", V("new row text"))),
           chg("map row", 1)),
    note("6. FINAL MAP CHECKS: exactly one player start and at least one exit.\n"
         "If anything went wrong, show the 'map problems' list on the stage.",
         if_(eq(V("player starts found"), 0), problem("No player start. Put one P on the map."))),
    if_(gt(V("player starts found"), 1),
        problem("Found ", V("player starts found"), " player starts (P). There should be only one.")),
    if_(eq(V("exits found"), 0), problem("No exit switch. Put an X in a wall next to floor.")),
    ifelse(gt(length("map problems"), 0), [show_list("map problems")], [hide_list("map problems")]),
    note("7. LEVEL SETTINGS: map size (for the minimap), start angle and the\n"
         "ceiling/floor colors, all read from item 'current level' of each list.",
         setv("level item count", length("item start x"))),
    setv("map width", V("first row length")), setv("map height", length("current map")),
    setv("minimap square size", floor_(div(112, V("map width")))),
    setv("player angle", item(V("current level"), "level start angles")),
    setv("ceiling hue", item(V("current level"), "level ceiling hues")),
    setv("ceiling saturation", item(V("current level"), "level ceiling saturations")),
    setv("floor hue", item(V("current level"), "level floor hues")),
    setv("floor saturation", item(V("current level"), "level floor saturations")),
    note("Big levels: rays stop after 'max ray steps' squares (far walls are\n"
         "black anyway), 'light falloff' = how fast walls get darker with\n"
         "distance, 'sprite darkness' = the same for monsters and items.",
         setv("max ray steps", item(V("current level"), "level max ray steps"))),
    setv("light falloff", item(V("current level"), "level light falloffs")),
    setv("sprite darkness", item(V("current level"), "level sprite darkness")),
    comment="LOAD LEVEL: turns the letters in 'level N map' into a playable level.\n"
            "The full step-by-step explanation and how to design your own levels\n"
            "is in the comments on the STAGE (click the Stage, then Code).")

# --------------------------------------------- camera + movement ---------------------------------------------
E.script(
    Def("update camera"),
    note("Look direction = which way you face, as an arrow 1 square long:\n"
         "x = cos(angle), y = sin(angle).",
         setv("look direction x", cos_(V("player angle")))), setv("look direction y", sin_(V("player angle"))),
    note("Camera plane = an arrow at right angles to the look direction. It is\n"
         "the 'window' the rays pass through. Its length = tan(field of view / 2):\n"
         "a longer window lets wider rays through. 66 degrees (length 0.66) is\n"
         "about what Wolfenstein 3D used. Change 'field of view' in the options.",
         setv("camera plane length", tan_(div(V("field of view"), 2)))),
    setv("camera plane x", mul(V("look direction y"), mul(-1, V("camera plane length")))),
    setv("camera plane y", mul(V("look direction x"), V("camera plane length"))),
    note("Projection factor: a number the monsters and items use to work out\n"
         "where they appear on screen. It is 1 / (the 'determinant' of the\n"
         "look direction and camera plane).",
         setv("projection factor", div(1, sub(mul(V("camera plane x"), V("look direction y")),
                                              mul(V("look direction x"), V("camera plane y")))))),
    comment="UPDATE CAMERA: works out which way the camera points from\n'player angle'. Runs every frame after turning.")

E.script(
    Def("move player with collision"),
    note("Try the X part of the step first. 'wall buffer' looks 0.25 squares\n"
         "ahead of you so you stop BEFORE your face touches the wall.",
         setv("next player x", add(V("player x"), V("move amount x")))),
    ifelse(gt(V("move amount x"), 0), [setv("wall buffer", 0.25)], [setv("wall buffer", -0.25)]),
    note("Only move if that square is floor (0).",
         if_(eq(map_letter_at(floor_(add(V("next player x"), V("wall buffer"))), floor_(V("player y"))), 0),
             setv("player x", V("next player x")))),
    note("Then try the Y part on its own. Doing X and Y separately lets you\n"
         "slide along a wall instead of getting stuck on it.",
         setv("next player y", add(V("player y"), V("move amount y")))),
    ifelse(gt(V("move amount y"), 0), [setv("wall buffer", 0.25)], [setv("wall buffer", -0.25)]),
    if_(eq(map_letter_at(floor_(V("player x")), floor_(add(V("next player y"), V("wall buffer")))), 0),
        setv("player y", V("next player y"))),
    comment="MOVE PLAYER WITH COLLISION: moves you by 'move amount x/y'\nunless a wall is in the way.")

E.script(Def("find facing square"),
         setv("facing square x", floor_(add(V("player x"), mul(V("look direction x"), 0.9)))),
         setv("facing square y", floor_(add(V("player y"), mul(V("look direction y"), 0.9)))),
         setv("facing letter", map_letter_at(V("facing square x"), V("facing square y"))),
         comment="FIND FACING SQUARE: which square is 0.9 squares in front of you,\n"
                 "and what letter is in it? Used for doors and the exit switch.")

E.script(Def("change map square"),
         note("Get the row, then rebuild it letter by letter.",
              setv("row text", item(add(V("square to change y"), 1), "current map"))),
         setv("new row text", ""), setv("letter position", 1),
         repeat(strlen(V("row text")),
                note("At the square we're changing, use 'new letter'.\nEverywhere else, copy the old letter.",
                     ifelse(eq(V("letter position"), add(V("square to change x"), 1)),
                            [setv("new row text", join(V("new row text"), V("new letter")))],
                            [setv("new row text", join(V("new row text"), letter(V("letter position"), V("row text"))))])),
                chg("letter position", 1)),
         replace("current map", add(V("square to change y"), 1), V("new row text")),
         comment="CHANGE MAP SQUARE: puts 'new letter' at 'square to change x/y'\n"
                 "in 'current map'. Scratch can't change one letter inside a piece\n"
                 "of text, so we rebuild the whole row with the new letter in it.")

E.script(Def("open door"),
         setv("square to change x", V("facing square x")), setv("square to change y", V("facing square y")),
         setv("new letter", 0), call("change map square"), play("door"),
         comment="OPEN DOOR: replace the door in front of you with floor (0).")

E.script(
    Def("use door or switch"), call("find facing square"),
    note("D = ordinary door: always opens.",
         if_(eq(V("facing letter"), "D"), call("open door"))),
    note("R = red door: opens with the red key, otherwise show a message.",
         if_(eq(V("facing letter"), "R"), ifelse(eq(V("has red key"), 1), [call("open door")],
             [setv("message name", "need red key"), setv("message timer", 50), play("locked")]))),
    note("B = blue door: same idea with the blue key.",
         if_(eq(V("facing letter"), "B"), ifelse(eq(V("has blue key"), 1), [call("open door")],
             [setv("message name", "need blue key"), setv("message timer", 50), play("locked")]))),
    note("Z = skull door: only the skull key the boss drops opens it.",
         if_(eq(V("facing letter"), "Z"), ifelse(eq(V("has skull key"), 1), [call("open door")],
             [setv("message name", "need skull key"), setv("message timer", 60), play("locked")]))),
    note("S = secret wall: slide it open (turn it into floor), count the secret\n"
         "and celebrate.",
         if_(eq(V("facing letter"), "S"),
             setv("square to change x", V("facing square x")), setv("square to change y", V("facing square y")),
             setv("new letter", 0), call("change map square"), play("secret"), chg("level secrets found", 1),
             setv("message name", "found secret"), setv("message timer", 60))),
    note("X = exit switch: change it to Y (the switch drawn green) and start\n"
         "the 'exit timer'. The main loop ends the level when it runs out.",
         if_(eq(V("facing letter"), "X"),
             setv("square to change x", V("facing square x")), setv("square to change y", V("facing square y")),
             setv("new letter", "Y"), call("change map square"), play("switch"),
             setv("message name", "exit activated"), setv("message timer", 40), setv("exit timer", 20))),
    comment="USE DOOR OR SWITCH: runs when you press E.")

# ------------------------------------------------ raycaster ------------------------------------------------
ceiling = [
    note("CEILING: 6 wide horizontal pen lines from the top of the screen down\n"
         "to the middle. Each band is a little brighter, which fakes depth.",
         setv("shading band number", 0)),
    pen_color("#ff0000"), pen_param("color", V("ceiling hue")),
    pen_param("saturation", V("ceiling saturation")), pen_size(31),
    repeat(6, pen_param("brightness", add(10, mul(V("shading band number"), 2))),
           *line(-240, sub(165, mul(V("shading band number"), 30)), 240, sub(165, mul(V("shading band number"), 30))),
           chg("shading band number", 1))]
floor_bands = [
    note("FLOOR: the same trick from the middle down, getting brighter toward\nyour feet.",
         setv("shading band number", 0)),
    pen_color("#ff0000"), pen_param("color", V("floor hue")), pen_param("saturation", V("floor saturation")),
    repeat(6, pen_param("brightness", add(14, mul(V("shading band number"), 6))),
           *line(-240, sub(-15, mul(V("shading band number"), 30)), 240, sub(-15, mul(V("shading band number"), 30))),
           chg("shading band number", 1))]

ray = [
    note("RAY DIRECTION: 'ray screen position' goes from -1 (left edge) to +1\n"
         "(right edge). The ray points along the look direction, bent\n"
         "sideways by that much of the camera plane.",
         setv("ray screen position", sub(div(mul(2, V("ray column")), RAY_COUNT), 1))),
    setv("ray direction x", add(V("look direction x"), mul(V("camera plane x"), V("ray screen position")))),
    setv("ray direction y", add(V("look direction y"), mul(V("camera plane y"), V("ray screen position")))),
    note("The ray starts in the square you are standing in.",
         setv("ray square x", floor_(V("player x")))), setv("ray square y", floor_(V("player y"))),
    note("SETUP FOR DDA ('digital differential analysis'):\n"
         "'distance between x lines' = how far the ray travels to cross from\n"
         "one vertical grid line to the next (same idea for y). A huge number\n"
         "stands in for 'never' when the ray runs exactly along an axis.",
         ifelse(lt(abs_(V("ray direction x")), 0.00001), [setv("distance between x lines", 100000)],
                [setv("distance between x lines", abs_(div(1, V("ray direction x"))))])),
    ifelse(lt(abs_(V("ray direction y")), 0.00001), [setv("distance between y lines", 100000)],
           [setv("distance between y lines", abs_(div(1, V("ray direction y"))))]),
    note("'ray step x' is -1 if the ray goes left, +1 if it goes right.\n"
         "'distance to next x line' = distance from you to the FIRST vertical\n"
         "grid line the ray crosses. Same for y.",
         ifelse(lt(V("ray direction x"), 0),
                [setv("ray step x", -1),
                 setv("distance to next x line", mul(sub(V("player x"), V("ray square x")), V("distance between x lines")))],
                [setv("ray step x", 1),
                 setv("distance to next x line", mul(sub(add(V("ray square x"), 1), V("player x")), V("distance between x lines")))])),
    ifelse(lt(V("ray direction y"), 0),
           [setv("ray step y", -1),
            setv("distance to next y line", mul(sub(V("player y"), V("ray square y")), V("distance between y lines")))],
           [setv("ray step y", 1),
            setv("distance to next y line", mul(sub(add(V("ray square y"), 1), V("player y")), V("distance between y lines")))]),
    setv("letter hit", 0), setv("ray steps taken", 0),
    note("DDA LOOP: hop square by square, always crossing whichever grid line\n"
         "is closer, until the square we land in isn't floor (0).\n"
         "Barrels (E) are skipped: they are drawn as sprites, not walls.\n"
         f"'hit side' 0 = hit an east/west face, 1 = a north/south face.\n"
         "Stop after 'max ray steps' steps (set per level): very far walls are\n"
         "black anyway, and big levels stay fast.",
         until(or_(and_(not_(eq(V("letter hit"), 0)), not_(eq(V("letter hit"), "E"))),
                   gt(V("ray steps taken"), V("max ray steps"))),
               ifelse(lt(V("distance to next x line"), V("distance to next y line")),
                      [chg("distance to next x line", V("distance between x lines")), chg("ray square x", V("ray step x")),
                       setv("hit side", 0)],
                      [chg("distance to next y line", V("distance between y lines")), chg("ray square y", V("ray step y")),
                       setv("hit side", 1)]),
               setv("letter hit", map_letter_at(V("ray square x"), V("ray square y"))), chg("ray steps taken", 1))),
    note("WALL DISTANCE: undo the last hop to get the distance to the wall.\n"
         "This is measured straight ahead (not along the ray), which stops\n"
         "the 'fish-eye' bulge you'd get otherwise.",
         ifelse(eq(V("hit side"), 0), [setv("wall distance", sub(V("distance to next x line"), V("distance between x lines")))],
                [setv("wall distance", sub(V("distance to next y line"), V("distance between y lines")))])),
    if_(lt(V("wall distance"), 0.05), setv("wall distance", 0.05)),
    note("Save the distance for this column. Monsters and items read it to\nknow if a wall is in front of them.",
         replace("wall distance per column", add(V("ray column"), 1), V("wall distance"))),
    note("STRIPE HEIGHT: a wall twice as far away looks half as tall.",
         setv("wall stripe height", div(360, V("wall distance")))),
    if_(gt(V("wall stripe height"), 720), setv("wall stripe height", 720)),
    note("SPOT ALONG WALL (0 to 1): exactly where on the wall's face the ray hit.\n"
         "Used to draw the dark seams between wall panels, door frames and\n"
         "the switch.",
         ifelse(eq(V("hit side"), 0),
                [setv("spot along wall", add(V("player y"), mul(V("wall distance"), V("ray direction y"))))],
                [setv("spot along wall", add(V("player x"), mul(V("wall distance"), V("ray direction x"))))])),
    setv("spot along wall", sub(V("spot along wall"), floor_(V("spot along wall")))),
    note("WALL COLOR: find the letter in 'wall letters', then use the same item\n"
         "number in 'wall hues', 'wall saturations', 'wall brightnesses'.\n"
         "Farther = darker. North/south faces are darker too, which makes\n"
         "corners easy to see.",
         setv("wall type number", itemnum(V("letter hit"), "wall letters"))),
    setv("wall style", item(V("wall type number"), "wall styles")),
    note("SECRET WALLS (style 4) borrow the colors of the wall digit named in\n"
         "'level secret wall looks' for this level. Their style stays 4, so\n"
         "they get no seams: that's the clue for sharp-eyed players.",
         if_(eq(V("wall style"), 4),
             setv("wall type number", itemnum(item(V("current level"), "level secret wall looks"), "wall letters")))),
    pen_color("#ff0000"),
    pen_param("color", item(V("wall type number"), "wall hues")),
    pen_param("saturation", item(V("wall type number"), "wall saturations")),
    setv("stripe brightness", sub(sub(item(V("wall type number"), "wall brightnesses"),
                                      mul(V("wall distance"), V("light falloff"))), mul(V("hit side"), 12))),
    note("Darker edges: thin seams on plain walls (style 0), a thick frame on\ndoors (style 1) and skull doors (style 5).",
         if_(and_(eq(V("wall style"), 0), or_(lt(V("spot along wall"), 0.05), gt(V("spot along wall"), 0.95))),
             chg("stripe brightness", -18))),
    if_(and_(or_(eq(V("wall style"), 1), eq(V("wall style"), 5)),
             or_(lt(V("spot along wall"), 0.1), gt(V("spot along wall"), 0.9))),
        chg("stripe brightness", -28)),
    pen_param("brightness", V("stripe brightness")),
    note("DRAW the stripe: a vertical pen line centered on the horizon.",
         setv("stripe screen x", add(-240 + STRIPE_WIDTH / 2, mul(V("ray column"), STRIPE_WIDTH)))),
    *line(V("stripe screen x"), div(V("wall stripe height"), 2), V("stripe screen x"), div(V("wall stripe height"), -2)),
    note("DOORS (style 1 and 5): draw a darker band across the middle.",
         if_(and_(or_(eq(V("wall style"), 1), eq(V("wall style"), 5)),
                  and_(not_(lt(V("spot along wall"), 0.1)), not_(gt(V("spot along wall"), 0.9)))),
             pen_param("brightness", sub(V("stripe brightness"), 24)),
             *line(V("stripe screen x"), mul(V("wall stripe height"), 0.07),
                   V("stripe screen x"), mul(V("wall stripe height"), -0.07)))),
    note("EXIT SWITCH (style 2 = off, 3 = on): a dark box with a glowing light\n"
         "inside. Hue = (style - 2) x 33, so red (0) when off, green (33) when on.",
         if_(and_(and_(gt(V("wall style"), 1), lt(V("wall style"), 4)),
                  and_(gt(V("spot along wall"), 0.36), lt(V("spot along wall"), 0.64))),
             pen_param("brightness", sub(V("stripe brightness"), 30)),
             *line(V("stripe screen x"), mul(V("wall stripe height"), 0.13),
                   V("stripe screen x"), mul(V("wall stripe height"), -0.13)),
             if_(and_(gt(V("spot along wall"), 0.4), lt(V("spot along wall"), 0.6)),
                 pen_param("color", mul(sub(V("wall style"), 2), 33)), pen_param("saturation", 95),
                 pen_param("brightness", sub(95, mul(V("wall distance"), 3))),
                 *line(V("stripe screen x"), mul(V("wall stripe height"), 0.09),
                       V("stripe screen x"), mul(V("wall stripe height"), -0.09))))),
    note("SKULL DOOR (style 5): two glowing red eyes above the middle band.",
         if_(and_(eq(V("wall style"), 5),
                  or_(and_(gt(V("spot along wall"), 0.3), lt(V("spot along wall"), 0.42)),
                      and_(gt(V("spot along wall"), 0.58), lt(V("spot along wall"), 0.7)))),
             pen_param("color", 0), pen_param("saturation", 95),
             pen_param("brightness", sub(95, mul(V("wall distance"), 3))),
             *line(V("stripe screen x"), mul(V("wall stripe height"), 0.24),
                   V("stripe screen x"), mul(V("wall stripe height"), 0.16)))),
    chg("ray column", 1),
]

SQUARE = V("minimap square size")
minimap = [
    note("MINIMAP: one dot per wall square in the top-left corner, in the wall's\n"
         "own color. 'minimap square size' shrinks the dots for bigger maps.",
         setv("map row", 0)),
    repeat(V("map height"), setv("map column", 0),
           repeat(V("map width"), setv("minimap letter", map_letter_at(V("map column"), V("map row"))),
                  if_(and_(not_(eq(V("minimap letter"), 0)), not_(eq(V("minimap letter"), "E"))),
                      setv("wall type number", itemnum(V("minimap letter"), "wall letters")),
                      if_(eq(V("minimap letter"), "S"),
                          setv("wall type number",
                               itemnum(item(V("current level"), "level secret wall looks"), "wall letters"))),
                      pen_color("#ff0000"), pen_param("color", item(V("wall type number"), "wall hues")),
                      pen_param("saturation", item(V("wall type number"), "wall saturations")),
                      pen_param("brightness", 78),
                      *dot(add(-236, mul(V("map column"), SQUARE)), sub(176, mul(V("map row"), SQUARE)))),
                  chg("map column", 1)),
           chg("map row", 1)),
    note("You: a green dot with two yellow lines showing your field of view.",
         setv("minimap player x", add(-236, mul(sub(V("player x"), 0.5), SQUARE)))),
    setv("minimap player y", sub(176, mul(sub(V("player y"), 0.5), SQUARE))),
    pen_color("#ffe14d"), pen_size(1),
    *line(V("minimap player x"), V("minimap player y"),
          add(V("minimap player x"), mul(add(V("look direction x"), V("camera plane x")), 14)),
          sub(V("minimap player y"), mul(add(V("look direction y"), V("camera plane y")), 14))),
    *line(V("minimap player x"), V("minimap player y"),
          add(V("minimap player x"), mul(sub(V("look direction x"), V("camera plane x")), 14)),
          sub(V("minimap player y"), mul(sub(V("look direction y"), V("camera plane y")), 14))),
    pen_color("#40ff40"), pen_size(5), *dot(V("minimap player x"), V("minimap player y")),
]

E.script(
    Def("draw 3D view"),
    note("Wipe last frame's drawing.", pen_clear()),
    *ceiling, *floor_bands,
    note(f"WALLS: one ray per screen column, {RAY_COUNT} columns, each stripe\n{STRIPE_WIDTH} pixels wide.",
         setv("ray column", 0)), pen_size(STRIPE_WIDTH + 1),
    repeat(RAY_COUNT, *ray),
    note("SCREEN FLASHES: red when a monster hits you, gold when you pick\nsomething up. One huge see-through dot covers the screen.",
         if_(gt(V("hurt flash timer"), 0),
             pen_color("#ff0000"), pen_param("transparency", 62), pen_size(620), *dot(0, 0),
             chg("hurt flash timer", -1))),
    if_(gt(V("pickup flash timer"), 0),
        pen_color("#ffd23f"), pen_param("transparency", 72), pen_size(620), *dot(0, 0),
        chg("pickup flash timer", -1)),
    if_(eq(V("map is showing"), 1), pen_size(add(SQUARE, 1)), *minimap),
    note("BOSS HEALTH BAR: a dark track, then a red line as long as the boss's\n"
         "health. The Boss Bar sprite draws the frame and name on top.",
         if_(and_(eq(V("boss is awake"), 1), gt(V("boss health"), 0)),
             pen_size(8), pen_color("#300000"), *line(-98, 94, 98, 94),
             pen_color("#e02424"),
             *line(-98, 94, add(-98, mul(196, div(V("boss health"), V("boss max health")))), 94))),
    note("SPRINT BAR (only while playing): a dark track, then the stamina.\n"
         "Green = plenty, yellow = under 30, flashing red/orange = out of\n"
         "breath (the cooldown). The HUD sprite draws the label and outline.",
         if_(eq(V("screen showing"), NONE),
             pen_size(5), pen_color("#151515"), *line(-222, -109, -126, -109),
             ifelse(eq(V("is exhausted"), 1),
                    [ifelse(lt(mod(mul(timer(), 4), 1), 0.5), [pen_color("#ff3020")], [pen_color("#ffa020")])],
                    [ifelse(lt(V("stamina"), 30), [pen_color("#ffd23f")], [pen_color("#40e060")])]),
             if_(gt(V("stamina"), 0.5),
                 *line(-222, -109, add(-222, mul(96, div(V("stamina"), 100))), -109)))),
    comment="DRAW 3D VIEW: the raycaster. Runs WITHOUT screen refresh so the\n"
            "whole picture appears at once.\n"
            "Idea: for each column of the screen, shoot a ray from the player\n"
            "across the map grid until it hits a wall. A closer wall = a taller,\n"
            "brighter stripe. Same technique as Wolfenstein 3D (1992).")

# ------------------------------------ shared by monsters + items ------------------------------------
def offset_from_player(x_var, y_var):
    return [setv("offset x from player", sub(V(x_var), V("player x"))),
            setv("offset y from player", sub(V(y_var), V("player y"))),
            setv("distance to player", sqrt_(add(mul(V("offset x from player"), V("offset x from player")),
                                                 mul(V("offset y from player"), V("offset y from player")))))]

def place_on_screen(when_visible, what, size=None, height=-180):
    """size = sprite size at depth 1 (default 225%); height = screen y at depth 1 (-180 = the floor)."""
    size = size if size is not None else 225
    return [
        note(f"PLACE ON SCREEN: turn the {what}'s map position into camera\n"
             "coordinates. 'sideways in view' = how far left/right of the\n"
             "crosshair, 'depth in view' = how far in front of you.",
             setv("sideways in view", mul(V("projection factor"),
                                           sub(mul(V("look direction y"), V("offset x from player")),
                                               mul(V("look direction x"), V("offset y from player")))))),
        setv("depth in view", mul(V("projection factor"),
                                  add(mul(sub(0, V("camera plane y")), V("offset x from player")),
                                      mul(V("camera plane x"), V("offset y from player"))))),
        note("Behind you (or right on top of you)? Then hide.",
             ifelse(gt(V("depth in view"), 0.4),
                    [note("Perspective: divide sideways by depth to get the screen x, then\n"
                          "find which wall column that x is in.",
                          setv("screen x", mul(240, div(V("sideways in view"), V("depth in view"))))),
                     setv("screen column index", floor_(div(add(V("screen x"), 240), STRIPE_WIDTH))),
                     note("Hide if off the screen, or if the wall in that column is closer\n"
                          "than we are (we're behind a wall).",
                          ifelse(or_(or_(lt(V("screen column index"), 0), gt(V("screen column index"), RAY_COUNT - 1)),
                                     lt(item(add(V("screen column index"), 1), "wall distance per column"),
                                        V("depth in view"))),
                                 [hide()],
                                 [note("Visible: farther = smaller and closer to the horizon. Layers:\n"
                                       "go to front, then back by 2 x depth, so near things cover far ones.",
                                       setsize(div(size, V("depth in view")))),
                                  gotoxy(V("screen x"), div(height, V("depth in view"))), show(),
                                  front(), backward(round_(mul(V("depth in view"), 2))), *when_visible]))],
                    [hide()]))]

def explosion_scan(x_var, y_var, *for_each_close_blast):
    """Loop over this frame's explosions; for each one, measure 'distance to blast' and run the blocks."""
    return [setv("explosion number", 1),
            repeat(length("explosion x"),
                   setv("distance to blast", sqrt_(add(
                       mul(sub(item(V("explosion number"), "explosion x"), V(x_var)),
                           sub(item(V("explosion number"), "explosion x"), V(x_var))),
                       mul(sub(item(V("explosion number"), "explosion y"), V(y_var)),
                           sub(item(V("explosion number"), "explosion y"), V(y_var)))))),
                   *for_each_close_blast, chg("explosion number", 1))]

# ============================================================================================
#                                              MONSTER
# ============================================================================================
M = Target(P, "Monster", layer=2, visible=False)
MONSTER_ART = {
    "imp": (assets.IMP_WALK1, assets.IMP_WALK2, assets.IMP_ATTACK, assets.IMP_DEAD),
    "spitter": (assets3.SPITTER_WALK1, assets3.SPITTER_WALK2, assets3.SPITTER_ATTACK, assets3.SPITTER_DEAD),
    "golem": (assets3.GOLEM_WALK1, assets3.GOLEM_WALK2, assets3.GOLEM_ATTACK, assets3.GOLEM_DEAD),
    "warden": (assets3.WARDEN_WALK1, assets3.WARDEN_WALK2, assets3.WARDEN_ATTACK, assets3.WARDEN_DEAD),
    "charger": (assets6.CHARGER_WALK1, assets6.CHARGER_WALK2, assets6.CHARGER_ATTACK, assets6.CHARGER_DEAD),
    "wraith": (assets6.WRAITH_WALK1, assets6.WRAITH_WALK2, assets6.WRAITH_ATTACK, assets6.WRAITH_DEAD),
    "colossus": (assets6.COLOSSUS_WALK1, assets6.COLOSSUS_WALK2, assets6.COLOSSUS_ATTACK, assets6.COLOSSUS_DEAD),
}
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        M.costume(f"{monster_name} {pose}", svg_art, 40, 120)
for nm, fn in (("pain", assets.monster_pain), ("death", assets.monster_death), ("player hurt", assets.player_hurt),
               ("spit", assets3.spit), ("fireball", assets3.fireball), ("slam", assets4.thud),
               ("blink", assets6.wraith_blink)):
    data, n = fn(); M.sound(nm, data, assets.RATE, n)
for name in ["monster id", "is clone", "monster type", "monster name", "monster x", "monster y", "is alive",
             "monster health", "attack cooldown", "volley cooldown", "pain flash timer", "attack pose timer",
             "is chasing", "moved this frame", "damage taken", "explosion number", "distance to blast",
             "offset x from player", "offset y from player", "distance to player", "next monster x",
             "next monster y", "sight is clear", "sight x", "sight y", "aim x", "aim y", "volley shot number",
             "spread angle", "sideways in view", "depth in view", "screen x", "screen column index",
             # special moves
             "speed multiplier", "charge state", "charge timer", "charge cooldown", "charge direction x",
             "charge direction y", "blink timer", "blink side", "has called for help", "helper x", "helper y"]:
    M.var(name)

def stat(column):
    """item (monster type) of the 'monster <column>' list — this monster's number for that stat."""
    return item(V("monster type"), f"monster {column}")

def step_monster(direction):
    """direction -1 = toward the player, +1 = away. X and Y are tried separately so it slides on walls."""
    return [
        setv("next monster x", add(V("monster x"), mul(div(V("offset x from player"), V("distance to player")),
                                                       mul(mul(stat("speed"), V("speed multiplier")), direction)))),
        if_(eq(map_letter_at(floor_(V("next monster x")), floor_(V("monster y"))), 0),
            setv("monster x", V("next monster x"))),
        setv("next monster y", add(V("monster y"), mul(div(V("offset y from player"), V("distance to player")),
                                                       mul(mul(stat("speed"), V("speed multiplier")), direction)))),
        if_(eq(map_letter_at(floor_(V("monster x")), floor_(V("next monster y"))), 0),
            setv("monster y", V("next monster y"))),
        setv("moved this frame", 1)]

M.script(flag(), hide(), setv("is clone", 0),
         comment="The original Monster sprite never appears. It only makes clones.")
M.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()),
         comment="CLEAR LEVEL: every monster clone deletes itself.")
def add_monster_clone():
    return [chg("monster id", 1),
            addto("monster x positions", add(item(V("monster id"), "monster start x"), 0.5)),
            addto("monster y positions", add(item(V("monster id"), "monster start y"), 0.5)),
            addto("monster alive flags", 1), clone()]
M.script(recv(SPAWN),
         if_(eq(V("is clone"), 0), setv("monster id", 0),
             clear_list("monster x positions"), clear_list("monster y positions"), clear_list("monster alive flags"),
             repeat(length("monster start x"), *add_monster_clone())),
         comment="SPAWN: the original makes one clone per monster letter on the map.\n"
                 "Each clone copies 'monster id' at the moment it is made, so the\n"
                 "clones are numbered 1, 2, 3 ... It also adds a line for each one to\n"
                 "'monster x/y positions' and 'monster alive flags'.")
M.script(recv(SUMMON),
         if_(eq(V("is clone"), 0),
             repeat(sub(length("monster start x"), V("monster id")), *add_monster_clone())),
         comment="SUMMON: a boss added monsters to the end of the start lists.\n"
                 "'monster id' still holds the last id handed out, so make clones\n"
                 "for the new entries only.")
M.script(as_clone(), setv("is clone", 1),
         note("Look up my start square and my TYPE (1 imp, 2 spitter, 3 golem,\n"
              "4 warden). Everything else about me comes from the 'monster ...'\n"
              "lists, using my type as the item number.",
              setv("monster x", add(item(V("monster id"), "monster start x"), 0.5))),
         setv("monster y", add(item(V("monster id"), "monster start y"), 0.5)),
         setv("monster type", item(V("monster id"), "monster start type")),
         setv("monster name", stat("names")), setv("monster health", stat("health")),
         setv("is alive", 1), setv("attack cooldown", 0), setv("volley cooldown", 30), setv("pain flash timer", 0),
         setv("attack pose timer", 0), setv("is chasing", 0),
         setv("speed multiplier", 1), setv("charge state", 0), setv("charge cooldown", 30), setv("blink timer", 60),
         setv("has called for help", 0),
         note("Bigger monsters get deeper voices: the same sounds, pitched down.",
              set_sound_effect("PITCH", stat("voice pitch"))),
         costume("imp walk 1", join(V("monster name"), " walk 1")), cleareffects(), hide(),
         comment="NEW CLONE: set myself up from the monster type lists.")

M.script(Def("check line of sight"),
         setv("sight is clear", 1), setv("sight x", V("monster x")), setv("sight y", V("monster y")),
         note("Walk an invisible point from me to the player in small steps.\n"
              "If any step lands in something that isn't floor, I can't see you.",
              repeat(floor_(div(V("distance to player"), 0.3)),
                     setv("sight x", sub(V("sight x"), mul(div(V("offset x from player"), V("distance to player")), 0.3))),
                     setv("sight y", sub(V("sight y"), mul(div(V("offset y from player"), V("distance to player")), 0.3))),
                     if_(not_(eq(map_letter_at(floor_(V("sight x")), floor_(V("sight y"))), 0)),
                         setv("sight is clear", 0)))),
         comment="CHECK LINE OF SIGHT: can I see the player? Ranged monsters only\n"
                 "shoot when the answer is yes, so you can hide behind walls.")

M.script(Def("fire volley"),
         note("Aim = a 1-square arrow from me toward the player.",
              setv("aim x", div(mul(-1, V("offset x from player")), V("distance to player")))),
         setv("aim y", div(mul(-1, V("offset y from player")), V("distance to player"))),
         setv("volley shot number", 1),
         repeat(stat("shots per volley"),
                note("Fan the shots out 12 degrees apart: a volley of 3 aims at -12, 0\n"
                     "and +12 degrees. Rotating the aim arrow uses sin and cos.",
                     setv("spread angle", mul(sub(V("volley shot number"), div(add(stat("shots per volley"), 1), 2)), 12))),
                note("Monsters can't make clones of the Projectile sprite directly, so\n"
                     "they add the shot to the 'new shot ...' lists. The Projectile\n"
                     "sprite launches everything in those lists.",
                     addto("new shot x", add(V("monster x"), mul(V("aim x"), 0.6)))),
                addto("new shot y", add(V("monster y"), mul(V("aim y"), 0.6))),
                addto("new shot speed x", mul(sub(mul(V("aim x"), cos_(V("spread angle"))),
                                                  mul(V("aim y"), sin_(V("spread angle")))), stat("shot speed"))),
                addto("new shot speed y", mul(add(mul(V("aim x"), sin_(V("spread angle"))),
                                                  mul(V("aim y"), cos_(V("spread angle")))), stat("shot speed"))),
                addto("new shot damage", rnd(div(stat("shot damage"), 2), stat("shot damage"))),
                addto("new shot look", stat("shot look")), addto("new shot owner", V("monster type")),
                chg("volley shot number", 1)),
         comment="FIRE VOLLEY: launch 'monster shots per volley' projectiles at you.")

M.script(Def("add up explosion damage"),
         *explosion_scan("monster x", "monster y",
                         if_(lt(V("distance to blast"), 2.6),
                             ifelse(lt(V("distance to blast"), 1.3), [chg("damage taken", 6)], [chg("damage taken", 3)]))),
         comment="ADD UP EXPLOSION DAMAGE: check every explosion this frame.\n"
                 "IMPORTANT: loops live in 'run without screen refresh' custom blocks.\n"
                 "A loop in a broadcast script pauses until the next frame, and the\n"
                 "next frame's broadcast would RESTART the script before it finishes.")

M.script(Def("charge at the player"),
    note("CHARGER. 'charge state': 0 = walking, 1 = winding up (head down, a\n"
         "warning!), 2 = charging in a straight line, 3 = stunned after\n"
         "slamming into a wall.",
         if_(gt(V("charge cooldown"), 0), chg("charge cooldown", -1))),
    if_(eq(V("charge state"), 0),
        if_(and_(eq(V("is chasing"), 1), gt(V("distance to player"), stat("keep distance"))), *step_monster(-1)),
        note("Start a charge if you're 2.5 to 9 squares away and in plain sight.",
             if_(and_(and_(eq(V("is chasing"), 1), lt(V("charge cooldown"), 1)),
                      and_(gt(V("distance to player"), 2.5), lt(V("distance to player"), 9))),
                 call("check line of sight"),
                 if_(eq(V("sight is clear"), 1),
                     setv("charge state", 1), setv("charge timer", 15), setv("attack pose timer", 15), play("pain"))))),
    ifelse(eq(V("charge state"), 1),
           [chg("charge timer", -1),
            note("Wind-up over: lock the direction toward where you are NOW. If you\n"
                 "move, it misses.",
                 if_(lt(V("charge timer"), 1),
                     setv("charge state", 2), setv("charge timer", 40),
                     setv("charge direction x", div(mul(-1, V("offset x from player")), V("distance to player"))),
                     setv("charge direction y", div(mul(-1, V("offset y from player")), V("distance to player")))))],
           [ifelse(eq(V("charge state"), 2),
                   [note("CHARGING: 0.17 squares a frame (about 7 times walking speed).\n"
                         "Hit a wall -> stunned. Reach you -> a big hit, and the charge ends.",
                         setv("next monster x", add(V("monster x"), mul(V("charge direction x"), 0.17)))),
                    setv("next monster y", add(V("monster y"), mul(V("charge direction y"), 0.17))),
                    ifelse(eq(map_letter_at(floor_(V("next monster x")), floor_(V("next monster y"))), 0),
                           [setv("monster x", V("next monster x")), setv("monster y", V("next monster y")),
                            setv("moved this frame", 1)],
                           [setv("charge state", 3), setv("charge timer", 45), play("slam")]),
                    setv("offset x from player", sub(V("monster x"), V("player x"))),
                    *offset_from_player("monster x", "monster y")[1:],
                    if_(and_(eq(V("charge state"), 2), lt(V("distance to player"), 1)),
                        chg("health", mul(-1, rnd(div(stat("claw damage"), 2), stat("claw damage")))),
                        setv("killer type", V("monster type")), setv("hurt flash timer", 6),
                        play("player hurt"), setv("charge state", 0), setv("charge cooldown", 60),
                        setv("attack pose timer", 10)),
                    chg("charge timer", -1),
                    if_(and_(eq(V("charge state"), 2), lt(V("charge timer"), 1)),
                        setv("charge state", 0), setv("charge cooldown", 50))],
                   [if_(eq(V("charge state"), 3), chg("charge timer", -1),
                        if_(lt(V("charge timer"), 1), setv("charge state", 0), setv("charge cooldown", 30)))])]),
    comment="CHARGE AT THE PLAYER: the charger's special move ('monster special\nmove' = charge).")

M.script(Def("blink sideways"),
    if_(gt(V("blink timer"), 0), chg("blink timer", -1)),
    note("Every 2-4 seconds, jump 1.6 squares to the left or right of the line\n"
         "between us. Turning an arrow 90 degrees just swaps x and y and flips\n"
         "one sign: (x, y) -> (y, -x).",
         if_(and_(and_(eq(V("is chasing"), 1), lt(V("blink timer"), 1)), gt(V("distance to player"), 2.5)),
             ifelse(eq(rnd(1, 2), 1), [setv("blink side", 1)], [setv("blink side", -1)]),
             setv("next monster x", add(V("monster x"), mul(div(V("offset y from player"), V("distance to player")),
                                                            mul(1.6, V("blink side"))))),
             setv("next monster y", sub(V("monster y"), mul(div(V("offset x from player"), V("distance to player")),
                                                            mul(1.6, V("blink side"))))),
             if_(eq(map_letter_at(floor_(V("next monster x")), floor_(V("next monster y"))), 0),
                 setv("monster x", V("next monster x")), setv("monster y", V("next monster y")), play("blink")),
             setv("blink timer", rnd(60, 120)))),
    comment="BLINK SIDEWAYS: the wraith's special move ('monster special move' = blink).")

M.script(Def("call for help"),
    note("RAGE at half health (once): faster, shoots more often, and calls in\n"
         "two chargers, one on each side of me (or on my square if that side\n"
         "is a wall).",
         setv("has called for help", 1)), setv("speed multiplier", 1.6),
    setv("message name", join("boss enraged ", V("monster name"))), setv("message timer", 70), play("pain"),
    *[blk for side in (-1.5, 1.5) for blk in (
        setv("helper x", floor_(add(V("monster x"), side))), setv("helper y", floor_(V("monster y"))),
        if_(not_(eq(map_letter_at(V("helper x"), V("helper y")), 0)),
            setv("helper x", floor_(V("monster x")))),
        addto("monster start x", V("helper x")), addto("monster start y", V("helper y")),
        addto("monster start type", CHARGER_TYPE))],
    chg("level monster count", 2), bcast(SUMMON),
    comment="CALL FOR HELP: the colossus's special move ('monster special move'\n= rage).")

M.script(recv(UPDATE), if_(eq(V("is clone"), 1),
    note("DAMAGE: add up everything that hurts me this frame. A weapon hit does\n"
         "'hit damage' (rolled when you fired). An explosion does 6 up close,\n"
         "3 farther out.",
         setv("damage taken", 0)),
    if_(and_(eq(V("target hit id"), V("monster id")), eq(V("is alive"), 1)), chg("damage taken", V("hit damage"))),
    call("add up explosion damage"),
    note("Take the damage. At 0 health I die and count as a kill. If I was the\n"
         "boss, the boss health bar goes away.",
         if_(and_(gt(V("damage taken"), 0), eq(V("is alive"), 1)),
             chg("monster health", mul(-1, V("damage taken"))), setv("pain flash timer", 4), setv("is chasing", 1),
             ifelse(lt(V("monster health"), 1),
                    [setv("is alive", 0), costume("imp dead", join(V("monster name"), " dead")), cleareffects(),
                     chg("total kills", 1), chg("level kills", 1), play("death"),
                     note("A dead BOSS drops the skull key where it fell.",
                          if_(eq(stat("is boss"), 1), setv("boss health", 0), setv("boss is awake", 0),
                              setv("boss is dead", 1), setv("boss death x", V("monster x")),
                              setv("boss death y", V("monster y"))))],
                    [play("pain")]))),
    note("Where is the player compared to me?",
         setv("offset x from player", sub(V("monster x"), V("player x")))),
    *offset_from_player("monster x", "monster y")[1:],
    note("THINK (only while alive and the game is being played).",
         if_(and_(eq(V("is alive"), 1), eq(V("game state"), PLAYING)),
             note("WAKE UP if the player comes within my 'wake distance', or fires a\nshot within 11 squares.",
                  if_(lt(V("distance to player"), stat("wake distance")), setv("is chasing", 1))),
             if_(and_(eq(V("shot fired this frame"), 1), lt(V("distance to player"), 11)), setv("is chasing", 1)),
             note("MOVE: come closer until I'm at my 'keep distance'. Spitters keep\n"
                  "about 4 squares away, and back off if you rush them. Chargers use\n"
                  "their own 'charge at the player' block instead.",
                  setv("moved this frame", 0)),
             ifelse(eq(stat("special move"), "charge"), [call("charge at the player")],
                    [if_(eq(V("is chasing"), 1),
                         if_(gt(V("distance to player"), stat("keep distance")), *step_monster(-1)),
                         if_(lt(V("distance to player"), sub(stat("keep distance"), 1.5)), *step_monster(1)))]),
             note("SPECIAL MOVES for wraiths (blink) and the colossus (rage).",
                  if_(eq(stat("special move"), "blink"), call("blink sideways"))),
             if_(and_(eq(stat("special move"), "rage"),
                      and_(eq(V("has called for help"), 0), lt(V("monster health"), div(stat("health"), 2)))),
                 call("call for help")),
             note("CLAW: when you're within 1.2 squares, hit you once a second\n"
                  "(30 frames) for half to all of my 'claw damage'.",
                  if_(gt(V("attack cooldown"), 0), chg("attack cooldown", -1))),
             if_(and_(and_(lt(V("distance to player"), 1.2), lt(V("attack cooldown"), 1)), eq(V("charge state"), 0)),
                 chg("health", mul(-1, rnd(div(stat("claw damage"), 2), stat("claw damage")))),
                 setv("killer type", V("monster type")),
                 setv("hurt flash timer", 5), setv("attack cooldown", 30), setv("attack pose timer", 12),
                 play("player hurt")),
             note("SHOOT: ranged monsters fire a volley when the delay has run out,\n"
                  "you're in range, and they can SEE you (no wall in between).",
                  if_(gt(V("volley cooldown"), 0), chg("volley cooldown", -1))),
             if_(and_(and_(gt(stat("shots per volley"), 0), eq(V("is chasing"), 1)),
                      and_(lt(V("volley cooldown"), 1), and_(lt(V("distance to player"), 14),
                                                              gt(V("distance to player"), 1.4)))),
                 call("check line of sight"),
                 if_(eq(V("sight is clear"), 1),
                     call("fire volley"), setv("volley cooldown", div(stat("shot delay"), V("speed multiplier"))),
                     setv("attack pose timer", 12),
                     ifelse(eq(stat("shot look"), "acid"), [play("spit")], [play("fireball")]))),
             note("COSTUME: attack pose right after an attack, otherwise swap the two\n"
                  "walking costumes 4 times a second while moving.",
                  ifelse(gt(V("attack pose timer"), 0),
                         [costume("imp attack", join(V("monster name"), " attack")), chg("attack pose timer", -1)],
                         [ifelse(eq(V("moved this frame"), 1),
                                 [costume("imp walk 1", joins(V("monster name"), " walk ",
                                                               add(mod(floor_(mul(timer(), 4)), 2), 1)))],
                                 [costume("imp walk 1", join(V("monster name"), " walk 1"))])])),
             note("EFFECTS: a bright flash for a few frames after being hurt. Otherwise\n"
                  "darker the farther away I am ('sprite darkness', set per level).\n"
                  "Wraiths also fade (ghost effect) with distance, and a stunned\n"
                  "charger flickers colors.",
                  cleareffects()),
             ifelse(gt(V("pain flash timer"), 0), [seteffect("BRIGHTNESS", 60), chg("pain flash timer", -1)],
                    [seteffect("BRIGHTNESS", mul(-1, mul(V("distance to player"), V("sprite darkness"))))]),
             if_(eq(stat("special move"), "blink"),
                 seteffect("GHOST", mul(sub(V("distance to player"), 1.5), 16)),
                 if_(gt(V("distance to player"), 6.5), seteffect("GHOST", 80)),
                 if_(lt(V("distance to player"), 1.5), seteffect("GHOST", 0))),
             if_(eq(V("charge state"), 3), seteffect("COLOR", mul(V("charge timer"), 8))),
             note("BOSS: share my health and name with the boss health bar, and\n"
                  "announce myself the first time I wake up.",
                  if_(eq(stat("is boss"), 1),
                      setv("boss health", V("monster health")), setv("boss max health", stat("health")),
                      setv("boss name", V("monster name")),
                      if_(and_(eq(V("is chasing"), 1), eq(V("boss is awake"), 0)),
                          setv("boss is awake", 1), setv("message name", join("boss awake ", V("monster name"))),
                          setv("message timer", 70)))),
             note("I may have moved, so measure the distance to the player again.",
                  setv("offset x from player", sub(V("monster x"), V("player x")))),
             *offset_from_player("monster x", "monster y")[1:])),
    note("Tell everyone where I am and whether I'm alive (rockets use this).",
         replace("monster x positions", V("monster id"), V("monster x"))),
    replace("monster y positions", V("monster id"), V("monster y")),
    replace("monster alive flags", V("monster id"), V("is alive")),
    note("MINIMAP: draw a red dot for me if the map is showing.",
         if_(and_(eq(V("map is showing"), 1), eq(V("is alive"), 1)),
             pen_color("#ff2020"), pen_size(add(SQUARE, 1)),
             *dot(add(-236, mul(sub(V("monster x"), 0.5), SQUARE)), sub(176, mul(sub(V("monster y"), 0.5), SQUARE))))),
    *place_on_screen([
        note("AM I THE TARGET? If a shot was fired, I'm alive, I'm under the\n"
             "crosshair (bigger monsters are easier to hit), nothing closer was\n"
             "hit already, no wall is in the way, and I'm within 'shot range',\n"
             "then I become the 'shot target id'.",
             if_(and_(and_(eq(V("shot fired this frame"), 1), eq(V("is alive"), 1)),
                      and_(and_(lt(abs_(V("screen x")), div(mul(mul(55, div(stat("size"), 100)), V("aim width")),
                                                            V("depth in view"))),
                                lt(V("depth in view"), V("closest target depth"))),
                           and_(gt(item(CENTER_COLUMN, "wall distance per column"), V("depth in view")),
                                lt(V("depth in view"), V("shot range"))))),
                 setv("closest target depth", V("depth in view")), setv("shot target id", V("monster id"))))],
        "monster", size=mul(225, div(stat("size"), 100)))),
    comment="UPDATE (every frame, for every monster clone):\n"
            "1) take damage  2) wake up, move (or use my special move), claw and\n"
            "shoot  3) minimap dot\n"
            "4) work out where I appear on screen and if I'm the shot target.")

# ============================================================================================
#                                          PICKUPS (items + keys)
# ============================================================================================
I = Target(P, "Pickup", layer=2, visible=False)
for nm, art in (("item 1", assets2.MEDKIT), ("item 2", assets2.SHELLS), ("item 3", assets2.RED_KEY),
                ("item 4", assets2.BLUE_KEY), ("item 6", assets6.BULLETS), ("item 7", assets6.ROCKETS)):
    I.costume(nm, art, 20, 40)
I.costume("item 5", assets6.SKULL_KEY, 20, 44)
for nm, art in (("item 8", assets6.SHOTGUN_PICKUP), ("item 9", assets6.CHAINGUN_PICKUP), ("item 10", assets6.LAUNCHER_PICKUP)):
    I.costume(nm, art, 32, 34)
for nm, fn in (("item", assets2.item), ("key", assets2.key), ("weapon", assets6.weapon_pickup)):
    d, n = fn(); I.sound(nm, d, assets.RATE, n)
for name in ["item id", "is clone", "item x", "item y", "item type", "is taken", "was picked up", "has dropped",
             "offset x from player", "offset y from player", "distance to player", "sideways in view",
             "depth in view", "screen x", "screen column index"]:
    I.var(name)
I.script(flag(), hide(), setv("is clone", 0),
         comment="The original Pickup sprite never appears. It only makes clones.\n"
                 "Item types: 1 health pack, 2 shells, 3 red key, 4 blue key,\n"
                 "5 skull key (dropped by a boss), 6 bullets, 7 rockets,\n"
                 "8 shotgun, 9 chaingun, 10 rocket launcher.")
I.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()),
         comment="CLEAR LEVEL: every item clone deletes itself.")
I.script(recv(SPAWN),
         if_(eq(V("is clone"), 0), setv("item id", 0), repeat(length("item start x"), chg("item id", 1), clone())),
         comment="SPAWN: one clone per item letter on the map (and one skull key per boss).")
I.script(as_clone(), setv("is clone", 1),
         setv("item x", add(item(V("item id"), "item start x"), 0.5)),
         setv("item y", add(item(V("item id"), "item start y"), 0.5)),
         setv("item type", item(V("item id"), "item start type")), setv("is taken", 0), setv("has dropped", 0),
         costume("item 1", join("item ", V("item type"))), hide(),
         comment="NEW CLONE: find my square and type, and wear the costume\n'item 1' to 'item 10' that matches my type.")

def add_ammo(slot, amount):
    """Add ammo, but never more than 'ammo limits' allows."""
    return [replace("ammo counts", slot, add(item(slot, "ammo counts"), amount)),
            if_(gt(item(slot, "ammo counts"), item(slot, "ammo limits")),
                replace("ammo counts", slot, item(slot, "ammo limits")))]

def weapon_pickup(type_number, slot, ammo_slot, amount):
    return if_(eq(V("item type"), type_number),
               if_(eq(item(slot, "weapons owned"), 0), setv("current weapon", slot), setv("weapon switch timer", 8)),
               replace("weapons owned", slot, 1), *add_ammo(ammo_slot, amount), setv("was picked up", 1))

I.script(recv(UPDATE), if_(and_(eq(V("is clone"), 1), eq(V("is taken"), 0)),
    ifelse(and_(eq(V("item type"), 5), eq(V("boss is dead"), 0)),
           [note("SKULL KEY: stays hidden (and can't be picked up) until the boss dies.",
                 hide())],
           [note("The moment the boss dies, jump to where it fell.",
                 if_(and_(eq(V("item type"), 5), eq(V("has dropped"), 0)),
                     setv("item x", V("boss death x")), setv("item y", V("boss death y")), setv("has dropped", 1))),
            *offset_from_player("item x", "item y"),
            note("PICK UP when the player is within 0.6 squares.\n"
                 "Health only counts if you're hurt (like in Doom), so it isn't wasted.\n"
                 "Ammo goes into 'ammo counts' (never above 'ammo limits').\n"
                 "A NEW weapon is switched to straight away; one you already own\n"
                 "just gives you its ammo.",
                 if_(and_(eq(V("game state"), PLAYING), lt(V("distance to player"), 0.6)),
                     setv("was picked up", 0),
                     if_(and_(eq(V("item type"), 1), lt(V("health"), 100)),
                         chg("health", 25), if_(gt(V("health"), 100), setv("health", 100)), setv("was picked up", 1)),
                     if_(eq(V("item type"), 2), *add_ammo(2, 8), setv("was picked up", 1)),
                     if_(eq(V("item type"), 3), setv("has red key", 1), setv("was picked up", 1)),
                     if_(eq(V("item type"), 4), setv("has blue key", 1), setv("was picked up", 1)),
                     if_(eq(V("item type"), 5), setv("has skull key", 1), setv("was picked up", 1)),
                     if_(eq(V("item type"), 6), *add_ammo(1, 20), setv("was picked up", 1)),
                     if_(eq(V("item type"), 7), *add_ammo(3, 4), setv("was picked up", 1)),
                     weapon_pickup(8, 3, 2, 8), weapon_pickup(9, 4, 1, 40), weapon_pickup(10, 5, 3, 4),
                     note("Picked up: count it, flash gold, show 'picked up N' and play a sound.",
                          if_(eq(V("was picked up"), 1),
                              setv("is taken", 1), chg("level items collected", 1), setv("pickup flash timer", 4),
                              setv("message name", join("picked up ", V("item type"))), setv("message timer", 45),
                              ifelse(gt(V("item type"), 7), [play("weapon")],
                                     [ifelse(and_(gt(V("item type"), 2), lt(V("item type"), 6)), [play("key")],
                                             [play("item")])]),
                              hide())))),
            if_(eq(V("is taken"), 0),
                *place_on_screen([note("Darker when far away on dark levels.",
                                       seteffect("BRIGHTNESS", mul(-1, mul(V("distance to player"), V("sprite darkness")))))],
                                 "item"))])),
    comment="UPDATE (every frame, for every item clone that hasn't been taken):\n"
            "check if the player walked over me, then place myself on screen\n"
            "the same way monsters do.")

# ============================================================================================
#                                     BARRELS (explode when shot)
# ============================================================================================
BR = Target(P, "Barrel", layer=2, visible=False)
BR.costume("barrel", assets3.BARREL, 20, 52)
for i, art in enumerate(assets3.EXPLOSIONS):
    BR.costume(f"explosion {i + 1}", art, 45, 78)
d, n = assets3.explosion(); BR.sound("explosion", d, assets.RATE, n)
for name in ["barrel id", "is clone", "barrel x", "barrel y", "barrel state", "fuse timer", "blast frame",
             "blast damage", "explosion number", "distance to blast", "offset x from player", "offset y from player",
             "distance to player", "sideways in view", "depth in view", "screen x", "screen column index"]:
    BR.var(name)
BR.script(flag(), hide(), setv("is clone", 0),
          comment="Barrels. 'barrel state': 0 = sitting there, 1 = about to blow\n"
                  "(fuse lit), 2 = exploding, 3 = gone.")
BR.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()))
BR.script(recv(SPAWN),
          if_(eq(V("is clone"), 0), setv("barrel id", 0), repeat(length("barrel start x"), chg("barrel id", 1), clone())),
          comment="SPAWN: one clone per E on the map.")
BR.script(as_clone(), setv("is clone", 1),
          setv("barrel x", add(item(V("barrel id"), "barrel start x"), 0.5)),
          setv("barrel y", add(item(V("barrel id"), "barrel start y"), 0.5)),
          setv("barrel state", 0), costume("barrel"), hide())
BR.script(Def("check nearby explosions"),
          *explosion_scan("barrel x", "barrel y",
                          if_(and_(eq(V("barrel state"), 0), lt(V("distance to blast"), 2.2)),
                              setv("barrel state", 1), setv("fuse timer", 5))),
          comment="CHECK NEARBY EXPLOSIONS: any blast within 2.2 squares lights my fuse.\n"
                  "(A loop, so it lives in a 'run without screen refresh' block.)")

BR.script(recv(UPDATE), if_(and_(eq(V("is clone"), 1), lt(V("barrel state"), 3)),
    note("SITTING THERE: a shotgun hit lights the fuse at once. A nearby\n"
         "explosion lights a short fuse, which makes chain reactions ripple\n"
         "outward instead of all going off in the same frame.",
         if_(eq(V("barrel state"), 0),
             if_(eq(V("target hit id"), add(1000, V("barrel id"))), setv("barrel state", 1), setv("fuse timer", 1)),
             call("check nearby explosions"))),
    note("FUSE: count down, then BOOM. Tell everyone where the blast is (the\n"
         "Engine shares it next frame), ask for my square to become floor,\n"
         "and hurt the player if close: up to 40 damage at the center.",
         if_(eq(V("barrel state"), 1), chg("fuse timer", -1),
             if_(lt(V("fuse timer"), 1),
                 addto("new explosion x", V("barrel x")), addto("new explosion y", V("barrel y")),
                 addto("squares to clear x", floor_(V("barrel x"))), addto("squares to clear y", floor_(V("barrel y"))),
                 *offset_from_player("barrel x", "barrel y"),
                 if_(lt(V("distance to player"), 2.6),
                     setv("blast damage", round_(mul(40, sub(1, div(V("distance to player"), 2.6))))),
                     chg("health", mul(-1, V("blast damage"))), setv("hurt flash timer", 6),
                     setv("killer type", 0)),
                 play("explosion"), setv("barrel state", 2), setv("blast frame", 0)))),
    note("EXPLODING: show the 3 explosion costumes, 4 frames each, then vanish.",
         if_(eq(V("barrel state"), 2), chg("blast frame", 1),
             costume("explosion 1", join("explosion ", add(floor_(div(V("blast frame"), 4)), 1))),
             if_(gt(V("blast frame"), 11), setv("barrel state", 3), hide()))),
    if_(lt(V("barrel state"), 3),
        *offset_from_player("barrel x", "barrel y"),
        *place_on_screen([
            note("Can be shot like a monster. Barrel ids start at 1001 so the game\n"
                 "can tell barrels and monsters apart.",
                 if_(and_(and_(eq(V("shot fired this frame"), 1), eq(V("barrel state"), 0)),
                          and_(and_(lt(abs_(V("screen x")), div(30, V("depth in view"))),
                                    lt(V("depth in view"), V("closest target depth"))),
                               and_(gt(item(CENTER_COLUMN, "wall distance per column"), V("depth in view")),
                                    lt(V("depth in view"), V("shot range"))))),
                     setv("closest target depth", V("depth in view")),
                     setv("shot target id", add(1000, V("barrel id")))))], "barrel"))),
    comment="UPDATE (every frame, for every barrel clone).")

# ============================================================================================
#                                 PROJECTILES (acid and fireballs)
# ============================================================================================
PR = Target(P, "Projectile", layer=2, visible=False)
PR.costume("shot acid", assets3.ACID_SHOT, 13, 13)
PR.costume("shot fire", assets3.FIRE_SHOT, 15, 15)
PR.costume("shot plasma", assets6.PLASMA_SHOT, 15, 15)
PR.costume("shot rocket", assets6.ROCKET_SHOT, 13, 13)
for i_, art in enumerate(assets3.EXPLOSIONS):
    PR.costume(f"explosion {i_ + 1}", art, 45, 78)
d, n = assets.player_hurt(); PR.sound("player hurt", d, assets.RATE, n)
d, n = assets3.explosion(); PR.sound("explosion", d, assets.RATE, n)
for name in ["is clone", "queue position", "shot x", "shot y", "shot speed x", "shot speed y", "shot damage",
             "shot look", "shot owner", "frames left", "offset x from player", "offset y from player", "distance to player",
             "sideways in view", "depth in view", "screen x", "screen column index",
             "is exploding", "blast frame", "blast damage", "draw height", "previous x", "previous y",
             "monster number", "distance to monster", "rocket hit something"]:
    PR.var(name)
PR.script(flag(), hide(), setv("is clone", 0))
PR.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()))
PR.script(Def("launch new shots"),
note("THE ORIGINAL launches every shot the monsters (and your rocket\n"
          "launcher) asked for: copy one entry from the 'new shot ...' lists into\n"
          "my variables, then make a clone (a clone starts with a copy of my\n"
          "variables).",
          setv("queue position", 1)),
     repeat(length("new shot x"),
            setv("shot x", item(V("queue position"), "new shot x")),
            setv("shot y", item(V("queue position"), "new shot y")),
            setv("shot speed x", item(V("queue position"), "new shot speed x")),
            setv("shot speed y", item(V("queue position"), "new shot speed y")),
            setv("shot damage", item(V("queue position"), "new shot damage")),
            setv("shot look", item(V("queue position"), "new shot look")),
            setv("shot owner", item(V("queue position"), "new shot owner")),
            clone(), chg("queue position", 1)),
     clear_list("new shot x"), clear_list("new shot y"), clear_list("new shot speed x"),
     clear_list("new shot speed y"), clear_list("new shot damage"), clear_list("new shot look"),
     clear_list("new shot owner"),
          comment="LAUNCH NEW SHOTS (runs without screen refresh, so the loop finishes\n"
                  "in one go before the next frame's broadcast can restart it).")

PR.script(Def("check rocket hits"),
    note("Did my rocket fly into a monster? Check every living monster's\n"
         "position in the 'monster ... positions' lists.",
         setv("rocket hit something", 0)), setv("monster number", 1),
    repeat(length("monster x positions"),
           if_(eq(item(V("monster number"), "monster alive flags"), 1),
               setv("distance to monster", sqrt_(add(
                   mul(sub(item(V("monster number"), "monster x positions"), V("shot x")),
                       sub(item(V("monster number"), "monster x positions"), V("shot x"))),
                   mul(sub(item(V("monster number"), "monster y positions"), V("shot y")),
                       sub(item(V("monster number"), "monster y positions"), V("shot y")))))),
               if_(lt(V("distance to monster"), 0.6), setv("rocket hit something", 1))),
           chg("monster number", 1)),
    comment="CHECK ROCKET HITS (a loop, so it runs without screen refresh).")

PR.script(Def("explode rocket"),
    note("BOOM, one step back from whatever I hit. The explosion goes in the\n"
         "same 'new explosion' lists barrels use, so monsters and barrels\n"
         "nearby get hurt next frame. Too close to YOU hurts you too.",
         setv("shot x", V("previous x"))), setv("shot y", V("previous y")),
    addto("new explosion x", V("shot x")), addto("new explosion y", V("shot y")),
    *offset_from_player("shot x", "shot y"),
    if_(lt(V("distance to player"), 2.6),
        setv("blast damage", round_(mul(35, sub(1, div(V("distance to player"), 2.6))))),
        chg("health", mul(-1, V("blast damage"))), setv("hurt flash timer", 6), setv("killer type", -1)),
    play("explosion"), setv("is exploding", 1), setv("blast frame", 0), setv("draw height", -180),
    costume("explosion 1"),
    comment="EXPLODE ROCKET: turn this rocket into an explosion.")

PR.script(recv(UPDATE), ifelse(eq(V("is clone"), 0),
    [call("launch new shots")],
    [if_(eq(V("game state"), PLAYING),
         ifelse(eq(V("is exploding"), 1),
                [note("EXPLODING: the 3 explosion costumes, 4 frames each, then vanish.",
                      chg("blast frame", 1)),
                 costume("explosion 1", join("explosion ", add(floor_(div(V("blast frame"), 4)), 1))),
                 if_(gt(V("blast frame"), 11), delete_clone())],
                [note("A CLONE flies in a straight line. Enemy shots disappear when they\n"
                      "hit a wall, a closed door or a barrel, or after 5 seconds.",
                      setv("previous x", V("shot x"))), setv("previous y", V("shot y")),
                 chg("shot x", V("shot speed x")), chg("shot y", V("shot speed y")), chg("frames left", -1),
                 ifelse(eq(V("shot look"), "rocket"),
                        [note("YOUR ROCKET explodes on walls, barrels and monsters.",
                              ifelse(not_(eq(map_letter_at(floor_(V("shot x")), floor_(V("shot y"))), 0)),
                                     [call("explode rocket")],
                                     [call("check rocket hits"),
                                      if_(or_(eq(V("rocket hit something"), 1), lt(V("frames left"), 1)),
                                          setv("previous x", V("shot x")), setv("previous y", V("shot y")),
                                          call("explode rocket"))]))],
                        [if_(not_(eq(map_letter_at(floor_(V("shot x")), floor_(V("shot y"))), 0)), delete_clone()),
                         if_(lt(V("frames left"), 1), delete_clone()),
                         note("HIT THE PLAYER? Within 0.45 squares = hit. Strafe to dodge!",
                              setv("offset x from player", sub(V("shot x"), V("player x")))),
                         *offset_from_player("shot x", "shot y")[1:],
                         if_(lt(V("distance to player"), 0.45),
                             chg("health", mul(-1, V("shot damage"))), setv("hurt flash timer", 5),
                             setv("killer type", V("shot owner")), play("player hurt"), delete_clone())])]),
         *offset_from_player("shot x", "shot y"),
         *place_on_screen([], "shot", height=V("draw height")))]),
    comment="PROJECTILES: acid (spitters), fireballs (warden), plasma (colossus)\n"
            "and YOUR rockets. The 'shot look' picks the costume.")
PR.script(as_clone(), setv("is clone", 1), setv("frames left", 150), setv("is exploding", 0),
          ifelse(eq(V("shot look"), "rocket"), [setv("draw height", -70)], [setv("draw height", -50)]),
          costume("shot acid", join("shot ", V("shot look"))), hide())

# ============================================================================================
#                                  WEAPON / CROSSHAIR / HUD / MESSAGES
# ============================================================================================
playing = eq(V("screen showing"), NONE)

Gn = Target(P, "Weapon", layer=3, x=0, y=-190, size=105, visible=False)
WEAPON_COSTUMES = {"shotgun": (assets.GUN_IDLE, assets.GUN_FIRE), **assets6.WEAPON_ART}
for weapon_name in assets6.WEAPON_NAMES:
    ready, firing = WEAPON_COSTUMES[weapon_name]
    Gn.costume(f"{weapon_name} ready", ready, 80, 190)
    Gn.costume(f"{weapon_name} firing", firing, 80, 190)
    Gn.costume(f"{weapon_name} firing 2", assets6.CHAINGUN_FIRE_2 if weapon_name == "chaingun" else firing, 80, 190)
for nm, fn in (("shotgun", assets.shotgun), ("fist", assets2.punch), ("pistol", assets6.pistol),
               ("chaingun", assets6.chaingun), ("rocket launcher", assets6.rocket_launch)):
    d, n = fn(); Gn.sound(nm, d, assets.RATE, n)
for name in ["weapon name", "firing pose timer", "flash number", "jab amount"]:
    Gn.var(name)
Gn.script(flag(), costume("pistol ready"), setsize(105), gotoxy(0, -190), setv("firing pose timer", 0), hide())
Gn.script(recv(DRAW_HUD), ifelse(playing,
          [setv("weapon name", item(V("current weapon"), "weapon names")),
           note("Costume '<weapon> ready', or '<weapon> firing' (and 'firing 2',\n"
                "so the chaingun's barrels flash in turn) just after a shot.",
                ifelse(gt(V("firing pose timer"), 0),
                       [ifelse(eq(mod(V("flash number"), 2), 0),
                               [costume("pistol firing", join(V("weapon name"), " firing"))],
                               [costume("pistol firing", join(V("weapon name"), " firing 2"))]),
                        chg("firing pose timer", -1)],
                       [costume("pistol ready", join(V("weapon name"), " ready"))])),
           show(), front(),
           note("A punch jabs the fist up 28 pixels while its pose lasts.",
                setv("jab amount", 0)),
           if_(and_(gt(V("firing pose timer"), 0), eq(V("current weapon"), 1)), setv("jab amount", 28)),
           note("sin/cos of 'gun bob angle' swing the gun while you walk. A weapon\n"
                "switch drops it out of sight and back up (12 pixels per frame left).",
                gotoxy(mul(sin_(V("gun bob angle")), 8),
                       sub(add(add(-192, mul(abs_(cos_(V("gun bob angle"))), 7)), V("jab amount")),
                           mul(V("weapon switch timer"), 12))))],
          [hide()]),
          comment="DRAW HUD: the weapon in your hands, always in front of the 3D view.")
Gn.script(recv(FIRE), play_named("pistol", item(V("current weapon"), "weapon names")),
          setv("firing pose timer", 2), chg("flash number", 1),
          comment="FIRE: the sound named after the weapon + 2 frames of muzzle flash.")
Gn.script(recv(PUNCH), play("fist"), setv("firing pose timer", 5),
          comment="PUNCH: the fist jabs forward for 5 frames.")

X = Target(P, "Crosshair", layer=4, visible=False)
X.costume("crosshair", assets.CROSSHAIR, 10, 10)
X.script(flag(), gotoxy(0, 0), hide())
X.script(recv(DRAW_HUD), ifelse(playing, [show(), front()], [hide()]),
         comment="Always in the exact middle: the column the shot checks.")

Hd = Target(P, "HUD", layer=5, visible=False)
for i, art in enumerate(assets6.HUDS):
    Hd.costume(f"keys {i}", art, 240, 180)
Hd.script(flag(), gotoxy(0, 0), hide())
Hd.script(recv(DRAW_HUD), ifelse(playing,
          [costume("keys 0", join("keys ", add(add(V("has red key"), mul(V("has blue key"), 2)),
                                               mul(V("has skull key"), 4)))), show(), front()],
          [hide()]),
          comment="HUD frame: the HEALTH label, the sprint bar frame and the key slots.\n"
                  "Costume number = red key (1) + blue key (2) + skull key (4), so\n"
                  "'keys 0' = no keys ... 'keys 7' = all three. Like binary!\n"
                  "The Digits sprite draws the numbers.")

AP = Target(P, "Arms Panel", layer=5, visible=False)
for (owned_code, weapon_slot), art in assets6.ARMS.items():
    AP.costume(f"arms {owned_code} {weapon_slot}", art, 240, 180)
AP.script(flag(), gotoxy(0, 0), hide())
AP.script(recv(DRAW_HUD), ifelse(playing,
          [costume("arms 0 2", joins("arms ", add(add(item(3, "weapons owned"), mul(item(4, "weapons owned"), 2)),
                                                    mul(item(5, "weapons owned"), 4)),
                                     " ", V("current weapon"))), show(), front()],
          [hide()]),
          comment="ARMS PANEL: the ammo box label and the 1-5 weapon row.\n"
                  "Costume 'arms <owned> <holding>': <owned> adds 1 for the shotgun,\n"
                  "2 for the chaingun, 4 for the rocket launcher (the same binary\n"
                  "trick as the HUD's keys); <holding> = the weapon in your hands.")

BB = Target(P, "Boss Bar", layer=5, visible=False)
for boss_name, art in assets6.BOSS_BARS.items():
    BB.costume(f"boss bar {boss_name}", art, 240, 180)
BB.script(flag(), gotoxy(0, 0), hide())
BB.script(recv(DRAW_HUD), ifelse(and_(playing, and_(eq(V("boss is awake"), 1), gt(V("boss health"), 0))),
          [costume("boss bar warden", join("boss bar ", V("boss name"))), show(), front()], [hide()]),
          comment="BOSS BAR: the frame and name. The red health line inside it is\n"
                  "drawn with the pen at the end of 'draw 3D view'.")

MESSAGES = {"door hint": "hintd", "switch hint": "hintx", "need red key": "needred", "need blue key": "needblue",
            "picked up 1": "p1", "picked up 2": "p2", "picked up 3": "p3", "picked up 4": "p4",
            "exit activated": "exit", "found secret": None, "out of breath": None,
            **{name: None for name in assets6.TOASTS}}
EXTRA_MESSAGES = {"found secret": assets2.toast("You found a secret area!", "#ffd23f"),
                  "out of breath": assets2.toast("Out of breath! Wait for the sprint bar", "#ffa040"),
                  **assets6.TOASTS}
T = Target(P, "Message", layer=6, visible=False)
for name, old in MESSAGES.items():
    T.costume(f"message {name}", assets2.TOASTS[old] if old else EXTRA_MESSAGES[name], 240, 180)
T.script(flag(), gotoxy(0, 0), hide())
T.script(recv(DRAW_HUD), ifelse(and_(playing, gt(V("message timer"), 0)),
         [costume("message door hint", join("message ", V("message name"))),
          show(), front(), chg("message timer", -1)],
         [hide()]),
         comment="MESSAGES at the top of the screen. Anything can show one:\n"
                 "set 'message name' (it picks the costume 'message <name>') and\n"
                 "'message timer' (how many frames it stays up).")

S = Target(P, "Screens", layer=7, visible=True)
S.costume("screen level complete", assets3.COMPLETE, 240, 180)
S.costume("screen episode complete", assets6.EPISODE_COMPLETE, 240, 180)
S.script(flag(), gotoxy(0, 0), hide())
S.script(recv(DRAW_HUD),
         ifelse(eq(V("screen showing"), COMPLETE),
                [ifelse(eq(V("current level"), 3), [costume("screen episode complete")], [costume("screen level complete")]),
                 show(), front()], [hide()]),
         comment="LEVEL COMPLETE page (the death and victory screens have their own\nanimated sprites).")

Dg = Target(P, "Digits", layer=8, visible=False)
for c, art in assets2.DIGITS.items():
    Dg.costume(f"digit {c}", art, 21, 14)
for name in ["is clone", "number slot", "digit place", "number text"]:
    Dg.var(name)
Dg.script(flag(), hide(), setv("is clone", 0), setv("number slot", 0),
          repeat(HUD_SLOTS, chg("number slot", 1), setv("digit place", 0), repeat(3, chg("digit place", 1), clone())),
          comment=f"Makes {HUD_SLOTS * 3} clones = {HUD_SLOTS} numbers x 3 digits each.\n"
                  "'number slot' = which number (see 'HUD number values').\n"
                  "'digit place' = 1 for the ones digit, 2 tens, 3 hundreds.")
Dg.script(as_clone(), setv("is clone", 1))
Dg.script(recv(DRAW_NUMBERS), if_(eq(V("is clone"), 1),
    setv("number text", item(V("number slot"), "HUD number values")),
    note("Show me only on the right screen ('HUD number screen') and only if\n"
         "the number has enough digits (no leading zeros).",
         ifelse(and_(eq(V("screen showing"), item(V("number slot"), "HUD number screen")),
                     not_(lt(strlen(V("number text")), V("digit place")))),
                [note("Wear the costume for my digit, counting from the right.\n"
                      "Each place moves left by 24 pixels (times the size).",
                      costume("digit 0", join("digit ", letter(add(sub(strlen(V("number text")), V("digit place")), 1),
                                                               V("number text"))))),
                 setsize(item(V("number slot"), "HUD number size")),
                 gotoxy(sub(item(V("number slot"), "HUD number x"),
                            mul(sub(V("digit place"), 1), mul(item(V("number slot"), "HUD number size"), 0.24))),
                        item(V("number slot"), "HUD number y")),
                 show(), front()],
                [hide()]))),
    comment="DRAW HUD NUMBERS: each clone draws one digit of one number.")

# ============================================================================================
#                                     ANIMATED TITLE SCREEN
# ============================================================================================
on_title = eq(V("game state"), TITLE)

stage.script(recv(SHOW_TITLE), backdrop("title sky"), cleareffects(), setv("lightning glow", 0),
             until(not_(on_title),
                   note("LIGHTNING: about once every 5 seconds the sky flashes bright, and\n"
                        "the flash fades away (82 percent of it is left each frame).",
                        if_(eq(rnd(1, 160), 1), setv("lightning glow", 45))),
                   seteffect("BRIGHTNESS", V("lightning glow")),
                   setv("lightning glow", mul(V("lightning glow"), 0.82)), wait(0)),
             cleareffects(), backdrop("black"),
             comment="TITLE BACKDROP: the sky, fortress and controls are the Stage's\n"
                     "'title sky' backdrop. It switches back to black for the game.", x=1300)

TL = Target(P, "Title Logo", layer=12, visible=False)
TL.costume("logo", assets4.LOGO, 220, 67)
d, n = assets4.thud(); TL.sound("thud", d, assets.RATE, n)
for name in ["fall speed", "bounces", "logo time", "shake timer"]:
    TL.var(name)
TL.script(flag(), hide())
TL.script(recv(SHOW_TITLE),
          note("Start near the top, invisible, then fall.", gotoxy(0, 175)),
          setv("fall speed", 0), setv("bounces", 0), setv("logo time", 0), setv("shake timer", 0),
          setsize(100), seteffect("GHOST", 100), show(), front(),
          until(not_(on_title),
                chg("logo time", 1),
                note("Fade in over the first 10 frames.",
                     if_(lt(V("logo time"), 11), change_effect("GHOST", -10))),
                note("GRAVITY + BOUNCE: speed gets more negative each frame (gravity).\n"
                     "When the logo reaches y = 108, flip the speed and keep 45 percent\n"
                     "of it, like a ball losing energy. First bounce: thud + shake.\n"
                     "After 3 bounces, pulse the size gently with sin().",
                     ifelse(lt(V("bounces"), 3),
                            [chg("fall speed", -1.3), change_y(V("fall speed")),
                             if_(lt(ypos(), 108),
                                 set_y(108), setv("fall speed", mul(V("fall speed"), -0.45)), chg("bounces", 1),
                                 if_(eq(V("bounces"), 1), play("thud"), setv("shake timer", 8)))],
                            [setsize(add(100, mul(2.5, sin_(mul(V("logo time"), 6)))))])),
                note("SHAKE: jump to a random x for a few frames.",
                     ifelse(gt(V("shake timer"), 0), [set_x(rnd(-5, 5)), chg("shake timer", -1)], [set_x(0)])),
                note("Stay on top, except while the options menu is open.",
                     if_(eq(V("options open"), 0), front()))),
          hide(),
          comment="TITLE LOGO: drops in, bounces, then pulses.")

TM = Target(P, "Title Monster", layer=10, visible=False)
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        TM.costume(f"{monster_name} {pose}", svg_art, 40, 120)
d, n = assets.monster_pain(); TM.sound("pain", d, assets.RATE, n)
TM.lst("lineup types", [3, 6, 4, 5, 1])
TM.lst("lineup x", [-175, -92, 0, 92, 178])
TM.lst("lineup y", [-98, -106, -80, -102, -90])
TM.lst("lineup size", [118, 100, 140, 108, 90])
for name in ["is clone", "lineup slot", "monster type", "monster name", "target x", "base y", "anim time",
             "pose timer", "has arrived"]:
    TM.var(name)
TM.script(flag(), hide(), setv("is clone", 0))
TM.script(recv(SHOW_TITLE),
          if_(eq(V("is clone"), 0), setv("lineup slot", 0),
              repeat(length("lineup types"), chg("lineup slot", 1), clone())),
          comment="One clone per entry in the 'lineup' lists (this sprite's own lists).\n"
                  "Type numbers match the 'monster ...' lists: 1 imp, 2 spitter,\n3 golem, 4 warden, 5 charger, 6 wraith, 7 colossus.")
TM.script(as_clone(), setv("is clone", 1),
          setv("monster type", item(V("lineup slot"), "lineup types")),
          setv("monster name", item(V("monster type"), "monster names")),
          setv("target x", item(V("lineup slot"), "lineup x")), setv("base y", item(V("lineup slot"), "lineup y")),
          setsize(item(V("lineup slot"), "lineup size")),
          set_sound_effect("PITCH", item(V("monster type"), "monster voice pitch")),
          costume("imp walk 1", join(V("monster name"), " walk 1")),
          setv("anim time", 0), setv("pose timer", 0), setv("has arrived", 0),
          note("The BOSS fades in behind the logo after a second, and roars.\n"
               "Everyone else walks in from the nearest side of the screen.",
               ifelse(eq(item(V("monster type"), "monster is boss"), 1),
                      [gotoxy(V("target x"), V("base y")), seteffect("GHOST", 100), show(), go_back(), wait(1),
                       repeat(25, change_effect("GHOST", -4)), setv("has arrived", 1), setv("pose timer", 30),
                       play("pain")],
                      [ifelse(lt(V("target x"), 0), [gotoxy(-300, V("base y"))], [gotoxy(300, V("base y"))]),
                       show()])),
          until(not_(on_title),
                chg("anim time", 1),
                note("WALK IN: 4 pixels a frame toward my spot, swapping walk\ncostumes every 6 frames.",
                     if_(eq(V("has arrived"), 0),
                         ifelse(gt(abs_(sub(xpos(), V("target x"))), 4),
                                [ifelse(lt(xpos(), V("target x")), [change_x(4)], [change_x(-4)]),
                                 costume("imp walk 1", joins(V("monster name"), " walk ",
                                                             add(mod(floor_(div(V("anim time"), 6)), 2), 1)))],
                                [set_x(V("target x")), setv("has arrived", 1)]))),
                note("BOB: sin() moves me up and down. Each lineup slot is 70 degrees\n"
                     "ahead of the last, so they don't all bob together.",
                     set_y(add(V("base y"), mul(2.5, sin_(add(mul(V("anim time"), 7), mul(V("lineup slot"), 70))))))),
                note("ROAR: about once every 6 seconds, strike the attack pose and roar.",
                     if_(and_(eq(V("has arrived"), 1), and_(eq(V("pose timer"), 0), eq(rnd(1, 170), 1))),
                         setv("pose timer", 24), play("pain"))),
                ifelse(gt(V("pose timer"), 0),
                       [costume("imp attack", join(V("monster name"), " attack")), chg("pose timer", -1)],
                       [if_(eq(V("has arrived"), 1), costume("imp walk 1", join(V("monster name"), " walk 1")))])),
          delete_clone())

EM = Target(P, "Title Embers", layer=11, visible=False)
EM.costume("ember", assets4.EMBER, 7, 7)
for name in ["is clone", "rise speed", "drift phase"]:
    EM.var(name)
ember_time = or_(on_title, eq(V("card is up"), 1))
EM.script(flag(), hide(), setv("is clone", 0))
for hat in (SHOW_TITLE, SHOW_CARD):
    EM.script(recv(hat), if_(eq(V("is clone"), 0),
                             until(not_(ember_time), if_(lt(rnd(1, 100), 28), clone()), wait(0))),
              comment="EMITTER: on about 1 frame in 4, make a new ember clone.")
EM.script(as_clone(), setv("is clone", 1),
          gotoxy(rnd(-235, 235), -175), setsize(rnd(30, 100)), seteffect("GHOST", rnd(0, 30)),
          setv("rise speed", rnd(1.2, 3.5)), setv("drift phase", rnd(0, 360)), show(),
          until(or_(gt(ypos(), 170), not_(ember_time)),
                change_y(V("rise speed")),
                change_x(mul(sin_(add(V("drift phase"), mul(ypos(), 2))), 0.7)),
                change_effect("GHOST", 0.7)),
          delete_clone(),
          comment="EMBER: float up at my own speed, wobble with sin(), fade out.")

TT = Target(P, "Prompt Text", layer=13, visible=False)
TT.costume("press space", assets4.PRESS_SPACE, 150, 20)
TT.costume("press space retry", assets5.PROMPT_RETRY, 135, 15)
TT.costume("green flag again", assets5.PROMPT_AGAIN, 213, 15)
d, n = assets5.victory_theme(); TT.sound("victory theme", d, assets.RATE, n)
d, n = assets4.title_riff(); TT.sound("title theme", d, assets.RATE, n)
TT.var("pulse time")
TT.script(flag(), hide())
TT.script(recv(SHOW_TITLE), costume("press space"), gotoxy(0, -110), setv("pulse time", 0), seteffect("GHOST", 100), show(), wait(1.4),
          until(not_(on_title),
                chg("pulse time", 1),
                note("Pulse between solid and 70 percent see-through.",
                     seteffect("GHOST", mul(35, add(1, sin_(mul(V("pulse time"), 8)))))),
                if_(eq(V("options open"), 0), front())),
          hide(),
          comment="PRESS SPACE TO START, pulsing.")
TT.script(recv(APPLY_MUSIC), set_volume(mul(V("music is on"), 100)),
          comment="MUSIC ON/OFF: volume 100 or 0. Changing the volume also affects a\nsound that's already playing.")
TT.script(recv(SHOW_TITLE), set_volume(mul(V("music is on"), 100)), until(not_(on_title), play_until_done("title theme")),
          comment="TITLE MUSIC: an original 6-second riff that loops (the Engine stops\nit when you press SPACE).")

# ============================================================================================
#                                     LEVEL INTRO CARDS
# ============================================================================================
card_up = eq(V("card is up"), 1)

CB = Target(P, "Card Background", layer=14, visible=False)
CB.costume("card next level", assets4.CARD_NEXT, 240, 180)
for i, art in enumerate(assets6.CARD_ART):
    CB.costume(f"card {i + 1}", art, 240, 180)
CB.script(flag(), hide())
CB.script(recv(SHOW_CARD),
          note("Pick 'card N' for this level. If there isn't one (a level you\n"
               "added), Scratch keeps 'card next level'.",
               costume("card next level")), costume("card next level", join("card ", V("current level"))),
          gotoxy(0, 0), seteffect("GHOST", 100), show(), go_back(),
          note("Fade in, wait until the Engine takes the card down, fade out.",
               repeat(10, change_effect("GHOST", -10))),
          wait_until(not_(card_up)), repeat(6, change_effect("GHOST", 17)), hide(),
          comment="LEVEL CARD background: name, goal and the new enemy's description.")

CH = Target(P, "Card Heading", layer=15, visible=False)
CH.costume("heading next level", assets4.HEADING_NEXT, assets4.text_width("NEXT LEVEL", 8) // 2 + 6, 35)
for i, art in enumerate(assets6.HEADINGS):
    CH.costume(f"heading {i + 1}", art, assets4.text_width(f"LEVEL {i + 1}", 8) // 2 + 6, 35)
d, n = assets4.thud(); CH.sound("thud", d, assets.RATE, n)
CH.script(flag(), hide())
CH.script(recv(SHOW_CARD),
          costume("heading next level"), costume("heading next level", join("heading ", V("current level"))),
          setsize(260), seteffect("GHOST", 100), gotoxy(0, 122), show(), front(), wait(0.25),
          note("SLAM: shrink from huge to normal while fading in, then thud and\nshake the heading.",
               repeat(8, change_size(-20), change_effect("GHOST", -12.5), front())),
          play("thud"), repeat(8, gotoxy(rnd(-6, 6), add(122, rnd(-6, 6)))), gotoxy(0, 122),
          wait_until(not_(card_up)), repeat(6, change_effect("GHOST", 17)), hide(),
          comment="LEVEL N heading.")

CM = Target(P, "Card Monster", layer=16, visible=False)
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        CM.costume(f"{monster_name} {pose}", svg_art, 40, 120)
d, n = assets.monster_pain(); CM.sound("pain", d, assets.RATE, n)
for name in ["is clone", "card role", "monster type", "monster name", "base y", "anim time", "pose timer",
             "has arrived"]:
    CM.var(name)
CM.script(flag(), hide(), setv("is clone", 0))
CM.script(recv(SHOW_CARD), if_(eq(V("is clone"), 0),
          note("Role 1 = the level's new enemy ('level intro monster').\n"
               "Role 2 = a boss waiting in the background ('level intro boss').",
               setv("monster type", item(V("current level"), "level intro monster"))),
          if_(not_(eq(V("monster type"), "")), setv("card role", 1), clone()),
          setv("monster type", item(V("current level"), "level intro boss")),
          if_(gt(V("monster type"), 0), setv("card role", 2), clone())))
CM.script(as_clone(), setv("is clone", 1),
          setv("monster name", item(V("monster type"), "monster names")),
          set_sound_effect("PITCH", item(V("monster type"), "monster voice pitch")),
          costume("imp walk 1", join(V("monster name"), " walk 1")),
          setv("anim time", 0), setv("pose timer", 0), setv("has arrived", 0),
          ifelse(eq(V("card role"), 2),
                 [setv("base y", -102), gotoxy(190, -102), setsize(150), seteffect("GHOST", 55), show(),
                  wait(0.1), go_back(), go_forward(1)],
                 [setv("base y", -122), gotoxy(300, -122), setsize(170), show(), front()]),
          until(not_(card_up),
                chg("anim time", 1),
                note("The new enemy walks on from the right, then roars when it arrives.",
                     if_(and_(eq(V("card role"), 1), eq(V("has arrived"), 0)),
                         ifelse(gt(xpos(), 125),
                                [change_x(-5), costume("imp walk 1", joins(V("monster name"), " walk ",
                                                                           add(mod(floor_(div(V("anim time"), 6)), 2), 1)))],
                                [setv("has arrived", 1), setv("pose timer", 26), play("pain")]))),
                note("The boss in the background raises its arms now and then.",
                     if_(and_(eq(V("card role"), 2), eq(rnd(1, 90), 1)), setv("pose timer", 20))),
                ifelse(gt(V("pose timer"), 0),
                       [costume("imp attack", join(V("monster name"), " attack")), chg("pose timer", -1)],
                       [if_(or_(eq(V("has arrived"), 1), eq(V("card role"), 2)),
                            costume("imp walk 1", join(V("monster name"), " walk 1")))]),
                set_y(add(V("base y"), mul(2, sin_(mul(V("anim time"), 8)))))),
          repeat(6, change_effect("GHOST", 17)), delete_clone(),
          comment="CARD MONSTER clone: walks on, roars, bobs; fades out with the card.")

# ============================================================================================
#                                     ANIMATED DEATH SCREEN
# ============================================================================================
on_death = eq(V("screen showing"), DIED)
on_win = eq(V("screen showing"), WIN)

def pulse_prompt(hat, prompt_costume, y, delay, condition):
    TT.script(recv(hat), costume(prompt_costume), gotoxy(0, y), setv("pulse time", 0), seteffect("GHOST", 100),
              show(), front(), wait(delay),
              until(not_(condition), chg("pulse time", 1),
                    seteffect("GHOST", mul(35, add(1, sin_(mul(V("pulse time"), 8))))), front()),
              hide())
pulse_prompt(SHOW_DEATH, "press space retry", -158, 1.4, on_death)
pulse_prompt(SHOW_WIN, "green flag again", -157, 2.2, on_win)
TT.script(recv(SHOW_WIN), set_volume(mul(V("music is on"), 100)), until(not_(on_win), play_until_done("victory theme")),
          comment="VICTORY MUSIC: an original loop that plays until the green flag.")

DO = Target(P, "Death Overlay", layer=17, visible=False)
DO.costume("blood red", assets5.DEATH_OVERLAY, 240, 180)
DO.script(flag(), hide())
DO.script(recv(SHOW_DEATH), gotoxy(0, 0), seteffect("GHOST", 100), show(), front(),
          note("The frozen game fades to blood red (ghost 100 -> 10).",
               repeat(15, change_effect("GHOST", -6))),
          wait_until(not_(on_death)), hide(),
          comment="DEATH OVERLAY: a red vignette over the last frame of the game.")

BD = Target(P, "Blood Drips", layer=18, visible=False)
BD.costume("drop", assets5.BLOOD_DROP, 5, 10)
for name in ["is clone", "fall speed"]:
    BD.var(name)
BD.script(flag(), hide(), setv("is clone", 0))
BD.script(recv(SHOW_DEATH), if_(eq(V("is clone"), 0),
          until(not_(on_death), if_(lt(rnd(1, 100), 14), clone()), wait(0))),
          comment="EMITTER: about 1 frame in 7, start a new drop at the top.")
BD.script(as_clone(), setv("is clone", 1), gotoxy(rnd(-230, 230), 176), setsize(rnd(60, 130)),
          setv("fall speed", 0), show(), front(),
          until(or_(lt(ypos(), -172), not_(on_death)),
                note("Gravity: each frame the drop falls a little faster.",
                     chg("fall speed", 0.25)), change_y(mul(-1, V("fall speed")))),
          delete_clone(),
          comment="DROP: slide down the screen, speeding up, then vanish.")

DK = Target(P, "Death Killer", layer=19, visible=False)
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        DK.costume(f"{monster_name} {pose}", svg_art, 40, 120)
for i, art in enumerate(assets3.EXPLOSIONS):
    DK.costume(f"explosion {i + 1}", art, 45, 78)
d, n = assets.monster_pain(); DK.sound("pain", d, assets.RATE, n)
for name in ["anim time", "pose timer", "base y"]:
    DK.var(name)
DK.script(flag(), hide())
DK.script(recv(SHOW_DEATH),
          note("Barrel: show a looping explosion. Monster: wear its costumes,\nand use its voice pitch.",
               ifelse(or_(eq(V("killer name"), "barrel"), eq(V("killer name"), "rocket")),
                      [costume("explosion 1"), setsize(150), setv("base y", -20)],
                      [costume("imp walk 1", join(V("killer name"), " walk 1")), setsize(120), setv("base y", -88),
                       set_sound_effect("PITCH", item(V("killer type"), "monster voice pitch"))])),
          gotoxy(0, V("base y")), seteffect("GHOST", 100), show(), front(), wait(0.5),
          note("LOOM: fade in while growing, as if stepping toward you.",
               repeat(15, change_effect("GHOST", -6.7), change_size(2.7))),
          play("pain"), setv("anim time", 0), setv("pose timer", 24),
          until(not_(on_death),
                chg("anim time", 1),
                ifelse(or_(eq(V("killer name"), "barrel"), eq(V("killer name"), "rocket")),
                       [costume("explosion 1", join("explosion ", add(mod(floor_(div(V("anim time"), 4)), 3), 1)))],
                       [note("GLOAT: strike the attack pose and roar every couple of seconds.",
                             if_(and_(eq(V("pose timer"), 0), eq(rnd(1, 55), 1)), setv("pose timer", 22), play("pain"))),
                        ifelse(gt(V("pose timer"), 0),
                               [costume("imp attack", join(V("killer name"), " attack")), chg("pose timer", -1)],
                               [costume("imp walk 1", join(V("killer name"), " walk 1"))]),
                        set_y(add(V("base y"), mul(2, sin_(mul(V("anim time"), 6)))))])),
          hide(),
          comment="DEATH KILLER: whatever killed you ('killer name') gloats.")

DH = Target(P, "Death Heading", layer=20, visible=False)
DH.costume("you died", assets5.YOU_DIED, *assets5.YOU_DIED_CENTER)
for nm, fn in (("thud", assets4.thud), ("death sting", assets5.death_sting)):
    d, n = fn(); DH.sound(nm, d, assets.RATE, n)
DH.var("throb time")
DH.script(flag(), hide())
DH.script(recv(SHOW_DEATH), setsize(260), seteffect("GHOST", 100), gotoxy(0, 118), show(), front(), wait(0.3),
          note("SLAM: shrink from huge while fading in, then thud and shake.",
               repeat(8, change_size(-20), change_effect("GHOST", -12.5), front())),
          play("thud"), play("death sting"),
          repeat(8, gotoxy(rnd(-6, 6), add(118, rnd(-6, 6)))), gotoxy(0, 118), setv("throb time", 0),
          until(not_(on_death), chg("throb time", 1),
                note("Throb slowly, like a heartbeat.",
                     setsize(add(100, mul(2, sin_(mul(V("throb time"), 5)))))), front()),
          hide(),
          comment="YOU DIED heading.")

DM = Target(P, "Death Message", layer=21, visible=False)
DM.costume("killed by monster", assets5.KILLED_BY["monster"], 220, 25)
for name, art in {**assets5.KILLED_BY, **assets6.KILLED_BY}.items():
    if name != "monster":
        DM.costume(f"killed by {name}", art, 220, 25)
DM.script(flag(), hide())
DM.script(recv(SHOW_DEATH),
          note("'killed by <name>' + a tip for that enemy. A monster you add with\n"
               "no costume here gets the general 'killed by monster' one.",
               costume("killed by monster")), costume("killed by monster", join("killed by ", V("killer name"))),
          gotoxy(0, -118), seteffect("GHOST", 100), show(), front(), wait(1),
          repeat(10, change_effect("GHOST", -10)),
          until(not_(on_death), front()), hide(),
          comment="KILLED BY ... and a tip for beating that enemy next time.")

# ============================================================================================
#                                     ANIMATED VICTORY SCREEN
# ============================================================================================
stage.script(recv(SHOW_WIN), backdrop("victory sky"), cleareffects(),
             comment="VICTORY BACKDROP: dawn over the fortress.", x=1300)

VL = Target(P, "Victory Logo", layer=22, visible=False)
VL.costume("victory", assets6.VICTORY_LOGO, *assets5.VICTORY_CENTER)
d, n = assets4.thud(); VL.sound("thud", d, assets.RATE, n)
for name in ["fall speed", "bounces", "logo time"]:
    VL.var(name)
VL.script(flag(), hide())
VL.script(recv(SHOW_WIN), gotoxy(0, 175), setv("fall speed", 0), setv("bounces", 0), setv("logo time", 0),
          setsize(100), seteffect("GHOST", 100), show(), front(),
          until(not_(on_win),
                chg("logo time", 1),
                if_(lt(V("logo time"), 11), change_effect("GHOST", -10)),
                note("Same gravity-and-bounce trick as the title logo.",
                     ifelse(lt(V("bounces"), 3),
                            [chg("fall speed", -1.3), change_y(V("fall speed")),
                             if_(lt(ypos(), 118),
                                 set_y(118), setv("fall speed", mul(V("fall speed"), -0.45)), chg("bounces", 1),
                                 if_(eq(V("bounces"), 1), play("thud")))],
                            [setsize(add(100, mul(2.5, sin_(mul(V("logo time"), 6)))))])),
                front()),
          hide(),
          comment="VICTORY logo: drops in, bounces, pulses.")

VM = Target(P, "Victory Monsters", layer=21, visible=False)
for monster_name, art in MONSTER_ART.items():
    VM.costume(f"{monster_name} dead", art[3], 40, 120)
VM.lst("fallen types", [2, 6, 7, 5, 1])
VM.lst("fallen x", [-185, -100, 5, 105, 185])
VM.lst("fallen y", [-48, -52, -46, -50, -48])
VM.lst("fallen size", [100, 100, 150, 120, 95])
for name in ["is clone", "fallen slot"]:
    VM.var(name)
VM.script(flag(), hide(), setv("is clone", 0))
VM.script(recv(SHOW_WIN), if_(eq(V("is clone"), 0), setv("fallen slot", 0),
          repeat(length("fallen types"), chg("fallen slot", 1), clone())),
          comment="The defeated monsters, one clone per entry in the 'fallen' lists.")
VM.script(as_clone(), setv("is clone", 1),
          costume("imp dead", join(item(item(V("fallen slot"), "fallen types"), "monster names"), " dead")),
          gotoxy(item(V("fallen slot"), "fallen x"), item(V("fallen slot"), "fallen y")),
          setsize(item(V("fallen slot"), "fallen size")), seteffect("GHOST", 100), show(), wait(0.4),
          repeat(12, change_effect("GHOST", -8.4)), wait_until(not_(on_win)), delete_clone())

SP = Target(P, "Victory Stats", layer=20, visible=False)
SP.costume("stats panel", assets5.STATS_PANEL, 150, 38)
SP.script(flag(), hide())
SP.script(recv(SHOW_WIN), gotoxy(0, -95), seteffect("GHOST", 100), show(), go_back(), wait(1),
          repeat(10, change_effect("GHOST", -10)), wait_until(not_(on_win)), hide(),
          comment="STATS PANEL: labels only. The numbers are Digits slots 7, 10 and 11.\n"
                  "'go to back' keeps it behind the digits and fireworks.")

FW = Target(P, "Fireworks", layer=19, visible=False)
FW.costume("rocket", assets5.ROCKET, 4, 9)
for name, art in assets5.SPARKS.items():
    FW.costume(f"spark {name}", art, 6, 6)
d, n = assets5.firework_pop(); FW.sound("pop", d, assets.RATE, n)
FW.lst("spark colors", list(assets5.SPARKS))
for name in ["is clone", "role", "speed x", "speed y", "frames left", "spark color", "spark number"]:
    FW.var(name)
FW.script(flag(), hide(), setv("is clone", 0))
FW.script(recv(SHOW_WIN), if_(eq(V("is clone"), 0), wait(0.8), setv("role", 1), clone(),
          until(not_(on_win), if_(lt(rnd(1, 100), 4), setv("role", 1), clone()), wait(0))),
          comment="LAUNCHER: about one rocket a second. role 1 = rocket, role 2 = spark.")
FW.script(as_clone(), setv("is clone", 1),
          ifelse(eq(V("role"), 1),
                 [note("ROCKET: shoot upward, slowing down (gravity), until it almost\n"
                       "stops. Then burst into 14 sparks of one random color.",
                       gotoxy(rnd(-200, 200), -175)), costume("rocket"), setsize(100), show(),
                  setv("speed y", rnd(6.8, 8.2)), setv("speed x", rnd(-1, 1)),
                  until(or_(lt(V("speed y"), 1), not_(on_win)),
                        change_x(V("speed x")), change_y(V("speed y")), chg("speed y", -0.18)),
                  play("pop"), setv("spark color", item(rnd(1, length("spark colors")), "spark colors")),
                  setv("role", 2), setv("spark number", 0),
                  repeat(14,
                         note("Each spark flies out at its own angle (360 / 14 apart) and speed.\n"
                              "A clone starts with a copy of my variables, so I set them first.",
                              setv("speed x", mul(rnd(2, 4), cos_(add(mul(V("spark number"), 25.7), rnd(0, 10)))))),
                         setv("speed y", mul(rnd(2, 4), sin_(add(mul(V("spark number"), 25.7), rnd(0, 10))))),
                         clone(), chg("spark number", 1))],
                 [costume("spark gold", join("spark ", V("spark color"))), setsize(rnd(110, 160)), show(),
                  setv("frames left", 40),
                  until(or_(lt(V("frames left"), 1), not_(on_win)),
                        note("SPARK: fly, fall (gravity), slow down (air), and fade.",
                             change_x(V("speed x"))), change_y(V("speed y")),
                        chg("speed y", -0.08), setv("speed x", mul(V("speed x"), 0.97)),
                        change_effect("GHOST", 2.5), chg("frames left", -1))]),
          delete_clone())

# ============================================================================================
#                                     OPTIONS MENU
# ============================================================================================
options_up = eq(V("options open"), 1)
OP = Target(P, "Options Panel", layer=23, visible=False)
OP.costume("options title", assets6.OPTIONS_TITLE, 240, 180)
OP.costume("options paused", assets6.OPTIONS_PAUSED, 240, 180)
OP.script(flag(), gotoxy(0, 0), hide())
OP.script(recv(DRAW_OPTIONS_PANEL),
          ifelse(options_up,
                 [ifelse(eq(V("options from game"), 1), [costume("options paused")], [costume("options title")]),
                  show(), front()],
                 [hide()]),
          comment="OPTIONS PANEL: the box, the labels and the slider tracks. From the\n"
                  "game it says PAUSED and the level select is switched off.")

ROW_Y = assets6.OPTION_ROW_Y
TRACK_LEFT, TRACK_RIGHT = assets6.TRACK_LEFT, assets6.TRACK_RIGHT
OW = Target(P, "Options Widgets", layer=24, visible=False)
OW.costume("row highlight", assets6.ROW_HIGHLIGHT, 190, 13)
OW.costume("knob", assets6.KNOB, 10, 10)
OW.costume("switch on", assets6.TOGGLE_ON, 28, 11)
OW.costume("switch off", assets6.TOGGLE_OFF, 28, 11)
for name in ["is clone", "widget role"]:
    OW.var(name)
OW.script(flag(), hide(), setv("is clone", 0), setv("widget role", 0), repeat(6, chg("widget role", 1), clone()),
          comment="Six clones, one per 'widget role':\n"
                  "1 the highlight on the chosen row, 2 turn speed knob,\n"
                  "3 mouse steering switch, 4 sensitivity knob, 5 field of view knob,\n6 music switch.")
OW.script(as_clone(), setv("is clone", 1))

def knob_at(setting, low, high, y):
    """Slide the knob along the track: (setting - low) / (high - low) of the way across."""
    return [costume("knob"), gotoxy(add(TRACK_LEFT, mul(TRACK_RIGHT - TRACK_LEFT, div(sub(V(setting), low), high - low))), y)]

def switch_at(setting, y):
    return [ifelse(eq(V(setting), 1), [costume("switch on")], [costume("switch off")]), gotoxy(40, y)]

OW.script(recv(DRAW_OPTIONS_WIDGETS), if_(eq(V("is clone"), 1),
    ifelse(options_up,
           [if_(eq(V("widget role"), 1), costume("row highlight"),
                gotoxy(0, sub(ROW_Y[0], mul(sub(V("options row"), 1), 30)))),
            if_(eq(V("widget role"), 2), *knob_at("turn speed", 1, 10, ROW_Y[0])),
            if_(eq(V("widget role"), 3), *switch_at("mouse steering", ROW_Y[1])),
            if_(eq(V("widget role"), 4), *knob_at("mouse sensitivity", 1, 10, ROW_Y[2])),
            if_(eq(V("widget role"), 5), *knob_at("field of view", MIN_FOV, MAX_FOV, ROW_Y[3])),
            if_(eq(V("widget role"), 6), *switch_at("music is on", ROW_Y[4])),
            show(), front()],
           [hide()])),
    comment="DRAW OPTIONS WIDGETS: each clone shows its own setting.")

# ============================================================================================
#                                          MUSIC
# ============================================================================================
MU = Target(P, "Music", layer=1, visible=False)
MU.costume("speaker", assets.TINY, 1, 1)
for nm, fn in (("episode 1 theme", assets6.episode_1_theme), ("episode 2 theme", assets6.episode_2_theme)):
    d, n = fn(); MU.sound(nm, d, assets.RATE, n)
MU.var("episode number")
MU.script(flag(), hide())
MU.script(recv(START_MUSIC), stop_sounds(), set_volume(mul(V("music is on"), 100)),
          note("Levels 1-3 are episode 1, levels 4-6 episode 2. Each has its own loop.",
               ifelse(lt(V("current level"), 4), [setv("episode number", 1)], [setv("episode number", 2)])),
          note("Loop the track until you die, go back to the title, or win. (Dying\n"
               "and winning stop all sounds, which ends 'play until done' early.)",
               until(or_(or_(eq(V("game state"), DEAD), eq(V("game state"), TITLE)), eq(V("screen showing"), WIN)),
                     play_until_done_named("episode 1 theme", joins("episode ", V("episode number"), " theme")))),
          comment="IN-GAME MUSIC: starts when each level starts.")
MU.script(recv(APPLY_MUSIC), set_volume(mul(V("music is on"), 100)),
          comment="MUSIC ON/OFF (N key or the options menu): volume 100 or 0.")

# ---------------- sanity checks: names must be unique between the Stage and each sprite ----------------
for sprite in P.targets[1:]:
    clash = set(sprite.vars) & set(P.stage_vars)
    assert not clash, (sprite.name, clash)
    for n in list(sprite.vars) + list(P.stage_vars) + list(P.stage_lists):
        assert len(n) > 2, f"name too short: {n}"

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "scratch-slayer.sb3"
    proj = P.save(out)
    print("saved", out, "blocks:", sum(len(t["blocks"]) for t in proj["targets"]),
          "comments:", sum(len(t["comments"]) for t in proj["targets"]))
