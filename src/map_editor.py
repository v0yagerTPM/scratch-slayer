"""The map editor: a web page for drawing and changing maps with the mouse.

    python3 src/map_editor.py            # writes docs/map-editor.html

Open docs/map-editor.html in any web browser (double-click it; no internet needed, apart from
the fonts). Pick a map of the game or start a new one, paint squares with the letters on the left,
and the page checks the map while you draw: the same checks the build runs (validate() in
levels.py), and the balance numbers (balance()). Download saves the map as a file named like
"level 1 map A.txt", ready for src/maps (or for importing into the Scratch list of that name).

HOW THE PAGE IS MADE
====================
The page's parts are in src/editor/:
  page.html       what's on the page (buttons, panels)
  editor.css      how it looks
  map_checker.js  validate() and balance() again, in JavaScript (the browser can't run Python)
  editor.js       the drawing tools, undo, opening and saving
This script puts them in one file, with EDITOR_DATA: the map letters from levels.py, the
tables and colors from game/config.py and map_preview.py, and every map of the game. So the
editor always knows the game's latest letters, numbers and maps. npm test fails if
docs/map-editor.html is out of date, and checks map_checker.js agrees with levels.py.

    python3 src/map_editor.py --artifact <file>
writes a copy for publishing as a claude.ai Artifact instead: the same page, without the outer
<html> tags (the Artifact adds its own) and without the Download button (Artifacts can't
download files; Copy map text works there).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game.config as config  # noqa: E402
import levels  # noqa: E402
from map_preview import BOSS_LETTERS, FLOOR_COLOR, SPECIAL_WALLS, THINGS, WALL_COLORS  # noqa: E402

SOURCE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor")
EDITOR_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "map-editor.html")
TITLE = "Slayer Map Editor"
FONTS = ("https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700"
         "&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap")

# What to call each wall digit in the palette (by its color in the WALLS table).
WALL_NAMES = {"1": "grey", "2": "brown", "3": "green", "4": "red", "5": "slate", "6": "moss",
              "7": "steel blue", "8": "crimson", "9": "violet grey"}
# The colors of doors and switches, as map_preview.py draws them.
DOOR_COLORS = {"D": "#8a6a4a", "R": "#e03131", "B": "#2f6fe0", "Z": "#8f5fc0", "X": "#e8e8e8"}


def sorted_letters(letters):
    return "".join(sorted(letters))


def editor_data(can_download=True):
    """Everything the page needs to know about the game, as one dict (it becomes EDITOR_DATA)."""
    shotgun = config.WEAPON_TYPES[2]
    game = dict(
        # The letter groups validate() uses (levels.py)
        wallLetters=sorted_letters(levels.WALL_LETTERS), monsterLetters=sorted_letters(levels.MONSTER_LETTERS),
        bossLetters=sorted_letters(levels.BOSS_LETTERS), pickupLetters=sorted_letters(levels.PICKUP_LETTERS),
        keyLetters=sorted_letters(levels.KEY_LETTERS), floorLetters=sorted_letters(levels.FLOOR_LETTERS),
        edgeLetters=sorted_letters(levels.EDGE_LETTERS), safeStartDistance=levels.SAFE_START_DISTANCE,
        # The tables balance() uses (game/config.py)
        monsters={row[0]: dict(name=row[1], health=row[2]) for row in config.MONSTER_TYPES},
        chargerLetter=config.MONSTER_TYPES[config.CHARGER_TYPE - 1][0],
        difficulties=[dict(name=row[0], monsterHealth=row[2], suppliesKept=row[3], pickupAmount=row[4])
                      for row in config.DIFFICULTIES],
        ammoPickups={letter: list(pickup) for letter, pickup in config.AMMO_PICKUPS.items()},
        damagePerAmmo={"bullets": 1, "shells": (shotgun[3] + shotgun[4]) / 2, "rockets": config.EXPLOSION_DAMAGE_UP_CLOSE},
        mysteryItems=config.MYSTERY_ITEMS, healthPack=config.HEALTH_PACK,
        supplyLetters=config.SUPPLY_LETTERS, supplyShareStart=config.SUPPLY_SHARE_START)
    look = dict(wallColors=WALL_COLORS, wallNames=WALL_NAMES, doorColors=DOOR_COLORS, floorColor=FLOOR_COLOR,
                things={letter: list(thing) for letter, thing in THINGS.items()}, specialWalls=SPECIAL_WALLS,
                bossLetters=sorted_letters(BOSS_LETTERS))
    maps = [dict(level=level_number, letter=map_letter, levelName=level["name"], mapName=game_map["name"],
                 fileName=levels.map_list_name(level_number, map_letter), rows=game_map["rows"],
                 secretLook=game_map["secret_look"], angle=game_map["angle"])
            for level_number, map_letter, level, game_map in levels.every_map()]
    return dict(game=game, look=look, maps=maps, levelCount=len(levels.LEVELS), canDownload=can_download)


def read_part(file_name):
    with open(os.path.join(SOURCE_FOLDER, file_name), encoding="utf-8") as part:
        return part.read()


def page_parts(can_download):
    """The page in two parts: what goes in its <head> (title, fonts, style) and in its <body>."""
    # "</" can't appear inside a <script> in HTML, so the data writes it as "<\\/" (same in JSON).
    data = json.dumps(editor_data(can_download), separators=(",", ":")).replace("</", "<\\/")
    head = "\n".join([
        f"<title>{TITLE}</title>",
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link rel="stylesheet" href="{FONTS}">',
        "<!-- Made by src/map_editor.py from the files in src/editor. Don't edit this file: edit those"
        " and run python3 src/map_editor.py again. -->",
        "<style>", read_part("editor.css"), "</style>"])
    body = "\n".join([
        read_part("page.html"),
        f"<script>window.EDITOR_DATA = {data};</script>",
        "<script>", read_part("map_checker.js"), "</script>",
        "<script>", read_part("editor.js"), "</script>"])
    return head, body


def editor_page():
    """docs/map-editor.html: the whole page, ready to open in a browser."""
    head, body = page_parts(can_download=True)
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f"{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n")


def artifact_page():
    """The copy for a claude.ai Artifact: no outer tags (the Artifact adds them), no Download."""
    head, body = page_parts(can_download=False)
    return f"{head}\n{body}\n"


def write(path, contents):
    with open(path, "w", encoding="utf-8", newline="\n") as page_file:
        page_file.write(contents)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--artifact":
        write(sys.argv[2], artifact_page())
        print(f"wrote {sys.argv[2]}")
    else:
        write(EDITOR_PAGE, editor_page())
        print(f"wrote {os.path.normpath(EDITOR_PAGE)}")
