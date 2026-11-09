"""The Pickup sprite: health, ammo, weapons and keys."""
from sb3extra import *
from game.config import *
import assets2, assets6
from game.screen_placement import offset_from_player, place_on_screen
from game.stage import project

pickup = Target(project, "Pickup", layer=2, visible=False)
for costume_name, art in (("item 1", assets2.MEDKIT), ("item 2", assets2.SHELLS), ("item 3", assets2.RED_KEY),
                ("item 4", assets2.BLUE_KEY), ("item 6", assets6.BULLETS), ("item 7", assets6.ROCKETS)):
    pickup.costume(costume_name, art, 20, 40)
pickup.costume("item 5", assets6.SKULL_KEY, 20, 44)
for costume_name, art in (("item 8", assets6.SHOTGUN_PICKUP), ("item 9", assets6.CHAINGUN_PICKUP), ("item 10", assets6.LAUNCHER_PICKUP)):
    pickup.costume(costume_name, art, 32, 34)
for sound_name, make_sound in (("item", assets2.item), ("key", assets2.key), ("weapon", assets6.weapon_pickup)):
    add_sound(pickup, sound_name, make_sound)
for name in ["item id", "is clone", "item x", "item y", "item type", "is taken", "was picked up", "has dropped",
             "offset x from player", "offset y from player", "distance to player", "sideways in view",
             "depth in view", "screen x", "screen column index"]:
    pickup.var(name)
pickup.script(flag(), hide(), setv("is clone", 0),
         comment="The original Pickup sprite never appears. It only makes clones.\n"
                 "Item types: 1 health pack, 2 shells, 3 red key, 4 blue key,\n"
                 "5 skull key (dropped by a boss), 6 bullets, 7 rockets,\n"
                 "8 shotgun, 9 chaingun, 10 rocket launcher.")
pickup.script(recv(CLEAR), if_(eq(V("is clone"), 1), delete_clone()),
         comment="CLEAR LEVEL: every item clone deletes itself.")
pickup.script(recv(SPAWN),
         if_(eq(V("is clone"), 0), setv("item id", 0), repeat(length("item start x"), chg("item id", 1), clone())),
         comment="SPAWN: one clone per item letter on the map (and one skull key per boss).")
pickup.script(as_clone(), setv("is clone", 1),
         setv("item x", add(item(V("item id"), "item start x"), 0.5)),
         setv("item y", add(item(V("item id"), "item start y"), 0.5)),
         setv("item type", item(V("item id"), "item start type")), setv("is taken", 0), setv("has dropped", 0),
         costume("item 1", join("item ", V("item type"))), hide(),
         comment="NEW CLONE: find my square and type, and wear the costume\n'item 1' to 'item 10' that matches my type.")

def add_ammo(slot, amount):
    """Add ammo, but never more than 'ammo limits' allows."""
    return [replace("ammo counts", slot, add(item(slot, "ammo counts"), amount)),
            if_(gt(item(slot, "ammo counts"), item(slot, "ammo limits")),
                replace("ammo counts", slot, item(slot, "ammo limits")))]

def weapon_pickup(type_number, slot, ammo_slot, amount):
    return if_(eq(V("item type"), type_number),
               if_(eq(item(slot, "weapons owned"), 0), setv("current weapon", slot), setv("weapon switch timer", 8)),
               replace("weapons owned", slot, 1), *add_ammo(ammo_slot, amount), setv("was picked up", 1))

pickup.script(recv(UPDATE), if_(and_(eq(V("is clone"), 1), eq(V("is taken"), 0)),
    ifelse(and_(eq(V("item type"), 5), eq(V("boss is dead"), 0)),
           [note("SKULL KEY: stays hidden (and can't be picked up) until the boss dies.",
                 hide())],
           [note("The moment the boss dies, jump to where it fell.",
                 if_(and_(eq(V("item type"), 5), eq(V("has dropped"), 0)),
                     setv("item x", V("boss death x")), setv("item y", V("boss death y")), setv("has dropped", 1))),
            *offset_from_player("item x", "item y"),
            note("PICK UP when the player is within 0.6 squares.\n"
                 "Health only counts if you're hurt (like in Doom), so it isn't wasted.\n"
                 "Ammo goes into 'ammo counts' (never above 'ammo limits').\n"
                 "A NEW weapon is switched to straight away; one you already own\n"
                 "just gives you its ammo.",
                 if_(and_(eq(V("game state"), PLAYING), lt(V("distance to player"), 0.6)),
                     setv("was picked up", 0),
                     if_(and_(eq(V("item type"), 1), lt(V("health"), 100)),
                         chg("health", 25), if_(gt(V("health"), 100), setv("health", 100)), setv("was picked up", 1)),
                     if_(eq(V("item type"), 2), *add_ammo(2, 8), setv("was picked up", 1)),
                     if_(eq(V("item type"), 3), setv("has red key", 1), setv("was picked up", 1)),
                     if_(eq(V("item type"), 4), setv("has blue key", 1), setv("was picked up", 1)),
                     if_(eq(V("item type"), 5), setv("has skull key", 1), setv("was picked up", 1)),
                     if_(eq(V("item type"), 6), *add_ammo(1, 20), setv("was picked up", 1)),
                     if_(eq(V("item type"), 7), *add_ammo(3, 4), setv("was picked up", 1)),
                     weapon_pickup(8, 3, 2, 8), weapon_pickup(9, 4, 1, 40), weapon_pickup(10, 5, 3, 4),
                     note("Picked up: count it, flash gold, show 'picked up N' and play a sound.",
                          if_(eq(V("was picked up"), 1),
                              setv("is taken", 1), chg("level items collected", 1), setv("pickup flash timer", 4),
                              setv("message name", join("picked up ", V("item type"))), setv("message timer", 45),
                              ifelse(gt(V("item type"), 7), [play("weapon")],
                                     [ifelse(and_(gt(V("item type"), 2), lt(V("item type"), 6)), [play("key")],
                                             [play("item")])]),
                              hide())))),
            if_(eq(V("is taken"), 0),
                *place_on_screen([note("Darker when far away on dark levels.",
                                       seteffect("BRIGHTNESS", mul(-1, mul(V("distance to player"), V("sprite darkness")))))],
                                 "item"))])),
    comment="UPDATE (every frame, for every item clone that hasn't been taken):\n"
            "check if the player walked over me, then place myself on screen\n"
            "the same way monsters do.")
