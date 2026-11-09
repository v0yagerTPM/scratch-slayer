"""The Projectile sprite: acid, fireballs, plasma and rockets."""
from sb3extra import *
from game.config import *
import pictures.world, sounds.world
from game.screen_placement import offset_from_player, place_on_screen
from game.stage import project

projectile = Target(project, "Projectile", layer=2, visible=False)
projectile.costume("shot acid", pictures.world.ACID_SHOT, 13, 13)
projectile.costume("shot fire", pictures.world.FIRE_SHOT, 15, 15)
projectile.costume("shot plasma", pictures.world.PLASMA_SHOT, 15, 15)
projectile.costume("shot rocket", pictures.world.ROCKET_SHOT, 13, 13)
for frame_number, art in enumerate(pictures.world.EXPLOSIONS, start=1):
    projectile.costume(f"explosion {frame_number}", art, 45, 78)
add_sound(projectile, "player hurt", sounds.world.player_hurt)
add_sound(projectile, "explosion", sounds.world.explosion)
for name in ["is clone", "queue position", "shot x", "shot y", "shot speed x", "shot speed y", "shot damage",
             "shot look", "shot owner", "frames left", "offset x from player", "offset y from player", "distance to player",
             "sideways in view", "depth in view", "screen x", "screen column index",
             "is exploding", "blast frame", "blast damage", "draw height", "previous x", "previous y",
             "monster number", "distance to monster", "rocket hit something"]:
    projectile.var(name)
projectile.script(flag(), hide(), setv("is clone", 0))
projectile.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()))
projectile.script(Def("launch new shots"),
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

projectile.script(Def("check rocket hits"),
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

projectile.script(Def("explode rocket"),
    note("BOOM, one step back from whatever I hit. The explosion goes in the\n"
         "same 'new explosion' lists barrels use, so monsters and barrels\n"
         "nearby get hurt next frame. Too close to YOU hurts you too.",
         setv("shot x", V("previous x"))), setv("shot y", V("previous y")),
    addto("new explosion x", V("shot x")), addto("new explosion y", V("shot y")),
    *offset_from_player("shot x", "shot y"),
    if_(lt(V("distance to player"), 2.6),
        setv("blast damage", round_(mul(35, sub(1, div(V("distance to player"), 2.6))))),
        hurt_player(V("blast damage")), setv("hurt flash timer", 6), setv("killer type", -1)),
    play("explosion"), setv("is exploding", 1), setv("blast frame", 0), setv("draw height", -180),
    costume("explosion 1"),
    comment="EXPLODE ROCKET: turn this rocket into an explosion.")

projectile.script(recv(UPDATE), ifelse(eq(V("is clone"), 0),
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
                             hurt_player(V("shot damage")), setv("hurt flash timer", 5),
                             setv("killer type", V("shot owner")), play("player hurt"), delete_clone())])]),
         *offset_from_player("shot x", "shot y"),
         *place_on_screen([], "shot", height=V("draw height")))]),
    comment="PROJECTILES: acid (spitters), fireballs (warden), plasma (colossus)\n"
            "and YOUR rockets. The 'shot look' picks the costume.")
projectile.script(as_clone(), setv("is clone", 1), setv("frames left", 150), setv("is exploding", 0),
          ifelse(eq(V("shot look"), "rocket"), [setv("draw height", -70)], [setv("draw height", -50)]),
          costume("shot acid", join("shot ", V("shot look"))), hide())
