"""Art + sound for round 6: weapons, ammo + weapon pickups, the skull key, the charger, wraith and
colossus, rockets and plasma, the new HUD panels, the options menu, level cards 3-6, and two
original in-game music loops. Everything is drawn here from scratch (no outside images)."""
import math, random
from assets import svg, _wav, _lowpass, RATE
import assets2, assets3, assets4, assets5
from assets4 import block_text, text_width, gradient, FIRE_STOPS

assets4.LETTERS.update({          # extra block letters for PAUSED and OPTIONS
    "P": "11110 10001 10001 11110 10000 10000 10000", "U": "10001 10001 10001 10001 10001 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110", "O": "01110 10001 10001 10001 10001 10001 01110",
    "I": "11111 00100 00100 00100 00100 00100 11111"})

GLOVE, GLOVE_DARK, GLOVE_LINE = "#4a6b33", "#3e5a2a", "#1d2b12"

# =============================== WEAPONS (160 x 190, bottom-center) ===============================
def _flash(cx, cy, scale=1.0):
    pts = []
    for i in range(16):
        a = i / 16 * 2 * math.pi - math.pi / 2
        r = (34 if i % 2 == 0 else 14) * scale
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a) * 0.8:.1f}")
    return (f'<polygon points="{" ".join(pts)}" fill="#ffd23f" stroke="#ff7a00" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{11 * scale:.1f}" fill="#fff8d0"/>')

def _hand(x, y, w=44, h=40):
    """A green-gloved hand gripping something, seen from behind."""
    return (f'<path d="M{x} {y + h} L{x + 4} {y + 8} Q{x + w / 2} {y - 4} {x + w - 4} {y + 8} L{x + w} {y + h} Z" '
            f'fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
            + "".join(f'<path d="M{x + 8 + i * (w - 16) / 3:.1f} {y + 6} V{y + 18}" stroke="{GLOVE_LINE}" stroke-width="1.5"/>'
                      for i in range(4)))

def _fist(punch):
    if punch:   # big fist thrown at the middle of the screen
        return svg(160, 190,
            f'<path d="M40 190 L56 120 L104 120 L120 190 Z" fill="{GLOVE_DARK}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
            f'<rect x="40" y="58" width="80" height="70" rx="18" fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2.5"/>'
            + "".join(f'<path d="M{54 + i * 17} 62 V100" stroke="{GLOVE_LINE}" stroke-width="2"/>' for i in range(4))
            + f'<path d="M44 96 Q80 88 116 96" stroke="{GLOVE_LINE}" stroke-width="2" fill="none"/>'
              '<path d="M58 66 H70 M75 66 H87 M92 66 H104" stroke="#7aa05a" stroke-width="3" stroke-linecap="round"/>')
    return svg(160, 190,
        f'<path d="M96 190 L104 150 L146 150 L156 190 Z" fill="{GLOVE_DARK}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
        f'<rect x="96" y="118" width="56" height="48" rx="14" fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2.5"/>'
        + "".join(f'<path d="M{106 + i * 12} 121 V146" stroke="{GLOVE_LINE}" stroke-width="2"/>' for i in range(4))
        + f'<path d="M4 190 L14 160 L50 160 L58 190 Z" fill="{GLOVE_DARK}" stroke="{GLOVE_LINE}" stroke-width="2"/>'
          f'<rect x="6" y="134" width="50" height="40" rx="12" fill="{GLOVE}" stroke="{GLOVE_LINE}" stroke-width="2.5"/>')

def _pistol(fire):
    g = _flash(80, 74, 0.75) if fire else ""
    g += ('<path d="M70 92 L90 92 L92 140 L68 140 Z" fill="#4a4a4a" stroke="#111" stroke-width="2"/>'
          '<rect x="73" y="86" width="14" height="9" fill="#151515"/>'
          '<rect x="78" y="82" width="4" height="6" fill="#151515"/>'
          '<path d="M72 102 H88 M72 110 H88" stroke="#2c2c2c" stroke-width="2"/>'
          '<path d="M68 138 L92 138 L96 176 L64 176 Z" fill="#5a3a1e" stroke="#2a1608" stroke-width="2"/>')
    g += _hand(56, 146, 48, 44)
    return svg(160, 190, g)

def _chaingun(flash_step):
    g = ""
    if flash_step:
        g += _flash(64 if flash_step == 1 else 96, 40, 0.8)
    for i, x in enumerate((62, 74, 86, 98)):                  # four barrels in a ring
        shade = "#6a6a6a" if (i + flash_step) % 2 else "#4c4c4c"
        g += f'<rect x="{x - 5}" y="40" width="10" height="70" rx="3" fill="{shade}" stroke="#111" stroke-width="1.5"/>'
    g += ('<rect x="54" y="52" width="52" height="10" rx="3" fill="#333" stroke="#111" stroke-width="1.5"/>'
          '<rect x="54" y="94" width="52" height="10" rx="3" fill="#333" stroke="#111" stroke-width="1.5"/>'
          '<path d="M46 108 L114 108 L124 170 L36 170 Z" fill="#6b5328" stroke="#2e220c" stroke-width="2"/>'
          '<path d="M52 122 H108 M50 136 H110 M48 150 H112" stroke="#4a3818" stroke-width="2"/>'
          '<rect x="70" y="112" width="20" height="14" rx="2" fill="#222"/>')
    g += _hand(14, 150, 44, 40) + _hand(102, 150, 44, 40)
    return svg(160, 190, g)

def _launcher(fire):
    g = ""
    if fire:
        g += ('<circle cx="80" cy="40" r="30" fill="#9a9a9a" opacity="0.45"/><circle cx="64" cy="30" r="18" fill="#bbbbbb" opacity="0.4"/>'
              + _flash(80, 50, 0.9))
    g += ('<path d="M52 56 L108 56 L116 190 L44 190 Z" fill="#5c6b2e" stroke="#202a0a" stroke-width="2.5"/>'
          '<ellipse cx="80" cy="57" rx="28" ry="10" fill="#3c4a1a" stroke="#202a0a" stroke-width="2"/>'
          '<ellipse cx="80" cy="58" rx="20" ry="6.5" fill="#0d0d0d"/>'
          '<path d="M48 92 H112 M46 132 H114" stroke="#c9a227" stroke-width="5"/>'
          '<rect x="108" y="98" width="16" height="26" rx="3" fill="#2b2b2b" stroke="#111" stroke-width="1.5"/>'
          '<circle cx="116" cy="106" r="4" fill="#e0402a"/>')
    g += _hand(26, 150, 44, 40) + _hand(92, 156, 44, 34)
    return svg(160, 190, g)

WEAPON_ART = {
    "fist": (_fist(False), _fist(True)),
    "pistol": (_pistol(False), _pistol(True)),
    "chaingun": (_chaingun(0), _chaingun(1)),
    "rocket launcher": (_launcher(False), _launcher(True)),
}
CHAINGUN_FIRE_2 = _chaingun(2)

# =============================== PICKUPS ===============================
SHADOW = '<ellipse cx="{c}" cy="{y}" rx="{r}" ry="2.5" fill="#000" opacity="0.35"/>'

BULLETS = svg(40, 40,
    SHADOW.format(c=20, y=38, r=16)
    + "".join(f'<path d="M{8 + i * 6} 18 V10 Q{10.5 + i * 6} 4 {13 + i * 6} 10 V18 Z" fill="#e0b040" stroke="#7a5a10"/>'
              for i in range(4))
    + '<rect x="5" y="17" width="30" height="21" rx="2" fill="#3c4a2a" stroke="#1a2010" stroke-width="1.5"/>'
      '<rect x="9" y="23" width="22" height="9" fill="#d9b44a"/>'
      '<text x="20" y="30.5" font-family="Sans Serif" font-size="5.5" font-weight="bold" fill="#1a2010" '
      'text-anchor="middle">BULLETS</text>')

def _rocket_body(x, y, angle=0):
    return (f'<g transform="translate({x},{y}) rotate({angle})">'
            '<rect x="-4" y="-14" width="8" height="24" rx="2" fill="#5c6b2e" stroke="#202a0a"/>'
            '<path d="M-4 -14 L0 -21 L4 -14 Z" fill="#d33" stroke="#601010"/>'
            '<path d="M-4 6 L-7 12 L-4 10 Z M4 6 L7 12 L4 10 Z" fill="#888"/></g>')
ROCKETS = svg(40, 40, SHADOW.format(c=20, y=38, r=16) + _rocket_body(13, 22, -8) + _rocket_body(27, 22, 8)
              + '<rect x="5" y="30" width="30" height="8" rx="2" fill="#6b4a1e" stroke="#2e1f0a"/>')

def _weapon_pickup(body, label, color):
    return svg(64, 34, SHADOW.format(c=32, y=32, r=28) + body
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
    + SHADOW.format(c=20, y=42, r=12)
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
    a, b = (106, 116) if phase == 0 else (116, 106)
    return (f'<path d="M22 86 L18 {a} L32 {a} L34 88 Z" fill="{HIDE_DARK}" {COUT}/>'
            f'<path d="M58 86 L62 {b} L48 {b} L46 88 Z" fill="{HIDE_DARK}" {COUT}/>'
            f'<path d="M16 {a} H34 V{a + 4} H16 Z M46 {b} H64 V{b + 4} H46 Z" fill="#222"/>')

def _charger_body(lowered):
    hy = 54 if lowered else 40          # head height: lowered = about to charge
    eye = "#ff2a00" if lowered else "#ffb000"
    b = (f'<ellipse cx="40" cy="66" rx="30" ry="26" fill="{HIDE}" {COUT}/>'
         f'<path d="M14 54 Q40 30 66 54" fill="{HIDE_LIGHT}" opacity="0.5"/>'
         f'<path d="M22 70 Q40 78 58 70 M24 80 Q40 86 56 80" stroke="{HIDE_DARK}" stroke-width="2" fill="none"/>'
         f'<path d="M10 64 Q4 78 8 94 L18 94 Q16 80 20 70 Z" fill="{HIDE_DARK}" {COUT}/>'
         f'<path d="M70 64 Q76 78 72 94 L62 94 Q64 80 60 70 Z" fill="{HIDE_DARK}" {COUT}/>'
         f'<ellipse cx="40" cy="{hy}" rx="15" ry="12" fill="{HIDE_DARK}" {COUT}/>'
         f'<path d="M27 {hy - 4} Q12 {hy - 10} 10 {hy - 24} Q20 {hy - 14} 30 {hy - 10} Z" fill="{HORN}" stroke="#5a5030"/>'
         f'<path d="M53 {hy - 4} Q68 {hy - 10} 70 {hy - 24} Q60 {hy - 14} 50 {hy - 10} Z" fill="{HORN}" stroke="#5a5030"/>'
         f'<ellipse cx="34" cy="{hy - 2}" rx="3" ry="2.2" fill="{eye}"/><ellipse cx="46" cy="{hy - 2}" rx="3" ry="2.2" fill="{eye}"/>'
         f'<path d="M33 {hy + 6} Q40 {hy + 11} 47 {hy + 6}" stroke="#111" stroke-width="2" fill="none"/>'
         f'<circle cx="37" cy="{hy + 4}" r="1.3" fill="#111"/><circle cx="43" cy="{hy + 4}" r="1.3" fill="#111"/>')
    if lowered:   # snorting steam
        b += (f'<circle cx="28" cy="{hy + 12}" r="5" fill="#ddd" opacity="0.55"/><circle cx="22" cy="{hy + 16}" r="4" fill="#ddd" opacity="0.4"/>'
              f'<circle cx="52" cy="{hy + 12}" r="5" fill="#ddd" opacity="0.55"/><circle cx="58" cy="{hy + 16}" r="4" fill="#ddd" opacity="0.4"/>')
    return b

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
    s = 5 if phase == 0 else -5
    return (f'<path d="M16 70 Q12 96 {20 + s} 116 L{28 + s} 104 L{36 - s} 118 L{44 + s} 104 L{52 - s} 117 '
            f'L{58 + s} 102 Q68 92 64 70 Z" fill="{ROBE_DARK}" {WOUT} opacity="0.95"/>')

def _wraith_top(reaching):
    b = (f'<path d="M20 74 Q14 40 26 22 Q40 4 54 22 Q66 40 60 74 Z" fill="{ROBE}" {WOUT}/>'
         f'<path d="M28 30 Q40 16 52 30 Q54 46 40 50 Q26 46 28 30 Z" fill="#0b0712"/>'
         f'<ellipse cx="34" cy="36" rx="3.5" ry="2.4" fill="{GLOW}"/><ellipse cx="46" cy="36" rx="3.5" ry="2.4" fill="{GLOW}"/>'
         f'<ellipse cx="40" cy="36" rx="14" ry="7" fill="{GLOW}" opacity="0.15"/>'
         f'<path d="M24 56 Q40 62 56 56" stroke="{ROBE_DARK}" stroke-width="2" fill="none"/>')
    if reaching:
        b += (f'<path d="M22 52 Q6 38 4 22 L12 20 Q14 34 28 44 Z" fill="{ROBE}" {WOUT}/>'
              f'<path d="M58 52 Q74 38 76 22 L68 20 Q66 34 52 44 Z" fill="{ROBE}" {WOUT}/>'
              '<path d="M4 22 L1 14 M7 21 L6 12 M10 21 L11 13 M76 22 L79 14 M73 21 L74 12 M70 21 L69 13" '
              f'stroke="{GLOW}" stroke-width="1.8" stroke-linecap="round"/>')
    else:
        b += (f'<path d="M22 50 Q10 62 12 80 L19 80 Q19 66 28 56 Z" fill="{ROBE}" {WOUT}/>'
              f'<path d="M58 50 Q70 62 68 80 L61 80 Q61 66 52 56 Z" fill="{ROBE}" {WOUT}/>')
    return b

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
    a, b = (108, 117) if phase == 0 else (117, 108)
    return (f'<path d="M22 84 L18 {a} L36 {a} L36 86 Z" fill="{PLATE_DARK}" {TOUT}/>'
            f'<path d="M58 84 L62 {b} L44 {b} L44 86 Z" fill="{PLATE_DARK}" {TOUT}/>'
            f'<path d="M14 {a} H38 V{a + 4} H14 Z M42 {b} H66 V{b + 4} H42 Z" fill="#1a1a1a"/>')

def _colossus_body(firing):
    glow = "#ffe680" if firing else "#ffb347"
    b = (f'<path d="M14 30 L66 30 L60 88 L20 88 Z" fill="{PLATE}" {TOUT}/>'
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
        b += (f'<path d="M66 34 Q76 24 76 10 L68 8 Q66 22 58 30 Z" fill="{PLATE}" {TOUT}/>'
              f'<rect x="64" y="0" width="14" height="12" rx="3" fill="{PLATE_DARK}" {TOUT}/>'
              '<circle cx="71" cy="2" r="7" fill="#c060ff" opacity="0.6"/><circle cx="71" cy="2" r="3.5" fill="#f0d0ff"/>')
    else:
        b += (f'<path d="M66 34 Q78 50 74 70 L66 70 Q68 54 60 42 Z" fill="{PLATE}" {TOUT}/>'
              f'<rect x="64" y="68" width="14" height="14" rx="3" fill="{PLATE_DARK}" {TOUT}/>'
              '<circle cx="71" cy="80" r="3" fill="#c060ff"/>')
    return b

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
def _key_slot(x, color, have, skull=False):
    if not have:
        return (f'<rect x="{x}" y="270" width="18" height="24" rx="2" fill="#000" fill-opacity="0.35" '
                'stroke="#777" stroke-dasharray="3 2"/>')
    if skull:
        return (f'<rect x="{x}" y="270" width="18" height="24" rx="2" fill="#5a2a8a" stroke="#000" stroke-width="1.5"/>'
                f'<circle cx="{x + 9}" cy="279" r="5.5" fill="#efe6c8"/>'
                f'<circle cx="{x + 7}" cy="278.5" r="1.4" fill="#2a0010"/><circle cx="{x + 11}" cy="278.5" r="1.4" fill="#2a0010"/>'
                f'<rect x="{x + 7}" y="284" width="4" height="7" fill="#c9a227"/>')
    return (f'<rect x="{x}" y="270" width="18" height="24" rx="2" fill="{color}" stroke="#000" stroke-width="1.5"/>'
            f'<rect x="{x + 3}" y="274" width="7" height="6" fill="#f5d36b"/>')

def hud(red, blue, skull):
    """HEALTH box, the three key slots (red, blue, skull) and the sprint bar frame."""
    body = ('<rect x="6" y="298" width="124" height="56" rx="6" fill="#000" fill-opacity="0.5"/>'
            + assets2._label(14, 314, "HEALTH")
            + '<text x="94" y="350" font-family="Sans Serif" font-weight="bold" font-size="24" fill="#ff4a24">%</text>'
            '<rect x="400" y="264" width="74" height="34" rx="5" fill="#000" fill-opacity="0.45"/>'
            + _key_slot(404, "#e02424", red) + _key_slot(427, "#2a6cf0", blue) + _key_slot(450, "", skull, skull=True))
    return assets5.hud_with_sprint(svg(480, 360, body))
HUDS = [hud(r, b, k) for k in (0, 1) for b in (0, 1) for r in (0, 1)]   # index = red + 2*blue + 4*skull

WEAPON_NAMES = ["fist", "pistol", "shotgun", "chaingun", "rocket launcher"]
AMMO_LABELS = ["FISTS", "BULLETS", "SHELLS", "BULLETS", "ROCKETS"]

def arms(owned_code, current):
    """The ammo box (label for the weapon in your hands) and the ARMS row: which of the
    5 weapon slots you own (white), don't own yet (dark) and are holding (yellow)."""
    owned = [1, 1, owned_code & 1, (owned_code >> 1) & 1, (owned_code >> 2) & 1]
    b = ('<rect x="350" y="298" width="124" height="56" rx="6" fill="#000" fill-opacity="0.5"/>'
         + assets2._label(358, 314, AMMO_LABELS[current - 1]))
    if current == 1:
        b += ('<text x="412" y="342" font-family="Sans Serif" font-size="11" fill="#999" text-anchor="middle">'
              'no ammo needed</text>')
    b += ('<rect x="350" y="240" width="124" height="21" rx="5" fill="#000" fill-opacity="0.45"/>'
          + assets2._label(356, 255, "ARMS", size=9, fill="#aaaaaa"))
    for slot in range(1, 6):
        x = 400 + (slot - 1) * 16
        color = "#ffe14d" if slot == current else ("#e8e8e8" if owned[slot - 1] else "#4a4a4a")
        b += (f'<text x="{x}" y="256" font-family="Sans Serif" font-weight="bold" font-size="13" fill="{color}" '
              f'text-anchor="middle">{slot}</text>')
        if slot == current:
            b += f'<rect x="{x - 6}" y="258" width="12" height="2" fill="#ffe14d"/>'
    return svg(480, 360, b)
ARMS = {(code, w): arms(code, w) for code in range(8) for w in range(1, 6)}

def boss_bar(name):
    w = 11 * len(name) + 30
    return svg(480, 360,
        f'<rect x="{240 - w / 2}" y="64" width="{w}" height="17" rx="5" fill="#000" fill-opacity="0.55"/>'
        + assets2._label(240, 77, name, "middle", 11, "#ffd23f")
        + '<rect x="140" y="82" width="200" height="8" rx="2" fill="none" stroke="#ffd23f" stroke-width="1.5"/>')
BOSS_BARS = {"warden": boss_bar("THE WARDEN"), "colossus": boss_bar("THE COLOSSUS")}

TOASTS = {
    "picked up 5": assets2.toast("Got the SKULL KEY! The exit unseals", "#d8a0ff"),
    "picked up 6": assets2.toast("+20 BULLETS", "#ffd23f"),
    "picked up 7": assets2.toast("+4 ROCKETS", "#ffa040"),
    "picked up 8": assets2.toast("SHOTGUN!  Press 3", "#ffe14d"),
    "picked up 9": assets2.toast("CHAINGUN!  Press 4", "#ffe14d"),
    "picked up 10": assets2.toast("ROCKET LAUNCHER!  Press 5", "#ffe14d"),
    "need skull key": assets2.toast("SEALED! Beat the boss for the SKULL KEY", "#d8a0ff"),
    "out of ammo": assets2.toast("Out of ammo! Switching weapons", "#ffa040"),
    "boss awake warden": assets2.toast("THE WARDEN AWAKENS", "#ff4040"),
    "boss awake colossus": assets2.toast("THE COLOSSUS AWAKENS", "#ff4040"),
    "boss enraged colossus": assets2.toast("THE COLOSSUS IS ENRAGED!", "#ff4040"),
    "music on": assets2.toast("Music ON  (N to switch)", "#60ff80"),
    "music off": assets2.toast("Music OFF  (N to switch)", "#aaaaaa"),
}

# =============================== OPTIONS MENU ===============================
OPTION_ROWS = ["TURN SPEED", "MOUSE STEERING", "MOUSE SENSITIVITY", "FIELD OF VIEW", "MUSIC", "START AT LEVEL"]
OPTION_ROW_Y = [80, 50, 20, -10, -40, -70]            # stage y of each row
TRACK_LEFT, TRACK_RIGHT = 0, 120                    # stage x of the slider tracks

def options_panel(paused):
    b = ('<rect width="480" height="360" fill="#000" fill-opacity="0.55"/>'
         '<rect x="44" y="28" width="392" height="306" rx="12" fill="#120304" fill-opacity="0.94" '
         'stroke="#ff6a00" stroke-opacity="0.6" stroke-width="2"/>')
    title = "PAUSED" if paused else "OPTIONS"
    unit = 5
    tw = text_width(title, unit)
    b += "<defs>" + gradient("ofire", 40, 40 + 7 * unit, FIRE_STOPS) + "</defs>"
    b += block_text(title, unit, 240 - tw / 2, 40, "ofire")
    for name, y in zip(OPTION_ROWS, OPTION_ROW_Y):
        sy = 180 - y
        b += assets2._label(70, sy + 5, name, size=12, fill="#e8d8c8")
        if name in ("TURN SPEED", "MOUSE SENSITIVITY", "FIELD OF VIEW"):
            b += (f'<line x1="{240 + TRACK_LEFT}" y1="{sy}" x2="{240 + TRACK_RIGHT}" y2="{sy}" stroke="#4a3a34" '
                  'stroke-width="5" stroke-linecap="round"/>')
    if paused:
        b += ('<text x="300" y="255" font-family="Sans Serif" font-size="11" fill="#8a8a8a" text-anchor="middle">'
              '(choose on the title screen)</text>')
    else:
        b += ('<text x="256" y="255" font-family="Sans Serif" font-size="16" font-weight="bold" fill="#ffd23f" '
              'text-anchor="middle">&lt;</text><text x="324" y="255" font-family="Sans Serif" font-size="16" '
              'font-weight="bold" fill="#ffd23f" text-anchor="middle">&gt;</text>')
    b += ('<text x="240" y="290" font-family="Sans Serif" font-size="11" fill="#cfcfcf" text-anchor="middle">'
          'UP / DOWN choose  •  LEFT / RIGHT change  •  or click and drag</text>')
    back = "P  to go back to the game" if paused else "O  to go back to the title screen"
    b += (f'<text x="240" y="312" font-family="Sans Serif" font-size="12" font-weight="bold" fill="#ffe14d" '
          f'text-anchor="middle">{back}</text>')
    return svg(480, 360, b)
OPTIONS_TITLE, OPTIONS_PAUSED = options_panel(False), options_panel(True)

ROW_HIGHLIGHT = svg(380, 26, '<rect x="1" y="1" width="378" height="24" rx="6" fill="#ff6a00" fill-opacity="0.2" '
                             'stroke="#ffb347" stroke-opacity="0.8" stroke-width="1.5"/>')
KNOB = svg(20, 20, '<circle cx="10" cy="10" r="8" fill="#ffd23f" stroke="#000" stroke-width="2"/>'
                   '<circle cx="8" cy="8" r="2.5" fill="#fff8d0"/>')
def _toggle(on):
    fill, text, tx = ("#2f9e44", "ON", 20) if on else ("#4a4a4a", "OFF", 36)
    knob_x = 45 if on else 11
    return svg(56, 22, f'<rect x="1" y="1" width="54" height="20" rx="10" fill="{fill}" stroke="#000" stroke-width="1.5"/>'
                       f'<circle cx="{knob_x}" cy="11" r="8" fill="#f0f0f0"/>'
                       f'<text x="{tx}" y="15.5" font-family="Sans Serif" font-size="11" font-weight="bold" fill="#fff" '
                       f'text-anchor="middle">{text}</text>')
TOGGLE_ON, TOGGLE_OFF = _toggle(True), _toggle(False)

# =============================== LEVEL CARDS, HEADINGS, SCREENS ===============================
CARDS = list(assets4.CARDS)
CARDS[2] = dict(CARDS[2], goal="Two keys, then slay the Warden",
                boss="BOSS: THE WARDEN carries the SKULL KEY to the exit")
CARDS += [
    dict(tint="#6a2a08", name="THE FOUNDRY", goal="Find the red key, then the exit", enemy="CHARGER",
         lines=["Lowers its head, then charges.", "Sidestep it and it slams into a wall."], boss=None),
    dict(tint="#0f3a4a", name="THE SUNKEN VAULTS", goal="Two keys, deep in the dark", enemy="WRAITH",
         lines=["Almost invisible from far away,", "and it blinks sideways. Stay sharp."], boss=None),
    dict(tint="#4a0a3a", name="THE CORE", goal="Destroy the Colossus, take its key", enemy="THE COLOSSUS",
         lines=["Huge, armored, and it gets angrier.", "At half health it calls for help."],
         boss="FINAL BOSS: the exit is sealed until it falls"),
]
CARD_ART = [assets4.card(c) for c in CARDS]
HEADINGS = [assets4.heading(f"LEVEL {i + 1}") for i in range(len(CARDS))]

EPISODE_COMPLETE = (assets3.COMPLETE
    .replace('font-size="40" fill="#40ff70"', 'font-size="30" fill="#40ff70"', 1)
    .replace(">LEVEL COMPLETE<", ">EPISODE 1 COMPLETE<", 1)
    .replace("</svg>", '<text x="240" y="126" font-family="Sans Serif" font-size="13" fill="#ffb080" '
                       'text-anchor="middle">The Warden has fallen... but something stirs far below.</text></svg>'))

KILLERS = {
    "charger": ("FLATTENED BY A CHARGER", "Tip: when it lowers its head, sidestep! It slams into walls."),
    "wraith": ("CAUGHT BY A WRAITH", "Tip: wraiths fade from far away. Keep your back to a wall."),
    "colossus": ("CRUSHED BY THE COLOSSUS", "Tip: hide behind the pillars, and save rockets for the boss."),
    "rocket": ("BLOWN UP BY YOUR OWN ROCKET", "Tip: don't fire rockets at monsters right next to you!"),
}
KILLED_BY = {name: assets5.killed_by(*text) for name, text in KILLERS.items()}

# =============================== SOUNDS ===============================
def _crack(dur, thump_hz, decay, seed, gain=1.0):
    rnd = random.Random(seed)
    n = int(RATE * dur)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(n)], 0.45)
    out = []
    for i in range(n):
        t = i / RATE
        s = noise[i] * 2.0 * math.exp(-t * decay) * min(1, t * 600)
        s += math.sin(2 * math.pi * thump_hz * t) * math.exp(-t * decay * 1.4) * 0.8
        out.append(s * gain)
    return _wav(out)

def pistol(): return _crack(0.25, 110, 30, 81)
def chaingun(): return _crack(0.13, 95, 42, 82, 0.9)

def rocket_launch():
    rnd = random.Random(83); n = int(RATE * 0.7); out, y = [], 0.0
    for i in range(n):
        t = i / RATE
        a = 0.05 + 0.3 * min(1, t / 0.15)
        y += a * (rnd.uniform(-1, 1) - y)
        s = y * 2.4 * math.exp(-t * 4) + math.sin(2 * math.pi * 60 * t) * math.exp(-t * 14) * 0.9
        out.append(s)
    return _wav(out)

def weapon_pickup():
    """Two metal clacks, then a bright ring."""
    rnd = random.Random(84); out = []
    for i in range(int(RATE * 0.5)):
        t = i / RATE; s = 0.0
        for c in (0.0, 0.11):
            if c <= t < c + 0.04:
                s += rnd.uniform(-1, 1) * 0.8 * math.exp(-(t - c) * 90)
        if t > 0.2:
            s += (math.sin(2 * math.pi * 1320 * t) + 0.5 * math.sin(2 * math.pi * 1980 * t)) * 0.25 * math.exp(-(t - 0.2) * 9)
        out.append(s)
    return _wav(out)

def wraith_blink():
    out = []
    for i in range(int(RATE * 0.45)):
        t = i / RATE
        f = 900 - 1400 * t
        s = math.sin(2 * math.pi * f * t) * 0.35 + math.sin(2 * math.pi * f * 1.5 * t) * 0.2
        out.append(s * math.sin(math.pi * t / 0.45) * (0.6 + 0.4 * math.sin(2 * math.pi * 30 * t)))
    return _wav(out)

def menu_click():
    out = [math.sin(2 * math.pi * 1500 * (i / RATE)) * math.exp(-(i / RATE) * 60) * 0.6 for i in range(int(RATE * 0.06))]
    return _wav(out)

def _note_freq(midi):
    return 440 * 2 ** ((midi - 69) / 12)

def _music(bpm, riff, root, kick_pattern, snare_pattern, seed, dark=False):
    """Mix an original loop: a distorted guitar riff (with a power-chord fifth on accents),
    a bass an octave down, and kick + snare + hi-hat drums. 'riff' = semitones above 'root'
    (None = rest), one per sixteenth note."""
    step = 60 / bpm / 4
    n = int(RATE * step * len(riff)); out = [0.0] * n
    rnd = random.Random(seed)
    for i, semi in enumerate(riff):
        if semi is None:
            continue
        start = int(i * step * RATE)
        accent = semi != 0
        length = int(RATE * step * (1.9 if accent else 0.6))
        for interval, gain in ((0, 0.26), (7, 0.16 if accent else 0), (-12, 0.22)):
            if not gain:
                continue
            f, ph = _note_freq(root + semi + interval), 0.0
            for k in range(length):
                if start + k >= n: break
                t = k / RATE
                ph += f / RATE
                wave = (2 * (ph % 1) - 1) if interval != -12 else math.sin(2 * math.pi * ph)
                env = min(1, t * 300) * math.exp(-t * (4 if accent else 18))
                shaped = math.tanh((3.5 if not dark else 2.5) * wave) if interval != -12 else wave
                out[start + k] += shaped * gain * env
    for s16 in range(len(riff)):
        start = int(s16 * step * RATE)
        if kick_pattern[s16 % len(kick_pattern)] == "x":
            for k in range(int(RATE * 0.2)):
                if start + k >= n: break
                t = k / RATE; out[start + k] += math.sin(2 * math.pi * (105 - 240 * t) * t) * math.exp(-t * 20) * 0.8
        if snare_pattern[s16 % len(snare_pattern)] == "x":
            for k in range(int(RATE * 0.18)):
                if start + k >= n: break
                t = k / RATE
                out[start + k] += (rnd.uniform(-1, 1) * 0.42 + math.sin(2 * math.pi * 190 * t) * 0.2) * math.exp(-t * 22)
        if s16 % 2 == 0:
            for k in range(int(RATE * 0.04)):
                if start + k >= n: break
                t = k / RATE; out[start + k] += rnd.uniform(-1, 1) * 0.07 * math.exp(-t * 90)
    smooth = _lowpass(out, 0.3 if dark else 0.38)
    peak = max(abs(s) for s in smooth) or 1
    return _wav([s / peak * 0.85 for s in smooth])

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

# =============================== TITLE SCREEN TEXT ===============================
def title_sky():
    """The title backdrop with a taller controls strip: the game has more keys now."""
    sky = assets4.TITLE_SKY
    start = sky.index('<rect y="318"')
    strip = ('<rect y="308" width="480" height="52" fill="#000" opacity="0.62"/>'
             '<text x="240" y="322" font-family="Sans Serif" font-size="9.5" font-weight="bold" fill="#e8a070" '
             'text-anchor="middle" letter-spacing="1.5">A RAYCASTING SHOOTER BUILT ENTIRELY IN SCRATCH</text>'
             '<text x="240" y="337" font-family="Sans Serif" font-size="11" fill="#cfcfcf" text-anchor="middle">'
             'ARROWS / WASD move  •  Q sprint  •  SPACE shoot  •  1-5 weapons</text>'
             '<text x="240" y="352" font-family="Sans Serif" font-size="11" fill="#cfcfcf" text-anchor="middle">'
             'E open / use  •  M map  •  N music  •  P pause  •  O OPTIONS</text>')
    return sky[:start] + strip + "</svg>"
TITLE_SKY = title_sky()

VICTORY_LOGO = assets5.VICTORY_LOGO.replace("YOU ESCAPED THE FORTRESS", "YOU DESTROYED THE CORE")
