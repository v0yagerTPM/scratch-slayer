"""The project itself and the Stage: every shared ('for all sprites') variable and list,
the level maps as lists, the HUD number slots, and the list boxes shown on the stage."""
from sb3extra import *
from game.config import *
import pictures.options_menu, pictures.tally_screen, pictures.title_screen, pictures.victory_screen, pictures.world
from levels import LEVELS, every_map, map_list_name

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
stage.var("map choice", 0)
stage.var("developer mode", 0)   # 1 = C opens the developer console (hold D + E + V on the title screen)
stage.var("god mode", 0); stage.var("console kill", 0)
stage.var("secret wall hint", 8)  # how much lighter and more colorful secret walls look (0 = no hint)   # the options menu's MAP setting: 0 = random, 1 = always map A, 2 = map B ...
# WHICH MAP is being played (worked out by the Engine's 'pick map' blocks):
#   map variant         1 = the level's map A, 2 = map B, 3 = map C ...
#   map variant letter  the same as a letter: A, B, C ...
#   map name            the name of its list, e.g. "level 1 map B"
#   map item number     which item of the "map ..." lists (start angles, colors, par times...)
#                       belongs to this map: its position in "map list names"
#   level map count     how many maps the current level has
stage.var("map variant", 1); stage.var("map variant letter", "A"); stage.var("map name", "level 1 map A")
stage.var("map item number", 1); stage.var("level map count", 1)
# LEVEL TALLY: worked out when you finish a level. The "... shown" numbers count up on screen.
stage.var("level time", 0); stage.var("par was beaten", 0)
for name in ["kills percent", "items percent", "secrets percent", "level seconds", "par seconds",
             "kills percent shown", "items percent shown", "secrets percent shown",
             "time minutes shown", "time seconds shown", "par minutes shown", "par seconds shown"]:
    stage.var(name, 0)
stage.var("game state", TITLE); stage.var("screen showing", TITLE); stage.var("message name", "")

# THE MAPS: one list per map, named "level 1 map A", "level 1 map B" ... (one item per row).
# Then one item per MAP in each "map ..." list, in the same order as "map list names":
# level 1's maps first (A, B, C), then level 2's, and so on.
MAP_LISTS = [map_list_name(level_number, map_letter) for level_number, map_letter, level, game_map in every_map()]
ALL_MAPS = [game_map for level_number, map_letter, level, game_map in every_map()]
for name, game_map in zip(MAP_LISTS, ALL_MAPS):
    stage.lst(name, game_map["rows"])
stage.lst("map list names", MAP_LISTS)
stage.lst("map start angles", [game_map["angle"] for game_map in ALL_MAPS])
stage.lst("map ceiling hues", [game_map["ceil"][0] for game_map in ALL_MAPS])
stage.lst("map ceiling saturations", [game_map["ceil"][1] for game_map in ALL_MAPS])
stage.lst("map floor hues", [game_map["floor"][0] for game_map in ALL_MAPS])
stage.lst("map floor saturations", [game_map["floor"][1] for game_map in ALL_MAPS])
stage.lst("map secret wall looks", [game_map["secret_look"] for game_map in ALL_MAPS])
stage.lst("map max ray steps", [game_map["max_ray_steps"] for game_map in ALL_MAPS])
stage.lst("map light falloffs", [game_map["light_falloff"] for game_map in ALL_MAPS])
stage.lst("map sprite darkness", [game_map["sprite_darkness"] for game_map in ALL_MAPS])
stage.lst("map par times", [game_map["par_seconds"] for game_map in ALL_MAPS])
# One item per LEVEL. The game counts the items in "level names" to know how many levels there are.
stage.lst("level names", [level["name"] for level in LEVELS])
# MYSTERY ITEMS (?): the item types a ? can turn into (1 health, 2 shells, 6 bullets, 7 rockets).
stage.lst("mystery item types", [ITEM_TYPES[letter] for letter in MYSTERY_ITEMS])
stage.lst("level select best weapon", [level["best_weapon"] for level in LEVELS])
stage.lst("level intro monster", [level["card_monster"] for level in LEVELS])   # walks onto the level card
stage.lst("level intro boss", [level["card_boss"] for level in LEVELS])         # waits in the card's background
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
stage.lst("console words")
stage.lst("developer console", CONSOLE_HELP)   # the developer console's list of commands
stage.lst("developer usernames", DEVELOPER_USERNAMES)   # who may switch developer mode on
stage.lst("rows to load"); stage.lst("monster on square"); stage.lst("current map"); stage.lst("wall distance per column", [0] * RAY_COUNT)
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
list_monitor("developer console", 10, 10, 330, 250)
for name in MAP_LISTS:
    list_monitor(name, 5, 5, 300, 350)
