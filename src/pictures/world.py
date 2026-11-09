"""Other things in the 3D world: barrels, explosions and projectiles. Also two tiny
helper pictures: an invisible dot and the black backdrop."""
import math, random
from pictures.drawing import svg

TINY = svg(2, 2, '<rect width="2" height="2" fill="#000" fill-opacity="0"/>')

BACKDROP = svg(480, 360, '<rect width="480" height="360" fill="#000"/>')

# ---------------- barrel + explosion ----------------
BARREL = svg(40, 52,
    '<ellipse cx="20" cy="50" rx="17" ry="2.5" fill="#000" opacity="0.35"/>'
    '<path d="M5 8 Q3 28 5 48 L35 48 Q37 28 35 8 Z" fill="#c2431b" stroke="#4a1505" stroke-width="1.5"/>'
    '<ellipse cx="20" cy="8" rx="15" ry="4" fill="#d9622e" stroke="#4a1505" stroke-width="1.5"/>'
    '<ellipse cx="20" cy="8" rx="5" ry="1.5" fill="#4a1505"/>'
    '<path d="M4 18 H36 M4 38 H36" stroke="#4a1505" stroke-width="2.5"/>'
    '<path d="M14 22 L20 33 L26 22 Z" fill="#ffd23f" stroke="#111" stroke-width="1"/>'
    '<path d="M20 25 V29 M20 31 V31.5" stroke="#111" stroke-width="1.5"/>'
    '<path d="M8 12 Q7 28 8 44" stroke="#fff" stroke-width="2" opacity="0.25" fill="none"/>')

def _blast(r_core, r_fire, smoke, embers):
    rnd = random.Random(r_fire)
    pts = []
    for point_number in range(16):
        angle = point_number / 16 * 2 * math.pi
        radius = r_fire * (0.75 + 0.35 * rnd.random())
        pts.append(f"{45 + radius * math.cos(angle):.1f},{50 + radius * math.sin(angle) * 0.9:.1f}")
    body = ''
    if smoke:
        body += f'<circle cx="45" cy="44" r="{r_fire + 4}" fill="#3a3330" opacity="0.6"/>'
    body += f'<polygon points="{" ".join(pts)}" fill="#ff7a00" opacity="{0.55 if smoke else 0.95}"/>'
    if r_core:
        body += f'<circle cx="45" cy="50" r="{r_core + 8}" fill="#ffd23f"/><circle cx="45" cy="50" r="{r_core}" fill="#fff8d0"/>'
    for ember_number in range(embers):
        angle = rnd.random() * 2 * math.pi; radius = r_fire * (0.6 + 0.6 * rnd.random())
        body += f'<circle cx="{45 + radius * math.cos(angle):.1f}" cy="{50 + radius * math.sin(angle):.1f}" r="2.5" fill="#ffcf4a"/>'
    return svg(90, 90, body)

EXPLOSIONS = [_blast(10, 22, False, 4), _blast(14, 38, False, 8), _blast(0, 36, True, 10)]

# ---------------- projectiles ----------------
ACID_SHOT = svg(26, 26,
    '<circle cx="13" cy="13" r="12" fill="#b6ff3a" opacity="0.35"/>'
    '<circle cx="13" cy="13" r="8" fill="#8fe024" stroke="#3f7a10" stroke-width="1.5"/>'
    '<circle cx="10" cy="10" r="2.5" fill="#f2ffd0"/>')

FIRE_SHOT = svg(30, 30,
    '<circle cx="15" cy="15" r="14" fill="#ff7a00" opacity="0.35"/>'
    '<path d="M15 3 Q22 9 24 15 Q24 25 15 27 Q6 25 6 15 Q8 9 15 3 Z" fill="#ff5a00" stroke="#a02800" stroke-width="1.2"/>'
    '<circle cx="15" cy="16" r="6" fill="#ffd23f"/><circle cx="15" cy="17" r="3" fill="#fff8d0"/>')

ROCKET_SHOT = svg(26, 26,
    '<circle cx="13" cy="13" r="12" fill="#ff7a00" opacity="0.35"/>'
    '<circle cx="13" cy="13" r="7" fill="#ffd23f"/><circle cx="13" cy="13" r="3.5" fill="#fff8d0"/>'
    '<path d="M13 1 L17 9 L9 9 Z" fill="#888" stroke="#333"/>')

PLASMA_SHOT = svg(30, 30,
    '<circle cx="15" cy="15" r="14" fill="#a040ff" opacity="0.35"/>'
    '<circle cx="15" cy="15" r="9" fill="#c070ff" stroke="#5a1a9a" stroke-width="1.2"/>'
    '<circle cx="15" cy="15" r="4.5" fill="#f0d8ff"/>')
