"""The animated death screen."""
from sb3extra import *
from game.config import *
import pictures.death_screen, pictures.world, sounds.monsters, sounds.music, sounds.screens
from game.monster import MONSTER_ART
from game.stage import project
from game.title_screen import prompt_text

on_death = eq(V("screen showing"), DIED)
on_win = eq(V("screen showing"), WIN)

def pulse_prompt(hat, prompt_costume, stage_y, delay, condition):
    prompt_text.script(recv(hat), costume(prompt_costume), gotoxy(0, stage_y), setv("pulse time", 0), seteffect("GHOST", 100),
              show(), front(), wait(delay),
              until(not_(condition), chg("pulse time", 1),
                    seteffect("GHOST", mul(35, add(1, sin_(mul(V("pulse time"), 8))))), front()),
              hide())
pulse_prompt(SHOW_DEATH, "press space retry", -158, 1.4, on_death)
pulse_prompt(SHOW_WIN, "green flag again", -157, 2.2, on_win)
prompt_text.script(recv(SHOW_WIN), set_volume(mul(V("music is on"), 100)), until(not_(on_win), play_until_done("victory theme")),
          comment="VICTORY MUSIC: an original loop that plays until the green flag.")

death_overlay = Target(project, "Death Overlay", layer=17, visible=False)
death_overlay.costume("blood red", pictures.death_screen.DEATH_OVERLAY, 240, 180)
death_overlay.script(flag(), hide())
death_overlay.script(recv(SHOW_DEATH), gotoxy(0, 0), seteffect("GHOST", 100), show(), front(),
          note("The frozen game fades to blood red (ghost 100 -> 10).",
               repeat(15, change_effect("GHOST", -6))),
          wait_until(not_(on_death)), hide(),
          comment="DEATH OVERLAY: a red vignette over the last frame of the game.")

blood_drips = Target(project, "Blood Drips", layer=18, visible=False)
blood_drips.costume("drop", pictures.death_screen.BLOOD_DROP, 5, 10)
for name in ["is clone", "fall speed"]:
    blood_drips.var(name)
blood_drips.script(flag(), hide(), setv("is clone", 0))
blood_drips.script(recv(SHOW_DEATH), if_(eq(V("is clone"), 0),
          until(not_(on_death), if_(lt(rnd(1, 100), 14), clone()), wait(0))),
          comment="EMITTER: about 1 frame in 7, start a new drop at the top.")
blood_drips.script(as_clone(), setv("is clone", 1), gotoxy(rnd(-230, 230), 176), setsize(rnd(60, 130)),
          setv("fall speed", 0), show(), front(),
          until(or_(lt(ypos(), -172), not_(on_death)),
                note("Gravity: each frame the drop falls a little faster.",
                     chg("fall speed", 0.25)), change_y(mul(-1, V("fall speed")))),
          delete_clone(),
          comment="DROP: slide down the screen, speeding up, then vanish.")

death_killer = Target(project, "Death Killer", layer=19, visible=False)
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        death_killer.costume(f"{monster_name} {pose}", svg_art, 40, 120)
for frame_number, art in enumerate(pictures.world.EXPLOSIONS, start=1):
    death_killer.costume(f"explosion {frame_number}", art, 45, 78)
add_sound(death_killer, "pain", sounds.monsters.monster_pain)
for name in ["anim time", "pose timer", "base y"]:
    death_killer.var(name)
death_killer.script(flag(), hide())
death_killer.script(recv(SHOW_DEATH),
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

death_heading = Target(project, "Death Heading", layer=20, visible=False)
death_heading.costume("you died", pictures.death_screen.YOU_DIED, *pictures.death_screen.YOU_DIED_CENTER)
for sound_name, make_sound in (("thud", sounds.screens.thud), ("death sting", sounds.music.death_sting)):
    add_sound(death_heading, sound_name, make_sound)
death_heading.var("throb time")
death_heading.script(flag(), hide())
death_heading.script(recv(SHOW_DEATH), setsize(260), seteffect("GHOST", 100), gotoxy(0, 118), show(), front(), wait(0.3),
          note("SLAM: shrink from huge while fading in, then thud and shake.",
               repeat(8, change_size(-20), change_effect("GHOST", -12.5), front())),
          play("thud"), play("death sting"),
          repeat(8, gotoxy(rnd(-6, 6), add(118, rnd(-6, 6)))), gotoxy(0, 118), setv("throb time", 0),
          until(not_(on_death), chg("throb time", 1),
                note("Throb slowly, like a heartbeat.",
                     setsize(add(100, mul(2, sin_(mul(V("throb time"), 5)))))), front()),
          hide(),
          comment="YOU DIED heading.")

death_message = Target(project, "Death Message", layer=21, visible=False)
death_message.costume("killed by monster", pictures.death_screen.KILLED_BY["monster"], 220, 25)
for name, art in pictures.death_screen.KILLED_BY.items():
    if name != "monster":
        death_message.costume(f"killed by {name}", art, 220, 25)
death_message.script(flag(), hide())
death_message.script(recv(SHOW_DEATH),
          note("'killed by <name>' + a tip for that enemy. A monster you add with\n"
               "no costume here gets the general 'killed by monster' one.",
               costume("killed by monster")), costume("killed by monster", join("killed by ", V("killer name"))),
          gotoxy(0, -118), seteffect("GHOST", 100), show(), front(), wait(1),
          repeat(10, change_effect("GHOST", -10)),
          until(not_(on_death), front()), hide(),
          comment="KILLED BY ... and a tip for beating that enemy next time.")
