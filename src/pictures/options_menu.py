"""The options menu: the panel, the row highlight, knobs, switches and difficulty words."""
from pictures.drawing import FIRE_STOPS, gradient, svg, text_label
from pictures.lettering import LETTERS, block_text, text_width

# The OPTIONS title uses an I with bars at the top and bottom, unlike the plain I in the other
# block-letter headings (YOU DIED, VICTORY).
OPTIONS_LETTERS = dict(LETTERS, I="11111 00100 00100 00100 00100 00100 11111")

OPTION_ROWS = ["TURN SPEED", "MOUSE STEERING", "MOUSE SENSITIVITY", "FIELD OF VIEW", "MUSIC", "DIFFICULTY",
               "START AT LEVEL", "MAP"]
TITLE_SCREEN_ONLY_ROWS = 3                            # the last 3 rows can't be changed while paused

OPTION_ROW_STEP = 25                                  # pixels between rows

OPTION_ROW_Y = [92 - OPTION_ROW_STEP * row for row in range(len(OPTION_ROWS))]   # stage y of each row

TRACK_LEFT, TRACK_RIGHT = 0, 120                    # stage x of the slider tracks

# The < > arrows (stage x) for the three "pick one" rows. They are only drawn on the title screen.
DIFFICULTY_ARROWS_X, LEVEL_ARROWS_X, MAP_ARROWS_X = (0, 100), (16, 84), (0, 100)

def options_panel(paused):
    picture = ('<rect width="480" height="360" fill="#000" fill-opacity="0.55"/>'
         '<rect x="44" y="28" width="392" height="306" rx="12" fill="#120304" fill-opacity="0.94" '
         'stroke="#ff6a00" stroke-opacity="0.6" stroke-width="2"/>')
    title = "PAUSED" if paused else "OPTIONS"
    unit = 5
    title_width = text_width(title, unit)
    picture += "<defs>" + gradient("ofire", 40, 40 + 7 * unit, FIRE_STOPS) + "</defs>"
    picture += block_text(title, unit, 240 - title_width / 2, 40, "ofire", font=OPTIONS_LETTERS)
    for name, stage_y in zip(OPTION_ROWS, OPTION_ROW_Y):
        picture_y = 180 - stage_y
        picture += text_label(70, picture_y + 5, name, size=12, fill="#e8d8c8")
        if name in ("TURN SPEED", "MOUSE SENSITIVITY", "FIELD OF VIEW"):
            picture += (f'<line x1="{240 + TRACK_LEFT}" y1="{picture_y}" x2="{240 + TRACK_RIGHT}" y2="{picture_y}" stroke="#4a3a34" '
                  'stroke-width="5" stroke-linecap="round"/>')
    level_y = 180 - OPTION_ROW_Y[6] + 5
    if paused:
        picture += (f'<text x="300" y="{level_y}" font-family="Sans Serif" font-size="11" fill="#8a8a8a" '
              'text-anchor="middle">(change these on the title screen)</text>')
    else:
        for arrows_x, row_y in ((DIFFICULTY_ARROWS_X, OPTION_ROW_Y[5]), (LEVEL_ARROWS_X, OPTION_ROW_Y[6]),
                                (MAP_ARROWS_X, OPTION_ROW_Y[7])):
            picture_y = 180 - row_y + 5
            picture += (f'<text x="{240 + arrows_x[0]}" y="{picture_y}" font-family="Sans Serif" font-size="16" font-weight="bold" '
                  f'fill="#ffd23f" text-anchor="middle">&lt;</text><text x="{240 + arrows_x[1]}" y="{picture_y}" '
                  'font-family="Sans Serif" font-size="16" font-weight="bold" fill="#ffd23f" '
                  'text-anchor="middle">&gt;</text>')
    picture += ('<text x="240" y="290" font-family="Sans Serif" font-size="11" fill="#cfcfcf" text-anchor="middle">'
          'UP / DOWN choose  •  LEFT / RIGHT change  •  or click and drag</text>')
    back = "P  to go back to the game" if paused else "O  to go back to the title screen"
    picture += (f'<text x="240" y="312" font-family="Sans Serif" font-size="12" font-weight="bold" fill="#ffe14d" '
          f'text-anchor="middle">{back}</text>')
    return svg(480, 360, picture)

OPTIONS_TITLE, OPTIONS_PAUSED = options_panel(False), options_panel(True)

ROW_HIGHLIGHT = svg(380, 24, '<rect x="1" y="1" width="378" height="22" rx="6" fill="#ff6a00" fill-opacity="0.2" '
                             'stroke="#ffb347" stroke-opacity="0.8" stroke-width="1.5"/>')

KNOB = svg(20, 20, '<circle cx="10" cy="10" r="8" fill="#ffd23f" stroke="#000" stroke-width="2"/>'
                   '<circle cx="8" cy="8" r="2.5" fill="#fff8d0"/>')

def _toggle(is_on):
    fill, text, text_x = ("#2f9e44", "ON", 20) if is_on else ("#4a4a4a", "OFF", 36)
    knob_x = 45 if is_on else 11
    return svg(56, 22, f'<rect x="1" y="1" width="54" height="20" rx="10" fill="{fill}" stroke="#000" stroke-width="1.5"/>'
                       f'<circle cx="{knob_x}" cy="11" r="8" fill="#f0f0f0"/>'
                       f'<text x="{text_x}" y="15.5" font-family="Sans Serif" font-size="11" font-weight="bold" fill="#fff" '
                       f'text-anchor="middle">{text}</text>')

TOGGLE_ON, TOGGLE_OFF = _toggle(True), _toggle(False)

# ---------------- difficulty words (options menu) ----------------
# One costume per difficulty, shown between the < > arrows on the DIFFICULTY row.
DIFFICULTY_COLORS = {"easy": "#60ff80", "normal": "#ffd23f", "hard": "#ff4a24"}

def difficulty_word(name):
    color = DIFFICULTY_COLORS[name]
    return svg(100, 22, f'<text x="50" y="17" font-family="Sans Serif" font-size="15" font-weight="bold" '
                        f'fill="{color}" stroke="#000" stroke-width="0.6" text-anchor="middle" '
                        f'letter-spacing="2">{name.upper()}</text>')

# ---------------- map words (options menu) ----------------
# The MAP row: RANDOM (each level picks one of its maps at random), or always map A, B, C ...
def map_word(text):
    color = "#ffd23f" if text == "RANDOM" else "#ff9a3c"
    return svg(100, 22, f'<text x="50" y="17" font-family="Sans Serif" font-size="15" font-weight="bold" '
                        f'fill="{color}" stroke="#000" stroke-width="0.6" text-anchor="middle" '
                        f'letter-spacing="2">{text}</text>')
