"""The Monster sprite: one clone per monster, with its AI, attacks and special moves."""
from sb3extra import *
from game.config import *
import pictures.monsters, sounds.monsters, sounds.screens, sounds.world
from game.engine.raycaster import SQUARE
from game.screen_placement import explosion_scan, offset_from_player, place_on_screen
from game.stage import project

monster = Target(project, "Monster", layer=2, visible=False)
MONSTER_ART = {
    "imp": (pictures.monsters.IMP_WALK1, pictures.monsters.IMP_WALK2, pictures.monsters.IMP_ATTACK, pictures.monsters.IMP_DEAD),
    "spitter": (pictures.monsters.SPITTER_WALK1, pictures.monsters.SPITTER_WALK2, pictures.monsters.SPITTER_ATTACK, pictures.monsters.SPITTER_DEAD),
    "golem": (pictures.monsters.GOLEM_WALK1, pictures.monsters.GOLEM_WALK2, pictures.monsters.GOLEM_ATTACK, pictures.monsters.GOLEM_DEAD),
    "warden": (pictures.monsters.WARDEN_WALK1, pictures.monsters.WARDEN_WALK2, pictures.monsters.WARDEN_ATTACK, pictures.monsters.WARDEN_DEAD),
    "charger": (pictures.monsters.CHARGER_WALK1, pictures.monsters.CHARGER_WALK2, pictures.monsters.CHARGER_ATTACK, pictures.monsters.CHARGER_DEAD),
    "wraith": (pictures.monsters.WRAITH_WALK1, pictures.monsters.WRAITH_WALK2, pictures.monsters.WRAITH_ATTACK, pictures.monsters.WRAITH_DEAD),
    "colossus": (pictures.monsters.COLOSSUS_WALK1, pictures.monsters.COLOSSUS_WALK2, pictures.monsters.COLOSSUS_ATTACK, pictures.monsters.COLOSSUS_DEAD),
}
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        monster.costume(f"{monster_name} {pose}", svg_art, 40, 120)
for sound_name, make_sound in (("pain", sounds.monsters.monster_pain), ("death", sounds.monsters.monster_death), ("player hurt", sounds.world.player_hurt),
               ("spit", sounds.monsters.spit), ("fireball", sounds.monsters.fireball), ("slam", sounds.screens.thud),
               ("blink", sounds.monsters.wraith_blink)):
    add_sound(monster, sound_name, make_sound)
for name in ["monster id", "is clone", "monster type", "monster name", "monster x", "monster y", "is alive",
             "monster health", "full health", "attack cooldown", "volley cooldown", "pain flash timer", "attack pose timer",
             "is chasing", "moved this frame", "damage taken", "explosion number", "distance to blast",
             "offset x from player", "offset y from player", "distance to player", "next monster x",
             "next monster y", "sight is clear", "sight x", "sight y", "aim x", "aim y", "volley shot number",
             "spread angle", "sideways in view", "depth in view", "screen x", "screen column index",
             # special moves
             "speed multiplier", "charge state", "charge timer", "charge cooldown", "charge direction x",
             "charge direction y", "blink timer", "blink side", "has called for help", "helper x", "helper y",
             # moving: one monster per square, and chasing what I can see
             "my square", "square to try", "step x", "step y", "target offset x", "target offset y", "target distance",
             "can see player", "sight timer", "knows where player is", "last seen x", "last seen y",
             # keeping my body out of the walls
             "my wall gap", "wall check x", "wall check y", "landing is clear", "offset from middle"]:
    monster.var(name)

def stat(column):
    """item (monster type) of the 'monster <column>' list — this monster's number for that stat."""
    return item(V("monster type"), f"monster {column}")

def square_number(x_value, y_value):
    """Which item of 'monster on square' belongs to the map square at (x, y): squares are
    numbered row by row, so square number = row x map width + column + 1."""
    return add(add(mul(floor_(y_value), V("map width")), floor_(x_value)), 1)

def is_floor(x_value, y_value):
    """True if the map square under the point (x, y) is floor (letter 0), not a wall or closed door."""
    return eq(map_letter_at(floor_(x_value), floor_(y_value)), 0)

def no_other_monster_on_square():
    """No OTHER monster stands on the square numbered 'square to try'."""
    return or_(eq(item(V("square to try"), "monster on square"), 0),
               eq(item(V("square to try"), "monster on square"), V("monster id")))

def leading_edge(position, step, edge):
    """Where my front edge would be along one direction: my middle plus 'my wall gap' in the
    direction I'm moving (minus it if the step goes backwards). Sets the variable 'edge'."""
    return ifelse(gt(step, 0), [setv(edge, add(position, V("my wall gap")))],
                  [setv(edge, sub(position, V("my wall gap")))])

def body_is_clear(x_value, y_value, why):
    """Blocks that set 'landing is clear' to 1 if a monster standing at (x, y) would fit: all
    four corners of my body (a square 'my wall gap' out from my middle each way) on floor, and
    my middle on a square no other monster has. 'why' becomes the comment on the first block."""
    gap = V("my wall gap")
    return [note(why, setv("square to try", square_number(x_value, y_value))), setv("landing is clear", 0),
            if_(and_(and_(and_(is_floor(sub(x_value, gap), sub(y_value, gap)), is_floor(add(x_value, gap), sub(y_value, gap))),
                          and_(is_floor(sub(x_value, gap), add(y_value, gap)), is_floor(add(x_value, gap), add(y_value, gap)))),
                     no_other_monster_on_square()),
                setv("landing is clear", 1))]

def step_along(axis, other_axis, step):
    """One half of 'take a step': move along 'axis' ("x" or "y") by 'step', if my body fits.
    My front edge is 'my wall gap' ahead of my middle; both of its corners must be on floor.
    If only one corner is blocked (I'm brushing past the corner of a wall, or lining up with a
    doorway), slide sideways toward the middle of my row (or column) instead, so next time I fit."""
    position, other = V(f"monster {axis}"), V(f"monster {other_axis}")
    edge, gap = V(f"wall check {axis}"), V("my wall gap")

    def floor_at(along, across):      # is_floor with the coordinates in the right order
        return is_floor(along, across) if axis == "x" else is_floor(across, along)
    return [setv(f"next monster {axis}", add(position, step)),
            leading_edge(V(f"next monster {axis}"), step, f"wall check {axis}"),
            setv("square to try", square_number(V("next monster x"), V("monster y")) if axis == "x"
                 else square_number(V("monster x"), V("next monster y"))),
            if_(no_other_monster_on_square(),
                ifelse(and_(floor_at(edge, sub(other, gap)), floor_at(edge, add(other, gap))),
                       [setv(f"monster {axis}", V(f"next monster {axis}"))],
                       [if_(floor_at(edge, other),
                            setv("offset from middle", sub(add(floor_(other), 0.5), other)),
                            ifelse(lt(abs_(V("offset from middle")), abs_(step)),
                                   [setv(f"monster {other_axis}", add(floor_(other), 0.5))],
                                   [ifelse(gt(V("offset from middle"), 0), [chg(f"monster {other_axis}", abs_(step))],
                                           [chg(f"monster {other_axis}", mul(-1, abs_(step)))])]))]))]

def claim_my_square():
    """After moving: if I'm on a new square, give the old one back (0) and put my id on the new one."""
    return [setv("square to try", square_number(V("monster x"), V("monster y"))),
            if_(not_(eq(V("square to try"), V("my square"))),
                replace("monster on square", V("my square"), 0),
                replace("monster on square", V("square to try"), V("monster id")),
                setv("my square", V("square to try")))]

def step_toward(target_x, target_y, direction):
    """Walk one step toward (direction -1) or away from (+1) a point, at my speed."""
    return [setv("target offset x", sub(V("monster x"), target_x)),
            setv("target offset y", sub(V("monster y"), target_y)),
            setv("target distance", sqrt_(add(mul(V("target offset x"), V("target offset x")),
                                              mul(V("target offset y"), V("target offset y"))))),
            if_(gt(V("target distance"), 0.05),
                setv("step x", mul(div(V("target offset x"), V("target distance")),
                                   mul(mul(stat("speed"), V("speed multiplier")), direction))),
                setv("step y", mul(div(V("target offset y"), V("target distance")),
                                   mul(mul(stat("speed"), V("speed multiplier")), direction))),
                call("take a step"))]

monster.script(flag(), hide(), setv("is clone", 0),
         comment="The original Monster sprite never appears. It only makes clones.")
monster.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()),
         comment="CLEAR LEVEL: every monster clone deletes itself.")
def add_monster_clone():
    return [chg("monster id", 1),
            addto("monster x positions", add(item(V("monster id"), "monster start x"), 0.5)),
            addto("monster y positions", add(item(V("monster id"), "monster start y"), 0.5)),
            addto("monster alive flags", 1), clone()]
monster.script(recv(SPAWN),
         if_(eq(V("is clone"), 0), setv("monster id", 0),
             clear_list("monster x positions"), clear_list("monster y positions"), clear_list("monster alive flags"),
             repeat(length("monster start x"), *add_monster_clone())),
         comment="SPAWN: the original makes one clone per monster letter on the map.\n"
                 "Each clone copies 'monster id' at the moment it is made, so the\n"
                 "clones are numbered 1, 2, 3 ... It also adds a line for each one to\n"
                 "'monster x/y positions' and 'monster alive flags'.")
monster.script(recv(SUMMON),
         if_(eq(V("is clone"), 0),
             repeat(sub(length("monster start x"), V("monster id")), *add_monster_clone())),
         comment="SUMMON: a boss added monsters to the end of the start lists.\n"
                 "'monster id' still holds the last id handed out, so make clones\n"
                 "for the new entries only.")
monster.script(as_clone(), setv("is clone", 1),
         note("Look up my start square and my TYPE (1 imp, 2 spitter, 3 golem,\n"
              "4 warden). Everything else about me comes from the 'monster ...'\n"
              "lists, using my type as the item number.",
              setv("monster x", add(item(V("monster id"), "monster start x"), 0.5))),
         setv("monster y", add(item(V("monster id"), "monster start y"), 0.5)),
         setv("monster type", item(V("monster id"), "monster start type")),
         setv("monster name", stat("names")),
         note("MY WALL GAP: how close my middle may come to a wall. My picture is\n"
              "wider than a point, so without a gap half of me would sink into the\n"
              "wall. Bigger monsters keep a bigger gap: 0.3 squares at size 100.\n"
              "Never more than 0.45, so I still fit through a 1-square doorway.\n"
              "(The player keeps 0.25: see 'wall buffer' in the Engine.)",
              setv("my wall gap", mul(0.3, div(stat("size"), 100)))),
         if_(gt(V("my wall gap"), 0.45), setv("my wall gap", 0.45)),
         note("DIFFICULTY: start with the difficulty's percent of my type's health\n"
              "(easy 75, normal 100, hard 125), rounded. An imp has 3 normally:\n"
              "2 on easy, 4 on hard.",
              setv("full health", round_(mul(stat("health"),
                                             div(item(V("difficulty"), "difficulty monster health"), 100))))),
         setv("monster health", V("full health")),
         setv("is alive", 1), setv("attack cooldown", 0), setv("volley cooldown", 30), setv("pain flash timer", 0),
         setv("attack pose timer", 0), setv("is chasing", 0),
         setv("speed multiplier", 1), setv("charge state", 0), setv("charge cooldown", 30), setv("blink timer", 60),
         setv("has called for help", 0), setv("can see player", 0), setv("knows where player is", 0),
         note("Check my line of sight every 4 frames, not every frame (it takes a lot\n"
              "of blocks). Monsters start at different points of the 4, so they take\n"
              "turns.",
              setv("sight timer", mod(V("monster id"), 4))),
         note("Stand on my square, so no other monster walks into it.",
              setv("my square", square_number(V("monster x"), V("monster y")))),
         replace("monster on square", V("my square"), V("monster id")),
         note("Bigger monsters get deeper voices: the same sounds, pitched down.",
              set_sound_effect("PITCH", stat("voice pitch"))),
         costume("imp walk 1", join(V("monster name"), " walk 1")), cleareffects(), hide(),
         comment="NEW CLONE: set myself up from the monster type lists.")

x_part = step_along("x", "y", V("step x"))
monster.script(Def("take a step"),
         note("Try the x part of the step, then the y part, so I slide along walls.\n"
              "My body is a square, 'my wall gap' out from my middle each way. To move:\n"
              "- both corners of my FRONT EDGE must stay on floor, so my picture never\n"
              "  sinks into a wall. If just one corner is blocked (a wall corner, or a\n"
              "  doorway I'm not lined up with), I slide toward the middle of my row\n"
              "  or column instead, and fit through next time;\n"
              "- no other monster may stand on the square my middle moves onto\n"
              "  ('monster on square'), so monsters queue up instead of piling on top\n"
              "  of each other. Wolfenstein 3D kept one thing per square too.",
              x_part[0]),
         *x_part[1:],
         *step_along("y", "x", V("step y")),
         *claim_my_square(), setv("moved this frame", 1),
         comment="TAKE A STEP: move by 'step x' and 'step y' if the squares are free.")

monster.script(Def("chase"),
         note("Where do I go? If I can SEE you, toward you (and remember where I saw\n"
              "you). If I can't, to the spot where I last saw you: usually the door\n"
              "or corner you went round, so I follow you instead of pushing against a\n"
              "wall. Once there, if you're gone, I wait.",
              ifelse(eq(V("can see player"), 1),
                     [setv("knows where player is", 1), setv("last seen x", V("player x")), setv("last seen y", V("player y")),
                      note("Come closer until I'm at my 'keep distance'. Spitters keep about 4\n"
                           "squares away, and back off if you rush them.",
                           if_(gt(V("distance to player"), stat("keep distance")), *step_toward(V("player x"), V("player y"), -1))),
                      if_(lt(V("distance to player"), sub(stat("keep distance"), 1.5)),
                          *step_toward(V("player x"), V("player y"), 1))],
                     [if_(eq(V("knows where player is"), 1),
                          *step_toward(V("last seen x"), V("last seen y"), -1),
                          if_(lt(V("target distance"), 0.3), setv("knows where player is", 0)))])),
         comment="CHASE: follow the player by sight, like the monsters in Wolfenstein 3D\nand Doom (they had no maps of the level either).")

monster.script(Def("check line of sight"),
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

monster.script(Def("fire volley"),
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

monster.script(Def("add up explosion damage"),
         *explosion_scan("monster x", "monster y",
                         if_(lt(V("distance to blast"), 2.6),
                             ifelse(lt(V("distance to blast"), 1.3), [chg("damage taken", EXPLOSION_DAMAGE_UP_CLOSE)],
                                    [chg("damage taken", EXPLOSION_DAMAGE_UP_CLOSE // 2)]))),
         comment="ADD UP EXPLOSION DAMAGE: check every explosion this frame.\n"
                 "IMPORTANT: loops live in 'run without screen refresh' custom blocks.\n"
                 "A loop in a broadcast script pauses until the next frame, and the\n"
                 "next frame's broadcast would RESTART the script before it finishes.")

monster.script(Def("charge at the player"),
    note("CHARGER. 'charge state': 0 = walking, 1 = winding up (head down, a\n"
         "warning!), 2 = charging in a straight line, 3 = stunned after\n"
         "slamming into a wall.",
         if_(gt(V("charge cooldown"), 0), chg("charge cooldown", -1))),
    if_(eq(V("charge state"), 0),
        if_(eq(V("is chasing"), 1), call("chase")),
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
                         "Hit a wall (or another monster) -> stunned. Reach you -> a big hit,\n"
                         "and the charge ends.",
                         setv("next monster x", add(V("monster x"), mul(V("charge direction x"), 0.17)))),
                    setv("next monster y", add(V("monster y"), mul(V("charge direction y"), 0.17))),
                    *body_is_clear(V("next monster x"), V("next monster y"),
                                   "Slam into the wall when my edge would touch it, not my middle."),
                    ifelse(eq(V("landing is clear"), 1),
                           [setv("monster x", V("next monster x")), setv("monster y", V("next monster y")),
                            *claim_my_square(), setv("moved this frame", 1)],
                           [setv("charge state", 3), setv("charge timer", 45), play("slam")]),
                    setv("offset x from player", sub(V("monster x"), V("player x"))),
                    *offset_from_player("monster x", "monster y")[1:],
                    if_(and_(eq(V("charge state"), 2), lt(V("distance to player"), 1)),
                        hurt_player(rnd(div(stat("claw damage"), 2), stat("claw damage"))),
                        setv("killer type", V("monster type")), setv("hurt flash timer", 6),
                        play("player hurt"), setv("charge state", 0), setv("charge cooldown", 60),
                        setv("attack pose timer", 10)),
                    chg("charge timer", -1),
                    if_(and_(eq(V("charge state"), 2), lt(V("charge timer"), 1)),
                        setv("charge state", 0), setv("charge cooldown", 50))],
                   [if_(eq(V("charge state"), 3), chg("charge timer", -1),
                        if_(lt(V("charge timer"), 1), setv("charge state", 0), setv("charge cooldown", 30)))])]),
    comment="CHARGE AT THE PLAYER: the charger's special move ('monster special\nmove' = charge).")

monster.script(Def("blink sideways"),
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
             *body_is_clear(V("next monster x"), V("next monster y"),
                            "Only land where all of me fits: not in a wall, not half in one, and\n"
                            "not on another monster's square."),
             if_(eq(V("landing is clear"), 1),
                 setv("monster x", V("next monster x")), setv("monster y", V("next monster y")),
                 *claim_my_square(), play("blink")),
             setv("blink timer", rnd(60, 120)))),
    comment="BLINK SIDEWAYS: the wraith's special move ('monster special move' = blink).")

monster.script(Def("call for help"),
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

monster.script(recv(UPDATE), if_(eq(V("is clone"), 1),
    note("DAMAGE: add up everything that hurts me this frame. A weapon hit does\n"
         "'hit damage' (rolled when you fired). An explosion does 6 up close,\n"
         "3 farther out.",
         setv("damage taken", 0)),
    if_(and_(eq(V("target hit id"), V("monster id")), eq(V("is alive"), 1)), chg("damage taken", V("hit damage"))),
    note("The developer console's 'kill' command: a hit nothing survives.",
         if_(eq(V("console kill"), 1), chg("damage taken", 9999))),
    call("add up explosion damage"),
    note("Take the damage. At 0 health I die and count as a kill. If I was the\n"
         "boss, the boss health bar goes away.",
         if_(and_(gt(V("damage taken"), 0), eq(V("is alive"), 1)),
             chg("monster health", mul(-1, V("damage taken"))), setv("pain flash timer", 4), setv("is chasing", 1),
             note("Hurt: now I know where you are.",
                  setv("knows where player is", 1)), setv("last seen x", V("player x")), setv("last seen y", V("player y")),
             ifelse(lt(V("monster health"), 1),
                    [setv("is alive", 0), costume("imp dead", join(V("monster name"), " dead")), cleareffects(),
                     note("A body doesn't block the way: give my square back.",
                          replace("monster on square", V("my square"), 0)),
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
             note("LOOK: every 4 frames, can I see you? (Only within 20 squares: farther\n"
                  "away doesn't matter.)",
                  chg("sight timer", -1)),
             if_(lt(V("sight timer"), 1), setv("sight timer", 4),
                 ifelse(lt(V("distance to player"), 20), [call("check line of sight"), setv("can see player", V("sight is clear"))],
                        [setv("can see player", 0)])),
             note("WAKE UP if I can SEE you within my 'wake distance', or you fire a shot\n"
                  "within 11 squares (I hear it through walls). Not in the first 1.5\n"
                  "seconds of a level, so you always get a moment to look around.",
                  if_(gt(V("level time"), 1.5),
                      if_(and_(eq(V("can see player"), 1), lt(V("distance to player"), stat("wake distance"))),
                          setv("is chasing", 1)),
                      if_(and_(eq(V("shot fired this frame"), 1), lt(V("distance to player"), 11)), setv("is chasing", 1)))),
             note("MOVE: chase you ('chase' block). Chargers use their own 'charge at the\n"
                  "player' block, which chases too.",
                  setv("moved this frame", 0)),
             ifelse(eq(stat("special move"), "charge"), [call("charge at the player")],
                    [if_(eq(V("is chasing"), 1), call("chase"))]),
             note("SPECIAL MOVES for wraiths (blink) and the colossus (rage).",
                  if_(eq(stat("special move"), "blink"), call("blink sideways"))),
             if_(and_(eq(stat("special move"), "rage"),
                      and_(eq(V("has called for help"), 0), lt(V("monster health"), div(V("full health"), 2)))),
                 call("call for help")),
             note("CLAW: when you're within 1.2 squares, hit you once a second\n"
                  "(30 frames) for half to all of my 'claw damage'.",
                  if_(gt(V("attack cooldown"), 0), chg("attack cooldown", -1))),
             if_(and_(and_(lt(V("distance to player"), 1.2), lt(V("attack cooldown"), 1)), eq(V("charge state"), 0)),
                 hurt_player(rnd(div(stat("claw damage"), 2), stat("claw damage"))),
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
                      setv("boss health", V("monster health")), setv("boss max health", V("full health")),
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
