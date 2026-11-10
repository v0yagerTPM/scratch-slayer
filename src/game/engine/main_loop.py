"""One frame of play, the main green-flag script (title -> level card -> play -> results),
the level intro and screen melt, the HUD numbers and the end-of-level tally."""
from sb3extra import *
from game.config import *
from game.engine.sprite import engine, wait_for_space

facing_a_door = or_(or_(or_(eq(V("facing letter"), "D"), eq(V("facing letter"), "R")),
                        or_(eq(V("facing letter"), "B"), eq(V("facing letter"), "X"))),
                    eq(V("facing letter"), "Z"))  # S stays secret: no hint
frame = [
    note("LEVEL CLOCK: add the time since the last frame to 'level time' (in\n"
         "seconds). Using Scratch's timer, not counting frames, keeps the clock\n"
         "right even when a big level makes the game slower than 30 frames a second.",
         chg("level time", sub(timer(), V("time at last frame")))),
    setv("time at last frame", timer()),
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
    *[if_(and_(key(str(weapon_number)), and_(eq(item(weapon_number, "weapons owned"), 1),
                                              not_(eq(V("current weapon"), weapon_number)))),
          setv("current weapon", weapon_number), setv("weapon switch timer", 8)) for weapon_number in range(2, 6)],
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

engine.script(
    flag(), hide(),
    note("NEW GAME: reset everything that carries over between levels.\n"
         "You start with your fists and the pistol (weapon slots 1 and 2).",
         setv("health", 100)), replace("weapons owned", 3, 0), replace("weapons owned", 4, 0),
    replace("weapons owned", 5, 0), setv("current weapon", 2), setv("weapon switch timer", 0),
    *[replace("ammo counts", ammo_slot, ammo[1]) for ammo_slot, ammo in enumerate(AMMO, start=1)], call("remember ammo at level start"),
    setv("total kills", 0), setv("total secrets found", 0), setv("total secret count", 0), setv("current level", 1), setv("map is showing", 0), setv("M key was held", 0),
    setv("E key was held", 0), setv("shot cooldown", 0), setv("shot fired this frame", 0),
    setv("target hit id", 0), setv("gun bob angle", 0), setv("player is moving", 0),
    hide_list("map problems"), stop_sounds(), pen_clear(),
    note("TITLE SCREEN: pick one of level 1's maps and load it (ready for\n"
         "later), then tell the title sprites to start their animations, and\n"
         "wait for SPACE. O opens the options menu.",
         setv("game state", TITLE)), setv("screen showing", TITLE), setv("show intro", 1), setv("card is up", 0),
    call("pick map"), call("start level", warp=False),
    bcast(SHOW_TITLE), wait_until(not_(key("space"))),
    until(key("space"), if_(key("o"), call("options menu", warp=False))),
    wait_until(not_(key("space"))),
    note("Leaving the title: changing 'game state' ends every title animation\n"
         "loop, and the music stops.",
         setv("game state", INTRO)), stop_sounds(),
    note("LEVEL SELECT: if the options menu picked a later level, start there\n"
         "with the weapons and ammo a player would have found by then.",
         if_(gt(V("start level choice"), 1),
             setv("current level", V("start level choice")), call("give level select weapons"))),
    note("PICK THE MAP again if you picked a later level, or a MAP setting other\n"
         "than RANDOM (the map loaded behind the title was picked before you\n"
         "could change it).",
         if_(or_(gt(V("start level choice"), 1), gt(V("map choice"), 0)), call("pick map"))),
    note("Load the level again if that changed the map, or if you changed the\n"
         "DIFFICULTY after level 1 was loaded behind the title screen (its\n"
         "monsters need the new health).",
         if_(or_(not_(eq(V("map name"), V("map name when loaded"))), not_(eq(V("difficulty"), V("difficulty when loaded")))),
             call("start level", warp=False))),
    note("LEVEL LOOP: each pass of 'forever' plays one level (or one retry).",
         forever(
             note("LEVEL START: a new level gets its intro card and the screen melt.\n"
                  "A retry after dying just melts in.",
                  ifelse(eq(V("show intro"), 1), [call("level intro", warp=False)], [call("melt in", warp=False)])),
             note("Start playing (and start the music). 'highest level reached' unlocks\n"
                  "levels in the options menu's level select.",
                  setv("game state", PLAYING)), setv("screen showing", NONE), bcast(START_MUSIC),
             note("Start the level clock from 0 (a retry after dying starts it again too).",
                  setv("level time", 0)), setv("time at last frame", timer()),
             if_(gt(V("current level"), V("highest level reached")), setv("highest level reached", V("current level"))),
             note("PLAY: repeat one frame at a time until you reach the exit or die.\n"
                  "Everything that happens in a frame is inside this loop.",
                  until(or_(eq(V("game state"), EXIT_REACHED), eq(V("game state"), DEAD)), *frame)),
             note("AFTER THE LEVEL:\n"
                  "Died -> show 'YOU DIED', take back this level's kills, refill health,\n"
                  f"give back the ammo you started the level with (at least {START_BULLETS}\n"
                  "bullets), and reload the SAME level: the same map, or (R) another one.\n"
                  "Exit -> count up the stats (the tally), go to the next level and pick\n"
                  "one of its maps. After the last level (the number of items in\n"
                  "'level names') show the win screen.",
                  ifelse(eq(V("game state"), DEAD),
                         [setv("screen showing", DIED), call("draw still frame", warp=False),
                          note("Who did it? 'killer type' was set by whatever hurt you last:\n"
                               "a monster type number, 0 for a barrel, -1 for your own rocket.",
                               ifelse(eq(V("killer type"), 0), [setv("killer name", "barrel")],
                                      [ifelse(eq(V("killer type"), -1), [setv("killer name", "rocket")],
                                              [setv("killer name", item(V("killer type"), "monster names"))])])),
                          stop_sounds(), bcast(SHOW_DEATH), wait(0.5),
                          wait_until(not_(or_(key("space"), key("r")))),
                          note("SPACE = try the same map again: it just melts back in.\n"
                               "R = a different map, with its own level card. R only works when\n"
                               "the level has more than one map ('level map count').",
                               wait_until(or_(key("space"), and_(key("r"), gt(V("level map count"), 1))))),
                          ifelse(key("space"), [setv("show intro", 0)],
                                 [call("pick a different map"), setv("show intro", 1)]),
                          wait_until(not_(or_(key("space"), key("r")))), stop_sounds(),
                          chg("total kills", mul(-1, V("level kills"))), setv("health", 100),
                          call("restore ammo at level start"),
                          call("start level", warp=False)],
                         [note("THE TALLY: work out the level's stats, show the screen, count\n"
                               "them up, then wait for SPACE.",
                               call("work out level stats")),
                          setv("screen showing", COMPLETE), call("draw still frame", warp=False),
                          call("count up level stats", warp=False), *wait_for_space(skip_pause=True),
                          chg("total secrets found", V("level secrets found")),
                          chg("total secret count", V("level secret count")),
                          chg("current level", 1),
                          if_(gt(V("current level"), length("level names")),
                              note("VICTORY: clear away the level, then let the victory sprites take\n"
                                   "over. The stats appear once their panel has faded in.",
                                   setv("screen showing", INTRO)), bcastw(DRAW_NUMBERS), bcastw(CLEAR), pen_clear(),
                              setv("screen showing", WIN), bcastw(DRAW_HUD), stop_sounds(), bcast(SHOW_WIN), wait(1.6),
                              call("copy numbers to HUD"), bcastw(DRAW_NUMBERS), stop_script()),
                          call("remember ammo at level start"), setv("show intro", 1),
                          call("pick map"), call("start level", warp=False)])),
         )),
    comment="MAIN GAME SCRIPT  (read the comments down the left side)\n"
            "Title screen -> then for each level: play frames until you\n"
            "flip the exit switch or die -> results screen -> next level.\n"
            "The level design guide is in the Stage's code area.")

engine.script(Def("share explosions and clear wreckage"),
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

engine.script(Def("level intro", warp=False),
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

engine.script(Def("melt in", warp=False),
         setv("game state", INTRO), setv("screen showing", INTRO),
         bcastw(DRAW_HUD), bcastw(DRAW_NUMBERS),
         call("start melt"), play("melt"),
         note("One frame per pass: draw the level, then the curtain on top of it.\n"
              "The curtain's columns slide down a bit more each frame.",
              until(eq(V("melt done"), 1), call("draw 3D view"), call("draw melt curtain"))),
         comment="MELT IN: reveal the level with a Doom-style screen melt.")

engine.script(Def("start melt"),
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

engine.script(Def("draw melt curtain"),
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

engine.script(Def("start level", warp=False),
         bcastw(CLEAR), call("load level"), setv("difficulty when loaded", V("difficulty")),
         setv("map name when loaded", V("map name")), bcastw(SPAWN),
         call("update camera"),
         comment="START LEVEL: delete the old monster and item clones, read the\n"
                 "map with 'load level' (the map 'pick map' chose), make new clones,\n"
                 "then aim the camera.")

engine.script(Def("draw still frame", warp=False),
         setv("target hit id", 0), setv("shot fired this frame", 0),
         call("draw 3D view"), bcastw(UPDATE), call("copy numbers to HUD"), bcastw(DRAW_HUD), bcastw(DRAW_NUMBERS),
         comment="DRAW STILL FRAME: draws one frame while the game is paused\n"
                 "(title, died, level complete, win). 'broadcast and wait' is fine\n"
                 "here because nothing is moving.")

HUD_SOURCES = ["health", "ammo shown", "kills percent shown", "items percent shown", "secrets percent shown",
               "time minutes shown", "time seconds shown", "par minutes shown", "par seconds shown",
               "total kills", "total secrets found", "total secret count",
               "turn speed", "mouse sensitivity", "field of view"]
engine.script(Def("copy numbers to HUD"),
         note("AMMO SHOWN = the ammo for the weapon in your hands. Fists use none, so\n"
              "it's empty text and the Digits sprite shows nothing.",
              setv("weapon ammo slot", item(V("current weapon"), "weapon ammo slots"))),
         ifelse(eq(V("weapon ammo slot"), 0), [setv("ammo shown", "")],
                [setv("ammo shown", item(V("weapon ammo slot"), "ammo counts"))]),
         *[replace("HUD number values", slot, V(source)) for slot, source in enumerate(HUD_SOURCES, start=1)],
         note("Slot 16 (start level) only shows in the title screen's options menu.",
              ifelse(eq(V("options from game"), 1), [replace("HUD number values", 16, "")],
                     [replace("HUD number values", 16, V("start level choice"))])),
         comment="COPY NUMBERS TO HUD: the Digits sprite draws whatever is in\n'HUD number values'. Slot 1 health, 2 ammo,\n"
                 "3-9 the level tally (kills %, items %, secrets %, time, par time),\n"
                 "10 total kills, 11-12 secrets in the whole game, 13-16 the options menu.")

def percent_of(found, total, result):
    """result = found / total x 100, rounded. Nothing to find counts as 100 percent."""
    return ifelse(eq(V(total), 0), [setv(result, 100)], [setv(result, round_(mul(div(V(found), V(total)), 100)))])

def two_digits(var):
    """Seconds always show two digits on a clock: 5 becomes "05"."""
    return if_(lt(V(var), 10), setv(var, join("0", V(var))))

engine.script(Def("work out level stats"),
    note("FINAL NUMBERS. Percentages are rounded to whole numbers.",
         percent_of("level kills", "level monster count", "kills percent")),
    percent_of("level items collected", "level item count", "items percent"),
    percent_of("level secrets found", "level secret count", "secrets percent"),
    setv("level seconds", round_(V("level time"))),
    setv("par seconds", item(V("map item number"), "map par times")),
    note("PAR TIME is shown straight away. A clock shows minutes:seconds:\n"
         "minutes = seconds / 60 rounded DOWN, and the seconds left over are\n"
         "seconds MOD 60 (the remainder). 135 seconds = 2:15.",
         setv("par minutes shown", floor_(div(V("par seconds"), 60)))),
    setv("par seconds shown", mod(V("par seconds"), 60)), two_digits("par seconds shown"),
    note("The counted numbers start at 0, and the badge stays hidden until\n"
         "the counting is done.",
         setv("kills percent shown", 0)), setv("items percent shown", 0), setv("secrets percent shown", 0),
    setv("time minutes shown", 0), setv("time seconds shown", "00"), setv("par was beaten", 0),
    comment="WORK OUT LEVEL STATS: runs once when you reach the exit, before\nthe tally screen appears.")

engine.script(Def("count up level stats", warp=False),
    setv("tally progress", 0),
    note("COUNT UP: one pass per frame. 'tally progress' goes from 0 to 1 in\n"
         "30 frames (1 second), and every number shows that fraction of its\n"
         "final value. Doom's intermission screen counted up the same way.\n"
         "SPACE jumps straight to the end.",
         until(gt(V("tally progress"), 0.999),
               chg("tally progress", div(1, 30)),
               if_(key("space"), setv("tally progress", 1)),
               if_(gt(V("tally progress"), 1), setv("tally progress", 1)),
               setv("kills percent shown", round_(mul(V("kills percent"), V("tally progress")))),
               setv("items percent shown", round_(mul(V("items percent"), V("tally progress")))),
               setv("secrets percent shown", round_(mul(V("secrets percent"), V("tally progress")))),
               setv("time shown in seconds", round_(mul(V("level seconds"), V("tally progress")))),
               setv("time minutes shown", floor_(div(V("time shown in seconds"), 60))),
               setv("time seconds shown", mod(V("time shown in seconds"), 60)), two_digits("time seconds shown"),
               note("Tick every third frame while counting.",
                    if_(eq(mod(round_(mul(V("tally progress"), 30)), 3), 0), play("tally tick"))),
               call("copy numbers to HUD"), bcast(DRAW_NUMBERS))),
    note("DONE: a thump, and the UNDER PAR! badge if you were at least as fast\n"
         "as the par time. The Screens sprite picks its costume from 'par was beaten'.",
         play("tally done")),
    if_(not_(gt(V("level seconds"), V("par seconds"))), setv("par was beaten", 1)),
    bcastw(DRAW_HUD), bcastw(DRAW_NUMBERS),
    comment="COUNT UP LEVEL STATS: the tally screen after each level.\n"
            "Kills, items and secrets as percentages, your time and the par time.")
