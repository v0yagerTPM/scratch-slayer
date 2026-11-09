"""The Barrel sprite: barrels that explode when shot."""
from sb3extra import *
from game.config import *
import assets3
from game.screen_placement import explosion_scan, offset_from_player, place_on_screen
from game.stage import project

barrel = Target(project, "Barrel", layer=2, visible=False)
barrel.costume("barrel", assets3.BARREL, 20, 52)
for frame_number, art in enumerate(assets3.EXPLOSIONS, start=1):
    barrel.costume(f"explosion {frame_number}", art, 45, 78)
add_sound(barrel, "explosion", assets3.explosion)
for name in ["barrel id", "is clone", "barrel x", "barrel y", "barrel state", "fuse timer", "blast frame",
             "blast damage", "explosion number", "distance to blast", "offset x from player", "offset y from player",
             "distance to player", "sideways in view", "depth in view", "screen x", "screen column index"]:
    barrel.var(name)
barrel.script(flag(), hide(), setv("is clone", 0),
          comment="Barrels. 'barrel state': 0 = sitting there, 1 = about to blow\n"
                  "(fuse lit), 2 = exploding, 3 = gone.")
barrel.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()))
barrel.script(recv(SPAWN),
          if_(eq(V("is clone"), 0), setv("barrel id", 0), repeat(length("barrel start x"), chg("barrel id", 1), clone())),
          comment="SPAWN: one clone per E on the map.")
barrel.script(as_clone(), setv("is clone", 1),
          setv("barrel x", add(item(V("barrel id"), "barrel start x"), 0.5)),
          setv("barrel y", add(item(V("barrel id"), "barrel start y"), 0.5)),
          setv("barrel state", 0), costume("barrel"), hide())
barrel.script(Def("check nearby explosions"),
          *explosion_scan("barrel x", "barrel y",
                          if_(and_(eq(V("barrel state"), 0), lt(V("distance to blast"), 2.2)),
                              setv("barrel state", 1), setv("fuse timer", 5))),
          comment="CHECK NEARBY EXPLOSIONS: any blast within 2.2 squares lights my fuse.\n"
                  "(A loop, so it lives in a 'run without screen refresh' block.)")

barrel.script(recv(UPDATE), if_(and_(eq(V("is clone"), 1), lt(V("barrel state"), 3)),
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
                     hurt_player(V("blast damage")), setv("hurt flash timer", 6),
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
