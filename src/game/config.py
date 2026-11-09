"""Settings tables (monsters, weapons, walls, ammo, difficulty, per-level numbers), the names
of broadcasts and game states, and a few block helpers every part of the game uses."""
from sb3extra import *
import sounds.synth
from levels import LEVELS, validate

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
# Per level: how far rays travel (bigger maps need a limit so the game stays fast), how quickly
# walls fade to black with distance, and how much monsters darken with distance.
LEVEL_MAX_RAY_STEPS = [64, 64, 64, 34, 26, 36]
LEVEL_LIGHT_FALLOFF = [4.5, 4.5, 4.5, 4.5, 6.5, 4.2]
LEVEL_SPRITE_DARKNESS = [0, 0, 0, 2, 5, 2]
LEVEL_SELECT_BEST_WEAPON = [2, 3, 4, 4, 5, 5]   # starting at level N from the options menu gives weapons 1..this
# PAR TIME: seconds a good player needs for each level, shown on the tally screen. Each one is about
# 3 times as long as simply walking the shortest route to the exit (keys and boss included), which
# leaves time for fighting, rounded to the nearest 15 seconds.
LEVEL_PAR_SECONDS = [60, 90, 135, 165, 180, 240]

# DIFFICULTY: one row per setting. Both numbers are percentages of the normal amount.
#   damage to you    how much each hit on the player hurts (50 = half as much)
#   monster health   how many hit points every monster starts with (rounded to a whole number)
DIFFICULTY_COLUMNS = ["names", "damage to you", "monster health"]
DIFFICULTIES = [
    ["easy",   50,  75],
    ["normal", 100, 100],
    ["hard",   150, 125],
]
NORMAL_DIFFICULTY = 2

for level in LEVELS:
    validate(level)

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

def add_sound(sprite, sound_name, make_sound):
    """Make a sound with one of the functions in sounds/ and give it to a sprite."""
    wav_data, sample_count = make_sound()
    sprite.sound(sound_name, wav_data, sounds.synth.RATE, sample_count)

def map_letter_at(column, row):
    """letter (column + 1) of item (row + 1) of current map — columns and rows count from 0."""
    return letter(add(column, 1), item(add(row, 1), "current map"))
