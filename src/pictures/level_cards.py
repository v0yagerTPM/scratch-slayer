"""The level intro cards and their LEVEL N headings: one card and one heading per map."""
from pictures.drawing import FIRE_STOPS, gradient, svg
from pictures.lettering import block_text, text_width
from levels import every_map

CARD_COLOR = "#120304"

# One card per MAP, from the records in src/levels.py: the level's name (in capitals) and its
# enemy, with the map's goal and glow color. A level with more than one map also shows which map
# this is: the map's name under the level's name, and a row of pips (filled = this map).
# Each card is keyed by (level number, map letter), the same as its costume name "card 1 B".
CARDS = {(level_number, map_letter): dict(level["card"], name=level["name"].upper(), goal=game_map["goal"],
                                          tint=game_map["tint"], map_name=game_map["name"],
                                          map_number=level["maps"].index(game_map) + 1, map_count=len(level["maps"]))
         for level_number, map_letter, level, game_map in every_map()}

def card(info):
    picture = (f'<defs><radialGradient id="glow" cx="0.7" cy="0.7" r="0.7"><stop offset="0" stop-color="{info["tint"]}"/>'
         f'<stop offset="1" stop-color="{CARD_COLOR}"/></radialGradient>'
         '<radialGradient id="spot"><stop offset="0" stop-color="#ffd9a0" stop-opacity="0.45"/>'
         '<stop offset="1" stop-color="#ffd9a0" stop-opacity="0"/></radialGradient></defs>'
         '<rect width="480" height="360" fill="url(#glow)"/>'
         '<rect x="8" y="8" width="464" height="344" rx="10" fill="none" stroke="#ff6a00" stroke-opacity="0.35" stroke-width="2"/>'
         '<ellipse cx="370" cy="302" rx="95" ry="18" fill="url(#spot)"/>')
    if info.get("map_count", 1) > 1:
        # WHICH MAP: "MAP" and a pip per map (this one filled), then the level's name with the
        # map's name under it. Everything sits a little higher to make room.
        picture += ('<text x="30" y="98" font-family="Sans Serif" font-size="10" font-weight="bold" fill="#ffd23f" '
                    'letter-spacing="2">MAP</text>')
        for pip_number in range(1, info["map_count"] + 1):
            fill = "#ff6a00" if pip_number == info["map_number"] else "none"
            picture += (f'<circle cx="{66 + 14 * (pip_number - 1)}" cy="94.5" r="4.5" fill="{fill}" '
                        'stroke="#ff6a00" stroke-width="1.5"/>')
        name_y, goal_y, line_y = 124, 166, 174
        picture += (f'<text x="30" y="146" font-family="Sans Serif" font-size="15" font-style="italic" font-weight="bold" '
                    f'fill="#ffb347" stroke="#000" stroke-width="2" paint-order="stroke">{info["map_name"]}</text>')
    else:
        name_y, goal_y, line_y = 132, 154, 168
    picture += (f'<text x="30" y="{name_y}" font-family="Sans Serif" font-size="{22 if len(info["name"]) < 16 else 18}" font-weight="bold" '
          f'fill="#ff4a24" stroke="#000" stroke-width="3" paint-order="stroke">{info["name"]}</text>'
          f'<text x="30" y="{goal_y}" font-family="Sans Serif" font-size="13" fill="#dddddd">{info["goal"]}</text>'
          f'<rect x="30" y="{line_y}" width="200" height="2" fill="#ff6a00" opacity="0.6"/>'
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

CARD_ART = {card_key: card(card_info) for card_key, card_info in CARDS.items()}

def heading_text(level_number, map_letter):
    """LEVEL 1 for a level with one map. With more maps, the map's letter too: LEVEL 1-B."""
    return f"LEVEL {level_number}" + (f"-{map_letter}" if CARDS[level_number, map_letter]["map_count"] > 1 else "")

HEADINGS = {card_key: heading(heading_text(*card_key)) for card_key in CARDS}
