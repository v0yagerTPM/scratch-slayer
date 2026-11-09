"""What's drawn over the 3D view: the weapon, crosshair, HUD, arms panel, boss bar,
messages, the results screen and the HUD digits."""
from sb3extra import *
from game.config import *
import assets, assets2, assets6, assets7
from game.stage import HUD_SLOTS, project

playing = eq(V("screen showing"), NONE)

weapon = Target(project, "Weapon", layer=3, x=0, y=-190, size=105, visible=False)
WEAPON_COSTUMES = {"shotgun": (assets.GUN_IDLE, assets.GUN_FIRE), **assets6.WEAPON_ART}
for weapon_name in assets6.WEAPON_NAMES:
    ready, firing = WEAPON_COSTUMES[weapon_name]
    weapon.costume(f"{weapon_name} ready", ready, 80, 190)
    weapon.costume(f"{weapon_name} firing", firing, 80, 190)
    weapon.costume(f"{weapon_name} firing 2", assets6.CHAINGUN_FIRE_2 if weapon_name == "chaingun" else firing, 80, 190)
for sound_name, make_sound in (("shotgun", assets.shotgun), ("fist", assets2.punch), ("pistol", assets6.pistol),
               ("chaingun", assets6.chaingun), ("rocket launcher", assets6.rocket_launch)):
    add_sound(weapon, sound_name, make_sound)
for name in ["weapon name", "firing pose timer", "flash number", "jab amount"]:
    weapon.var(name)
weapon.script(flag(), costume("pistol ready"), setsize(105), gotoxy(0, -190), setv("firing pose timer", 0), hide())
weapon.script(recv(DRAW_HUD), ifelse(playing,
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
weapon.script(recv(FIRE), play_named("pistol", item(V("current weapon"), "weapon names")),
          setv("firing pose timer", 2), chg("flash number", 1),
          comment="FIRE: the sound named after the weapon + 2 frames of muzzle flash.")
weapon.script(recv(PUNCH), play("fist"), setv("firing pose timer", 5),
          comment="PUNCH: the fist jabs forward for 5 frames.")

crosshair = Target(project, "Crosshair", layer=4, visible=False)
crosshair.costume("crosshair", assets.CROSSHAIR, 10, 10)
crosshair.script(flag(), gotoxy(0, 0), hide())
crosshair.script(recv(DRAW_HUD), ifelse(playing, [show(), front()], [hide()]),
         comment="Always in the exact middle: the column the shot checks.")

hud = Target(project, "HUD", layer=5, visible=False)
for keys_held, art in enumerate(assets6.HUDS):   # keys held = red + 2 x blue + 4 x skull
    hud.costume(f"keys {keys_held}", art, 240, 180)
hud.script(flag(), gotoxy(0, 0), hide())
hud.script(recv(DRAW_HUD), ifelse(playing,
          [costume("keys 0", join("keys ", add(add(V("has red key"), mul(V("has blue key"), 2)),
                                               mul(V("has skull key"), 4)))), show(), front()],
          [hide()]),
          comment="HUD frame: the HEALTH label, the sprint bar frame and the key slots.\n"
                  "Costume number = red key (1) + blue key (2) + skull key (4), so\n"
                  "'keys 0' = no keys ... 'keys 7' = all three. Like binary!\n"
                  "The Digits sprite draws the numbers.")

arms_panel = Target(project, "Arms Panel", layer=5, visible=False)
for (owned_code, weapon_slot), art in assets6.ARMS.items():
    arms_panel.costume(f"arms {owned_code} {weapon_slot}", art, 240, 180)
arms_panel.script(flag(), gotoxy(0, 0), hide())
arms_panel.script(recv(DRAW_HUD), ifelse(playing,
          [costume("arms 0 2", joins("arms ", add(add(item(3, "weapons owned"), mul(item(4, "weapons owned"), 2)),
                                                    mul(item(5, "weapons owned"), 4)),
                                     " ", V("current weapon"))), show(), front()],
          [hide()]),
          comment="ARMS PANEL: the ammo box label and the 1-5 weapon row.\n"
                  "Costume 'arms <owned> <holding>': <owned> adds 1 for the shotgun,\n"
                  "2 for the chaingun, 4 for the rocket launcher (the same binary\n"
                  "trick as the HUD's keys); <holding> = the weapon in your hands.")

boss_bar = Target(project, "Boss Bar", layer=5, visible=False)
for boss_name, art in assets6.BOSS_BARS.items():
    boss_bar.costume(f"boss bar {boss_name}", art, 240, 180)
boss_bar.script(flag(), gotoxy(0, 0), hide())
boss_bar.script(recv(DRAW_HUD), ifelse(and_(playing, and_(eq(V("boss is awake"), 1), gt(V("boss health"), 0))),
          [costume("boss bar warden", join("boss bar ", V("boss name"))), show(), front()], [hide()]),
          comment="BOSS BAR: the frame and name. The red health line inside it is\n"
                  "drawn with the pen at the end of 'draw 3D view'.")

message = Target(project, "Message", layer=6, visible=False)
for name, art in assets2.MESSAGES.items():
    message.costume(f"message {name}", art, 240, 180)
message.script(flag(), gotoxy(0, 0), hide())
message.script(recv(DRAW_HUD), ifelse(and_(playing, gt(V("message timer"), 0)),
         [costume("message door hint", join("message ", V("message name"))),
          show(), front(), chg("message timer", -1)],
         [hide()]),
         comment="MESSAGES at the top of the screen. Anything can show one:\n"
                 "set 'message name' (it picks the costume 'message <name>') and\n"
                 "'message timer' (how many frames it stays up).")

screens = Target(project, "Screens", layer=7, visible=True)
for costume_name, art in assets7.TALLY_SCREENS.items():
    screens.costume(costume_name, art, 240, 180)
screens.var("screen costume name"); screens.var("under par ending")
screens.script(flag(), gotoxy(0, 0), hide())
screens.script(recv(DRAW_HUD),
         ifelse(eq(V("screen showing"), COMPLETE),
                [note("Level 3 ends episode 1, so it gets its own heading. Then add\n"
                      "' under par' to the costume name if you beat the par time.",
                      ifelse(eq(V("current level"), 3), [setv("screen costume name", "screen episode complete")],
                             [setv("screen costume name", "screen level complete")])),
                 ifelse(eq(V("par was beaten"), 1), [setv("under par ending", " under par")],
                        [setv("under par ending", "")]),
                 costume("screen level complete", join(V("screen costume name"), V("under par ending"))),
                 show(), front()], [hide()]),
         comment="LEVEL COMPLETE page: the tally. The labels, % signs and clock\n"
                 "colons are in the costume; the Digits sprite draws the numbers.\n"
                 "(The death and victory screens have their own animated sprites.)")

digits = Target(project, "Digits", layer=8, visible=False)
for digit_character, art in assets2.DIGITS.items():
    digits.costume(f"digit {digit_character}", art, 21, 14)
for name in ["is clone", "number slot", "digit place", "number text"]:
    digits.var(name)
digits.script(flag(), hide(), setv("is clone", 0), setv("number slot", 0),
          repeat(HUD_SLOTS, chg("number slot", 1), setv("digit place", 0), repeat(3, chg("digit place", 1), clone())),
          comment=f"Makes {HUD_SLOTS * 3} clones = {HUD_SLOTS} numbers x 3 digits each.\n"
                  "'number slot' = which number (see 'HUD number values').\n"
                  "'digit place' = 1 for the ones digit, 2 tens, 3 hundreds.")
digits.script(as_clone(), setv("is clone", 1))
digits.script(recv(DRAW_NUMBERS), if_(eq(V("is clone"), 1),
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
