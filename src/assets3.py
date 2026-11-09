"""Art + sound for round 3: spitter, golem, warden boss, barrels, explosions, projectiles, boss bar, sounds."""
import math, random
from assets import svg, _wav, _lowpass, RATE
import assets2

# =============================== SPITTER (level 2) ===============================
# A squat slime creature with three eyes and a sac on its back. 80 x 120, feet at the bottom.
SLIME, SLIME_DARK, SLIME_LIGHT = "#5fae3c", "#356f1f", "#9fe06a"
SOUT = 'stroke="#1d3d10" stroke-width="1.5"'

def _spitter_legs(phase):
    out = ""
    for i, x in enumerate((16, 30, 50, 64)):
        lift = 5 if (i + phase) % 2 == 0 else 0
        out += f'<path d="M{x - 4} 100 L{x - 6} {118 - lift} L{x + 6} {118 - lift} L{x + 4} 100 Z" fill="{SLIME_DARK}" {SOUT}/>'
    return out

def _spitter(phase=0, mouth="closed"):
    body = (_spitter_legs(phase)
            + f'<ellipse cx="46" cy="66" rx="20" ry="16" fill="{SLIME_LIGHT}" opacity="0.85" {SOUT}/>'
              '<circle cx="40" cy="60" r="3" fill="#d7ff9e"/><circle cx="52" cy="66" r="2.5" fill="#d7ff9e"/>'
            + f'<ellipse cx="40" cy="88" rx="32" ry="20" fill="{SLIME}" {SOUT}/>'
              f'<circle cx="22" cy="84" r="3.5" fill="{SLIME_DARK}"/><circle cx="58" cy="94" r="3" fill="{SLIME_DARK}"/>'
              f'<circle cx="62" cy="80" r="2.5" fill="{SLIME_DARK}"/>')
    eyes = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#ffe14d" stroke="#1d3d10" stroke-width="1"/>'
                   f'<circle cx="{x}" cy="{y}" r="2" fill="#000"/>' for x, y in ((29, 74), (40, 70), (51, 74)))
    if mouth == "open":
        m = ('<ellipse cx="40" cy="92" rx="15" ry="11" fill="#1a0d05"/>'
             '<path d="M27 86 L30 91 L33 86 L36 91 L40 86 L44 91 L47 86 L50 91 L53 86" fill="none" stroke="#fff" stroke-width="2"/>'
             '<circle cx="40" cy="94" r="7" fill="#b6ff3a" stroke="#4c8f12" stroke-width="1.5"/>'
             '<circle cx="38" cy="92" r="2" fill="#f2ffd0"/>')
    else:
        m = ('<path d="M28 92 Q40 100 52 92 Q40 96 28 92 Z" fill="#1a0d05" stroke="#1d3d10"/>'
             '<path d="M44 96 Q45 102 43 106" stroke="#b6ff3a" stroke-width="2" fill="none"/>')
    return svg(80, 120, body + eyes + m)

SPITTER_WALK1, SPITTER_WALK2, SPITTER_ATTACK = _spitter(0), _spitter(1), _spitter(0, "open")
SPITTER_DEAD = svg(80, 120,
    f'<ellipse cx="40" cy="113" rx="36" ry="7" fill="{SLIME_DARK}" opacity="0.9"/>'
    f'<ellipse cx="38" cy="109" rx="24" ry="7" fill="{SLIME}" {SOUT}/>'
    '<circle cx="30" cy="107" r="3" fill="#ffe14d"/><circle cx="44" cy="106" r="3" fill="#ffe14d"/>'
    '<path d="M28 105 l4 4 m0 -4 l-4 4 M42 104 l4 4 m0 -4 l-4 4" stroke="#222" stroke-width="1.2"/>'
    '<circle cx="64" cy="113" r="3" fill="#b6ff3a"/><circle cx="12" cy="112" r="2" fill="#b6ff3a"/>')

# =============================== GOLEM (level 3) ===============================
# A hulking stone creature with glowing cracks and huge fists.
STONE, STONE_DARK, GLOW = "#6f6878", "#4a4452", "#ff8a1f"
GOUT = 'stroke="#25212b" stroke-width="1.5"'

def _golem_legs(phase):
    ly, ry = (108, 116) if phase == 0 else (116, 108)
    return (f'<path d="M24 86 L20 {ly} L36 {ly} L38 86 Z" fill="{STONE_DARK}" {GOUT}/>'
            f'<path d="M56 86 L60 {ry} L44 {ry} L42 86 Z" fill="{STONE_DARK}" {GOUT}/>'
            f'<rect x="16" y="{ly}" width="24" height="7" rx="2" fill="#2f2a36"/>'
            f'<rect x="40" y="{ry}" width="24" height="7" rx="2" fill="#2f2a36"/>')

def _golem_body():
    return (f'<path d="M16 42 L64 42 L58 90 L22 90 Z" fill="{STONE}" {GOUT}/>'
            f'<path d="M30 50 L36 62 L32 74 M50 48 L46 60 L52 70 M40 78 L44 86" stroke="{GLOW}" stroke-width="2.5" fill="none"/>'
            f'<rect x="28" y="20" width="24" height="22" rx="6" fill="{STONE}" {GOUT}/>'
            f'<rect x="31" y="27" width="7" height="4" fill="{GLOW}"/><rect x="42" y="27" width="7" height="4" fill="{GLOW}"/>'
            '<path d="M33 37 H47" stroke="#25212b" stroke-width="2"/>')

def _golem_arms_down(swing):
    return (f'<path d="M16 46 Q{6 + swing} 66 {8 + swing} 84 L{18 + swing} 84 Q{18 + swing} 66 24 52 Z" fill="{STONE_DARK}" {GOUT}/>'
            f'<path d="M64 46 Q{74 - swing} 66 {72 - swing} 84 L{62 - swing} 84 Q{62 - swing} 66 56 52 Z" fill="{STONE_DARK}" {GOUT}/>'
            f'<rect x="{3 + swing}" y="82" width="20" height="18" rx="5" fill="{STONE}" {GOUT}/>'
            f'<rect x="{57 - swing}" y="82" width="20" height="18" rx="5" fill="{STONE}" {GOUT}/>')

def _golem_arms_up():
    return (f'<path d="M18 46 Q6 30 10 12 L20 12 Q20 30 28 42 Z" fill="{STONE_DARK}" {GOUT}/>'
            f'<path d="M62 46 Q74 30 70 12 L60 12 Q60 30 52 42 Z" fill="{STONE_DARK}" {GOUT}/>'
            f'<rect x="4" y="0" width="20" height="18" rx="5" fill="{STONE}" {GOUT}/>'
            f'<rect x="56" y="0" width="20" height="18" rx="5" fill="{STONE}" {GOUT}/>')

GOLEM_WALK1 = svg(80, 120, _golem_legs(0) + _golem_body() + _golem_arms_down(2))
GOLEM_WALK2 = svg(80, 120, _golem_legs(1) + _golem_body() + _golem_arms_down(-2))
GOLEM_ATTACK = svg(80, 120, _golem_legs(0) + _golem_arms_up() + _golem_body())
GOLEM_DEAD = svg(80, 120,
    ''.join(f'<path d="M{x} 120 L{x + 4} {y} L{x + w - 3} {y - 2} L{x + w} 120 Z" fill="{c}" {GOUT}/>'
            for x, y, w, c in ((6, 104, 22, STONE_DARK), (24, 98, 26, STONE), (46, 104, 24, STONE_DARK), (16, 108, 16, STONE)))
    + f'<path d="M30 108 L36 114 M50 110 L46 116" stroke="{GLOW}" stroke-width="2" opacity="0.6"/>')

# =============================== WARDEN (boss) ===============================
# Tall armored demon lord: crimson plate, gold trim, glowing visor, fire in hand.
ARMOR, ARMOR_DARK, GOLD, CAPE = "#7a1527", "#4a0b17", "#d8a83c", "#3b0610"
WOUT = 'stroke="#1a0308" stroke-width="1.5"'

def _warden_legs(phase):
    ly, ry = (110, 117) if phase == 0 else (117, 110)
    return (f'<path d="M28 82 L26 {ly} L37 {ly} L38 82 Z" fill="{ARMOR_DARK}" {WOUT}/>'
            f'<path d="M52 82 L54 {ry} L43 {ry} L42 82 Z" fill="{ARMOR_DARK}" {WOUT}/>'
            f'<path d="M22 {ly} H38 V{ly + 3} H22 Z" fill="{GOLD}"/><path d="M42 {ry} H58 V{ry + 3} H42 Z" fill="{GOLD}"/>')

def _warden_body():
    return (f'<path d="M20 40 L60 40 L70 104 L10 104 Z" fill="{CAPE}" opacity="0.95"/>'
            f'<path d="M24 40 L56 40 L54 84 L26 84 Z" fill="{ARMOR}" {WOUT}/>'
            f'<path d="M26 60 H54 M28 72 H52" stroke="{GOLD}" stroke-width="2"/>'
            f'<path d="M40 44 L46 52 L40 60 L34 52 Z" fill="{GOLD}"/>'
            f'<ellipse cx="22" cy="44" rx="8" ry="6" fill="{GOLD}" {WOUT}/><ellipse cx="58" cy="44" rx="8" ry="6" fill="{GOLD}" {WOUT}/>'
            f'<path d="M30 16 Q40 8 50 16 L50 36 L30 36 Z" fill="{ARMOR_DARK}" {WOUT}/>'
            f'<path d="M30 18 Q20 8 22 0 Q28 10 34 14 Z M50 18 Q60 8 58 0 Q52 10 46 14 Z" fill="#e8dcb8" stroke="#5a5030"/>'
            '<rect x="33" y="24" width="14" height="4" rx="1" fill="#ffdd55"/>')

def _warden_arms(raised):
    if raised:
        return (f'<path d="M24 44 Q12 30 18 14 L26 16 Q22 30 30 40 Z" fill="{ARMOR}" {WOUT}/>'
                f'<path d="M56 44 Q68 30 62 14 L54 16 Q58 30 50 40 Z" fill="{ARMOR}" {WOUT}/>'
                '<circle cx="40" cy="10" r="10" fill="#ffd23f" opacity="0.6"/><circle cx="40" cy="10" r="6" fill="#fff6c0"/>'
                '<circle cx="22" cy="12" r="5" fill="#ff7a00"/><circle cx="58" cy="12" r="5" fill="#ff7a00"/>')
    return (f'<path d="M24 44 Q14 62 16 80 L24 80 Q24 64 30 52 Z" fill="{ARMOR}" {WOUT}/>'
            f'<path d="M56 44 Q66 62 64 80 L56 80 Q56 64 50 52 Z" fill="{ARMOR}" {WOUT}/>'
            '<circle cx="62" cy="84" r="7" fill="#ff7a00" opacity="0.8"/><circle cx="62" cy="84" r="4" fill="#ffe680"/>')

WARDEN_WALK1 = svg(80, 120, _warden_legs(0) + _warden_body() + _warden_arms(False))
WARDEN_WALK2 = svg(80, 120, _warden_legs(1) + _warden_body() + _warden_arms(False))
WARDEN_ATTACK = svg(80, 120, _warden_legs(0) + _warden_body() + _warden_arms(True))
WARDEN_DEAD = svg(80, 120,
    f'<path d="M4 118 Q40 96 76 118 Z" fill="{CAPE}"/>'
    f'<path d="M18 116 L24 102 L56 100 L62 116 Z" fill="{ARMOR}" {WOUT}/>'
    f'<path d="M24 108 H56" stroke="{GOLD}" stroke-width="2"/>'
    f'<path d="M58 110 Q66 98 76 104 L74 116 L58 116 Z" fill="{ARMOR_DARK}" {WOUT}/>'
    '<path d="M64 102 Q70 92 72 86 Q72 96 68 104 Z" fill="#e8dcb8" stroke="#5a5030"/>'
    '<rect x="62" y="108" width="10" height="3" fill="#5a4a20"/>')

# =============================== BARREL + EXPLOSION ===============================
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
    for i in range(16):
        a = i / 16 * 2 * math.pi
        r = r_fire * (0.75 + 0.35 * rnd.random())
        pts.append(f"{45 + r * math.cos(a):.1f},{50 + r * math.sin(a) * 0.9:.1f}")
    body = ''
    if smoke:
        body += f'<circle cx="45" cy="44" r="{r_fire + 4}" fill="#3a3330" opacity="0.6"/>'
    body += f'<polygon points="{" ".join(pts)}" fill="#ff7a00" opacity="{0.55 if smoke else 0.95}"/>'
    if r_core:
        body += f'<circle cx="45" cy="50" r="{r_core + 8}" fill="#ffd23f"/><circle cx="45" cy="50" r="{r_core}" fill="#fff8d0"/>'
    for i in range(embers):
        a = rnd.random() * 2 * math.pi; r = r_fire * (0.6 + 0.6 * rnd.random())
        body += f'<circle cx="{45 + r * math.cos(a):.1f}" cy="{50 + r * math.sin(a):.1f}" r="2.5" fill="#ffcf4a"/>'
    return svg(90, 90, body)

EXPLOSIONS = [_blast(10, 22, False, 4), _blast(14, 38, False, 8), _blast(0, 36, True, 10)]

# =============================== PROJECTILES ===============================
ACID_SHOT = svg(26, 26,
    '<circle cx="13" cy="13" r="12" fill="#b6ff3a" opacity="0.35"/>'
    '<circle cx="13" cy="13" r="8" fill="#8fe024" stroke="#3f7a10" stroke-width="1.5"/>'
    '<circle cx="10" cy="10" r="2.5" fill="#f2ffd0"/>')
FIRE_SHOT = svg(30, 30,
    '<circle cx="15" cy="15" r="14" fill="#ff7a00" opacity="0.35"/>'
    '<path d="M15 3 Q22 9 24 15 Q24 25 15 27 Q6 25 6 15 Q8 9 15 3 Z" fill="#ff5a00" stroke="#a02800" stroke-width="1.2"/>'
    '<circle cx="15" cy="16" r="6" fill="#ffd23f"/><circle cx="15" cy="17" r="3" fill="#fff8d0"/>')

# =============================== BOSS BAR + RESULTS SCREEN ===============================
BOSS_BAR = svg(480, 360,
    '<rect x="186" y="64" width="108" height="17" rx="5" fill="#000" fill-opacity="0.55"/>'
    + assets2._label(240, 77, "THE WARDEN", "middle", 11, "#ffd23f")
    + '<rect x="140" y="82" width="200" height="8" rx="2" fill="none" stroke="#ffd23f" stroke-width="1.5"/>')

COMPLETE = assets2._screen("LEVEL COMPLETE", "#40ff70", [("Press SPACE to continue", 300, 18, "#ffe14d")],
    assets2._label(110, 156, "KILLS", size=18) + assets2._label(110, 201, "ITEMS", size=18)
    + assets2._label(110, 246, "SECRETS", size=18)
    + "".join(f'<text x="285" y="{y}" font-family="Sans Serif" font-weight="bold" font-size="30" fill="#ff4a24" '
              f'text-anchor="middle">/</text>' for y in (160, 205, 250)), 0.88)

# =============================== SOUNDS ===============================
def spit():
    rnd = random.Random(11); n = int(RATE * 0.3)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(n)], 0.25)
    out = []
    for i in range(n):
        t = i / RATE
        out.append(noise[i] * 2.2 * math.exp(-t * 14) + math.sin(2 * math.pi * (500 - 900 * t) * t) * 0.3 * math.exp(-t * 10))
    return _wav(out)

def fireball():
    rnd = random.Random(12); n = int(RATE * 0.5)
    noise = [rnd.uniform(-1, 1) for _ in range(n)]
    out, y = [], 0.0
    for i in range(n):
        t = i / RATE
        a = 0.05 + 0.25 * min(1, t / 0.2)
        y += a * (noise[i] - y)
        out.append(y * 2.5 * min(1, t * 30) * (1 - t / 0.5) + math.sin(2 * math.pi * 90 * t) * 0.3 * (1 - t / 0.5))
    return _wav(out)

def explosion():
    rnd = random.Random(13); n = int(RATE * 1.1)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(n)], 0.08)
    out = []
    for i in range(n):
        t = i / RATE
        s = noise[i] * 5 * math.exp(-t * 3.5) * min(1, t * 300)
        s += math.sin(2 * math.pi * (60 - 25 * t) * t) * math.exp(-t * 4) * 0.9
        out.append(s)
    return _wav(out)

def secret():
    rnd = random.Random(14); n = int(RATE * 0.9)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(n)], 0.03)
    out = []
    for i in range(n):
        t = i / RATE
        s = noise[i] * 4 * (1 - t / 0.9) * min(1, t * 10)
        if t > 0.55:
            for f in (523, 784):
                s += math.sin(2 * math.pi * f * t) * 0.15 * math.exp(-(t - 0.55) * 6)
        out.append(s)
    return _wav(out)

TITLE = assets2._screen("SCRATCH SLAYER", "#e02424", [
    ("A raycasting shooter built entirely in Scratch", 132, 14, "#bbbbbb"),
    ("UP / DOWN  or  W / S  -  move       LEFT / RIGHT  -  turn", 166, 14, "#ffffff"),
    ("A / D  -  strafe       SPACE  -  shoot       M  -  map", 188, 14, "#ffffff"),
    ("E  -  open doors and flip switches", 210, 14, "#ffffff"),
    ("Fight through 3 levels. Find the EXIT SWITCH on each one.", 240, 14, "#40ff70"),
    ("Shoot barrels to blast monsters. Some walls hide secrets...", 262, 13, "#ffd23f"),
    ("Press SPACE to start", 304, 20, "#ffe14d")])
