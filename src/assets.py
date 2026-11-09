"""Original SVG art + synthesized WAV sound effects for the game."""
import math, random, struct, io, wave

def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{body}</svg>')

OUT = 'stroke="#2a0e04" stroke-width="1.5"'
SKIN, SKIN2, CHEST, BONE = "#8b3a1a", "#6e2c12", "#a8542b", "#e0d6b0"

def _head():
    return (f'<path d="M31 22 Q21 11 25 1 Q29 12 36 17 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>'
            f'<path d="M49 22 Q59 11 55 1 Q51 12 44 17 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>'
            f'<ellipse cx="40" cy="28" rx="14" ry="13" fill="{SKIN}" {OUT}/>'
            '<path d="M28 23 L40 27 L52 23 L52 25 L40 29 L28 25 Z" fill="#3a1206"/>'
            '<ellipse cx="34" cy="28" rx="3.6" ry="2.6" fill="#ffe14d"/>'
            '<ellipse cx="46" cy="28" rx="3.6" ry="2.6" fill="#ffe14d"/>'
            '<circle cx="34" cy="28" r="1.2" fill="#c00"/><circle cx="46" cy="28" r="1.2" fill="#c00"/>'
            '<path d="M32 34 Q40 41 48 34 L46 37 Q40 43 34 37 Z" fill="#2a0000"/>'
            '<path d="M35 35.5 L36.5 38 L38 36.3 L40 38.5 L42 36.3 L43.5 38 L45 35.5 Z" fill="#fff"/>')

def _body():
    return (f'<ellipse cx="40" cy="64" rx="21" ry="25" fill="{SKIN}" {OUT}/>'
            f'<ellipse cx="40" cy="68" rx="12" ry="15" fill="{CHEST}"/>'
            '<path d="M32 62 Q40 65 48 62 M31 69 Q40 72 49 69 M32 76 Q40 79 48 76" stroke="#6e2c12" stroke-width="1.5" fill="none"/>'
            f'<path d="M19 46 L13 37 L24 43 Z M61 46 L67 37 L56 43 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>')

def _claws(x, y, up=False):
    d = -1 if up else 1
    return "".join(f'<path d="M{x+i*3-1} {y} L{x+i*3} {y+6*d} L{x+i*3+1.5} {y} Z" fill="{BONE}"/>' for i in range(3))

def _legs(lift_left=False, lift_right=False):
    ly = 108 if lift_left else 116
    ry = 108 if lift_right else 116
    return (f'<path d="M28 84 L24 {ly} L34 {ly} L37 86 Z" fill="{SKIN2}" {OUT}/>'
            f'<path d="M52 84 L56 {ry} L46 {ry} L43 86 Z" fill="{SKIN2}" {OUT}/>'
            f'<path d="M21 {ly} L36 {ly} L35 {ly+3} L20 {ly+3} Z" fill="#2a0e04"/>'
            f'<path d="M44 {ry} L59 {ry} L60 {ry+3} L45 {ry+3} Z" fill="#2a0e04"/>')

def _arms_down(swing=0):
    return (f'<path d="M21 50 Q{10+swing} 70 {13+swing} 90 L{20+swing} 90 Q{18+swing} 72 27 58 Z" fill="#7a3215" {OUT}/>'
            f'<path d="M59 50 Q{70-swing} 70 {67-swing} 90 L{60-swing} 90 Q{62-swing} 72 53 58 Z" fill="#7a3215" {OUT}/>'
            + _claws(13 + swing, 90) + _claws(60 - swing, 90))

def _arms_up():
    return (f'<path d="M22 50 Q8 34 12 12 L19 12 Q17 32 28 46 Z" fill="#7a3215" {OUT}/>'
            f'<path d="M58 50 Q72 34 68 12 L61 12 Q63 32 52 46 Z" fill="#7a3215" {OUT}/>'
            + _claws(12, 12, up=True) + _claws(61, 12, up=True))

IMP_WALK1 = svg(80, 120, _legs(lift_left=True) + _arms_down(2) + _body() + _head())
IMP_WALK2 = svg(80, 120, _legs(lift_right=True) + _arms_down(-2) + _body() + _head())
IMP_ATTACK = svg(80, 120, _legs() + _arms_up() + _body() + _head())
IMP_DEAD = svg(80, 120,
    '<ellipse cx="40" cy="114" rx="36" ry="6" fill="#3d0f04" opacity="0.85"/>'
    f'<ellipse cx="44" cy="108" rx="25" ry="8" fill="#7a3215" {OUT}/>'
    f'<ellipse cx="44" cy="106" rx="14" ry="4" fill="{CHEST}"/>'
    f'<ellipse cx="18" cy="107" rx="9" ry="7" fill="{SKIN}" {OUT}/>'
    f'<path d="M14 101 Q6 94 2 98 Q8 100 12 104 Z" fill="{BONE}" stroke="#5a5030" stroke-width="1"/>'
    '<path d="M15 105 l3 3 m0 -3 l-3 3 M20 105 l3 3 m0 -3 l-3 3" stroke="#222" stroke-width="1.2"/>'
    + _claws(66, 110))

def _gun(flash):
    g = ""
    if flash:
        g += ('<polygon points="80,0 89,38 112,16 96,50 134,48 98,62 80,66 62,62 26,48 64,50 48,16 71,38" '
              'fill="#ffd23f" stroke="#ff7a00" stroke-width="3"/>'
              '<circle cx="80" cy="56" r="13" fill="#fff8d0"/>')
    shade = "#5a5a5a" if flash else "#3b3b3b"
    g += ('<g transform="translate(0,60)">'
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
    return svg(160, 190, g)

GUN_IDLE, GUN_FIRE = _gun(False), _gun(True)

CROSSHAIR = svg(20, 20, '<path d="M10 1 V7 M10 13 V19 M1 10 H7 M13 10 H19" stroke="#000" stroke-width="4"/>'
                        '<path d="M10 1 V7 M10 13 V19 M1 10 H7 M13 10 H19" stroke="#ffe14d" stroke-width="2"/>')

TINY = svg(2, 2, '<rect width="2" height="2" fill="#000" fill-opacity="0"/>')
BACKDROP = svg(480, 360, '<rect width="480" height="360" fill="#000"/>')

def _screen(bg, op, title, color, lines):
    body = f'<rect width="480" height="360" fill="{bg}" fill-opacity="{op}"/>'
    body += (f'<text x="240" y="120" font-family="Pixel" font-size="40" fill="{color}" stroke="#000" '
             f'stroke-width="2" text-anchor="middle">{title}</text>')
    y = 170
    for txt, size, fill in lines:
        body += (f'<text x="240" y="{y}" font-family="Sans Serif" font-size="{size}" fill="{fill}" '
                 f'text-anchor="middle">{txt}</text>')
        y += size + 10
    return svg(480, 360, body)

TITLE = _screen("#000", 0.7, "SCRATCH SLAYER", "#e02424", [
    ("A raycasting shooter built entirely in Scratch", 15, "#bbbbbb"),
    ("UP / DOWN  or  W / S  -  move", 16, "#ffffff"),
    ("LEFT / RIGHT  -  turn       A / D  -  strafe", 16, "#ffffff"),
    ("SPACE  -  shoot       M  -  toggle map", 16, "#ffffff"),
    ("Press SPACE to start", 20, "#ffe14d")])
DIED = _screen("#600000", 0.6, "YOU DIED", "#ff4040", [
    ("The monsters got you.", 18, "#ffffff"),
    ("Click the green flag to try again", 18, "#ffe14d")])
WIN = _screen("#002a10", 0.6, "AREA CLEARED", "#40ff70", [
    ("Every monster has been defeated!", 18, "#ffffff"),
    ("Click the green flag to play again", 18, "#ffe14d")])

# ---------------- sounds ----------------
RATE = 22050
def _wav(samples):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 30000)) for s in samples))
    return buf.getvalue(), len(samples)

def _lowpass(xs, a):
    y, out = 0.0, []
    for x in xs:
        y += a * (x - y); out.append(y)
    return out

def shotgun():
    rnd = random.Random(1)
    n = int(RATE * 0.6)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(n)], 0.3)
    out = []
    for i in range(n):
        t = i / RATE
        s = noise[i] * 2.2 * math.exp(-t * 10) * min(1, t * 400)
        s += math.sin(2 * math.pi * 55 * t) * math.exp(-t * 16) * 0.9
        for c in (0.36, 0.45):  # pump click-clack
            if c <= t < c + 0.025:
                s += rnd.uniform(-1, 1) * 0.5 * math.exp(-(t - c) * 120)
        out.append(s * 0.8)
    return _wav(out)

def _growl(dur, f0, f1, vib, seed):
    rnd = random.Random(seed)
    n, ph, out = int(RATE * dur), 0.0, []
    for i in range(n):
        t = i / RATE
        f = f0 + (f1 - f0) * (t / dur)
        f *= 1 + 0.08 * math.sin(2 * math.pi * vib * t)
        ph += f / RATE
        saw = 2 * (ph % 1) - 1
        env = min(1, t * 60) * (1 - t / dur) ** 1.5
        out.append((saw * 0.7 + rnd.uniform(-1, 1) * 0.3) * env)
    return _wav([s * 1.4 for s in _lowpass(out, 0.18)])

def monster_pain(): return _growl(0.22, 260, 150, 30, 2)
def monster_death(): return _growl(0.85, 170, 45, 14, 3)
def player_hurt():
    n, ph, out = int(RATE * 0.22), 0.0, []
    for i in range(n):
        t = i / RATE
        ph += (150 - 200 * t) / RATE
        sq = 1 if (ph % 1) < 0.5 else -1
        out.append(sq * min(1, t * 80) * (1 - t / 0.22))
    return _wav([s * 1.2 for s in _lowpass(out, 0.12)])
