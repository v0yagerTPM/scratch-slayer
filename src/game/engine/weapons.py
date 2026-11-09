"""Firing weapons, switching weapons, and ammo."""
from sb3extra import *
from game.config import *
from game.engine.sprite import engine

engine.script(Def("fire current weapon"),
    note("Which ammo does this weapon use? 0 = none (fists), otherwise an item\n"
         "number in 'ammo counts' (1 bullets, 2 shells, 3 rockets).",
         setv("weapon ammo slot", item(V("current weapon"), "weapon ammo slots"))),
    ifelse(or_(eq(V("weapon ammo slot"), 0), gt(item(V("weapon ammo slot"), "ammo counts"), 0)),
           [note("FIRE: spend one round, start the reload, and copy this weapon's numbers\n"
                 "from the 'weapon ...' lists. 'hit damage' is rolled now; the monster\n"
                 "in the crosshair takes it next frame. 'aim width' > 1 = easier to hit\n"
                 "(the shotgun's spread).",
                 if_(gt(V("weapon ammo slot"), 0),
                     replace("ammo counts", V("weapon ammo slot"), sub(item(V("weapon ammo slot"), "ammo counts"), 1)))),
            setv("shot cooldown", item(V("current weapon"), "weapon reload frames")),
            setv("shot fired this frame", 1), setv("closest target depth", 999), setv("shot target id", 0),
            setv("shot range", item(V("current weapon"), "weapon ranges")),
            setv("hit damage", rnd(item(V("current weapon"), "weapon damage min"), item(V("current weapon"), "weapon damage max"))),
            setv("aim width", item(V("current weapon"), "weapon aim widths")),
            note("ROCKETS aren't instant: the launcher adds a rocket to the 'new shot'\n"
                 "lists (owner 0 = you) and the Projectile sprite flies it. Its range\n"
                 "is 0, so nothing is hit instantly.",
                 if_(eq(V("current weapon"), 5),
                     addto("new shot x", add(V("player x"), mul(V("look direction x"), 0.4))),
                     addto("new shot y", add(V("player y"), mul(V("look direction y"), 0.4))),
                     addto("new shot speed x", mul(V("look direction x"), 0.3)),
                     addto("new shot speed y", mul(V("look direction y"), 0.3)),
                     addto("new shot damage", 0), addto("new shot look", "rocket"), addto("new shot owner", 0))),
            ifelse(eq(V("current weapon"), 1), [bcast(PUNCH)], [bcast(FIRE)])],
           [note("OUT OF AMMO: switch to the best weapon that still has some.",
                 call("pick best weapon")),
            setv("message name", "out of ammo"), setv("message timer", 45)]),
    comment="FIRE CURRENT WEAPON: runs when you press SPACE and the weapon is ready.\n"
            "Every weapon works the same way; their differences are just numbers\n"
            "in the 'weapon ...' lists on the Stage (try changing them!).")

engine.script(Def("pick best weapon"),
    note("Try slot 5, then 4, 3, 2. The first one you own that has ammo wins.\n"
         "If none do, you're down to your fists (slot 1).",
         setv("current weapon", 1)), setv("weapon to try", 5),
    repeat(4,
           setv("weapon ammo slot", item(V("weapon to try"), "weapon ammo slots")),
           if_(and_(and_(eq(V("current weapon"), 1), eq(item(V("weapon to try"), "weapons owned"), 1)),
                    gt(item(V("weapon ammo slot"), "ammo counts"), 0)),
               setv("current weapon", V("weapon to try"))),
           chg("weapon to try", -1)),
    setv("weapon switch timer", 8),
    comment="PICK BEST WEAPON: like Doom, switch away from an empty gun.")

engine.script(Def("remember ammo at level start"),
    *[replace("ammo at level start", ammo_slot, item(ammo_slot, "ammo counts")) for ammo_slot in range(1, len(AMMO) + 1)],
    comment="REMEMBER AMMO AT LEVEL START: so dying gives this level's ammo back.")

engine.script(Def("restore ammo at level start"),
    *[replace("ammo counts", ammo_slot, item(ammo_slot, "ammo at level start")) for ammo_slot in range(1, len(AMMO) + 1)],
    if_(lt(item(1, "ammo counts"), START_BULLETS), replace("ammo counts", 1, START_BULLETS)),
    comment="RESTORE AMMO AT LEVEL START: after dying. You always get at least\n"
            f"{START_BULLETS} bullets back so the pistol works.")

engine.script(Def("give level select weapons"),
    note("Own every weapon from slot 3 up to 'level select best weapon' for\n"
         "the chosen level, with some ammo for each.",
         setv("weapon to try", 3)),
    repeat(3, if_(not_(gt(V("weapon to try"), item(V("current level"), "level select best weapon"))),
                  replace("weapons owned", V("weapon to try"), 1)),
           chg("weapon to try", 1)),
    replace("ammo counts", 1, 120),
    if_(eq(item(3, "weapons owned"), 1), replace("ammo counts", 2, 24)),
    if_(eq(item(5, "weapons owned"), 1), replace("ammo counts", 3, 8)),
    setv("current weapon", item(V("current level"), "level select best weapon")),
    call("remember ammo at level start"),
    comment="GIVE LEVEL SELECT WEAPONS: starting part-way through the game.")

engine.script(Def("switch music"),
    setv("music is on", sub(1, V("music is on"))), bcast(APPLY_MUSIC),
    ifelse(eq(V("music is on"), 1), [setv("message name", "music on")], [setv("message name", "music off")]),
    setv("message timer", 40),
    comment="SWITCH MUSIC: N key. The Music and Prompt Text sprites listen for\n'apply music setting' and set their volume.")
