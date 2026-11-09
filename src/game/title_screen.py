"""The animated title screen."""
from sb3extra import *
from game.config import *
import assets, assets4, assets5
from game.monster import MONSTER_ART
from game.stage import project, stage

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
                     "'title sky' backdrop. It switches back to black for the game.", canvas_x=1300)

title_logo = Target(project, "Title Logo", layer=12, visible=False)
title_logo.costume("logo", assets4.LOGO, 220, 67)
add_sound(title_logo, "thud", assets4.thud)
for name in ["fall speed", "bounces", "logo time", "shake timer"]:
    title_logo.var(name)
title_logo.script(flag(), hide())
title_logo.script(recv(SHOW_TITLE),
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

title_monster = Target(project, "Title Monster", layer=10, visible=False)
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        title_monster.costume(f"{monster_name} {pose}", svg_art, 40, 120)
add_sound(title_monster, "pain", assets.monster_pain)
title_monster.lst("lineup types", [3, 6, 4, 5, 1])
title_monster.lst("lineup x", [-175, -92, 0, 92, 178])
title_monster.lst("lineup y", [-98, -106, -80, -102, -90])
title_monster.lst("lineup size", [118, 100, 140, 108, 90])
for name in ["is clone", "lineup slot", "monster type", "monster name", "target x", "base y", "anim time",
             "pose timer", "has arrived"]:
    title_monster.var(name)
title_monster.script(flag(), hide(), setv("is clone", 0))
title_monster.script(recv(SHOW_TITLE),
          if_(eq(V("is clone"), 0), setv("lineup slot", 0),
              repeat(length("lineup types"), chg("lineup slot", 1), clone())),
          comment="One clone per entry in the 'lineup' lists (this sprite's own lists).\n"
                  "Type numbers match the 'monster ...' lists: 1 imp, 2 spitter,\n3 golem, 4 warden, 5 charger, 6 wraith, 7 colossus.")
title_monster.script(as_clone(), setv("is clone", 1),
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

title_embers = Target(project, "Title Embers", layer=11, visible=False)
title_embers.costume("ember", assets4.EMBER, 7, 7)
for name in ["is clone", "rise speed", "drift phase"]:
    title_embers.var(name)
ember_time = or_(on_title, eq(V("card is up"), 1))
title_embers.script(flag(), hide(), setv("is clone", 0))
for hat in (SHOW_TITLE, SHOW_CARD):
    title_embers.script(recv(hat), if_(eq(V("is clone"), 0),
                             until(not_(ember_time), if_(lt(rnd(1, 100), 28), clone()), wait(0))),
              comment="EMITTER: on about 1 frame in 4, make a new ember clone.")
title_embers.script(as_clone(), setv("is clone", 1),
          gotoxy(rnd(-235, 235), -175), setsize(rnd(30, 100)), seteffect("GHOST", rnd(0, 30)),
          setv("rise speed", rnd(1.2, 3.5)), setv("drift phase", rnd(0, 360)), show(),
          until(or_(gt(ypos(), 170), not_(ember_time)),
                change_y(V("rise speed")),
                change_x(mul(sin_(add(V("drift phase"), mul(ypos(), 2))), 0.7)),
                change_effect("GHOST", 0.7)),
          delete_clone(),
          comment="EMBER: float up at my own speed, wobble with sin(), fade out.")

prompt_text = Target(project, "Prompt Text", layer=13, visible=False)
prompt_text.costume("press space", assets4.PRESS_SPACE, 150, 20)
prompt_text.costume("press space retry", assets5.PROMPT_RETRY, 135, 15)
prompt_text.costume("green flag again", assets5.PROMPT_AGAIN, 213, 15)
add_sound(prompt_text, "victory theme", assets5.victory_theme)
add_sound(prompt_text, "title theme", assets4.title_riff)
prompt_text.var("pulse time")
prompt_text.script(flag(), hide())
prompt_text.script(recv(SHOW_TITLE), costume("press space"), gotoxy(0, -110), setv("pulse time", 0), seteffect("GHOST", 100), show(), wait(1.4),
          until(not_(on_title),
                chg("pulse time", 1),
                note("Pulse between solid and 70 percent see-through.",
                     seteffect("GHOST", mul(35, add(1, sin_(mul(V("pulse time"), 8)))))),
                if_(eq(V("options open"), 0), front())),
          hide(),
          comment="PRESS SPACE TO START, pulsing.")
prompt_text.script(recv(APPLY_MUSIC), set_volume(mul(V("music is on"), 100)),
          comment="MUSIC ON/OFF: volume 100 or 0. Changing the volume also affects a\nsound that's already playing.")
prompt_text.script(recv(SHOW_TITLE), set_volume(mul(V("music is on"), 100)), until(not_(on_title), play_until_done("title theme")),
          comment="TITLE MUSIC: an original 6-second riff that loops (the Engine stops\nit when you press SPACE).")
