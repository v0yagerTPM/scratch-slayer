"""The level design guide: the big comments students read first in the Stage's code area."""
from sb3extra import *
from game.config import *
from game.stage import stage

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
(Teachers: the game's Python source keeps its maps in exactly this
format, in src/maps/level 1 map.txt and so on, so an exported map can
go straight into the project.)

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
   "level light falloffs", "level sprite darkness",
   "level select best weapon" and "level par times" (seconds).
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
difficulty          1 easy, 2 normal, 3 hard (see DIFFICULTY below)
start level choice  level select (only levels you have reached:
                    "highest level reached")

Difficulty and start level can only be changed on the title screen,
not while a game is paused, so you can't switch to easy mid-fight!
These are NOT reset by the green flag, so settings stick while the
project is open. The menu is drawn by the Options Panel and Options
Widgets sprites; the Engine's 'handle options input' block reads the
keys and the mouse.""",

"""DIFFICULTY  (easy, normal, hard)

The "difficulty ..." lists line up item by item, like the monster lists:
item 1 easy, 2 normal, 3 hard. Item 'difficulty' of each list is the
one in use. Both numbers are PERCENTAGES of the normal amount.

difficulty names           the word shown in the options menu
difficulty damage to you   every hit on you is multiplied by this / 100.
                           Easy = 50, so a 12-damage claw only does 6.
difficulty monster health  every monster starts with this percent of
                           its "monster health", rounded. Hard = 125,
                           so an imp (3) needs 4 pistol shots.

Where it happens: search for "difficulty" in the Monster sprite (when
a clone starts) and in every block that does 'change health by'
(Monster, Barrel and Projectile sprites).

Doom (1993) had five skill levels. Its easiest one also halved the
damage you take, just like our easy setting.""",

"""THE LEVEL TALLY  (the screen after each level)

When you flip the exit switch, the Engine's 'work out level stats'
block works out:
  kills percent   = level kills / level monster count x 100
  items percent   = level items collected / level item count x 100
  secrets percent = level secrets found / level secret count x 100
(A level with nothing to find counts as 100 percent.)
  level seconds   = how long you played the level. 'level time'
                    goes up by the time each frame took, using
                    Scratch's timer. The pause menu doesn't count.
  par seconds     = item 'current level' of "level par times"

Then 'count up level stats' counts the numbers up from 0 for one second
with a ticking sound,
like the intermission screen in Doom. SPACE skips the counting.
Beat the par time and an UNDER PAR! badge appears.

TIME is shown as minutes:seconds. 125 seconds = 2:05, because
125 / 60 = 2 (rounded down) and 125 mod 60 = 5. The 'mod' block gives
the remainder after dividing.""",
]
guide_y = 0
for text in GUIDE:
    guide_height = 60 + 18 * len(text.split("\n"))
    stage.workspace_comment(text, 0, guide_y, width=560, height=guide_height)
    guide_y += guide_height + 40
