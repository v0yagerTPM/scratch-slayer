"""The Engine sprite: its sounds and its own ('for this sprite only') variables."""
from sb3extra import *
from game.config import *
import pictures.world, sounds.screens, sounds.world
from game.stage import project

engine = Target(project, "Engine", layer=1, visible=False)
engine.costume("dot", pictures.world.TINY, 1, 1)
for sound_name, make_sound in (("door", sounds.world.door), ("switch", sounds.world.switch), ("locked", sounds.world.locked),
               ("secret", sounds.world.secret), ("melt", sounds.screens.melt), ("out of breath", sounds.world.out_of_breath),
               ("menu click", sounds.screens.menu_click), ("tally tick", sounds.screens.tally_tick),
               ("tally done", sounds.screens.tally_done)):
    add_sound(engine, sound_name, make_sound)
ENGINE_VARS = [
    # raycaster
    "ray column", "ray screen position", "ray direction x", "ray direction y", "ray square x", "ray square y",
    "distance between x lines", "distance between y lines", "ray step x", "ray step y",
    "distance to next x line", "distance to next y line", "letter hit", "hit side", "ray steps taken",
    "wall distance", "wall stripe height", "spot along wall", "stripe screen x", "stripe brightness",
    "wall type number", "wall style", "shading band number",
    # movement + input
    "forward input", "strafe input", "move amount x", "move amount y", "next player x", "next player y",
    "wall buffer", "M key was held", "E key was held", "shot cooldown", "exit timer",
    "facing square x", "facing square y", "facing letter",
    # level loading + map editing
    "map row", "map column", "map letter", "row text", "new row text", "row count", "letter position",
    "first row length", "player starts found", "exits found",
    "square to change x", "square to change y", "new letter", "queue position",
    # level intro + melt
    "show intro", "intro start time", "melt column", "column offset", "curtain top", "melt done",
    # minimap
    "minimap letter", "minimap player x", "minimap player y",
    # weapons
    "weapon ammo slot", "weapon to try", "N key was held",
    # options menu
    "screen before options", "up key was held", "down key was held",
    "change direction", "change repeat timer", "mouse row", "mouse was down", "slider fraction", "last options row",
    # level clock + tally
    "time at last frame", "tally progress", "time shown in seconds", "difficulty when loaded"]
for name in ENGINE_VARS:
    engine.var(name)

def wait_for_space(skip_pause=False):
    blocks = [wait_until(not_(key("space"))), wait_until(key("space")), wait_until(not_(key("space")))]
    return blocks if skip_pause else [wait(0.5)] + blocks
