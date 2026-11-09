"""The project itself and the Stage: every shared ('for all sprites') variable and list,
the level maps as lists, the HUD number slots, and the list boxes shown on the stage."""
from sb3extra import *
from game.config import *
import pictures.options_menu, pictures.tally_screen, pictures.title_screen, pictures.victory_screen, pictures.world
from levels import LEVELS

project = Project()
stage = Target(project, "Stage", is_stage=True)
stage.costume("black", pictures.world.BACKDROP, 240, 180)
stage.costume("title sky", pictures.title_screen.TITLE_SKY, 240, 180)
stage.costume("victory sky", pictures.victory_screen.VICTORY_SKY, 240, 180)

STAGE_VARS = ["player x", "player y", "player angle", "look direction x", "look direction y",
              "camera plane x", "camera plane y", "projection factor", "hurt flash timer",
              "pickup flash timer", "map is showing", "shot fired this frame", "closest target depth",
              "shot target id", "shot range", "target hit id", "gun bob angle", "player is moving",
              "current level", "has red key", "has blue key", "level kills", "level monster count",
              "level item count", "level items collected", "message timer", "ceiling hue",
              "ceiling saturation", "floor hue", "floor saturation", "map width", "map height",
              "minimap square size", "health", "total kills",
              "boss health", "boss max health", "boss is awake", "level secret count", "level secrets found",
              # weapons
              "current weapon", "weapon switch timer", "hit damage", "aim width", "ammo shown",
              # bosses + the skull key
              "has skull key", "boss is dead", "boss death x", "boss death y", "boss name",
              # per-level look
              "max ray steps", "light falloff", "sprite darkness", "camera plane length",
              "options open", "options row", "options from game"]
for name in STAGE_VARS:
    stage.var(name)
stage.var("card is up", 0); stage.var("lightning glow", 0)
stage.var("killer type", 0); stage.var("killer name", "monster")
stage.var("total secrets found", 0); stage.var("total secret count", 0)
stage.var("stamina", 100); stage.var("is exhausted", 0); stage.var("is sprinting", 0)
stage.var("speed boost", 1); stage.var("stamina rest timer", 0)
# OPTIONS: these are NOT reset by the green flag, so your settings stick while the project is open.
stage.var("turn speed", 4); stage.var("mouse steering", 0); stage.var("mouse sensitivity", 5)
stage.var("field of view", 66); stage.var("music is on", 1); stage.var("start level choice", 1)
stage.var("highest level reached", 1); stage.var("difficulty", NORMAL_DIFFICULTY)
# LEVEL TALLY: worked out when you finish a level. The "... shown" numbers count up on screen.
stage.var("level time", 0); stage.var("par was beaten", 0)
for name in ["kills percent", "items percent", "secrets percent", "level seconds", "par seconds",
             "kills percent shown", "items percent shown", "secrets percent shown",
             "time minutes shown", "time seconds shown", "par minutes shown", "par seconds shown"]:
    stage.var(name, 0)
stage.var("game state", TITLE); stage.var("screen showing", TITLE); stage.var("message name", "")

LEVEL_LISTS = [f"level {level_number} map" for level_number in range(1, len(LEVELS) + 1)]
for name, level in zip(LEVEL_LISTS, LEVELS):
    stage.lst(name, level["rows"])
stage.lst("level start angles", [level["angle"] for level in LEVELS])
stage.lst("level ceiling hues", [level["ceil"][0] for level in LEVELS])
stage.lst("level ceiling saturations", [level["ceil"][1] for level in LEVELS])
stage.lst("level floor hues", [level["floor"][0] for level in LEVELS])
stage.lst("level floor saturations", [level["floor"][1] for level in LEVELS])
stage.lst("level secret wall looks", [level["secret_look"] for level in LEVELS])
stage.lst("level max ray steps", LEVEL_MAX_RAY_STEPS)
stage.lst("level light falloffs", LEVEL_LIGHT_FALLOFF)
stage.lst("level sprite darkness", LEVEL_SPRITE_DARKNESS)
stage.lst("level select best weapon", LEVEL_SELECT_BEST_WEAPON)
stage.lst("level par times", LEVEL_PAR_SECONDS)
stage.lst("level intro monster", [1, 2, 3, 5, 6, 7])   # monster type shown walking onto each level's card
stage.lst("level intro boss", [0, 0, 4, 0, 0, 0])      # a boss shown in the background of the card (0 = none)
stage.lst("melt offsets", [0] * 24)
for column_number, column in enumerate(MONSTER_COLUMNS):
    stage.lst(f"monster {column}", [row[column_number] for row in MONSTER_TYPES])
for column_number, column in enumerate(WEAPON_COLUMNS):
    stage.lst(f"weapon {column}", [row[column_number] for row in WEAPON_TYPES])
for column_number, column in enumerate(DIFFICULTY_COLUMNS):
    stage.lst(f"difficulty {column}", [row[column_number] for row in DIFFICULTIES])
stage.lst("weapons owned", [1, 1, 0, 0, 0])          # 1 = you have it. Item N = weapon slot N.
stage.lst("ammo names", [ammo[0] for ammo in AMMO])
stage.lst("ammo counts", [ammo[1] for ammo in AMMO])
stage.lst("ammo limits", [ammo[2] for ammo in AMMO])
stage.lst("ammo at level start", [ammo[1] for ammo in AMMO])
# Where every monster is right now (item N = monster id N). Rockets use these to find what they hit.
stage.lst("monster x positions"); stage.lst("monster y positions"); stage.lst("monster alive flags")
stage.lst("wall letters", [wall[0] for wall in WALLS]); stage.lst("wall hues", [wall[1] for wall in WALLS])
stage.lst("wall saturations", [wall[2] for wall in WALLS]); stage.lst("wall brightnesses", [wall[3] for wall in WALLS])
stage.lst("wall styles", [wall[4] for wall in WALLS])
stage.lst("current map"); stage.lst("wall distance per column", [0] * RAY_COUNT)
for name in ["monster start x", "monster start y", "monster start type", "item start x", "item start y",
             "item start type", "barrel start x", "barrel start y",
             "new shot x", "new shot y", "new shot speed x", "new shot speed y", "new shot damage", "new shot look",
             "new shot owner",
             "new explosion x", "new explosion y", "explosion x", "explosion y",
             "squares to clear x", "squares to clear y"]:
    stage.lst(name)
problems_id = stage.lst("map problems")
# HUD number slots: 1 health, 2 ammo for the weapon in your hands,
# 3-9 the level tally: 3 kills %, 4 items %, 5 secrets %, 6-7 your time (minutes, seconds),
#     8-9 par time (minutes, seconds),
# 10 total kills (win screen), 11-12 secrets found / in the whole game (win screen),
# 13-16 the options menu: turn speed, mouse sensitivity, field of view, start level
HUD_SLOTS = 16
OPTION_ROW_Y = pictures.options_menu.OPTION_ROW_Y
TALLY_Y = [pictures.tally_screen.tally_digit_y(row) for row in range(1, 6)]
PERCENT_X, MINUTES_X = pictures.tally_screen.PERCENT_X, pictures.tally_screen.MINUTES_X
stage.lst("HUD number values", [0] * HUD_SLOTS)
stage.lst("HUD number x", [-150, 222, PERCENT_X, PERCENT_X, PERCENT_X, MINUTES_X, PERCENT_X, MINUTES_X, PERCENT_X,
                           120, 50, 120, 176, 176, 176, 57])
stage.lst("HUD number y", [-158, -158, TALLY_Y[0], TALLY_Y[1], TALLY_Y[2], TALLY_Y[3], TALLY_Y[3], TALLY_Y[4], TALLY_Y[4],
                           -78, -112, -112, OPTION_ROW_Y[0], OPTION_ROW_Y[2], OPTION_ROW_Y[3], OPTION_ROW_Y[6]])
stage.lst("HUD number size", [100] * 12 + [70] * 4)
stage.lst("HUD number screen", [NONE, NONE] + [COMPLETE] * 7 + [WIN, WIN, WIN, OPTIONS, OPTIONS, OPTIONS, OPTIONS])

def list_monitor(name, left, top, width, height):
    """A list's box on the stage (hidden until the game or a student shows it)."""
    list_id = project.stage_lists[name][0]
    project.monitors.append({"id": list_id, "mode": "list", "opcode": "data_listcontents", "params": {"LIST": name},
                       "spriteName": None, "value": [], "width": width, "height": height, "x": left, "y": top,
                       "visible": False})
list_monitor("map problems", 10, 10, 460, 230)
for name in LEVEL_LISTS:
    list_monitor(name, 5, 5, 300, 350)
