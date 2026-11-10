"""Map previews: draws every map as a top-down picture, so you can see a map without playing it.

    python3 src/map_preview.py            # writes docs/maps: one picture per map + README.md

For each map it writes docs/maps/level 1 map A.svg (any web browser opens an .svg file, and
GitHub shows them), and docs/maps/README.md shows them all on one page, level by level, with
each map's balance numbers (see balance() in levels.py). Run it after changing a map;
npm test fails if the pictures are out of date, so they always match the maps.

HOW A PICTURE IS DRAWN
======================
The picture is the map seen from above, one small square per letter, with row 0 at the top,
exactly like the text file. Walls get the color the game gives them (the 'WALLS' table in
game/config.py), and things standing on the floor get a round token with their letter:
monsters red, bosses big and dark red, health green, ammo yellow, weapons orange, keys in
their color, the player start green with an arrow showing which way you face.
Every fifth column and row is numbered along the edges, so you can find a square in the text
file: column 10 is the 11th letter of a line, row 10 is the 11th line.
"""
import colorsys
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game.config import MONSTER_TYPES, WALLS  # noqa: E402
from levels import LEVELS, balance, every_map, map_list_name  # noqa: E402
import game.config  # noqa: E402

PREVIEW_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "maps")
SQUARE = 16                 # pixels per map square
MARGIN_LEFT, MARGIN_TOP = 28, 72   # room for the row numbers on the left, title and column numbers on top
FLOOR_COLOR, GRID_COLOR = "#1c1a1e", "#2a272d"

# ---------------- what each letter looks like ----------------
def pen_color_to_hex(hue, saturation, brightness):
    """Scratch pen colors use 0-100 for hue, saturation and brightness. Turn one into #rrggbb."""
    red, green, blue = colorsys.hsv_to_rgb(hue / 100, saturation / 100, brightness / 100)
    return "#{:02x}{:02x}{:02x}".format(round(red * 255), round(green * 255), round(blue * 255))

WALL_COLORS = {letter: pen_color_to_hex(hue, saturation, brightness)
               for letter, hue, saturation, brightness, style in WALLS}

MONSTER_NAMES = {row[0]: row[1] for row in MONSTER_TYPES}
BOSS_LETTERS = {row[0] for row in MONSTER_TYPES if row[14] == 1}
# Things on the floor: letter -> (token color, name in the legend)
THINGS = {"P": ("#40c057", "player start"),
          **{letter: ("#7a0c0c" if letter in BOSS_LETTERS else "#e03131",
                      name + (" (boss)" if letter in BOSS_LETTERS else "")) for letter, name in MONSTER_NAMES.items()},
          "H": ("#2f9e44", "health"), "A": ("#f2c200", "shells"), "I": ("#f2c200", "bullets"),
          "U": ("#f2c200", "rockets"), "N": ("#fd7e14", "shotgun"), "Q": ("#fd7e14", "chaingun"),
          "L": ("#fd7e14", "rocket launcher"), "K": ("#ff5a5a", "red key"), "J": ("#4a8bff", "blue key"),
          "E": ("#6b7a2a", "barrel")}
# Special squares in the walls: letter -> name in the legend
SPECIAL_WALLS = {"D": "door", "R": "red door", "B": "blue door", "Z": "skull door", "X": "exit switch",
                 "S": "secret wall"}


def text(text_x, text_y, words, size=10, fill="#cfcfcf", anchor="middle", weight="normal"):
    return (f'<text x="{text_x}" y="{text_y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{words}</text>')


def square_picture(letter, left, top, secret_look, start_angle):
    """The drawing for one square of the map: a wall, a door, or floor. (Things standing on the
    floor are drawn by thing_picture() afterwards, on top of every square, so a big boss token
    isn't covered by the square next to it.)"""
    middle_x, middle_y = left + SQUARE / 2, top + SQUARE / 2
    if letter in WALL_COLORS and letter not in SPECIAL_WALLS:          # a plain wall
        return f'<rect x="{left}" y="{top}" width="{SQUARE}" height="{SQUARE}" fill="{WALL_COLORS[letter]}"/>'
    if letter == "S":    # a secret wall: looks like its wall, with a dashed gold outline
        return (f'<rect x="{left}" y="{top}" width="{SQUARE}" height="{SQUARE}" fill="{WALL_COLORS[secret_look]}"/>'
                f'<rect x="{left + 1.5}" y="{top + 1.5}" width="{SQUARE - 3}" height="{SQUARE - 3}" fill="none" '
                'stroke="#ffd23f" stroke-width="1.5" stroke-dasharray="2.5 2"/>')
    if letter in SPECIAL_WALLS:  # doors and the exit: their color, with their letter
        color = {"D": "#8a6a4a", "R": "#e03131", "B": "#2f6fe0", "Z": "#8f5fc0", "X": "#e8e8e8"}[letter]
        letter_color = "#000" if letter == "X" else "#fff"
        return (f'<rect x="{left}" y="{top}" width="{SQUARE}" height="{SQUARE}" fill="{color}"/>'
                + text(middle_x, top + SQUARE - 4, letter, size=11, fill=letter_color, weight="bold"))
    return f'<rect x="{left}" y="{top}" width="{SQUARE}" height="{SQUARE}" fill="{FLOOR_COLOR}"/>'


def thing_picture(letter, left, top, start_angle):
    """A token for a thing standing on the floor: a circle with its letter (keys are diamonds,
    so they don't look like monsters), or nothing if the square has no thing on it."""
    middle_x, middle_y = left + SQUARE / 2, top + SQUARE / 2
    picture = ""
    if letter in THINGS:
        color = THINGS[letter][0]
        radius = SQUARE * (0.62 if letter in BOSS_LETTERS else 0.42)
        if letter in "KJ":
            size = SQUARE * 0.55
            picture += (f'<rect x="{middle_x - size / 2}" y="{middle_y - size / 2}" width="{size}" height="{size}" '
                        f'fill="{color}" stroke="#000" stroke-width="1" transform="rotate(45 {middle_x} {middle_y})"/>')
        else:
            picture += f'<circle cx="{middle_x}" cy="{middle_y}" r="{radius}" fill="{color}" stroke="#000" stroke-width="1"/>'
        if letter == "P":   # an arrow for the start angle (0 = right, 90 = down, like the game)
            picture += (f'<path d="M -3 -3.5 L 4.5 0 L -3 3.5 Z" fill="#fff" '
                        f'transform="translate({middle_x} {middle_y}) rotate({start_angle})"/>')
        else:
            letter_color = "#000" if color in ("#f2c200", "#fd7e14") else "#fff"
            picture += text(middle_x, middle_y + 3.5, letter, size=9, fill=letter_color, weight="bold")
    return picture


def by_difficulty(map_rows):
    """'ammo ratio 10.0 / 4.44 / 2.78, health 114 / 75 / 50 (easy / normal / hard)'"""
    names = [row[0] for row in game.config.DIFFICULTIES]
    numbers = [balance(map_rows, game.config, name) for name in names]
    return (f"ammo ratio {' / '.join(str(each['ammo_ratio']) for each in numbers)}, "
            f"health {' / '.join(str(each['health']) for each in numbers)} ({' / '.join(names)})")


def map_picture(level_number, map_letter, level, game_map):
    """The whole picture for one map, as SVG text."""
    map_rows = game_map["rows"]
    map_height, map_width = len(map_rows), len(map_rows[0])
    legend_letters = [letter for letter in list(THINGS) + list(SPECIAL_WALLS) if any(letter in row for row in map_rows)]
    legend_rows = (len(legend_letters) + 3) // 4
    picture_width = max(MARGIN_LEFT + map_width * SQUARE + 12, 470)
    picture_height = MARGIN_TOP + map_height * SQUARE + 16 + legend_rows * 18 + 8
    numbers = balance(map_rows, game.config)
    body = [f'<rect width="{picture_width}" height="{picture_height}" fill="#0e0d10"/>',
            text(8, 20, f"LEVEL {level_number}-{map_letter}  {level['name'].upper()}: {game_map['name']}",
                 size=14, fill="#ff6a2a", anchor="start", weight="bold"),
            text(8, 36, f"{map_width} x {map_height} squares, {numbers['monsters']} monsters, par "
                        f"{game_map['par_seconds']} s", size=10, anchor="start"),
            text(8, 50, by_difficulty(map_rows), size=10, anchor="start")]
    # Column numbers along the top, row numbers down the left: every fifth one.
    for column in range(0, map_width, 5):
        body.append(text(MARGIN_LEFT + column * SQUARE + SQUARE / 2, MARGIN_TOP - 5, column, size=9, fill="#8a8a8a"))
    for row in range(0, map_height, 5):
        body.append(text(MARGIN_LEFT - 5, MARGIN_TOP + row * SQUARE + SQUARE / 2 + 3, row, size=9, fill="#8a8a8a",
                         anchor="end"))
    for drawing_pass in (square_picture, thing_picture):     # all the squares first, then the things
        for row, row_text in enumerate(map_rows):
            for column, letter in enumerate(row_text):
                left, top = MARGIN_LEFT + column * SQUARE, MARGIN_TOP + row * SQUARE
                if drawing_pass is square_picture:
                    body.append(square_picture(letter.upper(), left, top, game_map["secret_look"], game_map["angle"]))
                else:
                    body.append(thing_picture(letter.upper(), left, top, game_map["angle"]))
    # Faint lines every 5 squares, to help count.
    for column in range(0, map_width + 1, 5):
        line_x = MARGIN_LEFT + column * SQUARE
        body.append(f'<line x1="{line_x}" y1="{MARGIN_TOP}" x2="{line_x}" y2="{MARGIN_TOP + map_height * SQUARE}" '
                    'stroke="#ffffff" stroke-opacity="0.12" stroke-width="1"/>')
    for row in range(0, map_height + 1, 5):
        line_y = MARGIN_TOP + row * SQUARE
        body.append(f'<line x1="{MARGIN_LEFT}" y1="{line_y}" x2="{MARGIN_LEFT + map_width * SQUARE}" y2="{line_y}" '
                    'stroke="#ffffff" stroke-opacity="0.12" stroke-width="1"/>')
    # The legend: only the letters this map uses.
    legend_top = MARGIN_TOP + map_height * SQUARE + 16
    for legend_number, letter in enumerate(legend_letters):
        left = 8 + (legend_number % 4) * 115
        top = legend_top + (legend_number // 4) * 18
        body.append(square_picture(letter, left, top, game_map["secret_look"], 0) + thing_picture(letter, left, top, 0))
        name = THINGS[letter][1] if letter in THINGS else SPECIAL_WALLS[letter]
        body.append(text(left + SQUARE + 5, top + 12, f"{letter} {name}", size=10, anchor="start"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{picture_width}" height="{picture_height}" '
            f'viewBox="0 0 {picture_width} {picture_height}">' + "".join(body) + "</svg>\n")


def index_page():
    """docs/maps/README.md: every map, level by level, with its numbers."""
    lines = ["# Map previews", "",
             "Every map of every level, seen from above. Made by `python3 src/map_preview.py` from the map files",
             "in `src/maps/` (don't edit these pictures: run the script again after changing a map).", "",
             "**Ammo ratio** = how much damage all the ammo lying on the map can do, divided by the health of all",
             "its monsters. Bigger = easier. **Health** = what its health packs give. Both are shown for easy /",
             "normal / hard: the difficulty changes monster health, how many supplies appear and how much each gives.", ""]
    for level_number, level in enumerate(LEVELS, start=1):
        lines += [f"## Level {level_number}: {level['name']} (episode {level['episode']})", ""]
        for map_letter, game_map in zip("ABCDEFGHI", level["maps"]):
            numbers = balance(game_map["rows"], game.config)
            file_name = map_list_name(level_number, map_letter) + ".svg"
            lines += [f"### Map {map_letter}: {game_map['name']}", "",
                      f"{len(game_map['rows'][0])} x {len(game_map['rows'])} squares · {numbers['monsters']} monsters · "
                      f"par {game_map['par_seconds']} s · {by_difficulty(game_map['rows'])}", "",
                      f"![{level['name']}, map {map_letter}]({file_name.replace(' ', '%20')})", ""]
    return "\n".join(lines)


def all_previews():
    """Every file this script writes: {file name: its text}."""
    files = {map_list_name(level_number, map_letter) + ".svg": map_picture(level_number, map_letter, level, game_map)
             for level_number, map_letter, level, game_map in every_map()}
    files["README.md"] = index_page()
    return files


if __name__ == "__main__":
    os.makedirs(PREVIEW_FOLDER, exist_ok=True)
    previews = all_previews()
    for old_file in os.listdir(PREVIEW_FOLDER):     # remove pictures of maps that no longer exist
        if old_file not in previews:
            os.remove(os.path.join(PREVIEW_FOLDER, old_file))
    for file_name, contents in previews.items():
        with open(os.path.join(PREVIEW_FOLDER, file_name), "w", encoding="utf-8", newline="\n") as preview_file:
            preview_file.write(contents)
    print(f"wrote {len(previews)} files to {os.path.normpath(PREVIEW_FOLDER)}")
