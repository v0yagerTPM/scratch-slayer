"""The HUD around the 3D view: the panels and key slots, the arms panel, boss bars,
messages and the big red digits."""
from pictures.drawing import svg, text_label
from pictures.lettering import GLYPHS

def digit(character):
    rows = GLYPHS[character].split()
    lit_squares = [(column, row) for row, row_bits in enumerate(rows) for column, bit in enumerate(row_bits) if bit == "1"]
    shadow = "".join(f'<rect x="{column * 4 + 1}" y="{row * 4 + 1}" width="4" height="4" fill="#000"/>' for column, row in lit_squares)
    main = "".join(f'<rect x="{column * 4}" y="{row * 4}" width="4" height="4" fill="#ff4a24"/>' for column, row in lit_squares)
    return svg(21, 29, shadow + main)

DIGITS = {character: digit(character) for character in GLYPHS}

# ---------------- messages along the top of the screen ----------------
def toast(text, color="#ffffff"):
    box_width = max(200, 11 * len(text) + 40)
    return svg(480, 360, f'<rect x="{240 - box_width / 2}" y="14" width="{box_width}" height="32" rx="8" fill="#000" fill-opacity="0.6"/>'
                         f'<text x="240" y="36" font-family="Sans Serif" font-weight="bold" font-size="16" '
                         f'fill="{color}" text-anchor="middle">{text}</text>')

# Every message the Message sprite can show, in costume order. The key is the costume name
# without "message " (so "door hint" is the costume "message door hint").
MESSAGES = {
    "door hint": toast("Press E to open the door", "#ffe14d"),
    "switch hint": toast("Press E to flip the EXIT switch", "#40ff70"),
    "need red key": toast("You need the RED key to open this door", "#ff6060"),
    "need blue key": toast("You need the BLUE key to open this door", "#70a0ff"),
    "picked up 1": toast("+25 HEALTH", "#60ff80"),
    "picked up 2": toast("+8 SHELLS", "#ffd23f"),
    "picked up 3": toast("Picked up the RED KEY", "#ff6060"),
    "picked up 4": toast("Picked up the BLUE KEY", "#70a0ff"),
    "exit activated": toast("EXIT ACTIVATED", "#40ff70"),
    "found secret": toast("You found a secret area!", "#ffd23f"),
    "out of breath": toast("Out of breath! Wait for the sprint bar", "#ffa040"),
    "picked up 5": toast("Got the SKULL KEY! The exit unseals", "#d8a0ff"),
    "picked up 6": toast("+20 BULLETS", "#ffd23f"),
    "picked up 7": toast("+4 ROCKETS", "#ffa040"),
    "picked up 8": toast("SHOTGUN!  Press 3", "#ffe14d"),
    "picked up 9": toast("CHAINGUN!  Press 4", "#ffe14d"),
    "picked up 10": toast("ROCKET LAUNCHER!  Press 5", "#ffe14d"),
    "need skull key": toast("SEALED! Beat the boss for the SKULL KEY", "#d8a0ff"),
    "out of ammo": toast("Out of ammo! Switching weapons", "#ffa040"),
    "boss awake warden": toast("THE WARDEN AWAKENS", "#ff4040"),
    "boss awake colossus": toast("THE COLOSSUS AWAKENS", "#ff4040"),
    "boss enraged colossus": toast("THE COLOSSUS IS ENRAGED!", "#ff4040"),
    "music on": toast("Music ON  (N to switch)", "#60ff80"),
    "music off": toast("Music OFF  (N to switch)", "#aaaaaa"),
}

# ---------------- sprint ----------------
SPRINT_FRAME = ('<rect x="6" y="268" width="124" height="15" rx="4" fill="#000" fill-opacity="0.5"/>'
                '<text x="14" y="279" font-family="Sans Serif" font-weight="bold" font-size="9" fill="#d8d8d8" '
                'letter-spacing="1.5">SPRINT (HOLD Q)</text>'
                '<rect x="12" y="285" width="112" height="9" rx="3" fill="none" stroke="#d8d8d8" stroke-opacity="0.8" stroke-width="1.2"/>')

def hud_with_sprint(hud_svg):
    """The HUD frame plus the sprint bar's label and outline. The bar's fill is drawn with the pen."""
    return hud_svg.replace("</svg>", SPRINT_FRAME + "</svg>")

# ---------------- the HUD panels: health, ammo, key slots, arms, boss bars ----------------
def _key_slot(slot_x, color, have, skull=False):
    if not have:
        return (f'<rect x="{slot_x}" y="270" width="18" height="24" rx="2" fill="#000" fill-opacity="0.35" '
                'stroke="#777" stroke-dasharray="3 2"/>')
    if skull:
        return (f'<rect x="{slot_x}" y="270" width="18" height="24" rx="2" fill="#5a2a8a" stroke="#000" stroke-width="1.5"/>'
                f'<circle cx="{slot_x + 9}" cy="279" r="5.5" fill="#efe6c8"/>'
                f'<circle cx="{slot_x + 7}" cy="278.5" r="1.4" fill="#2a0010"/><circle cx="{slot_x + 11}" cy="278.5" r="1.4" fill="#2a0010"/>'
                f'<rect x="{slot_x + 7}" y="284" width="4" height="7" fill="#c9a227"/>')
    return (f'<rect x="{slot_x}" y="270" width="18" height="24" rx="2" fill="{color}" stroke="#000" stroke-width="1.5"/>'
            f'<rect x="{slot_x + 3}" y="274" width="7" height="6" fill="#f5d36b"/>')

def hud(red, blue, skull):
    """HEALTH box, the three key slots (red, blue, skull) and the sprint bar frame."""
    body = ('<rect x="6" y="298" width="124" height="56" rx="6" fill="#000" fill-opacity="0.5"/>'
            + text_label(14, 314, "HEALTH")
            + '<text x="94" y="350" font-family="Sans Serif" font-weight="bold" font-size="24" fill="#ff4a24">%</text>'
            '<rect x="400" y="264" width="74" height="34" rx="5" fill="#000" fill-opacity="0.45"/>'
            + _key_slot(404, "#e02424", red) + _key_slot(427, "#2a6cf0", blue) + _key_slot(450, "", skull, skull=True))
    return hud_with_sprint(svg(480, 360, body))

HUDS = [hud(red, blue, skull) for skull in (0, 1) for blue in (0, 1) for red in (0, 1)]   # index = red + 2*blue + 4*skull

WEAPON_NAMES = ["fist", "pistol", "shotgun", "chaingun", "rocket launcher"]

AMMO_LABELS = ["FISTS", "BULLETS", "SHELLS", "BULLETS", "ROCKETS"]

def arms(owned_code, current):
    """The ammo box (label for the weapon in your hands) and the ARMS row: which of the
    5 weapon slots you own (white), don't own yet (dark) and are holding (yellow)."""
    owned = [1, 1, owned_code & 1, (owned_code >> 1) & 1, (owned_code >> 2) & 1]
    picture = ('<rect x="350" y="298" width="124" height="56" rx="6" fill="#000" fill-opacity="0.5"/>'
         + text_label(358, 314, AMMO_LABELS[current - 1]))
    if current == 1:
        picture += ('<text x="412" y="342" font-family="Sans Serif" font-size="11" fill="#999" text-anchor="middle">'
              'no ammo needed</text>')
    picture += ('<rect x="350" y="240" width="124" height="21" rx="5" fill="#000" fill-opacity="0.45"/>'
          + text_label(356, 255, "ARMS", size=9, fill="#aaaaaa"))
    for slot in range(1, 6):
        slot_x = 400 + (slot - 1) * 16
        color = "#ffe14d" if slot == current else ("#e8e8e8" if owned[slot - 1] else "#4a4a4a")
        picture += (f'<text x="{slot_x}" y="256" font-family="Sans Serif" font-weight="bold" font-size="13" fill="{color}" '
              f'text-anchor="middle">{slot}</text>')
        if slot == current:
            picture += f'<rect x="{slot_x - 6}" y="258" width="12" height="2" fill="#ffe14d"/>'
    return svg(480, 360, picture)

ARMS = {(code, weapon_number): arms(code, weapon_number) for code in range(8) for weapon_number in range(1, 6)}

def boss_bar(name):
    box_width = 11 * len(name) + 30
    return svg(480, 360,
        f'<rect x="{240 - box_width / 2}" y="64" width="{box_width}" height="17" rx="5" fill="#000" fill-opacity="0.55"/>'
        + text_label(240, 77, name, "middle", 11, "#ffd23f")
        + '<rect x="140" y="82" width="200" height="8" rx="2" fill="none" stroke="#ffd23f" stroke-width="1.5"/>')

BOSS_BARS = {"warden": boss_bar("THE WARDEN"), "colossus": boss_bar("THE COLOSSUS")}
