"""Art + sound for round 7: the difficulty setting and the end-of-level tally (kills, items and
secrets as percentages, your time and the par time). Everything is drawn here from scratch."""
import math, random
from assets import svg, _wav, RATE
import assets2

# =============================== DIFFICULTY WORDS (options menu) ===============================
# One costume per difficulty, shown between the < > arrows on the DIFFICULTY row.
DIFFICULTY_COLORS = {"easy": "#60ff80", "normal": "#ffd23f", "hard": "#ff4a24"}

def difficulty_word(name):
    color = DIFFICULTY_COLORS[name]
    return svg(100, 22, f'<text x="50" y="17" font-family="Sans Serif" font-size="15" font-weight="bold" '
                        f'fill="{color}" stroke="#000" stroke-width="0.6" text-anchor="middle" '
                        f'letter-spacing="2">{name.upper()}</text>')

# =============================== THE TALLY SCREEN ===============================
# Rows of the tally, as (label, text baseline y in the picture). The Digits sprite draws the
# numbers on top, centered 6 pixels above each baseline.
TALLY_ROWS = [("KILLS", 162), ("ITEMS", 194), ("SECRETS", 226), ("TIME", 268), ("PAR", 300)]
def tally_digit_y(row_number):
    """Stage y of the digits on tally row 1-5 (stage y = 180 - picture y)."""
    return 180 - (TALLY_ROWS[row_number - 1][1] - 6)

PERCENT_X = 110          # stage x of the right edge of the percentages (and of the seconds)
MINUTES_X = 48           # stage x of the right edge of the minutes, left of the colon
DIGIT_RED = "#ff4a24"

def _colon(baseline):
    """Two pixel squares, styled like the digits (with a black shadow)."""
    center = baseline - 6
    x = 240 + MINUTES_X + 5      # between the minutes and the tens digit of the seconds
    return "".join(f'<rect x="{x + 1}" y="{y + 1}" width="5" height="5" fill="#000"/>'
                   f'<rect x="{x}" y="{y}" width="5" height="5" fill="{DIGIT_RED}"/>'
                   for y in (center - 8, center + 3))

def tally_screen(title, subtitle=None, under_par=False):
    body = ""
    for label, baseline in TALLY_ROWS:
        fill = "#9a9a9a" if label == "PAR" else "#d8d8d8"
        body += assets2._label(110, baseline, label, size=18, fill=fill)
    for _, baseline in TALLY_ROWS[:3]:
        body += (f'<text x="{240 + PERCENT_X + 4}" y="{baseline + 4}" font-family="Sans Serif" font-weight="bold" '
                 f'font-size="26" fill="{DIGIT_RED}" stroke="#000" stroke-width="1">%</text>')
    body += '<line x1="100" y1="244" x2="380" y2="244" stroke="#ffffff" stroke-opacity="0.2" stroke-width="2"/>'
    for _, baseline in TALLY_ROWS[3:]:
        body += _colon(baseline)
    if under_par:
        body += ('<rect x="364" y="249" width="102" height="24" rx="6" fill="#3a2a00" stroke="#ffd23f" stroke-width="2"/>'
                 '<text x="415" y="266" font-family="Sans Serif" font-size="13" font-weight="bold" fill="#ffd23f" '
                 'text-anchor="middle" letter-spacing="1">UNDER PAR!</text>')
    lines = [("Press SPACE to continue", 338, 16, "#ffe14d")]
    if subtitle:
        lines.append((subtitle, 126, 13, "#ffb080"))
    art = assets2._screen(title, "#40ff70", lines, body, 0.88)
    if subtitle:   # a long title needs smaller letters to fit
        art = art.replace('font-size="40" fill="#40ff70"', 'font-size="30" fill="#40ff70"', 1)
    return art

EPISODE_1_SUBTITLE = "The Warden has fallen... but something stirs far below."
TALLY_SCREENS = {
    "screen level complete": tally_screen("LEVEL COMPLETE"),
    "screen level complete under par": tally_screen("LEVEL COMPLETE", under_par=True),
    "screen episode complete": tally_screen("EPISODE 1 COMPLETE", EPISODE_1_SUBTITLE),
    "screen episode complete under par": tally_screen("EPISODE 1 COMPLETE", EPISODE_1_SUBTITLE, under_par=True),
}

# =============================== SOUNDS ===============================
def tally_tick():
    """A short metallic click while the numbers count up."""
    sample_count = int(RATE * 0.025)
    noise = random.Random(71)
    return _wav([(math.sin(2 * math.pi * 2200 * (i / RATE)) * 0.5 + noise.uniform(-0.3, 0.3))
                 * math.exp(-(i / RATE) * 180) for i in range(sample_count)])

def tally_done():
    """A low thump when the counting finishes."""
    sample_count = int(RATE * 0.25)
    out = []
    for i in range(sample_count):
        seconds = i / RATE
        pitch = 140 - 260 * seconds
        out.append(math.sin(2 * math.pi * pitch * seconds) * 0.9 * math.exp(-seconds * 14))
    return _wav(out)
