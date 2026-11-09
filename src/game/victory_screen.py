"""The animated victory screen and fireworks."""
from sb3extra import *
from game.config import *
import assets4, assets5, assets6
from game.monster import MONSTER_ART
from game.death_screen import on_win
from game.stage import project, stage

stage.script(recv(SHOW_WIN), backdrop("victory sky"), cleareffects(),
             comment="VICTORY BACKDROP: dawn over the fortress.", canvas_x=1300)

victory_logo = Target(project, "Victory Logo", layer=22, visible=False)
victory_logo.costume("victory", assets6.VICTORY_LOGO, *assets5.VICTORY_CENTER)
add_sound(victory_logo, "thud", assets4.thud)
for name in ["fall speed", "bounces", "logo time"]:
    victory_logo.var(name)
victory_logo.script(flag(), hide())
victory_logo.script(recv(SHOW_WIN), gotoxy(0, 175), setv("fall speed", 0), setv("bounces", 0), setv("logo time", 0),
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

victory_monsters = Target(project, "Victory Monsters", layer=21, visible=False)
for monster_name, art in MONSTER_ART.items():
    victory_monsters.costume(f"{monster_name} dead", art[3], 40, 120)
victory_monsters.lst("fallen types", [2, 6, 7, 5, 1])
victory_monsters.lst("fallen x", [-185, -100, 5, 105, 185])
victory_monsters.lst("fallen y", [-48, -52, -46, -50, -48])
victory_monsters.lst("fallen size", [100, 100, 150, 120, 95])
for name in ["is clone", "fallen slot"]:
    victory_monsters.var(name)
victory_monsters.script(flag(), hide(), setv("is clone", 0))
victory_monsters.script(recv(SHOW_WIN), if_(eq(V("is clone"), 0), setv("fallen slot", 0),
          repeat(length("fallen types"), chg("fallen slot", 1), clone())),
          comment="The defeated monsters, one clone per entry in the 'fallen' lists.")
victory_monsters.script(as_clone(), setv("is clone", 1),
          costume("imp dead", join(item(item(V("fallen slot"), "fallen types"), "monster names"), " dead")),
          gotoxy(item(V("fallen slot"), "fallen x"), item(V("fallen slot"), "fallen y")),
          setsize(item(V("fallen slot"), "fallen size")), seteffect("GHOST", 100), show(), wait(0.4),
          repeat(12, change_effect("GHOST", -8.4)), wait_until(not_(on_win)), delete_clone())

victory_stats = Target(project, "Victory Stats", layer=20, visible=False)
victory_stats.costume("stats panel", assets5.STATS_PANEL, 150, 38)
victory_stats.script(flag(), hide())
victory_stats.script(recv(SHOW_WIN), gotoxy(0, -95), seteffect("GHOST", 100), show(), go_back(), wait(1),
          repeat(10, change_effect("GHOST", -10)), wait_until(not_(on_win)), hide(),
          comment="STATS PANEL: labels only. The numbers are Digits slots 7, 10 and 11.\n"
                  "'go to back' keeps it behind the digits and fireworks.")

fireworks = Target(project, "Fireworks", layer=19, visible=False)
fireworks.costume("rocket", assets5.ROCKET, 4, 9)
for name, art in assets5.SPARKS.items():
    fireworks.costume(f"spark {name}", art, 6, 6)
add_sound(fireworks, "pop", assets5.firework_pop)
fireworks.lst("spark colors", list(assets5.SPARKS))
for name in ["is clone", "role", "speed x", "speed y", "frames left", "spark color", "spark number"]:
    fireworks.var(name)
fireworks.script(flag(), hide(), setv("is clone", 0))
fireworks.script(recv(SHOW_WIN), if_(eq(V("is clone"), 0), wait(0.8), setv("role", 1), clone(),
          until(not_(on_win), if_(lt(rnd(1, 100), 4), setv("role", 1), clone()), wait(0))),
          comment="LAUNCHER: about one rocket a second. role 1 = rocket, role 2 = spark.")
fireworks.script(as_clone(), setv("is clone", 1),
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
