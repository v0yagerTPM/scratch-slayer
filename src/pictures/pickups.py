"""Things to pick up: health, ammo boxes, keys, the skull key and the weapon pickups."""
from pictures.drawing import svg

# ---------------- pickups (40x40, anchored bottom-center) ----------------
MEDKIT = svg(40, 40,
    '<ellipse cx="20" cy="38" rx="17" ry="2.5" fill="#000" opacity="0.35"/>'
    '<rect x="3" y="14" width="34" height="24" rx="3" fill="#f2f2f2" stroke="#555" stroke-width="1.5"/>'
    '<rect x="14" y="10" width="12" height="5" rx="1.5" fill="#999" stroke="#555"/>'
    '<path d="M17 18 H23 V23 H28 V29 H23 V34 H17 V29 H12 V23 H17 Z" fill="#e01e1e"/>')

SHELLS = svg(40, 40,
    '<ellipse cx="20" cy="38" rx="17" ry="2.5" fill="#000" opacity="0.35"/>'
    + "".join(f'<rect x="{6 + shell_number * 6}" y="9" width="5" height="12" rx="1" fill="#c62020" stroke="#601010"/>'
              f'<rect x="{6 + shell_number * 6}" y="17" width="5" height="4" fill="#d9b44a"/>' for shell_number in range(5))
    + '<rect x="3" y="20" width="34" height="18" rx="2" fill="#6b4a1e" stroke="#2e1f0a" stroke-width="1.5"/>'
      '<rect x="8" y="25" width="24" height="8" fill="#d9b44a"/>'
      '<text x="20" y="32" font-family="Sans Serif" font-size="7" font-weight="bold" fill="#2e1f0a" '
      'text-anchor="middle">SHELLS</text>')

def _key(color, edge_color):
    return svg(40, 40,
        f'<circle cx="20" cy="22" r="17" fill="{color}" opacity="0.25"/>'
        '<ellipse cx="20" cy="38" rx="12" ry="2" fill="#000" opacity="0.35"/>'
        f'<rect x="8" y="8" width="24" height="30" rx="3" fill="{color}" stroke="{edge_color}" stroke-width="2"/>'
        '<rect x="12" y="13" width="10" height="8" rx="1" fill="#f5d36b" stroke="#8a6d1a"/>'
        '<rect x="12" y="26" width="16" height="3" fill="#fff" opacity="0.7"/>'
        '<rect x="12" y="31" width="11" height="3" fill="#fff" opacity="0.7"/>')

RED_KEY, BLUE_KEY = _key("#e02424", "#6a0d0d"), _key("#2a6cf0", "#0d2a6a")

# ---------------- ammo, weapon pickups and the skull key ----------------
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
