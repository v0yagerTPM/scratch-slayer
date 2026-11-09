"""The level intro cards and their LEVEL N headings."""
from pictures.drawing import FIRE_STOPS, gradient, svg
from pictures.lettering import block_text, text_width
from levels import LEVELS

CARD_COLOR = "#120304"

# Each level's card, from the card settings in its record in src/levels.py. The card's title is the
# level's name in capitals.
CARDS = [dict(level["card"], name=level["name"].upper()) for level in LEVELS]

def card(info):
    picture = (f'<defs><radialGradient id="glow" cx="0.7" cy="0.7" r="0.7"><stop offset="0" stop-color="{info["tint"]}"/>'
         f'<stop offset="1" stop-color="{CARD_COLOR}"/></radialGradient>'
         '<radialGradient id="spot"><stop offset="0" stop-color="#ffd9a0" stop-opacity="0.45"/>'
         '<stop offset="1" stop-color="#ffd9a0" stop-opacity="0"/></radialGradient></defs>'
         '<rect width="480" height="360" fill="url(#glow)"/>'
         '<rect x="8" y="8" width="464" height="344" rx="10" fill="none" stroke="#ff6a00" stroke-opacity="0.35" stroke-width="2"/>'
         '<ellipse cx="370" cy="302" rx="95" ry="18" fill="url(#spot)"/>')
    picture += (f'<text x="30" y="132" font-family="Sans Serif" font-size="{22 if len(info["name"]) < 16 else 18}" font-weight="bold" '
          f'fill="#ff4a24" stroke="#000" stroke-width="3" paint-order="stroke">{info["name"]}</text>'
          f'<text x="30" y="154" font-family="Sans Serif" font-size="13" fill="#dddddd">{info["goal"]}</text>'
          '<rect x="30" y="168" width="200" height="2" fill="#ff6a00" opacity="0.6"/>'
          '<text x="30" y="192" font-family="Sans Serif" font-size="11" font-weight="bold" fill="#ffd23f" letter-spacing="2">NEW ENEMY</text>'
          f'<text x="30" y="218" font-family="Sans Serif" font-size="24" font-weight="bold" fill="#ffffff">{info["enemy"]}</text>')
    for line_number, line in enumerate(info["lines"]):
        picture += f'<text x="30" y="{242 + 16 * line_number}" font-family="Sans Serif" font-size="12" fill="#d8d8d8">{line}</text>'
    if info["boss"]:
        picture += (f'<text x="30" y="292" font-family="Sans Serif" font-size="12" font-weight="bold" fill="#ff5050">{info["boss"]}</text>')
    picture += '<text x="462" y="344" font-family="Sans Serif" font-size="10" fill="#8a8a8a" text-anchor="end">SPACE to skip</text>'
    return svg(480, 360, picture)

CARD_NEXT = card(dict(tint="#3a1a10", name="NEXT LEVEL", goal="Find the exit switch", enemy="?",
                      lines=["Stay sharp.", ""], boss=None))

def heading(text):
    unit = 8
    heading_width = text_width(text, unit) + 12
    body = "<defs>" + gradient("hfire", 4, 4 + 7 * unit, FIRE_STOPS) + "</defs>" + block_text(text, unit, 4, 4, "hfire")
    return svg(heading_width, 7 * unit + 14, body)

HEADING_NEXT = heading("NEXT LEVEL")

CARD_ART = [card(card_info) for card_info in CARDS]

HEADINGS = [heading(f"LEVEL {level_index + 1}") for level_index in range(len(CARDS))]
