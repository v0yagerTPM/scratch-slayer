"""The weapons in your hands (fist, pistol, shotgun, chaingun, rocket launcher) and the crosshair."""
import math
from pictures.drawing import svg

# ---------------- the shotgun and the crosshair ----------------
def _gun(flash):
    picture = ""
    if flash:
        picture += ('<polygon points="80,0 89,38 112,16 96,50 134,48 98,62 80,66 62,62 26,48 64,50 48,16 71,38" '
              'fill="#ffd23f" stroke="#ff7a00" stroke-width="3"/>'
              '<circle cx="80" cy="56" r="13" fill="#fff8d0"/>')
    shade = "#5a5a5a" if flash else "#3b3b3b"
    picture += ('<g transform="translate(0,60)">'
          f'<path d="M70 0 L90 0 L100 70 L60 70 Z" fill="{shade}" stroke="#111" stroke-width="2"/>'
          '<path d="M73 0 L87 0 L86 6 L74 6 Z" fill="#111"/>'
          '<line x1="80" y1="2" x2="80" y2="70" stroke="#777" stroke-width="2"/>'
          '<path d="M62 40 L98 40 L106 82 L54 82 Z" fill="#8a5428" stroke="#3b220d" stroke-width="2"/>'
          '<path d="M60 50 H100 M59 58 H101 M57 66 H103 M56 74 H104" stroke="#5e3615" stroke-width="2"/>'
          '<path d="M50 80 L110 80 L122 130 L38 130 Z" fill="#2b2b2b" stroke="#111" stroke-width="2"/>'
          '<path d="M64 86 L96 86 L100 100 L60 100 Z" fill="#454545"/>'
          '<path d="M44 74 L18 130 L46 130 L62 80 Z" fill="#4a6b33" stroke="#1d2b12" stroke-width="2"/>'
          '<path d="M38 60 Q50 50 63 57 L65 77 Q52 84 41 77 Z" fill="#3e5a2a" stroke="#1d2b12" stroke-width="2"/>'
          '<path d="M46 59 L56 62 M44 66 L57 68 M44 73 L57 74" stroke="#1d2b12" stroke-width="1.5"/>'
          '<path d="M104 100 Q122 94 134 106 L138 130 L104 130 Z" fill="#3e5a2a" stroke="#1d2b12" stroke-width="2"/>'
          '<path d="M134 106 L150 130 L138 130 Z" fill="#4a6b33" stroke="#1d2b12" stroke-width="2"/>'
          '</g>')
    return svg(160, 190, picture)

GUN_IDLE, GUN_FIRE = _gun(False), _gun(True)

CROSSHAIR = svg(20, 20, '<path d="M10 1 V7 M10 13 V19 M1 10 H7 M13 10 H19" stroke="#000" stroke-width="4"/>'
                        '<path d="M10 1 V7 M10 13 V19 M1 10 H7 M13 10 H19" stroke="#ffe14d" stroke-width="2"/>')

GLOVE, GLOVE_DARK, GLOVE_LINE = "#4a6b33", "#3e5a2a", "#1d2b12"

# ---------------- weapons (160 x 190, bottom-center) ----------------
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
