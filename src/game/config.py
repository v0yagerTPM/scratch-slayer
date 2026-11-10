"""Settings tables (monsters, weapons, walls, ammo, difficulty, per-level numbers), the names
of broadcasts and game states, and a few block helpers every part of the game uses."""
from sb3extra import *
import sounds.synth
from levels import LEVELS, MAP_LETTERS, check_level_list, every_map, map_title, validate

RAY_COUNT, STRIPE_WIDTH = 80, 6      # 80 rays, each drawn as a 6-px-wide vertical stripe
WALK_SPEED, MONSTER_SPEED, TURN_SPEED = 0.07, 0.025, 4   # per frame, at 30 frames per second
SPRINT_BOOST, SPRINT_DRAIN, STAMINA_REST, STAMINA_REFILL, EXHAUSTED_UNTIL = 1.75, 1.2, 20, 0.6, 40
CENTER_COLUMN = RAY_COUNT // 2 + 1   # list item of the crosshair column
START_BULLETS = 50
MIN_FOV, MAX_FOV = 60, 100

# wall letter, hue, saturation, brightness (Scratch pen 0-100 scales), style
#   style 0 = plain wall, 1 = door, 2 = exit switch (off), 3 = exit switch (on), 4 = secret wall
WALLS = [("1", 0, 0, 72, 0), ("2", 8, 55, 68, 0), ("3", 33, 50, 62, 0), ("4", 0, 70, 66, 0),
         ("5", 45, 18, 62, 0), ("6", 30, 75, 58, 0), ("7", 58, 28, 64, 0),
         ("8", 98, 72, 50, 0), ("9", 75, 22, 50, 0),
         ("D", 10, 30, 58, 1), ("R", 0, 90, 72, 1), ("B", 60, 90, 72, 1),
         ("X", 0, 0, 55, 2), ("Y", 0, 0, 55, 3), ("S", 0, 0, 60, 4), ("Z", 75, 30, 70, 5)]
#   style 5 = skull door: a door frame with two glowing red eyes

# One row per monster type. Each column becomes a Scratch list ("monster health", "monster speed"...),
# so students can rebalance monsters without touching any code.
MONSTER_COLUMNS = ["letters", "names", "health", "speed", "claw damage", "size", "keep distance",
                   "wake distance", "shots per volley", "shot delay", "shot speed", "shot damage",
                   "shot look", "voice pitch", "is boss", "special move"]
MONSTER_TYPES = [
    ["M", "imp",      3,  0.025, 12, 100, 0.9, 7,  0, 0,  0,    0,  "none",   0,    0, "none"],
    ["V", "spitter",  3,  0.02,  6,  95,  4,   9,  1, 75, 0.11, 10, "acid",   60,   0, "none"],
    ["G", "golem",    6,  0.022, 16, 130, 0.9, 7,  0, 0,  0,    0,  "none",   -90,  0, "none"],
    ["W", "warden",   24, 0.02,  16, 165, 2,   10, 3, 55, 0.13, 14, "fire",   -140, 1, "none"],
    ["C", "charger",  5,  0.028, 14, 120, 0.9, 9,  0, 0,  0,    0,  "none",   -40,  0, "charge"],
    ["F", "wraith",   4,  0.034, 10, 100, 0.9, 8,  0, 0,  0,    0,  "none",   120,  0, "blink"],
    ["T", "colossus", 60, 0.018, 25, 210, 2.2, 12, 3, 60, 0.14, 16, "plasma", -200, 1, "rage"],
]
CHARGER_TYPE = 5     # the colossus calls in two of these at half health

# One row per weapon, same idea as the monster table. 'ammo slot' = item number in "ammo counts":
# 0 = needs no ammo, 1 = bullets, 2 = shells, 3 = rockets.
WEAPON_COLUMNS = ["names", "ammo slots", "reload frames", "damage min", "damage max", "ranges", "aim widths"]
WEAPON_TYPES = [
    ["fist",            0, 16, 1, 2, 1.5, 1],
    ["pistol",          1, 14, 1, 1, 999, 1],
    ["shotgun",         2, 26, 2, 3, 999, 1.6],
    ["chaingun",        1, 5,  1, 1, 999, 1],
    ["rocket launcher", 3, 30, 0, 0, 0,   1],
]
AMMO = [("bullets", START_BULLETS, 200), ("shells", 0, 99), ("rockets", 0, 50)]   # name, new-game amount, most you can carry
# What each ammo or weapon pickup gives you: map letter -> (ammo name, how much).
AMMO_PICKUPS = {"I": ("bullets", 20), "A": ("shells", 8), "U": ("rockets", 4),
                "N": ("shells", 8), "Q": ("bullets", 40), "L": ("rockets", 4)}
HEALTH_PACK = 25   # health one health pack (H) gives, at normal difficulty
# An explosion (barrel or rocket) does this much damage to a monster close to it, half as much
# further away.
EXPLOSION_DAMAGE_UP_CLOSE = 6
# Everything about each level (map, colors, draw distance, par time, card...) is in its record in
# LEVELS, in src/levels.py. The one thing worked out here: where episode 1 ends, for the music
# (one track per episode) and the "EPISODE 1 COMPLETE" screen.
LAST_LEVEL_OF_EPISODE_1 = max(level_number for level_number, level in enumerate(LEVELS, start=1)
                              if level["episode"] == 1)

# DIFFICULTY: one row per setting. All the numbers are percentages of the normal amount.
#   damage to you    how much each hit on the player hurts (50 = half as much)
#   monster health   how many hit points every monster starts with (rounded to a whole number)
#   supplies kept    how many of a map's health packs and ammo boxes (H, A, I, U) appear. At 70,
#                    7 in every 10 do, spread evenly over the map. Keys and weapons always appear.
#   pickup amount    how much each health pack and each ammo pickup (weapons too) gives you
#                    (150 = one and a half times as much, rounded). Doom's easiest skill doubled ammo.
DIFFICULTY_COLUMNS = ["names", "damage to you", "monster health", "supplies kept", "pickup amount"]
DIFFICULTIES = [
    ["easy",   50,  75,  100, 150],
    ["normal", 100, 100, 100, 100],
    ["hard",   150, 125, 70,  100],
]
SUPPLY_LETTERS = "HAIU"     # the pickups 'supplies kept' can leave out: health, shells, bullets, rockets
SUPPLY_SHARE_START = 50     # where the sharing-out count starts (see 'load level' and supplies_kept())
NORMAL_DIFFICULTY = 2

# Check every map of every level (see validate() in levels.py). A broken map stops the build here.
check_level_list()
for level_number, map_letter, level, game_map in every_map():
    validate(dict(name=map_title(level_number, map_letter, level, game_map), rows=game_map["rows"]))
# The most maps any level has. The options menu's MAP setting goes up to this many letters.
MOST_MAPS_IN_A_LEVEL = max(len(level["maps"]) for level in LEVELS)

# ---------------- names used in Scratch ----------------
# broadcasts
CLEAR, SPAWN, UPDATE, DRAW_HUD, DRAW_NUMBERS, FIRE, PUNCH = (
    "clear level", "spawn monsters and objects", "update monsters and objects", "draw HUD",
    "draw HUD numbers", "fire weapon", "punch")
SUMMON, START_MUSIC, APPLY_MUSIC = "summon monsters", "start music", "apply music setting"
DRAW_OPTIONS_PANEL, DRAW_OPTIONS_WIDGETS = "draw options panel", "draw options widgets"
DRAW_OPTIONS_HIGHLIGHT = "draw options highlight"
OPTIONS = "options"   # 'screen showing' while the options menu is open
# screens + game states
NONE, TITLE, DIED, COMPLETE, WIN = "none", "title", "died", "level complete", "you win"
PLAYING, EXIT_REACHED, DEAD = "playing", "exit reached", "dead"
INTRO = "intro"   # used for both 'game state' and 'screen showing' while a level card or melt is on screen
SHOW_TITLE, SHOW_CARD = "show title", "show level card"
SHOW_DEATH, SHOW_WIN = "show death screen", "show victory screen"

def V(name): return Var(name)

def hurt_player(amount):
    """change health by -(amount x the difficulty's 'damage to you' percent / 100), rounded.
    EVERY hit on the player goes through this, so the difficulty setting works everywhere."""
    return chg("health", mul(-1, round_(mul(amount, div(item(V("difficulty"), "difficulty damage to you"), 100)))))

def pickup_amount(amount):
    """amount x the difficulty's 'pickup amount' percent / 100, rounded. Every health pack and
    ammo pickup goes through this, so the difficulty setting works for all of them."""
    return round_(mul(amount, div(item(V("difficulty"), "difficulty pickup amount"), 100)))

def scratch_round(number):
    """Python's round() rounds 2.5 to 2 (to the even number); Scratch's 'round' block rounds it
    up to 3. The balance report uses this one so its numbers match the game's."""
    return int(number + 0.5) if number >= 0 else -int(-number + 0.5)

def supplies_kept(map_rows, percent_kept):
    """Which of a map's supply pickups appear at this 'supplies kept' percent: a list of
    (column, row, letter), in the order 'load level' reads them. It shares them out the same way
    the game does: a running count goes up by the percent at each supply; when it reaches 100 the
    pickup appears and 100 comes off the count. At 70 that gives keep, skip, keep, keep, keep,
    skip ... 7 in every 10, spread evenly."""
    share, kept = SUPPLY_SHARE_START, []
    for row, row_text in enumerate(map_rows):
        for column, letter in enumerate(row_text.upper()):
            if letter in SUPPLY_LETTERS:
                share += percent_kept
                if share >= 100:
                    share -= 100
                    kept.append((column, row, letter))
    return kept

def add_sound(sprite, sound_name, make_sound):
    """Make a sound with one of the functions in sounds/ and give it to a sprite."""
    wav_data, sample_count = make_sound()
    sprite.sound(sound_name, wav_data, sounds.synth.RATE, sample_count)

def map_letter_at(column, row):
    """letter (column + 1) of item (row + 1) of current map — columns and rows count from 0."""
    return letter(add(column, 1), item(add(row, 1), "current map"))
