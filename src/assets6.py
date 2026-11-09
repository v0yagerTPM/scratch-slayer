"""Art + sound for round 6: weapons, ammo + weapon pickups, the skull key, the charger, wraith and
colossus, rockets and plasma, the new HUD panels, the options menu, level cards 3-6, and two
original in-game music loops. Everything is drawn here from scratch (no outside images)."""
import math, random
from assets import svg, _wav, _lowpass, RATE
import assets2, assets3, assets4, assets5
from assets4 import block_text, text_width, gradient, FIRE_STOPS

# The OPTIONS title uses an I with bars at the top and bottom, unlike the plain I in the other
# block-letter headings (YOU DIED, VICTORY).
OPTIONS_LETTERS = dict(assets4.LETTERS, I="11111 00100 00100 00100 00100 00100 11111")

GLOVE, GLOVE_DARK, GLOVE_LINE = "#4a6b33", "#3e5a2a", "#1d2b12"

# =============================== WEAPONS (160 x 190, bottom-center) ===============================
def _flash(center_x, center_y, scale=1.0):
    pts = []
    for point_number in range(16):
        angle = point_number / 16 * 2 * math.pi - math.pi / 2
        radius = (34 if point_number % 2 == 0 else 14) * scale
        pts.append(f"{center_x + radius * math.cos(angle):.1f},{center_y + radius * math.sin(angle) * 0.8:.1f}")
    return (f'<polygon points="{" ".join(pts)}" fill="#ffd23f" stroke="#ff7a00" stroke-width="3"/>'
            f'<circle cx="{center_x}" cy="{center_y}" r="{11 * scale:.1f}" fill="#fff8d0"/>')

def _hand(left, top, width=44, height=40):
    """A green-gloved hand gripping something, seen from behind."""
    return (f'<path d="M{left} {top + height} L{left + 4} {top + 8} Q{left + width / 2} {top - 4} {left + width - 4} {top + 8} L{left + width} {top + height} Z" '
            f'fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
            + "".join(f'<path d="M{left + 8 + finger_number * (width - 16) / 3:.1f} {top + 6} V{top + 18}" stroke="{GLOVE_LINE}" stroke-width="1.5"/>'
                      for finger_number in range(4)))

def _fist(punch):
    if punch:   # big fist thrown at the middle of the screen
        return svg(160, 190,
            f'<path d="M40 190 L56 120 L104 120 L120 190 Z" fill="{GLOVE_DARK}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
            f'<rect x="40" y="58" width="80" height="70" rx="18" fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2.5"/>'
            + "".join(f'<path d="M{54 + finger_number * 17} 62 V100" stroke="{GLOVE_LINE}" stroke-width="2"/>' for finger_number in range(4))
            + f'<path d="M44 96 Q80 88 116 96" stroke="{GLOVE_LINE}" stroke-width="2" fill="none"/>'
              '<path d="M58 66 H70 M75 66 H87 M92 66 H104" stroke="#7aa05a" stroke-width="3" stroke-linecap="round"/>')
    return svg(160, 190,
        f'<path d="M96 190 L104 150 L146 150 L156 190 Z" fill="{GLOVE_DARK}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
        f'<rect x="96" y="118" width="56" height="48" rx="14" fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2.5"/>'
        + "".join(f'<path d="M{106 + finger_number * 12} 121 V146" stroke="{GLOVE_LINE}" stroke-width="2"/>' for finger_number in range(4))
        + f'<path d="M4 190 L14 160 L50 160 L58 190 Z" fill="{GLOVE_DARK}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
          f'<rect x="6" y="134" width="50" height="40" rx="12" fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2.5"/>')

def _pistol(fire):
    picture = _flash(80, 74, 0.75) if fire else ""
    picture += ('<path d="M70 92 L90 92 L92 140 L68 140 Z" fill="#4a4a4a" stroke="#111" stroke-width="2"/>'
          '<rect x="73" y="86" width="14" height="9" fill="#151515"/>'
          '<rect x="78" y="82" width="4" height="6" fill="#151515"/>'
          '<path d="M72 102 H88 M72 110 H88" stroke="#2c2c2c" stroke-width="2"/>'
          '<path d="M68 138 L92 138 L96 176 L64 176 Z" fill="#5a3a1e" stroke="#2a1608" stroke-width="2"/>')
    picture += _hand(56, 146, 48, 44)
    return svg(160, 190, picture)

def _chaingun(flash_step):
    picture = ""
    if flash_step:
        picture += _flash(64 if flash_step == 1 else 96, 40, 0.8)
    for barrel_number, barrel_x in enumerate((62, 74, 86, 98)):                  # four barrels in a ring
        shade = "#6a6a6a" if (barrel_number + flash_step) % 2 else "#4c4c4c"
        picture += f'<rect x="{barrel_x - 5}" y="40" width="10" height="70" rx="3" fill="{shade}" stroke="#111" stroke-width="1.5"/>'
    picture += ('<rect x="54" y="52" width="52" height="10" rx="3" fill="#333" stroke="#111" stroke-width="1.5"/>'
          '<rect x="54" y="94" width="52" height="10" rx="3" fill="#333" stroke="#111" stroke-width="1.5"/>'
          '<path d="M46 108 L114 108 L124 170 L36 170 Z" fill="#6b5328" stroke="#2e220c" stroke-width="2"/>'
          '<path d="M52 122 H108 M50 136 H110 M48 150 H112" stroke="#4a3818" stroke-width="2"/>'
          '<rect x="70" y="112" width="20" height="14" rx="2" fill="#222"/>')
    picture += _hand(14, 150, 44, 40) + _hand(102, 150, 44, 40)
    return svg(160, 190, picture)

def _launcher(fire):
    picture = ""
    if fire:
        picture += ('<circle cx="80" cy="40" r="30" fill="#9a9a9a" opacity="0.45"/><circle cx="64" cy="30" r="18" fill="#bbbbbb" opacity="0.4"/>'
              + _flash(80, 50, 0.9))
    picture += ('<path d="M52 56 L108 56 L116 190 L44 190 Z" fill="#5c6b2e" stroke="#202a0a" stroke-width="2.5"/>'
          '<ellipse cx="80" cy="57" rx="28" ry="10" fill="#3c4a1a" stroke="#202a0a" stroke-width="2"/>'
          '<ellipse cx="80" cy="58" rx="20" ry="6.5" fill="#0d0d0d"/>'
          '<path d="M48 92 H112 M46 132 H114" stroke="#c9a227" stroke-width="5"/>'
          '<rect x="108" y="98" width="16" height="26" rx="3" fill="#2b2b2b" stroke="#111" stroke-width="1.5"/>'
          '<circle cx="116" cy="106" r="4" fill="#e0402a"/>')
    picture += _hand(26, 150, 44, 40) + _hand(92, 156, 44, 34)
    return svg(160, 190, picture)

WEAPON_ART = {
    "fist": (_fist(False), _fist(True)),
    "pistol": (_pistol(False), _pistol(True)),
    "chaingun": (_chaingun(0), _chaingun(1)),
    "rocket launcher": (_launcher(False), _launcher(True)),
}
CHAINGUN_FIRE_2 = _chaingun(2)

# =============================== PICKUPS ===============================
SHADOW = '<ellipse cx="{center_x}" cy="{ground_y}" rx="{radius}" ry="2.5" fill="#000" opacity="0.35"/>'

BULLETS = svg(40, 40,
    SHADOW.format(center_x=20, ground_y=38, radius=16)
    + "".join(f'<path d="M{8 + bullet_number * 6} 18 V10 Q{10.5 + bullet_number * 6} 4 {13 + bullet_number * 6} 10 V18 Z" fill="#e0b040" stroke="#7a5a10"/>'
              for bullet_number in range(4))
    + '<rect x="5" y="17" width="30" height="21" rx="2" fill="#3c4a2a" stroke="#1a2010" stroke-width="1.5"/>'
      '<rect x="9" y="23" width="22" height="9" fill="#d9b44a"/>'
      '<text x="20" y="30.5" font-family="Sans Serif" font-size="5.5" font-weight="bold" fill="#1a2010" '
      'text-anchor="middle">BULLETS</text>')

def _rocket_body(offset_x, offset_y, angle=0):
    return (f'<g transform="translate({offset_x},{offset_y}) rotate({angle})">'
            '<rect x="-4" y="-14" width="8" height="24" rx="2" fill="#5c6b2e" stroke="#202a0a"/>'
            '<path d="M-4 -14 L0 -21 L4 -14 Z" fill="#d33" stroke="#601010"/>'
            '<path d="M-4 6 L-7 12 L-4 10 Z M4 6 L7 12 L4 10 Z" fill="#888"/></g>')
ROCKETS = svg(40, 40, SHADOW.format(center_x=20, ground_y=38, radius=16) + _rocket_body(13, 22, -8) + _rocket_body(27, 22, 8)
              + '<rect x="5" y="30" width="30" height="8" rx="2" fill="#6b4a1e" stroke="#2e1f0a"/>')

def _weapon_pickup(body, label, color):
    return svg(64, 34, SHADOW.format(center_x=32, ground_y=32, radius=28) + body
               + f'<text x="32" y="10" font-family="Sans Serif" font-size="8" font-weight="bold" fill="{color}" '
                 f'stroke="#000" stroke-width="2" paint-order="stroke" text-anchor="middle">{label}</text>')
SHOTGUN_PICKUP = _weapon_pickup(
    '<path d="M4 20 H44 V24 H4 Z" fill="#3b3b3b" stroke="#111"/><path d="M28 19 H44 V26 H28 Z" fill="#8a5428" stroke="#3b220d"/>'
    '<path d="M44 18 L60 22 L58 30 L44 27 Z" fill="#8a5428" stroke="#3b220d"/>', "SHOTGUN", "#ffd23f")
CHAINGUN_PICKUP = _weapon_pickup(
    '<rect x="4" y="17" width="30" height="4" fill="#555" stroke="#111"/><rect x="4" y="22" width="30" height="4" fill="#666" stroke="#111"/>'
    '<rect x="32" y="15" width="22" height="14" rx="2" fill="#6b5328" stroke="#2e220c"/>'
    '<rect x="52" y="20" width="8" height="10" fill="#333"/>', "CHAINGUN", "#ffd23f")
LAUNCHER_PICKUP = _weapon_pickup(
    '<rect x="6" y="15" width="50" height="13" rx="4" fill="#5c6b2e" stroke="#202a0a"/>'
    '<ellipse cx="7" cy="21.5" rx="3" ry="6.5" fill="#111"/><path d="M20 15 V28 M40 15 V28" stroke="#c9a227" stroke-width="3"/>'
    '<rect x="30" y="27" width="8" height="5" fill="#333"/>', "LAUNCHER", "#ffd23f")

SKULL_KEY = svg(40, 44,
    '<circle cx="20" cy="22" r="19" fill="#b070ff" opacity="0.3"/>'
    + SHADOW.format(center_x=20, ground_y=42, radius=12)
    + '<path d="M8 18 Q8 4 20 4 Q32 4 32 18 Q32 25 27 27 V33 H13 V27 Q8 25 8 18 Z" fill="#efe6c8" stroke="#5a5030" stroke-width="1.5"/>'
      '<ellipse cx="15" cy="17" rx="3.6" ry="4.2" fill="#2a0010"/><ellipse cx="25" cy="17" rx="3.6" ry="4.2" fill="#2a0010"/>'
      '<circle cx="15" cy="17" r="1.4" fill="#ff3050"/><circle cx="25" cy="17" r="1.4" fill="#ff3050"/>'
      '<path d="M18 23 L20 20 L22 23 Z" fill="#2a0010"/>'
      '<path d="M15 33 V29 M18 33 V29 M22 33 V29 M25 33 V29" stroke="#5a5030" stroke-width="1"/>'
      '<rect x="18" y="33" width="4" height="9" fill="#c9a227" stroke="#5a4a10"/>'
      '<rect x="22" y="37" width="5" height="2.5" fill="#c9a227"/>')

# =============================== CHARGER (level 4) ===============================
# A hunched, horned brute that lowers its head and charges in a straight line.
HIDE, HIDE_DARK, HIDE_LIGHT, HORN = "#5b6474", "#3c4250", "#7d889c", "#e8dcb8"
COUT = 'stroke="#161a22" stroke-width="1.5"'

def _charger_legs(phase):
    left_foot_y, right_foot_y = (106, 116) if phase == 0 else (116, 106)
    return (f'<path d="M22 86 L18 {left_foot_y} L32 {left_foot_y} L34 88 Z" fill="{HIDE_DARK}" {COUT}/>'
            f'<path d="M58 86 L62 {right_foot_y} L48 {right_foot_y} L46 88 Z" fill="{HIDE_DARK}" {COUT}/>'
            f'<path d="M16 {left_foot_y} H34 V{left_foot_y + 4} H16 Z M46 {right_foot_y} H64 V{right_foot_y + 4} H46 Z" fill="#222"/>')

def _charger_body(lowered):
    head_y = 54 if lowered else 40          # head height: lowered = about to charge
    eye = "#ff2a00" if lowered else "#ffb000"
    picture = (f'<ellipse cx="40" cy="66" rx="30" ry="26" fill="{HIDE}" {COUT}/>'
         f'<path d="M14 54 Q40 30 66 54" fill="{HIDE_LIGHT}" opacity="0.5"/>'
         f'<path d="M22 70 Q40 78 58 70 M24 80 Q40 86 56 80" stroke="{HIDE_DARK}" stroke-width="2" fill="none"/>'
         f'<path d="M10 64 Q4 78 8 94 L18 94 Q16 80 20 70 Z" fill="{HIDE_DARK}" {COUT}/>'
         f'<path d="M70 64 Q76 78 72 94 L62 94 Q64 80 60 70 Z" fill="{HIDE_DARK}" {COUT}/>'
         f'<ellipse cx="40" cy="{head_y}" rx="15" ry="12" fill="{HIDE_DARK}" {COUT}/>'
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
    f'<ellipse cx="42" cy="104" rx="30" ry="12" fill="{HIDE}" {COUT}/>'
    f'<ellipse cx="14" cy="108" rx="11" ry="8" fill="{HIDE_DARK}" {COUT}/>'
    f'<path d="M8 104 Q-2 96 2 88 Q6 98 12 100 Z" fill="{HORN}" stroke="#5a5030"/>'
    '<path d="M10 106 l3 3 m0 -3 l-3 3" stroke="#111" stroke-width="1.3"/>'
    f'<path d="M60 112 L76 108 L74 116 Z" fill="{HIDE_DARK}" {COUT}/>')

# =============================== WRAITH (level 5) ===============================
# A floating hooded shade with glowing eyes. It is drawn solid; the game fades it with distance.
ROBE, ROBE_DARK, GLOW = "#4a4060", "#2a2238", "#7ff6ff"
WOUT = 'stroke="#120c1c" stroke-width="1.5"'

def _wraith_tail(phase):
    sway = 5 if phase == 0 else -5
    return (f'<path d="M16 70 Q12 96 {20 + sway} 116 L{28 + sway} 104 L{36 - sway} 118 L{44 + sway} 104 L{52 - sway} 117 '
            f'L{58 + sway} 102 Q68 92 64 70 Z" fill="{ROBE_DARK}" {WOUT} opacity="0.95"/>')

def _wraith_top(reaching):
    picture = (f'<path d="M20 74 Q14 40 26 22 Q40 4 54 22 Q66 40 60 74 Z" fill="{ROBE}" {WOUT}/>'
         f'<path d="M28 30 Q40 16 52 30 Q54 46 40 50 Q26 46 28 30 Z" fill="#0b0712"/>'
         f'<ellipse cx="34" cy="36" rx="3.5" ry="2.4" fill="{GLOW}"/><ellipse cx="46" cy="36" rx="3.5" ry="2.4" fill="{GLOW}"/>'
         f'<ellipse cx="40" cy="36" rx="14" ry="7" fill="{GLOW}" opacity="0.15"/>'
         f'<path d="M24 56 Q40 62 56 56" stroke="{ROBE_DARK}" stroke-width="2" fill="none"/>')
    if reaching:
        picture += (f'<path d="M22 52 Q6 38 4 22 L12 20 Q14 34 28 44 Z" fill="{ROBE}" {WOUT}/>'
              f'<path d="M58 52 Q74 38 76 22 L68 20 Q66 34 52 44 Z" fill="{ROBE}" {WOUT}/>'
              '<path d="M4 22 L1 14 M7 21 L6 12 M10 21 L11 13 M76 22 L79 14 M73 21 L74 12 M70 21 L69 13" '
              f'stroke="{GLOW}" stroke-width="1.8" stroke-linecap="round"/>')
    else:
        picture += (f'<path d="M22 50 Q10 62 12 80 L19 80 Q19 66 28 56 Z" fill="{ROBE}" {WOUT}/>'
              f'<path d="M58 50 Q70 62 68 80 L61 80 Q61 66 52 56 Z" fill="{ROBE}" {WOUT}/>')
    return picture

WRAITH_WALK1 = svg(80, 120, _wraith_tail(0) + _wraith_top(False))
WRAITH_WALK2 = svg(80, 120, _wraith_tail(1) + _wraith_top(False))
WRAITH_ATTACK = svg(80, 120, _wraith_tail(0) + _wraith_top(True))
WRAITH_DEAD = svg(80, 120,
    f'<ellipse cx="40" cy="114" rx="30" ry="5" fill="{GLOW}" opacity="0.25"/>'
    f'<path d="M10 116 Q20 96 40 98 Q60 96 70 116 Z" fill="{ROBE_DARK}" {WOUT}/>'
    f'<path d="M26 112 Q40 100 54 112" stroke="{ROBE}" stroke-width="3" fill="none"/>'
    f'<circle cx="40" cy="92" r="4" fill="{GLOW}" opacity="0.5"/><circle cx="34" cy="82" r="2.5" fill="{GLOW}" opacity="0.35"/>'
    f'<circle cx="46" cy="74" r="1.8" fill="{GLOW}" opacity="0.25"/>')

# =============================== COLOSSUS (level 6 boss) ===============================
# An armored giant with a furnace in its chest, a cannon arm and a claw.
PLATE, PLATE_DARK, CORE = "#4b4f57", "#2c2f35", "#ff7a1a"
TOUT = 'stroke="#121317" stroke-width="1.6"'

def _colossus_legs(phase):
    left_foot_y, right_foot_y = (108, 117) if phase == 0 else (117, 108)
    return (f'<path d="M22 84 L18 {left_foot_y} L36 {left_foot_y} L36 86 Z" fill="{PLATE_DARK}" {TOUT}/>'
            f'<path d="M58 84 L62 {right_foot_y} L44 {right_foot_y} L44 86 Z" fill="{PLATE_DARK}" {TOUT}/>'
            f'<path d="M14 {left_foot_y} H38 V{left_foot_y + 4} H14 Z M42 {right_foot_y} H66 V{right_foot_y + 4} H42 Z" fill="#1a1a1a"/>')

def _colossus_body(firing):
    glow = "#ffe680" if firing else "#ffb347"
    picture = (f'<path d="M14 30 L66 30 L60 88 L20 88 Z" fill="{PLATE}" {TOUT}/>'
         f'<path d="M14 30 L66 30 L62 44 L18 44 Z" fill="#5d626c"/>'
         f'<circle cx="40" cy="60" r="12" fill="{PLATE_DARK}" {TOUT}/>'
         f'<circle cx="40" cy="60" r="8" fill="{CORE}"/><circle cx="40" cy="60" r="4" fill="{glow}"/>'
         f'<path d="M22 50 H32 M48 50 H58 M24 76 H56" stroke="{PLATE_DARK}" stroke-width="2"/>'
         f'<rect x="30" y="12" width="20" height="18" rx="4" fill="{PLATE_DARK}" {TOUT}/>'
         f'<rect x="33" y="18" width="14" height="4" rx="1" fill="{CORE}"/>'
         f'<path d="M30 14 L24 4 L32 10 Z M50 14 L56 4 L48 10 Z" fill="#8a8f99"/>'
         # claw arm (left)
         f'<path d="M14 34 Q2 50 6 70 L14 70 Q12 54 20 42 Z" fill="{PLATE}" {TOUT}/>'
         '<path d="M4 70 L2 80 M8 71 L8 82 M12 70 L14 80" stroke="#c9ccd2" stroke-width="2.5" stroke-linecap="round"/>')
    if firing:   # cannon raised and blazing
        picture += (f'<path d="M66 34 Q76 24 76 10 L68 8 Q66 22 58 30 Z" fill="{PLATE}" {TOUT}/>'
              f'<rect x="64" y="0" width="14" height="12" rx="3" fill="{PLATE_DARK}" {TOUT}/>'
              '<circle cx="71" cy="2" r="7" fill="#c060ff" opacity="0.6"/><circle cx="71" cy="2" r="3.5" fill="#f0d0ff"/>')
    else:
        picture += (f'<path d="M66 34 Q78 50 74 70 L66 70 Q68 54 60 42 Z" fill="{PLATE}" {TOUT}/>'
              f'<rect x="64" y="68" width="14" height="14" rx="3" fill="{PLATE_DARK}" {TOUT}/>'
              '<circle cx="71" cy="80" r="3" fill="#c060ff"/>')
    return picture

COLOSSUS_WALK1 = svg(80, 120, _colossus_legs(0) + _colossus_body(False))
COLOSSUS_WALK2 = svg(80, 120, _colossus_legs(1) + _colossus_body(False))
COLOSSUS_ATTACK = svg(80, 120, _colossus_legs(0) + _colossus_body(True))
COLOSSUS_DEAD = svg(80, 120,
    '<ellipse cx="40" cy="114" rx="38" ry="6" fill="#111" opacity="0.85"/>'
    f'<path d="M8 116 L14 98 L58 94 L70 116 Z" fill="{PLATE}" {TOUT}/>'
    f'<circle cx="38" cy="104" r="7" fill="{PLATE_DARK}"/><circle cx="38" cy="104" r="3.5" fill="#6a2a0a"/>'
    f'<rect x="58" y="100" width="18" height="12" rx="3" fill="{PLATE_DARK}" {TOUT}/>'
    '<circle cx="20" cy="88" r="6" fill="#666" opacity="0.5"/><circle cx="28" cy="78" r="5" fill="#777" opacity="0.35"/>'
    '<path d="M2 110 L6 104 M6 112 L12 106" stroke="#c9ccd2" stroke-width="2"/>')

# =============================== PROJECTILES ===============================
ROCKET_SHOT = svg(26, 26,
    '<circle cx="13" cy="13" r="12" fill="#ff7a00" opacity="0.35"/>'
    '<circle cx="13" cy="13" r="7" fill="#ffd23f"/><circle cx="13" cy="13" r="3.5" fill="#fff8d0"/>'
    '<path d="M13 1 L17 9 L9 9 Z" fill="#888" stroke="#333"/>')
PLASMA_SHOT = svg(30, 30,
    '<circle cx="15" cy="15" r="14" fill="#a040ff" opacity="0.35"/>'
    '<circle cx="15" cy="15" r="9" fill="#c070ff" stroke="#5a1a9a" stroke-width="1.2"/>'
    '<circle cx="15" cy="15" r="4.5" fill="#f0d8ff"/>')

# =============================== HUD ===============================
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
            + assets2._label(14, 314, "HEALTH")
            + '<text x="94" y="350" font-family="Sans Serif" font-weight="bold" font-size="24" fill="#ff4a24">%</text>'
            '<rect x="400" y="264" width="74" height="34" rx="5" fill="#000" fill-opacity="0.45"/>'
            + _key_slot(404, "#e02424", red) + _key_slot(427, "#2a6cf0", blue) + _key_slot(450, "", skull, skull=True))
    return assets5.hud_with_sprint(svg(480, 360, body))
HUDS = [hud(red, blue, skull) for skull in (0, 1) for blue in (0, 1) for red in (0, 1)]   # index = red + 2*blue + 4*skull

WEAPON_NAMES = ["fist", "pistol", "shotgun", "chaingun", "rocket launcher"]
AMMO_LABELS = ["FISTS", "BULLETS", "SHELLS", "BULLETS", "ROCKETS"]

def arms(owned_code, current):
    """The ammo box (label for the weapon in your hands) and the ARMS row: which of the
    5 weapon slots you own (white), don't own yet (dark) and are holding (yellow)."""
    owned = [1, 1, owned_code & 1, (owned_code >> 1) & 1, (owned_code >> 2) & 1]
    picture = ('<rect x="350" y="298" width="124" height="56" rx="6" fill="#000" fill-opacity="0.5"/>'
         + assets2._label(358, 314, AMMO_LABELS[current - 1]))
    if current == 1:
        picture += ('<text x="412" y="342" font-family="Sans Serif" font-size="11" fill="#999" text-anchor="middle">'
              'no ammo needed</text>')
    picture += ('<rect x="350" y="240" width="124" height="21" rx="5" fill="#000" fill-opacity="0.45"/>'
          + assets2._label(356, 255, "ARMS", size=9, fill="#aaaaaa"))
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
        + assets2._label(240, 77, name, "middle", 11, "#ffd23f")
        + '<rect x="140" y="82" width="200" height="8" rx="2" fill="none" stroke="#ffd23f" stroke-width="1.5"/>')
BOSS_BARS = {"warden": boss_bar("THE WARDEN"), "colossus": boss_bar("THE COLOSSUS")}


# =============================== OPTIONS MENU ===============================
OPTION_ROWS = ["TURN SPEED", "MOUSE STEERING", "MOUSE SENSITIVITY", "FIELD OF VIEW", "MUSIC", "DIFFICULTY",
               "START AT LEVEL"]
OPTION_ROW_STEP = 27                                  # pixels between rows
OPTION_ROW_Y = [88 - OPTION_ROW_STEP * row for row in range(len(OPTION_ROWS))]   # stage y of each row
TRACK_LEFT, TRACK_RIGHT = 0, 120                    # stage x of the slider tracks
# The < > arrows (stage x) for the two "pick one" rows. They are only drawn on the title screen.
DIFFICULTY_ARROWS_X, LEVEL_ARROWS_X = (0, 100), (16, 84)

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
        picture += assets2._label(70, picture_y + 5, name, size=12, fill="#e8d8c8")
        if name in ("TURN SPEED", "MOUSE SENSITIVITY", "FIELD OF VIEW"):
            picture += (f'<line x1="{240 + TRACK_LEFT}" y1="{picture_y}" x2="{240 + TRACK_RIGHT}" y2="{picture_y}" stroke="#4a3a34" '
                  'stroke-width="5" stroke-linecap="round"/>')
    level_y = 180 - OPTION_ROW_Y[-1] + 5
    if paused:
        picture += (f'<text x="300" y="{level_y}" font-family="Sans Serif" font-size="11" fill="#8a8a8a" '
              'text-anchor="middle">(change these two on the title screen)</text>')
    else:
        for arrows_x, row_y in ((DIFFICULTY_ARROWS_X, OPTION_ROW_Y[-2]), (LEVEL_ARROWS_X, OPTION_ROW_Y[-1])):
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

ROW_HIGHLIGHT = svg(380, 26, '<rect x="1" y="1" width="378" height="24" rx="6" fill="#ff6a00" fill-opacity="0.2" '
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




# =============================== SOUNDS ===============================
def _crack(dur, thump_hz, decay, seed, gain=1.0):
    rnd = random.Random(seed)
    sample_count = int(RATE * dur)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.45)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        sample = noise[sample_number] * 2.0 * math.exp(-seconds * decay) * min(1, seconds * 600)
        sample += math.sin(2 * math.pi * thump_hz * seconds) * math.exp(-seconds * decay * 1.4) * 0.8
        out.append(sample * gain)
    return _wav(out)

def pistol(): return _crack(0.25, 110, 30, 81)
def chaingun(): return _crack(0.13, 95, 42, 82, 0.9)

def rocket_launch():
    rnd = random.Random(83); sample_count = int(RATE * 0.7); out, smoothed = [], 0.0
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        smoothing = 0.05 + 0.3 * min(1, seconds / 0.15)
        smoothed += smoothing * (rnd.uniform(-1, 1) - smoothed)
        sample = smoothed * 2.4 * math.exp(-seconds * 4) + math.sin(2 * math.pi * 60 * seconds) * math.exp(-seconds * 14) * 0.9
        out.append(sample)
    return _wav(out)

def weapon_pickup():
    """Two metal clacks, then a bright ring."""
    rnd = random.Random(84); out = []
    for sample_number in range(int(RATE * 0.5)):
        seconds = sample_number / RATE; sample = 0.0
        for click_time in (0.0, 0.11):
            if click_time <= seconds < click_time + 0.04:
                sample += rnd.uniform(-1, 1) * 0.8 * math.exp(-(seconds - click_time) * 90)
        if seconds > 0.2:
            sample += (math.sin(2 * math.pi * 1320 * seconds) + 0.5 * math.sin(2 * math.pi * 1980 * seconds)) * 0.25 * math.exp(-(seconds - 0.2) * 9)
        out.append(sample)
    return _wav(out)

def wraith_blink():
    out = []
    for sample_number in range(int(RATE * 0.45)):
        seconds = sample_number / RATE
        pitch = 900 - 1400 * seconds
        sample = math.sin(2 * math.pi * pitch * seconds) * 0.35 + math.sin(2 * math.pi * pitch * 1.5 * seconds) * 0.2
        out.append(sample * math.sin(math.pi * seconds / 0.45) * (0.6 + 0.4 * math.sin(2 * math.pi * 30 * seconds)))
    return _wav(out)

def menu_click():
    out = [math.sin(2 * math.pi * 1500 * (sample_number / RATE)) * math.exp(-(sample_number / RATE) * 60) * 0.6 for sample_number in range(int(RATE * 0.06))]
    return _wav(out)

def _note_freq(midi):
    return 440 * 2 ** ((midi - 69) / 12)

def _music(bpm, riff, root, kick_pattern, snare_pattern, seed, dark=False):
    """Mix an original loop: a distorted guitar riff (with a power-chord fifth on accents),
    a bass an octave down, and kick + snare + hi-hat drums. 'riff' = semitones above 'root'
    (None = rest), one per sixteenth note."""
    step = 60 / bpm / 4
    sample_count = int(RATE * step * len(riff)); out = [0.0] * sample_count
    rnd = random.Random(seed)
    for step_number, semi in enumerate(riff):
        if semi is None:
            continue
        start = int(step_number * step * RATE)
        accent = semi != 0
        length = int(RATE * step * (1.9 if accent else 0.6))
        for interval, gain in ((0, 0.26), (7, 0.16 if accent else 0), (-12, 0.22)):
            if not gain:
                continue
            pitch, phase = _note_freq(root + semi + interval), 0.0
            for sample_in_note in range(length):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                phase += pitch / RATE
                wave = (2 * (phase % 1) - 1) if interval != -12 else math.sin(2 * math.pi * phase)
                env = min(1, seconds * 300) * math.exp(-seconds * (4 if accent else 18))
                shaped = math.tanh((3.5 if not dark else 2.5) * wave) if interval != -12 else wave
                out[start + sample_in_note] += shaped * gain * env
    for s16 in range(len(riff)):
        start = int(s16 * step * RATE)
        if kick_pattern[s16 % len(kick_pattern)] == "x":
            for sample_in_note in range(int(RATE * 0.2)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += math.sin(2 * math.pi * (105 - 240 * seconds) * seconds) * math.exp(-seconds * 20) * 0.8
        if snare_pattern[s16 % len(snare_pattern)] == "x":
            for sample_in_note in range(int(RATE * 0.18)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                out[start + sample_in_note] += (rnd.uniform(-1, 1) * 0.42 + math.sin(2 * math.pi * 190 * seconds) * 0.2) * math.exp(-seconds * 22)
        if s16 % 2 == 0:
            for sample_in_note in range(int(RATE * 0.04)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += rnd.uniform(-1, 1) * 0.07 * math.exp(-seconds * 90)
    smooth = _lowpass(out, 0.3 if dark else 0.38)
    peak = max(abs(sample) for sample in smooth) or 1
    return _wav([sample / peak * 0.85 for sample in smooth])

def episode_1_theme():
    """Original: a brooding, mid-tempo chug in E minor (about 8.7 seconds, loops cleanly)."""
    bar_a = [0, 0, None, 0, 0, None, 3, None, 0, 0, None, 0, 5, None, 3, None]
    bar_b = [0, 0, None, 0, 0, None, 3, None, 0, 0, None, 0, 7, 6, 5, 3]
    bar_c = [0, 0, None, 0, 0, None, 3, None, 0, 0, None, 0, 1, None, -2, None]
    riff = bar_a + bar_b + bar_a + bar_c
    return _music(110, riff, 40, "x.......x.x.....", "....x.......x...", 91, dark=True)

def episode_2_theme():
    """Original: a faster, heavier gallop in D minor (about 7.4 seconds, loops cleanly)."""
    gallop = [0, 0, 0, None, 0, 0, 0, None]
    bar_a = gallop + [0, 0, 3, None, 5, None, 3, None]
    bar_b = gallop + [0, 0, 6, None, 5, None, 3, 1]
    bar_c = gallop + [8, None, 7, None, 5, None, 3, None]
    riff = bar_a + bar_b + bar_a + bar_c
    return _music(130, riff, 38, "x.x...x.x.x...x.", "....x.......x...", 92)

