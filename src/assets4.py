"""Round 4 art + audio: title sky, block-letter logo, level cards, card headings, embers, title riff, thud, melt."""
import math, random
from assets import svg, _wav, _lowpass, RATE
import assets2

# =============================== BLOCK-LETTER FONT (5 x 7 pixels per letter) ===============================
LETTERS = {
    "S": "01111 10000 10000 01110 00001 00001 11110", "C": "01111 10000 10000 10000 10000 10000 01111",
    "R": "11110 10001 10001 11110 10100 10010 10001", "A": "01110 10001 10001 11111 10001 10001 10001",
    "T": "11111 00100 00100 00100 00100 00100 00100", "H": "10001 10001 10001 11111 10001 10001 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111", "Y": "10001 10001 01010 00100 00100 00100 00100",
    "E": "11111 10000 10000 11110 10000 10000 11111", "V": "10001 10001 10001 10001 10001 01010 00100",
    "N": "10001 11001 10101 10011 10001 10001 10001", "X": "10001 10001 01010 00100 01010 10001 10001",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}
LETTERS.update(assets2.GLYPHS)

def block_text(text, unit, x0, y0, grad_id, depth=0.4):
    """Chunky beveled pixel letters: black outline, dark extrusion, then a gradient face."""
    cells = []
    for i, ch in enumerate(text):
        rows = LETTERS[ch].split()
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "1":
                    cells.append((x0 + (i * 6 + rx) * unit, y0 + ry * unit))
    u, d, o = unit, unit * depth, max(1.5, unit * 0.22)
    outline = "".join(f'<rect x="{x - o:.1f}" y="{y - o:.1f}" width="{u + 2 * o + d:.1f}" height="{u + 2 * o + d:.1f}" fill="#000"/>' for x, y in cells)
    extrude = "".join(f'<rect x="{x + d:.1f}" y="{y + d:.1f}" width="{u + 0.6:.1f}" height="{u + 0.6:.1f}" fill="#3a0000"/>' for x, y in cells)
    face = "".join(f'<rect x="{x:.1f}" y="{y:.1f}" width="{u + 0.6:.1f}" height="{u + 0.6:.1f}" fill="url(#{grad_id})"/>' for x, y in cells)
    shine = "".join(f'<rect x="{x:.1f}" y="{y:.1f}" width="{u + 0.6:.1f}" height="{max(1, u * 0.18):.1f}" fill="#fff6c8" opacity="0.55"/>' for x, y in cells)
    return outline + extrude + face + shine

def text_width(text, unit):
    return (len(text) * 6 - 1) * unit

def gradient(grad_id, y_top, y_bottom, stops):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (f'<linearGradient id="{grad_id}" gradientUnits="userSpaceOnUse" x1="0" y1="{y_top}" x2="0" y2="{y_bottom}">'
            f'{s}</linearGradient>')

FIRE_STOPS = [(0, "#fff3a0"), (0.35, "#ffc23a"), (0.7, "#ff6a00"), (1, "#c41400")]

# =============================== TITLE LOGO ===============================
def _logo():
    small, big = 5, 10
    w1, w2 = text_width("SCRATCH", small), text_width("SLAYER", big)
    W, H = 440, 134
    y1, y2 = 8, 8 + 7 * small + 12
    body = "<defs>" + gradient("fire1", y1, y1 + 7 * small, FIRE_STOPS) + gradient("fire2", y2, y2 + 7 * big, FIRE_STOPS) + "</defs>"
    body += f'<ellipse cx="{W / 2}" cy="{y2 + 35}" rx="210" ry="48" fill="#ff3a00" opacity="0.18"/>'
    body += block_text("SCRATCH", small, (W - w1) / 2, y1, "fire1")
    body += block_text("SLAYER", big, (W - w2) / 2, y2, "fire2")
    return svg(W, H, body)
LOGO = _logo()

# =============================== TITLE SKY (stage backdrop) ===============================
def _title_sky():
    rnd = random.Random(21)
    b = ('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#070104"/><stop offset="0.55" stop-color="#2a0608"/>'
         '<stop offset="1" stop-color="#6a160c"/></linearGradient>'
         '<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#2a0e08"/><stop offset="1" stop-color="#070202"/></linearGradient>'
         '<radialGradient id="moon"><stop offset="0" stop-color="#ffb070"/><stop offset="0.6" stop-color="#e0401c"/>'
         '<stop offset="1" stop-color="#e0401c" stop-opacity="0"/></radialGradient></defs>'
         '<rect width="480" height="250" fill="url(#sky)"/>')
    b += "".join(f'<circle cx="{rnd.uniform(0, 480):.0f}" cy="{rnd.uniform(0, 150):.0f}" r="{rnd.choice([0.7, 1, 1.3])}" '
                 f'fill="#ffd9c0" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>' for _ in range(45))
    b += '<circle cx="402" cy="58" r="70" fill="url(#moon)" opacity="0.5"/><circle cx="402" cy="58" r="30" fill="#e8582a"/>'
    b += '<circle cx="392" cy="50" r="6" fill="#c2401c" opacity="0.6"/><circle cx="412" cy="68" r="4" fill="#c2401c" opacity="0.6"/>'
    # far mountains
    b += '<path d="M0 205 L40 170 L80 190 L130 150 L170 185 L215 160 L260 190 L310 145 L355 180 L400 160 L440 185 L480 165 L480 250 L0 250 Z" fill="#250707"/>'
    # fortress silhouette
    fort = "M60 250 V196 H72 V184 H80 V196 H96 V170 H104 V160 H112 V170 H120 V196 H150 V176 H164 V196 H330 V180 H344 V196 H360 V166 H368 V150 H376 V166 H384 V196 H404 V186 H414 V196 H420 V250 Z"
    b += f'<path d="{fort}" fill="#120305"/>'
    for x, y in ((106, 176), (106, 186), (370, 170), (370, 182), (156, 184), (336, 188), (84, 200), (300, 206), (200, 208)):
        b += f'<rect x="{x}" y="{y}" width="4" height="6" fill="#ffb347"/><rect x="{x - 2}" y="{y - 2}" width="8" height="10" fill="#ff8a1f" opacity="0.25"/>'
    # ground with glowing cracks
    b += '<rect y="236" width="480" height="124" fill="url(#ground)"/>'
    for d in ("M0 270 L60 262 L110 275 L170 266", "M300 280 L350 270 L410 284 L480 272", "M150 320 L210 306 L260 322 L330 310",
              "M20 340 L80 330 L120 345", "M380 340 L440 326 L480 334"):
        b += f'<path d="{d}" stroke="#ff6a00" stroke-width="4" fill="none" opacity="0.25"/><path d="{d}" stroke="#ffb347" stroke-width="1.5" fill="none" opacity="0.8"/>'
    # bottom strip with controls
    b += '<rect y="318" width="480" height="42" fill="#000" opacity="0.62"/>'
    b += ('<text x="240" y="334" font-family="Sans Serif" font-size="10.5" font-weight="bold" fill="#e8a070" '
          'text-anchor="middle" letter-spacing="1.5">A RAYCASTING SHOOTER BUILT ENTIRELY IN SCRATCH</text>')
    b += ('<text x="240" y="351" font-family="Sans Serif" font-size="11.5" fill="#cfcfcf" text-anchor="middle">'
          'ARROWS / WASD move  •  Q sprint  •  SPACE shoot  •  E open / use  •  M map</text>')
    return svg(480, 360, b)
TITLE_SKY = _title_sky()

PRESS_SPACE = svg(300, 40,
    '<rect x="20" y="4" width="260" height="32" rx="16" fill="#000" opacity="0.55"/>'
    '<text x="150" y="27" font-family="Sans Serif" font-size="18" font-weight="bold" fill="#ffe14d" '
    'text-anchor="middle" letter-spacing="2">PRESS SPACE TO START</text>')

EMBER = svg(14, 14, '<circle cx="7" cy="7" r="6.5" fill="#ff7a00" opacity="0.35"/>'
                    '<circle cx="7" cy="7" r="3.5" fill="#ffb347"/><circle cx="7" cy="7" r="1.6" fill="#fff3c0"/>')

# =============================== LEVEL CARDS ===============================
CARD_COLOR = "#120304"
CARDS = [
    dict(tint="#5a2a10", name="THE OUTPOST", goal="Find the exit switch", enemy="IMP",
         lines=["Fast and vicious up close.", "Keep your distance and blast it."], boss=None),
    dict(tint="#1f5a14", name="THE PROCESSING PLANT", goal="Find the red key, then the exit", enemy="SPITTER",
         lines=["Spits acid from far away. Strafe", "with A and D to dodge it."], boss=None),
    dict(tint="#5a0f2a", name="THE FORTRESS", goal="Two keys guard the exit", enemy="GOLEM",
         lines=["Slow, tough, and hits like a truck.", "Lure it next to a barrel."],
         boss="BOSS: THE WARDEN waits at the exit"),
]

def card(info):
    b = (f'<defs><radialGradient id="glow" cx="0.7" cy="0.7" r="0.7"><stop offset="0" stop-color="{info["tint"]}"/>'
         f'<stop offset="1" stop-color="{CARD_COLOR}"/></radialGradient>'
         '<radialGradient id="spot"><stop offset="0" stop-color="#ffd9a0" stop-opacity="0.45"/>'
         '<stop offset="1" stop-color="#ffd9a0" stop-opacity="0"/></radialGradient></defs>'
         '<rect width="480" height="360" fill="url(#glow)"/>'
         '<rect x="8" y="8" width="464" height="344" rx="10" fill="none" stroke="#ff6a00" stroke-opacity="0.35" stroke-width="2"/>'
         '<ellipse cx="370" cy="302" rx="95" ry="18" fill="url(#spot)"/>')
    b += (f'<text x="30" y="132" font-family="Sans Serif" font-size="{22 if len(info["name"]) < 16 else 18}" font-weight="bold" '
          f'fill="#ff4a24" stroke="#000" stroke-width="3" paint-order="stroke">{info["name"]}</text>'
          f'<text x="30" y="154" font-family="Sans Serif" font-size="13" fill="#dddddd">{info["goal"]}</text>'
          '<rect x="30" y="168" width="200" height="2" fill="#ff6a00" opacity="0.6"/>'
          '<text x="30" y="192" font-family="Sans Serif" font-size="11" font-weight="bold" fill="#ffd23f" letter-spacing="2">NEW ENEMY</text>'
          f'<text x="30" y="218" font-family="Sans Serif" font-size="24" font-weight="bold" fill="#ffffff">{info["enemy"]}</text>')
    for i, line in enumerate(info["lines"]):
        b += f'<text x="30" y="{242 + 16 * i}" font-family="Sans Serif" font-size="12" fill="#d8d8d8">{line}</text>'
    if info["boss"]:
        b += (f'<text x="30" y="292" font-family="Sans Serif" font-size="12" font-weight="bold" fill="#ff5050">{info["boss"]}</text>')
    b += '<text x="462" y="344" font-family="Sans Serif" font-size="10" fill="#8a8a8a" text-anchor="end">SPACE to skip</text>'
    return svg(480, 360, b)

CARD_ART = [card(c) for c in CARDS]
CARD_NEXT = card(dict(tint="#3a1a10", name="NEXT LEVEL", goal="Find the exit switch", enemy="?",
                      lines=["Stay sharp.", ""], boss=None))

def heading(text):
    unit = 8
    W = text_width(text, unit) + 12
    body = "<defs>" + gradient("hfire", 4, 4 + 7 * unit, FIRE_STOPS) + "</defs>" + block_text(text, unit, 4, 4, "hfire")
    return svg(W, 7 * unit + 14, body)

HEADINGS = [heading(f"LEVEL {i + 1}") for i in range(3)]
HEADING_NEXT = heading("NEXT LEVEL")

# =============================== SOUNDS ===============================
def _note_freq(midi):
    return 440 * 2 ** ((midi - 69) / 12)

def title_riff():
    """An original chugging riff: 2 bars of sixteenths at 150 BPM, with kick and snare. Loops cleanly."""
    step = 60 / 150 / 4
    E = 40
    bar1 = [E, E, E + 3, E, E, E, E + 6, E + 5, E, E, E + 3, E, E, E, E - 2, E - 1]
    bar2 = [E, E, E + 3, E, E, E, E + 6, E + 5, E, E, E + 7, E + 6, E + 5, E + 3, E + 2, E]
    notes = bar1 + bar2 + bar1 + bar2
    n = int(RATE * step * len(notes))
    out = [0.0] * n
    rnd = random.Random(5)
    for i, midi in enumerate(notes):
        start = int(i * step * RATE)
        accent = midi != E
        length = int(RATE * step * (0.95 if accent else 0.55))
        f, ph = _note_freq(midi), 0.0
        for k in range(length):
            if start + k >= n: break
            t = k / RATE
            ph += f / RATE
            saw = 2 * (ph % 1) - 1 + 0.6 * (2 * ((ph * 2.005) % 1) - 1)
            env = min(1, t * 400) * math.exp(-t * (6 if accent else 22))
            out[start + k] += math.tanh(3.2 * saw) * 0.32 * env
    for beat in range(len(notes) // 4):                      # kick on every beat, snare on 2 and 4
        start = int(beat * 4 * step * RATE)
        for k in range(int(RATE * 0.18)):
            if start + k >= n: break
            t = k / RATE
            out[start + k] += math.sin(2 * math.pi * (110 - 260 * t) * t) * math.exp(-t * 22) * 0.75
        if beat % 2 == 1:
            for k in range(int(RATE * 0.16)):
                if start + k >= n: break
                t = k / RATE
                out[start + k] += rnd.uniform(-1, 1) * math.exp(-t * 26) * 0.35
    smooth = _lowpass(out, 0.35)
    return _wav([max(-1, min(1, s)) * 0.9 for s in smooth])

def thud():
    rnd = random.Random(31); out = []
    for i in range(int(RATE * 0.45)):
        t = i / RATE
        out.append(math.sin(2 * math.pi * (70 - 50 * t) * t) * math.exp(-t * 9) * 1.1 + rnd.uniform(-1, 1) * math.exp(-t * 40) * 0.5)
    return _wav(_lowpass(out, 0.3))

def melt():
    rnd = random.Random(32); n = int(RATE * 1.2); out, y = [], 0.0
    for i in range(n):
        t = i / RATE
        a = 0.25 * (1 - t / 1.2) + 0.02
        y += a * (rnd.uniform(-1, 1) - y)
        out.append(y * 3 * min(1, t * 20) * (1 - t / 1.2) + math.sin(2 * math.pi * (180 - 120 * t) * t) * 0.15 * (1 - t / 1.2))
    return _wav(out)
