"""The level intro cards."""
from sb3extra import *
from game.config import *
import pictures.lettering, pictures.level_cards, sounds.monsters, sounds.screens
from game.monster import MONSTER_ART
from game.stage import project

card_up = eq(V("card is up"), 1)

card_background = Target(project, "Card Background", layer=14, visible=False)
card_background.costume("card next level", pictures.level_cards.CARD_NEXT, 240, 180)
for level_number, art in enumerate(pictures.level_cards.CARD_ART, start=1):
    card_background.costume(f"card {level_number}", art, 240, 180)
card_background.script(flag(), hide())
card_background.script(recv(SHOW_CARD),
          note("Pick 'card N' for this level. If there isn't one (a level you\n"
               "added), Scratch keeps 'card next level'.",
               costume("card next level")), costume("card next level", join("card ", V("current level"))),
          gotoxy(0, 0), seteffect("GHOST", 100), show(), go_back(),
          note("Fade in, wait until the Engine takes the card down, fade out.",
               repeat(10, change_effect("GHOST", -10))),
          wait_until(not_(card_up)), repeat(6, change_effect("GHOST", 17)), hide(),
          comment="LEVEL CARD background: name, goal and the new enemy's description.")

card_heading = Target(project, "Card Heading", layer=15, visible=False)
card_heading.costume("heading next level", pictures.level_cards.HEADING_NEXT, pictures.lettering.text_width("NEXT LEVEL", 8) // 2 + 6, 35)
for level_number, art in enumerate(pictures.level_cards.HEADINGS, start=1):
    card_heading.costume(f"heading {level_number}", art, pictures.lettering.text_width(f"LEVEL {level_number}", 8) // 2 + 6, 35)
add_sound(card_heading, "thud", sounds.screens.thud)
card_heading.script(flag(), hide())
card_heading.script(recv(SHOW_CARD),
          costume("heading next level"), costume("heading next level", join("heading ", V("current level"))),
          setsize(260), seteffect("GHOST", 100), gotoxy(0, 122), show(), front(), wait(0.25),
          note("SLAM: shrink from huge to normal while fading in, then thud and\nshake the heading.",
               repeat(8, change_size(-20), change_effect("GHOST", -12.5), front())),
          play("thud"), repeat(8, gotoxy(rnd(-6, 6), add(122, rnd(-6, 6)))), gotoxy(0, 122),
          wait_until(not_(card_up)), repeat(6, change_effect("GHOST", 17)), hide(),
          comment="LEVEL N heading.")

card_monster = Target(project, "Card Monster", layer=16, visible=False)
for monster_name, art in MONSTER_ART.items():
    for pose, svg_art in zip(("walk 1", "walk 2", "attack", "dead"), art):
        card_monster.costume(f"{monster_name} {pose}", svg_art, 40, 120)
add_sound(card_monster, "pain", sounds.monsters.monster_pain)
for name in ["is clone", "card role", "monster type", "monster name", "base y", "anim time", "pose timer",
             "has arrived"]:
    card_monster.var(name)
card_monster.script(flag(), hide(), setv("is clone", 0))
card_monster.script(recv(SHOW_CARD), if_(eq(V("is clone"), 0),
          note("Role 1 = the level's new enemy ('level intro monster').\n"
               "Role 2 = a boss waiting in the background ('level intro boss').",
               setv("monster type", item(V("current level"), "level intro monster"))),
          if_(not_(eq(V("monster type"), "")), setv("card role", 1), clone()),
          setv("monster type", item(V("current level"), "level intro boss")),
          if_(gt(V("monster type"), 0), setv("card role", 2), clone())))
card_monster.script(as_clone(), setv("is clone", 1),
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
