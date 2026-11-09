"""Art + sound for round 2: pickups, keys, HUD, messages, screens, digits, door/switch sounds."""
import math, random
from assets import svg, _wav, _lowpass, RATE

# ---------------- pickups (40x40, anchored bottom-center) ----------------
MEDKIT = svg(40, 40,
    '<ellipse cx="20" cy="38" rx="17" ry="2.5" fill="#000" opacity="0.35"/>'
    '<rect x="3" y="14" width="34" height="24" rx="3" fill="#f2f2f2" stroke="#555" stroke-width="1.5"/>'
    '<rect x="14" y="10" width="12" height="5" rx="1.5" fill="#999" stroke="#555"/>'
    '<path d="M17 18 H23 V23 H28 V29 H23 V34 H17 V29 H12 V23 H17 Z" fill="#e01e1e"/>')
SHELLS = svg(40, 40,
    '<ellipse cx="20" cy="38" rx="17" ry="2.5" fill="#000" opacity="0.35"/>'
    + "".join(f'<rect x="{6 + i * 6}" y="9" width="5" height="12" rx="1" fill="#c62020" stroke="#601010"/>'
              f'<rect x="{6 + i * 6}" y="17" width="5" height="4" fill="#d9b44a"/>' for i in range(5))
    + '<rect x="3" y="20" width="34" height="18" rx="2" fill="#6b4a1e" stroke="#2e1f0a" stroke-width="1.5"/>'
      '<rect x="8" y="25" width="24" height="8" fill="#d9b44a"/>'
      '<text x="20" y="32" font-family="Sans Serif" font-size="7" font-weight="bold" fill="#2e1f0a" '
      'text-anchor="middle">SHELLS</text>')

def _key(c1, c2):
    return svg(40, 40,
        f'<circle cx="20" cy="22" r="17" fill="{c1}" opacity="0.25"/>'
        '<ellipse cx="20" cy="38" rx="12" ry="2" fill="#000" opacity="0.35"/>'
        f'<rect x="8" y="8" width="24" height="30" rx="3" fill="{c1}" stroke="{c2}" stroke-width="2"/>'
        '<rect x="12" y="13" width="10" height="8" rx="1" fill="#f5d36b" stroke="#8a6d1a"/>'
        '<rect x="12" y="26" width="16" height="3" fill="#fff" opacity="0.7"/>'
        '<rect x="12" y="31" width="11" height="3" fill="#fff" opacity="0.7"/>')
RED_KEY, BLUE_KEY = _key("#e02424", "#6a0d0d"), _key("#2a6cf0", "#0d2a6a")

# ---------------- big pixel digits for the HUD (20x28, anchored right-middle) ----------------
GLYPHS = {
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
}
def digit(ch):
    rows = GLYPHS[ch].split()
    px = [(x, y) for y, r in enumerate(rows) for x, b in enumerate(r) if b == "1"]
    shadow = "".join(f'<rect x="{x * 4 + 1}" y="{y * 4 + 1}" width="4" height="4" fill="#000"/>' for x, y in px)
    main = "".join(f'<rect x="{x * 4}" y="{y * 4}" width="4" height="4" fill="#ff4a24"/>' for x, y in px)
    return svg(21, 29, shadow + main)
DIGITS = {c: digit(c) for c in GLYPHS}

# ---------------- HUD frame: labels + key slots (full-stage canvas) ----------------
def _label(x, y, t, anchor="start", size=13, fill="#d8d8d8"):
    return (f'<text x="{x}" y="{y}" font-family="Sans Serif" font-weight="bold" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="2">{t}</text>')

def _slot(x, color, have):
    if have:
        return (f'<rect x="{x}" y="270" width="18" height="24" rx="2" fill="{color}" stroke="#000" stroke-width="1.5"/>'
                f'<rect x="{x + 3}" y="274" width="7" height="6" fill="#f5d36b"/>')
    return f'<rect x="{x}" y="270" width="18" height="24" rx="2" fill="#000" fill-opacity="0.35" stroke="#777" stroke-dasharray="3 2"/>'

def hud(red, blue):
    body = ('<rect x="6" y="298" width="124" height="56" rx="6" fill="#000" fill-opacity="0.5"/>'
            + _label(14, 314, "HEALTH")
            + '<text x="94" y="350" font-family="Sans Serif" font-weight="bold" font-size="24" fill="#ff4a24">%</text>'
            '<rect x="350" y="298" width="124" height="56" rx="6" fill="#000" fill-opacity="0.5"/>'
            + _label(358, 314, "SHELLS")
            + '<rect x="402" y="264" width="50" height="34" rx="5" fill="#000" fill-opacity="0.45"/>'
            + _slot(406, "#e02424", red) + _slot(430, "#2a6cf0", blue))
    return svg(480, 360, body)
HUDS = [hud(r, b) for b in (0, 1) for r in (0, 1)]   # index = red + 2*blue

# ---------------- messages along the top of the screen ----------------
def toast(text, color="#ffffff"):
    w = max(200, 11 * len(text) + 40)
    return svg(480, 360, f'<rect x="{240 - w / 2}" y="14" width="{w}" height="32" rx="8" fill="#000" fill-opacity="0.6"/>'
                         f'<text x="240" y="36" font-family="Sans Serif" font-weight="bold" font-size="16" '
                         f'fill="{color}" text-anchor="middle">{text}</text>')

def banner(n, name, sub):
    return svg(480, 360, '<rect x="70" y="40" width="340" height="78" rx="10" fill="#000" fill-opacity="0.65"/>'
                         + _label(240, 64, f"LEVEL {n}", "middle", 14, "#ffe14d")
                         + f'<text x="240" y="92" font-family="Pixel" font-size="24" fill="#e02424" '
                           f'stroke="#000" stroke-width="1" text-anchor="middle">{name.upper()}</text>'
                         + _label(240, 110, sub, "middle", 11, "#cccccc"))

TOASTS = {
    "hintd": toast("Press E to open the door", "#ffe14d"),
    "hintx": toast("Press E to flip the EXIT switch", "#40ff70"),
    "needred": toast("You need the RED key to open this door", "#ff6060"),
    "needblue": toast("You need the BLUE key to open this door", "#70a0ff"),
    "p1": toast("+25 HEALTH", "#60ff80"),
    "p2": toast("+8 SHELLS", "#ffd23f"),
    "p3": toast("Picked up the RED KEY", "#ff6060"),
    "p4": toast("Picked up the BLUE KEY", "#70a0ff"),
    "noammo": toast("Out of shells - punching!", "#ffa040"),
    "exit": toast("EXIT ACTIVATED", "#40ff70"),
}

# ---------------- full-screen overlays ----------------
def _screen(title, color, lines, extra="", opacity=0.72):
    body = (f'<rect width="480" height="360" fill="#000" fill-opacity="{opacity}"/>'
            f'<text x="240" y="100" font-family="Pixel" font-size="40" fill="{color}" stroke="#000" '
            f'stroke-width="2" text-anchor="middle">{title}</text>')
    for txt, y, size, fill in lines:
        body += (f'<text x="240" y="{y}" font-family="Sans Serif" font-size="{size}" fill="{fill}" '
                 f'text-anchor="middle">{txt}</text>')
    return svg(480, 360, body + extra)

TITLE = _screen("SCRATCH SLAYER", "#e02424", [
    ("A raycasting shooter built entirely in Scratch", 132, 14, "#bbbbbb"),
    ("UP / DOWN  or  W / S  -  move       LEFT / RIGHT  -  turn", 170, 14, "#ffffff"),
    ("A / D  -  strafe       SPACE  -  shoot       M  -  map", 194, 14, "#ffffff"),
    ("E  -  open doors and flip switches", 218, 14, "#ffffff"),
    ("Fight through 3 levels. Find the EXIT SWITCH on each one.", 252, 14, "#40ff70"),
    ("Press SPACE to start", 300, 20, "#ffe14d")])
DIED = _screen("YOU DIED", "#ff4040", [
    ("The monsters got you.", 160, 18, "#ffffff"),
    ("Press SPACE to retry this level", 290, 18, "#ffe14d")],
    '<rect width="480" height="360" fill="#600000" fill-opacity="0.35"/>')
COMPLETE = _screen("LEVEL COMPLETE", "#40ff70", [
    ("Press SPACE to continue", 300, 18, "#ffe14d")],
    _label(110, 178, "KILLS", size=18) + _label(110, 228, "ITEMS", size=18)
    + '<text x="285" y="182" font-family="Sans Serif" font-weight="bold" font-size="30" fill="#ff4a24" text-anchor="middle">/</text>'
      '<text x="285" y="232" font-family="Sans Serif" font-weight="bold" font-size="30" fill="#ff4a24" text-anchor="middle">/</text>', 0.88)
WIN = _screen("YOU ESCAPED!", "#40ff70", [
    ("All three levels cleared. The base is safe.", 140, 16, "#ffffff"),
    ("Click the green flag to play again", 300, 18, "#ffe14d")],
    _label(120, 208, "TOTAL KILLS", size=18), 0.88)
OVERLAYS = {"title": TITLE, "died": DIED, "complete": COMPLETE, "win": WIN}

# ---------------- sounds ----------------
def door():
    rnd = random.Random(5); n = int(RATE * 0.55)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(n)], 0.05)
    out = []
    for i in range(n):
        t = i / RATE
        s = noise[i] * 3.5 * min(1, t * 20) * (1 - t / 0.55)
        s += math.sin(2 * math.pi * (60 + 40 * t) * t) * 0.35 * (1 - t / 0.55)
        if t > 0.47: s += math.sin(2 * math.pi * 80 * t) * math.exp(-(t - 0.47) * 40)
        out.append(s)
    return _wav(out)

def switch():
    out = []
    for i in range(int(RATE * 0.45)):
        t = i / RATE
        s = (1 if t < 0.01 else 0) * 0.8
        f = 440 if t < 0.15 else 660
        if t > 0.04: s += (1 if math.sin(2 * math.pi * f * t) > 0 else -1) * 0.3 * math.exp(-(t % 0.15) * 8)
        out.append(s)
    return _wav(_lowpass(out, 0.4))

def locked():
    out = [(1 if (i * 110 / RATE) % 1 < 0.5 else -1) * 0.5 * (1 - i / (RATE * 0.3)) for i in range(int(RATE * 0.3))]
    return _wav(_lowpass(out, 0.2))

def punch():
    rnd = random.Random(7); out = []
    for i in range(int(RATE * 0.18)):
        t = i / RATE
        out.append(math.sin(2 * math.pi * 85 * t) * math.exp(-t * 25) + rnd.uniform(-1, 1) * 0.5 * math.exp(-t * 60))
    return _wav(out)

def item():
    out, ph = [], 0.0
    for i in range(int(RATE * 0.16)):
        t = i / RATE; ph += (600 + 4000 * t) / RATE
        out.append((1 if ph % 1 < 0.5 else -1) * 0.35 * (1 - t / 0.16))
    return _wav(_lowpass(out, 0.5))

def key():
    out = []
    for j, f in enumerate((523, 659, 784, 1047)):
        for i in range(int(RATE * 0.08)):
            t = i / RATE
            out.append((1 if math.sin(2 * math.pi * f * t) > 0 else -1) * 0.3 * (1 - t / 0.08))
    return _wav(_lowpass(out, 0.5))
