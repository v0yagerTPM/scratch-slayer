"""Every monster's four costumes (walk 1, walk 2, attack, dead): imp, spitter, golem,
warden, charger, wraith and colossus."""
from pictures.drawing import svg

# ---------------- imp (level 1) ----------------
IMP_OUTLINE = 'stroke="#2a0e04" stroke-width="1.5"'

SKIN, SKIN2, CHEST, BONE = "#8b3a1a", "#6e2c12", "#a8542b", "#e0d6b0"

def _head():
    return (f'<path d="M31 22 Q21 11 25 1 Q29 12 36 17 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>'
            f'<path d="M49 22 Q59 11 55 1 Q51 12 44 17 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>'
            f'<ellipse cx="40" cy="28" rx="14" ry="13" fill="{SKIN}" {IMP_OUTLINE}/>'
            '<path d="M28 23 L40 27 L52 23 L52 25 L40 29 L28 25 Z" fill="#3a1206"/>'
            '<ellipse cx="34" cy="28" rx="3.6" ry="2.6" fill="#ffe14d"/>'
            '<ellipse cx="46" cy="28" rx="3.6" ry="2.6" fill="#ffe14d"/>'
            '<circle cx="34" cy="28" r="1.2" fill="#c00"/><circle cx="46" cy="28" r="1.2" fill="#c00"/>'
            '<path d="M32 34 Q40 41 48 34 L46 37 Q40 43 34 37 Z" fill="#2a0000"/>'
            '<path d="M35 35.5 L36.5 38 L38 36.3 L40 38.5 L42 36.3 L43.5 38 L45 35.5 Z" fill="#fff"/>')

def _body():
    return (f'<ellipse cx="40" cy="64" rx="21" ry="25" fill="{SKIN}" {IMP_OUTLINE}/>'
            f'<ellipse cx="40" cy="68" rx="12" ry="15" fill="{CHEST}"/>'
            '<path d="M32 62 Q40 65 48 62 M31 69 Q40 72 49 69 M32 76 Q40 79 48 76" stroke="#6e2c12" stroke-width="1.5" fill="none"/>'
            f'<path d="M19 46 L13 37 L24 43 Z M61 46 L67 37 L56 43 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>')

def _claws(left, top, pointing_up=False):
    direction = -1 if pointing_up else 1
    return "".join(f'<path d="M{left+claw_number*3-1} {top} L{left+claw_number*3} {top+6*direction} L{left+claw_number*3+1.5} {top} Z" fill="{BONE}"/>' for claw_number in range(3))

def _legs(lift_left=False, lift_right=False):
    left_foot_y = 108 if lift_left else 116
    right_foot_y = 108 if lift_right else 116
    return (f'<path d="M28 84 L24 {left_foot_y} L34 {left_foot_y} L37 86 Z" fill="{SKIN2}" {IMP_OUTLINE}/>'
            f'<path d="M52 84 L56 {right_foot_y} L46 {right_foot_y} L43 86 Z" fill="{SKIN2}" {IMP_OUTLINE}/>'
            f'<path d="M21 {left_foot_y} L36 {left_foot_y} L35 {left_foot_y+3} L20 {left_foot_y+3} Z" fill="#2a0e04"/>'
            f'<path d="M44 {right_foot_y} L59 {right_foot_y} L60 {right_foot_y+3} L45 {right_foot_y+3} Z" fill="#2a0e04"/>')

def _arms_down(swing=0):
    return (f'<path d="M21 50 Q{10+swing} 70 {13+swing} 90 L{20+swing} 90 Q{18+swing} 72 27 58 Z" fill="#7a3215" {IMP_OUTLINE}/>'
            f'<path d="M59 50 Q{70-swing} 70 {67-swing} 90 L{60-swing} 90 Q{62-swing} 72 53 58 Z" fill="#7a3215" {IMP_OUTLINE}/>'
            + _claws(13 + swing, 90) + _claws(60 - swing, 90))

def _arms_up():
    return (f'<path d="M22 50 Q8 34 12 12 L19 12 Q17 32 28 46 Z" fill="#7a3215" {IMP_OUTLINE}/>'
            f'<path d="M58 50 Q72 34 68 12 L61 12 Q63 32 52 46 Z" fill="#7a3215" {IMP_OUTLINE}/>'
            + _claws(12, 12, pointing_up=True) + _claws(61, 12, pointing_up=True))

IMP_WALK1 = svg(80, 120, _legs(lift_left=True) + _arms_down(2) + _body() + _head())

IMP_WALK2 = svg(80, 120, _legs(lift_right=True) + _arms_down(-2) + _body() + _head())

IMP_ATTACK = svg(80, 120, _legs() + _arms_up() + _body() + _head())

IMP_DEAD = svg(80, 120,
    '<ellipse cx="40" cy="114" rx="36" ry="6" fill="#3d0f04" opacity="0.85"/>'
    f'<ellipse cx="44" cy="108" rx="25" ry="8" fill="#7a3215" {IMP_OUTLINE}/>'
    f'<ellipse cx="44" cy="106" rx="14" ry="4" fill="{CHEST}"/>'
    f'<ellipse cx="18" cy="107" rx="9" ry="7" fill="{SKIN}" {IMP_OUTLINE}/>'
    f'<path d="M14 101 Q6 94 2 98 Q8 100 12 104 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>'
    '<path d="M15 105 l3 3 m0 -3 l-3 3 M20 105 l3 3 m0 -3 l-3 3" stroke="#222" stroke-width="1.2"/>'
    + _claws(66, 110))

# ---------------- spitter (level 2) ----------------
# A squat slime creature with three eyes and a sac on its back. 80 x 120, feet at the bottom.
SLIME, SLIME_DARK, SLIME_LIGHT = "#5fae3c", "#356f1f", "#9fe06a"

SPITTER_OUTLINE = 'stroke="#1d3d10" stroke-width="1.5"'

def _spitter_legs(phase):
    out = ""
    for leg_number, leg_x in enumerate((16, 30, 50, 64)):
        lift = 5 if (leg_number + phase) % 2 == 0 else 0
        out += f'<path d="M{leg_x - 4} 100 L{leg_x - 6} {118 - lift} L{leg_x + 6} {118 - lift} L{leg_x + 4} 100 Z" fill="{SLIME_DARK}" {SPITTER_OUTLINE}/>'
    return out

def _spitter(phase=0, mouth="closed"):
    body = (_spitter_legs(phase)
            + f'<ellipse cx="46" cy="66" rx="20" ry="16" fill="{SLIME_LIGHT}" opacity="0.85" {SPITTER_OUTLINE}/>'
              '<circle cx="40" cy="60" r="3" fill="#d7ff9e"/><circle cx="52" cy="66" r="2.5" fill="#d7ff9e"/>'
            + f'<ellipse cx="40" cy="88" rx="32" ry="20" fill="{SLIME}" {SPITTER_OUTLINE}/>'
              f'<circle cx="22" cy="84" r="3.5" fill="{SLIME_DARK}"/><circle cx="58" cy="94" r="3" fill="{SLIME_DARK}"/>'
              f'<circle cx="62" cy="80" r="2.5" fill="{SLIME_DARK}"/>')
    eyes = "".join(f'<circle cx="{eye_x}" cy="{eye_y}" r="5" fill="#ffe14d" stroke="#1d3d10" stroke-width="1"/>'
                   f'<circle cx="{eye_x}" cy="{eye_y}" r="2" fill="#000"/>' for eye_x, eye_y in ((29, 74), (40, 70), (51, 74)))
    if mouth == "open":
        mouth = ('<ellipse cx="40" cy="92" rx="15" ry="11" fill="#1a0d05"/>'
             '<path d="M27 86 L30 91 L33 86 L36 91 L40 86 L44 91 L47 86 L50 91 L53 86" fill="none" stroke="#fff" stroke-width="2"/>'
             '<circle cx="40" cy="94" r="7" fill="#b6ff3a" stroke="#4c8f12" stroke-width="1.5"/>'
             '<circle cx="38" cy="92" r="2" fill="#f2ffd0"/>')
    else:
        mouth = ('<path d="M28 92 Q40 100 52 92 Q40 96 28 92 Z" fill="#1a0d05" stroke="#1d3d10"/>'
             '<path d="M44 96 Q45 102 43 106" stroke="#b6ff3a" stroke-width="2" fill="none"/>')
    return svg(80, 120, body + eyes + mouth)

SPITTER_WALK1, SPITTER_WALK2, SPITTER_ATTACK = _spitter(0), _spitter(1), _spitter(0, "open")

SPITTER_DEAD = svg(80, 120,
    f'<ellipse cx="40" cy="113" rx="36" ry="7" fill="{SLIME_DARK}" opacity="0.9"/>'
    f'<ellipse cx="38" cy="109" rx="24" ry="7" fill="{SLIME}" {SPITTER_OUTLINE}/>'
    '<circle cx="30" cy="107" r="3" fill="#ffe14d"/><circle cx="44" cy="106" r="3" fill="#ffe14d"/>'
    '<path d="M28 105 l4 4 m0 -4 l-4 4 M42 104 l4 4 m0 -4 l-4 4" stroke="#222" stroke-width="1.2"/>'
    '<circle cx="64" cy="113" r="3" fill="#b6ff3a"/><circle cx="12" cy="112" r="2" fill="#b6ff3a"/>')

# ---------------- golem (level 3) ----------------
# A hulking stone creature with glowing cracks and huge fists.
STONE, STONE_DARK, GOLEM_GLOW = "#6f6878", "#4a4452", "#ff8a1f"

GOLEM_OUTLINE = 'stroke="#25212b" stroke-width="1.5"'

def _golem_legs(phase):
    left_foot_y, right_foot_y = (108, 116) if phase == 0 else (116, 108)
    return (f'<path d="M24 86 L20 {left_foot_y} L36 {left_foot_y} L38 86 Z" fill="{STONE_DARK}" {GOLEM_OUTLINE}/>'
            f'<path d="M56 86 L60 {right_foot_y} L44 {right_foot_y} L42 86 Z" fill="{STONE_DARK}" {GOLEM_OUTLINE}/>'
            f'<rect x="16" y="{left_foot_y}" width="24" height="7" rx="2" fill="#2f2a36"/>'
            f'<rect x="40" y="{right_foot_y}" width="24" height="7" rx="2" fill="#2f2a36"/>')

def _golem_body():
    return (f'<path d="M16 42 L64 42 L58 90 L22 90 Z" fill="{STONE}" {GOLEM_OUTLINE}/>'
            f'<path d="M30 50 L36 62 L32 74 M50 48 L46 60 L52 70 M40 78 L44 86" stroke="{GOLEM_GLOW}" stroke-width="2.5" fill="none"/>'
            f'<rect x="28" y="20" width="24" height="22" rx="6" fill="{STONE}" {GOLEM_OUTLINE}/>'
            f'<rect x="31" y="27" width="7" height="4" fill="{GOLEM_GLOW}"/><rect x="42" y="27" width="7" height="4" fill="{GOLEM_GLOW}"/>'
            '<path d="M33 37 H47" stroke="#25212b" stroke-width="2"/>')

def _golem_arms_down(swing):
    return (f'<path d="M16 46 Q{6 + swing} 66 {8 + swing} 84 L{18 + swing} 84 Q{18 + swing} 66 24 52 Z" fill="{STONE_DARK}" {GOLEM_OUTLINE}/>'
            f'<path d="M64 46 Q{74 - swing} 66 {72 - swing} 84 L{62 - swing} 84 Q{62 - swing} 66 56 52 Z" fill="{STONE_DARK}" {GOLEM_OUTLINE}/>'
            f'<rect x="{3 + swing}" y="82" width="20" height="18" rx="5" fill="{STONE}" {GOLEM_OUTLINE}/>'
            f'<rect x="{57 - swing}" y="82" width="20" height="18" rx="5" fill="{STONE}" {GOLEM_OUTLINE}/>')

def _golem_arms_up():
    return (f'<path d="M18 46 Q6 30 10 12 L20 12 Q20 30 28 42 Z" fill="{STONE_DARK}" {GOLEM_OUTLINE}/>'
            f'<path d="M62 46 Q74 30 70 12 L60 12 Q60 30 52 42 Z" fill="{STONE_DARK}" {GOLEM_OUTLINE}/>'
            f'<rect x="4" y="0" width="20" height="18" rx="5" fill="{STONE}" {GOLEM_OUTLINE}/>'
            f'<rect x="56" y="0" width="20" height="18" rx="5" fill="{STONE}" {GOLEM_OUTLINE}/>')

GOLEM_WALK1 = svg(80, 120, _golem_legs(0) + _golem_body() + _golem_arms_down(2))

GOLEM_WALK2 = svg(80, 120, _golem_legs(1) + _golem_body() + _golem_arms_down(-2))

GOLEM_ATTACK = svg(80, 120, _golem_legs(0) + _golem_arms_up() + _golem_body())

GOLEM_DEAD = svg(80, 120,
    ''.join(f'<path d="M{rubble_x} 120 L{rubble_x + 4} {rubble_top} L{rubble_x + rubble_width - 3} {rubble_top - 2} L{rubble_x + rubble_width} 120 Z" fill="{rubble_color}" {GOLEM_OUTLINE}/>'
            for rubble_x, rubble_top, rubble_width, rubble_color in ((6, 104, 22, STONE_DARK), (24, 98, 26, STONE), (46, 104, 24, STONE_DARK), (16, 108, 16, STONE)))
    + f'<path d="M30 108 L36 114 M50 110 L46 116" stroke="{GOLEM_GLOW}" stroke-width="2" opacity="0.6"/>')

# ---------------- warden (boss) ----------------
# Tall armored demon lord: crimson plate, gold trim, glowing visor, fire in hand.
ARMOR, ARMOR_DARK, GOLD, CAPE = "#7a1527", "#4a0b17", "#d8a83c", "#3b0610"

WARDEN_OUTLINE = 'stroke="#1a0308" stroke-width="1.5"'

def _warden_legs(phase):
    left_foot_y, right_foot_y = (110, 117) if phase == 0 else (117, 110)
    return (f'<path d="M28 82 L26 {left_foot_y} L37 {left_foot_y} L38 82 Z" fill="{ARMOR_DARK}" {WARDEN_OUTLINE}/>'
            f'<path d="M52 82 L54 {right_foot_y} L43 {right_foot_y} L42 82 Z" fill="{ARMOR_DARK}" {WARDEN_OUTLINE}/>'
            f'<path d="M22 {left_foot_y} H38 V{left_foot_y + 3} H22 Z" fill="{GOLD}"/><path d="M42 {right_foot_y} H58 V{right_foot_y + 3} H42 Z" fill="{GOLD}"/>')

def _warden_body():
    return (f'<path d="M20 40 L60 40 L70 104 L10 104 Z" fill="{CAPE}" opacity="0.95"/>'
            f'<path d="M24 40 L56 40 L54 84 L26 84 Z" fill="{ARMOR}" {WARDEN_OUTLINE}/>'
            f'<path d="M26 60 H54 M28 72 H52" stroke="{GOLD}" stroke-width="2"/>'
            f'<path d="M40 44 L46 52 L40 60 L34 52 Z" fill="{GOLD}"/>'
            f'<ellipse cx="22" cy="44" rx="8" ry="6" fill="{GOLD}" {WARDEN_OUTLINE}/><ellipse cx="58" cy="44" rx="8" ry="6" fill="{GOLD}" {WARDEN_OUTLINE}/>'
            f'<path d="M30 16 Q40 8 50 16 L50 36 L30 36 Z" fill="{ARMOR_DARK}" {WARDEN_OUTLINE}/>'
            f'<path d="M30 18 Q20 8 22 0 Q28 10 34 14 Z M50 18 Q60 8 58 0 Q52 10 46 14 Z" fill="#e8dcb8" stroke="#5a5030"/>'
            '<rect x="33" y="24" width="14" height="4" rx="1" fill="#ffdd55"/>')

def _warden_arms(raised):
    if raised:
        return (f'<path d="M24 44 Q12 30 18 14 L26 16 Q22 30 30 40 Z" fill="{ARMOR}" {WARDEN_OUTLINE}/>'
                f'<path d="M56 44 Q68 30 62 14 L54 16 Q58 30 50 40 Z" fill="{ARMOR}" {WARDEN_OUTLINE}/>'
                '<circle cx="40" cy="10" r="10" fill="#ffd23f" opacity="0.6"/><circle cx="40" cy="10" r="6" fill="#fff6c0"/>'
                '<circle cx="22" cy="12" r="5" fill="#ff7a00"/><circle cx="58" cy="12" r="5" fill="#ff7a00"/>')
    return (f'<path d="M24 44 Q14 62 16 80 L24 80 Q24 64 30 52 Z" fill="{ARMOR}" {WARDEN_OUTLINE}/>'
            f'<path d="M56 44 Q66 62 64 80 L56 80 Q56 64 50 52 Z" fill="{ARMOR}" {WARDEN_OUTLINE}/>'
            '<circle cx="62" cy="84" r="7" fill="#ff7a00" opacity="0.8"/><circle cx="62" cy="84" r="4" fill="#ffe680"/>')

WARDEN_WALK1 = svg(80, 120, _warden_legs(0) + _warden_body() + _warden_arms(False))

WARDEN_WALK2 = svg(80, 120, _warden_legs(1) + _warden_body() + _warden_arms(False))

WARDEN_ATTACK = svg(80, 120, _warden_legs(0) + _warden_body() + _warden_arms(True))

WARDEN_DEAD = svg(80, 120,
    f'<path d="M4 118 Q40 96 76 118 Z" fill="{CAPE}"/>'
    f'<path d="M18 116 L24 102 L56 100 L62 116 Z" fill="{ARMOR}" {WARDEN_OUTLINE}/>'
    f'<path d="M24 108 H56" stroke="{GOLD}" stroke-width="2"/>'
    f'<path d="M58 110 Q66 98 76 104 L74 116 L58 116 Z" fill="{ARMOR_DARK}" {WARDEN_OUTLINE}/>'
    '<path d="M64 102 Q70 92 72 86 Q72 96 68 104 Z" fill="#e8dcb8" stroke="#5a5030"/>'
    '<rect x="62" y="108" width="10" height="3" fill="#5a4a20"/>')

# ---------------- charger (level 4) ----------------
# A hunched, horned brute that lowers its head and charges in a straight line.
HIDE, HIDE_DARK, HIDE_LIGHT, HORN = "#5b6474", "#3c4250", "#7d889c", "#e8dcb8"

CHARGER_OUTLINE = 'stroke="#161a22" stroke-width="1.5"'

def _charger_legs(phase):
    left_foot_y, right_foot_y = (106, 116) if phase == 0 else (116, 106)
    return (f'<path d="M22 86 L18 {left_foot_y} L32 {left_foot_y} L34 88 Z" fill="{HIDE_DARK}" {CHARGER_OUTLINE}/>'
            f'<path d="M58 86 L62 {right_foot_y} L48 {right_foot_y} L46 88 Z" fill="{HIDE_DARK}" {CHARGER_OUTLINE}/>'
            f'<path d="M16 {left_foot_y} H34 V{left_foot_y + 4} H16 Z M46 {right_foot_y} H64 V{right_foot_y + 4} H46 Z" fill="#222"/>')

def _charger_body(lowered):
    head_y = 54 if lowered else 40          # head height: lowered = about to charge
    eye = "#ff2a00" if lowered else "#ffb000"
    picture = (f'<ellipse cx="40" cy="66" rx="30" ry="26" fill="{HIDE}" {CHARGER_OUTLINE}/>'
         f'<path d="M14 54 Q40 30 66 54" fill="{HIDE_LIGHT}" opacity="0.5"/>'
         f'<path d="M22 70 Q40 78 58 70 M24 80 Q40 86 56 80" stroke="{HIDE_DARK}" stroke-width="2" fill="none"/>'
         f'<path d="M10 64 Q4 78 8 94 L18 94 Q16 80 20 70 Z" fill="{HIDE_DARK}" {CHARGER_OUTLINE}/>'
         f'<path d="M70 64 Q76 78 72 94 L62 94 Q64 80 60 70 Z" fill="{HIDE_DARK}" {CHARGER_OUTLINE}/>'
         f'<ellipse cx="40" cy="{head_y}" rx="15" ry="12" fill="{HIDE_DARK}" {CHARGER_OUTLINE}/>'
         f'<path d="M27 {head_y - 4} Q12 {head_y - 10} 10 {head_y - 24} Q20 {head_y - 14} 30 {head_y - 10} Z" fill="{HORN}" stroke="#5a5030"/>'
         f'<path d="M53 {head_y - 4} Q68 {head_y - 10} 70 {head_y - 24} Q60 {head_y - 14} 50 {head_y - 10} Z" fill="{HORN}" stroke="#5a5030"/>'
         f'<ellipse cx="34" cy="{head_y - 2}" rx="3" ry="2.2" fill="{eye}"/><ellipse cx="46" cy="{head_y - 2}" rx="3" ry="2.2" fill="{eye}"/>'
         f'<path d="M33 {head_y + 6} Q40 {head_y + 11} 47 {head_y + 6}" stroke="#111" stroke-width="2" fill="none"/>'
         f'<circle cx="37" cy="{head_y + 4}" r="1.3" fill="#111"/><circle cx="43" cy="{head_y + 4}" r="1.3" fill="#111"/>')
    if lowered:   # snorting steam
        picture += (f'<circle cx="28" cy="{head_y + 12}" r="5" fill="#ddd" opacity="0.55"/><circle cx="22" cy="{head_y + 16}" r="4" fill="#ddd" opacity="0.4"/>'
              f'<circle cx="52" cy="{head_y + 12}" r="5" fill="#ddd" opacity="0.55"/><circle cx="58" cy="{head_y + 16}" r="4" fill="#ddd" opacity="0.4"/>')
    return picture

CHARGER_WALK1 = svg(80, 120, _charger_legs(0) + _charger_body(False))

CHARGER_WALK2 = svg(80, 120, _charger_legs(1) + _charger_body(False))

CHARGER_ATTACK = svg(80, 120, _charger_legs(0) + _charger_body(True))

CHARGER_DEAD = svg(80, 120,
    '<ellipse cx="40" cy="114" rx="38" ry="6" fill="#20242c" opacity="0.85"/>'
    f'<ellipse cx="42" cy="104" rx="30" ry="12" fill="{HIDE}" {CHARGER_OUTLINE}/>'
    f'<ellipse cx="14" cy="108" rx="11" ry="8" fill="{HIDE_DARK}" {CHARGER_OUTLINE}/>'
    f'<path d="M8 104 Q-2 96 2 88 Q6 98 12 100 Z" fill="{HORN}" stroke="#5a5030"/>'
    '<path d="M10 106 l3 3 m0 -3 l-3 3" stroke="#111" stroke-width="1.3"/>'
    f'<path d="M60 112 L76 108 L74 116 Z" fill="{HIDE_DARK}" {CHARGER_OUTLINE}/>')

# ---------------- wraith (level 5) ----------------
# A floating hooded shade with glowing eyes. It is drawn solid; the game fades it with distance.
ROBE, ROBE_DARK, WRAITH_GLOW = "#4a4060", "#2a2238", "#7ff6ff"

WRAITH_OUTLINE = 'stroke="#120c1c" stroke-width="1.5"'

def _wraith_tail(phase):
    sway = 5 if phase == 0 else -5
    return (f'<path d="M16 70 Q12 96 {20 + sway} 116 L{28 + sway} 104 L{36 - sway} 118 L{44 + sway} 104 L{52 - sway} 117 '
            f'L{58 + sway} 102 Q68 92 64 70 Z" fill="{ROBE_DARK}" {WRAITH_OUTLINE} opacity="0.95"/>')

def _wraith_top(reaching):
    picture = (f'<path d="M20 74 Q14 40 26 22 Q40 4 54 22 Q66 40 60 74 Z" fill="{ROBE}" {WRAITH_OUTLINE}/>'
         f'<path d="M28 30 Q40 16 52 30 Q54 46 40 50 Q26 46 28 30 Z" fill="#0b0712"/>'
         f'<ellipse cx="34" cy="36" rx="3.5" ry="2.4" fill="{WRAITH_GLOW}"/><ellipse cx="46" cy="36" rx="3.5" ry="2.4" fill="{WRAITH_GLOW}"/>'
         f'<ellipse cx="40" cy="36" rx="14" ry="7" fill="{WRAITH_GLOW}" opacity="0.15"/>'
         f'<path d="M24 56 Q40 62 56 56" stroke="{ROBE_DARK}" stroke-width="2" fill="none"/>')
    if reaching:
        picture += (f'<path d="M22 52 Q6 38 4 22 L12 20 Q14 34 28 44 Z" fill="{ROBE}" {WRAITH_OUTLINE}/>'
              f'<path d="M58 52 Q74 38 76 22 L68 20 Q66 34 52 44 Z" fill="{ROBE}" {WRAITH_OUTLINE}/>'
              '<path d="M4 22 L1 14 M7 21 L6 12 M10 21 L11 13 M76 22 L79 14 M73 21 L74 12 M70 21 L69 13" '
              f'stroke="{WRAITH_GLOW}" stroke-width="1.8" stroke-linecap="round"/>')
    else:
        picture += (f'<path d="M22 50 Q10 62 12 80 L19 80 Q19 66 28 56 Z" fill="{ROBE}" {WRAITH_OUTLINE}/>'
              f'<path d="M58 50 Q70 62 68 80 L61 80 Q61 66 52 56 Z" fill="{ROBE}" {WRAITH_OUTLINE}/>')
    return picture

WRAITH_WALK1 = svg(80, 120, _wraith_tail(0) + _wraith_top(False))

WRAITH_WALK2 = svg(80, 120, _wraith_tail(1) + _wraith_top(False))

WRAITH_ATTACK = svg(80, 120, _wraith_tail(0) + _wraith_top(True))

WRAITH_DEAD = svg(80, 120,
    f'<ellipse cx="40" cy="114" rx="30" ry="5" fill="{WRAITH_GLOW}" opacity="0.25"/>'
    f'<path d="M10 116 Q20 96 40 98 Q60 96 70 116 Z" fill="{ROBE_DARK}" {WRAITH_OUTLINE}/>'
    f'<path d="M26 112 Q40 100 54 112" stroke="{ROBE}" stroke-width="3" fill="none"/>'
    f'<circle cx="40" cy="92" r="4" fill="{WRAITH_GLOW}" opacity="0.5"/><circle cx="34" cy="82" r="2.5" fill="{WRAITH_GLOW}" opacity="0.35"/>'
    f'<circle cx="46" cy="74" r="1.8" fill="{WRAITH_GLOW}" opacity="0.25"/>')

# ---------------- colossus (level 6 boss) ----------------
# An armored giant with a furnace in its chest, a cannon arm and a claw.
PLATE, PLATE_DARK, CORE = "#4b4f57", "#2c2f35", "#ff7a1a"

COLOSSUS_OUTLINE = 'stroke="#121317" stroke-width="1.6"'

def _colossus_legs(phase):
    left_foot_y, right_foot_y = (108, 117) if phase == 0 else (117, 108)
    return (f'<path d="M22 84 L18 {left_foot_y} L36 {left_foot_y} L36 86 Z" fill="{PLATE_DARK}" {COLOSSUS_OUTLINE}/>'
            f'<path d="M58 84 L62 {right_foot_y} L44 {right_foot_y} L44 86 Z" fill="{PLATE_DARK}" {COLOSSUS_OUTLINE}/>'
            f'<path d="M14 {left_foot_y} H38 V{left_foot_y + 4} H14 Z M42 {right_foot_y} H66 V{right_foot_y + 4} H42 Z" fill="#1a1a1a"/>')

def _colossus_body(firing):
    glow = "#ffe680" if firing else "#ffb347"
    picture = (f'<path d="M14 30 L66 30 L60 88 L20 88 Z" fill="{PLATE}" {COLOSSUS_OUTLINE}/>'
         f'<path d="M14 30 L66 30 L62 44 L18 44 Z" fill="#5d626c"/>'
         f'<circle cx="40" cy="60" r="12" fill="{PLATE_DARK}" {COLOSSUS_OUTLINE}/>'
         f'<circle cx="40" cy="60" r="8" fill="{CORE}"/><circle cx="40" cy="60" r="4" fill="{glow}"/>'
         f'<path d="M22 50 H32 M48 50 H58 M24 76 H56" stroke="{PLATE_DARK}" stroke-width="2"/>'
         f'<rect x="30" y="12" width="20" height="18" rx="4" fill="{PLATE_DARK}" {COLOSSUS_OUTLINE}/>'
         f'<rect x="33" y="18" width="14" height="4" rx="1" fill="{CORE}"/>'
         f'<path d="M30 14 L24 4 L32 10 Z M50 14 L56 4 L48 10 Z" fill="#8a8f99"/>'
         # claw arm (left)
         f'<path d="M14 34 Q2 50 6 70 L14 70 Q12 54 20 42 Z" fill="{PLATE}" {COLOSSUS_OUTLINE}/>'
         '<path d="M4 70 L2 80 M8 71 L8 82 M12 70 L14 80" stroke="#c9ccd2" stroke-width="2.5" stroke-linecap="round"/>')
    if firing:   # cannon raised and blazing
        picture += (f'<path d="M66 34 Q76 24 76 10 L68 8 Q66 22 58 30 Z" fill="{PLATE}" {COLOSSUS_OUTLINE}/>'
              f'<rect x="64" y="0" width="14" height="12" rx="3" fill="{PLATE_DARK}" {COLOSSUS_OUTLINE}/>'
              '<circle cx="71" cy="2" r="7" fill="#c060ff" opacity="0.6"/><circle cx="71" cy="2" r="3.5" fill="#f0d0ff"/>')
    else:
        picture += (f'<path d="M66 34 Q78 50 74 70 L66 70 Q68 54 60 42 Z" fill="{PLATE}" {COLOSSUS_OUTLINE}/>'
              f'<rect x="64" y="68" width="14" height="14" rx="3" fill="{PLATE_DARK}" {COLOSSUS_OUTLINE}/>'
              '<circle cx="71" cy="80" r="3" fill="#c060ff"/>')
    return picture

COLOSSUS_WALK1 = svg(80, 120, _colossus_legs(0) + _colossus_body(False))

COLOSSUS_WALK2 = svg(80, 120, _colossus_legs(1) + _colossus_body(False))

COLOSSUS_ATTACK = svg(80, 120, _colossus_legs(0) + _colossus_body(True))

COLOSSUS_DEAD = svg(80, 120,
    '<ellipse cx="40" cy="114" rx="38" ry="6" fill="#111" opacity="0.85"/>'
    f'<path d="M8 116 L14 98 L58 94 L70 116 Z" fill="{PLATE}" {COLOSSUS_OUTLINE}/>'
    f'<circle cx="38" cy="104" r="7" fill="{PLATE_DARK}"/><circle cx="38" cy="104" r="3.5" fill="#6a2a0a"/>'
    f'<rect x="58" y="100" width="18" height="12" rx="3" fill="{PLATE_DARK}" {COLOSSUS_OUTLINE}/>'
    '<circle cx="20" cy="88" r="6" fill="#666" opacity="0.5"/><circle cx="28" cy="78" r="5" fill="#777" opacity="0.35"/>'
    '<path d="M2 110 L6 104 M6 112 L12 106" stroke="#c9ccd2" stroke-width="2"/>')
