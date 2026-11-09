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
    "I": "01110 00100 00100 00100 00100 00100 01110", "O": "01110 10001 10001 10001 10001 10001 01110",
    "U": "10001 10001 10001 10001 10001 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
}
LETTERS.update(assets2.GLYPHS)

def block_text(text, unit, left, top, grad_id, depth=0.4, font=LETTERS):
    """Chunky beveled pixel letters: black outline, dark extrusion, then a gradient face.
    font = which letter shapes to use (LETTERS unless a picture needs a different one)."""
    cells = []
    for letter_number, character in enumerate(text):
        rows = font[character].split()
        for pixel_row, row in enumerate(rows):
            for pixel_column, bit in enumerate(row):
                if bit == "1":
                    cells.append((left + (letter_number * 6 + pixel_column) * unit, top + pixel_row * unit))
    pixel_size, shadow_depth, outline_width = unit, unit * depth, max(1.5, unit * 0.22)
    outline = "".join(f'<rect x="{pixel_x - outline_width:.1f}" y="{pixel_y - outline_width:.1f}" width="{pixel_size + 2 * outline_width + shadow_depth:.1f}" height="{pixel_size + 2 * outline_width + shadow_depth:.1f}" fill="#000"/>' for pixel_x, pixel_y in cells)
    extrude = "".join(f'<rect x="{pixel_x + shadow_depth:.1f}" y="{pixel_y + shadow_depth:.1f}" width="{pixel_size + 0.6:.1f}" height="{pixel_size + 0.6:.1f}" fill="#3a0000"/>' for pixel_x, pixel_y in cells)
    face = "".join(f'<rect x="{pixel_x:.1f}" y="{pixel_y:.1f}" width="{pixel_size + 0.6:.1f}" height="{pixel_size + 0.6:.1f}" fill="url(#{grad_id})"/>' for pixel_x, pixel_y in cells)
    shine = "".join(f'<rect x="{pixel_x:.1f}" y="{pixel_y:.1f}" width="{pixel_size + 0.6:.1f}" height="{max(1, pixel_size * 0.18):.1f}" fill="#fff6c8" opacity="0.55"/>' for pixel_x, pixel_y in cells)
    return outline + extrude + face + shine

def text_width(text, unit):
    return (len(text) * 6 - 1) * unit

def gradient(grad_id, y_top, y_bottom, stops):
    stop_tags = "".join(f'<stop offset="{offset}" stop-color="{color}"/>' for offset, color in stops)
    return (f'<linearGradient id="{grad_id}" gradientUnits="userSpaceOnUse" x1="0" y1="{y_top}" x2="0" y2="{y_bottom}">'
            f'{stop_tags}</linearGradient>')

FIRE_STOPS = [(0, "#fff3a0"), (0.35, "#ffc23a"), (0.7, "#ff6a00"), (1, "#c41400")]

# =============================== TITLE LOGO ===============================
def _logo():
    small, big = 5, 10
    small_width, big_width = text_width("SCRATCH", small), text_width("SLAYER", big)
    logo_width, logo_height = 440, 134
    small_top, big_top = 8, 8 + 7 * small + 12
    body = "<defs>" + gradient("fire1", small_top, small_top + 7 * small, FIRE_STOPS) + gradient("fire2", big_top, big_top + 7 * big, FIRE_STOPS) + "</defs>"
    body += f'<ellipse cx="{logo_width / 2}" cy="{big_top + 35}" rx="210" ry="48" fill="#ff3a00" opacity="0.18"/>'
    body += block_text("SCRATCH", small, (logo_width - small_width) / 2, small_top, "fire1")
    body += block_text("SLAYER", big, (logo_width - big_width) / 2, big_top, "fire2")
    return svg(logo_width, logo_height, body)
LOGO = _logo()

# =============================== TITLE SKY (stage backdrop) ===============================
def _title_sky():
    rnd = random.Random(21)
    picture = ('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#070104"/><stop offset="0.55" stop-color="#2a0608"/>'
         '<stop offset="1" stop-color="#6a160c"/></linearGradient>'
         '<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#2a0e08"/><stop offset="1" stop-color="#070202"/></linearGradient>'
         '<radialGradient id="moon"><stop offset="0" stop-color="#ffb070"/><stop offset="0.6" stop-color="#e0401c"/>'
         '<stop offset="1" stop-color="#e0401c" stop-opacity="0"/></radialGradient></defs>'
         '<rect width="480" height="250" fill="url(#sky)"/>')
    picture += "".join(f'<circle cx="{rnd.uniform(0, 480):.0f}" cy="{rnd.uniform(0, 150):.0f}" r="{rnd.choice([0.7, 1, 1.3])}" '
                 f'fill="#ffd9c0" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>' for _ in range(45))
    picture += '<circle cx="402" cy="58" r="70" fill="url(#moon)" opacity="0.5"/><circle cx="402" cy="58" r="30" fill="#e8582a"/>'
    picture += '<circle cx="392" cy="50" r="6" fill="#c2401c" opacity="0.6"/><circle cx="412" cy="68" r="4" fill="#c2401c" opacity="0.6"/>'
    # far mountains
    picture += '<path d="M0 205 L40 170 L80 190 L130 150 L170 185 L215 160 L260 190 L310 145 L355 180 L400 160 L440 185 L480 165 L480 250 L0 250 Z" fill="#250707"/>'
    # fortress silhouette
    fort = "M60 250 V196 H72 V184 H80 V196 H96 V170 H104 V160 H112 V170 H120 V196 H150 V176 H164 V196 H330 V180 H344 V196 H360 V166 H368 V150 H376 V166 H384 V196 H404 V186 H414 V196 H420 V250 Z"
    picture += f'<path d="{fort}" fill="#120305"/>'
    for window_x, window_y in ((106, 176), (106, 186), (370, 170), (370, 182), (156, 184), (336, 188), (84, 200), (300, 206), (200, 208)):
        picture += f'<rect x="{window_x}" y="{window_y}" width="4" height="6" fill="#ffb347"/><rect x="{window_x - 2}" y="{window_y - 2}" width="8" height="10" fill="#ff8a1f" opacity="0.25"/>'
    # ground with glowing cracks
    picture += '<rect y="236" width="480" height="124" fill="url(#ground)"/>'
    for crack_path in ("M0 270 L60 262 L110 275 L170 266", "M300 280 L350 270 L410 284 L480 272", "M150 320 L210 306 L260 322 L330 310",
              "M20 340 L80 330 L120 345", "M380 340 L440 326 L480 334"):
        picture += f'<path d="{crack_path}" stroke="#ff6a00" stroke-width="4" fill="none" opacity="0.25"/><path d="{crack_path}" stroke="#ffb347" stroke-width="1.5" fill="none" opacity="0.8"/>'
    # bottom strip with the controls (two lines: there are a lot of keys)
    picture += ('<rect y="308" width="480" height="52" fill="#000" opacity="0.62"/>'
                '<text x="240" y="322" font-family="Sans Serif" font-size="9.5" font-weight="bold" fill="#e8a070" '
                'text-anchor="middle" letter-spacing="1.5">A RAYCASTING SHOOTER BUILT ENTIRELY IN SCRATCH</text>'
                '<text x="240" y="337" font-family="Sans Serif" font-size="11" fill="#cfcfcf" text-anchor="middle">'
                'ARROWS / WASD move  •  Q sprint  •  SPACE shoot  •  1-5 weapons</text>'
                '<text x="240" y="352" font-family="Sans Serif" font-size="11" fill="#cfcfcf" text-anchor="middle">'
                'E open / use  •  M map  •  N music  •  P pause  •  O OPTIONS</text>')
    return svg(480, 360, picture)
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
    dict(tint="#5a0f2a", name="THE FORTRESS", goal="Two keys, then slay the Warden", enemy="GOLEM",
         lines=["Slow, tough, and hits like a truck.", "Lure it next to a barrel."],
         boss="BOSS: THE WARDEN carries the SKULL KEY to the exit"),
    dict(tint="#6a2a08", name="THE FOUNDRY", goal="Find the red key, then the exit", enemy="CHARGER",
         lines=["Lowers its head, then charges.", "Sidestep it and it slams into a wall."], boss=None),
    dict(tint="#0f3a4a", name="THE SUNKEN VAULTS", goal="Two keys, deep in the dark", enemy="WRAITH",
         lines=["Almost invisible from far away,", "and it blinks sideways. Stay sharp."], boss=None),
    dict(tint="#4a0a3a", name="THE CORE", goal="Destroy the Colossus, take its key", enemy="THE COLOSSUS",
         lines=["Huge, armored, and it gets angrier.", "At half health it calls for help."],
         boss="FINAL BOSS: the exit is sealed until it falls"),
]

def card(info):
    picture = (f'<defs><radialGradient id="glow" cx="0.7" cy="0.7" r="0.7"><stop offset="0" stop-color="{info["tint"]}"/>'
         f'<stop offset="1" stop-color="{CARD_COLOR}"/></radialGradient>'
         '<radialGradient id="spot"><stop offset="0" stop-color="#ffd9a0" stop-opacity="0.45"/>'
         '<stop offset="1" stop-color="#ffd9a0" stop-opacity="0"/></radialGradient></defs>'
         '<rect width="480" height="360" fill="url(#glow)"/>'
         '<rect x="8" y="8" width="464" height="344" rx="10" fill="none" stroke="#ff6a00" stroke-opacity="0.35" stroke-width="2"/>'
         '<ellipse cx="370" cy="302" rx="95" ry="18" fill="url(#spot)"/>')
    picture += (f'<text x="30" y="132" font-family="Sans Serif" font-size="{22 if len(info["name"]) < 16 else 18}" font-weight="bold" '
          f'fill="#ff4a24" stroke="#000" stroke-width="3" paint-order="stroke">{info["name"]}</text>'
          f'<text x="30" y="154" font-family="Sans Serif" font-size="13" fill="#dddddd">{info["goal"]}</text>'
          '<rect x="30" y="168" width="200" height="2" fill="#ff6a00" opacity="0.6"/>'
          '<text x="30" y="192" font-family="Sans Serif" font-size="11" font-weight="bold" fill="#ffd23f" letter-spacing="2">NEW ENEMY</text>'
          f'<text x="30" y="218" font-family="Sans Serif" font-size="24" font-weight="bold" fill="#ffffff">{info["enemy"]}</text>')
    for line_number, line in enumerate(info["lines"]):
        picture += f'<text x="30" y="{242 + 16 * line_number}" font-family="Sans Serif" font-size="12" fill="#d8d8d8">{line}</text>'
    if info["boss"]:
        picture += (f'<text x="30" y="292" font-family="Sans Serif" font-size="12" font-weight="bold" fill="#ff5050">{info["boss"]}</text>')
    picture += '<text x="462" y="344" font-family="Sans Serif" font-size="10" fill="#8a8a8a" text-anchor="end">SPACE to skip</text>'
    return svg(480, 360, picture)

CARD_NEXT = card(dict(tint="#3a1a10", name="NEXT LEVEL", goal="Find the exit switch", enemy="?",
                      lines=["Stay sharp.", ""], boss=None))

def heading(text):
    unit = 8
    heading_width = text_width(text, unit) + 12
    body = "<defs>" + gradient("hfire", 4, 4 + 7 * unit, FIRE_STOPS) + "</defs>" + block_text(text, unit, 4, 4, "hfire")
    return svg(heading_width, 7 * unit + 14, body)

HEADING_NEXT = heading("NEXT LEVEL")
CARD_ART = [card(card_info) for card_info in CARDS]
HEADINGS = [heading(f"LEVEL {level_index + 1}") for level_index in range(len(CARDS))]

# =============================== SOUNDS ===============================
def _note_freq(midi):
    return 440 * 2 ** ((midi - 69) / 12)

def title_riff():
    """An original chugging riff: 2 bars of sixteenths at 150 BPM, with kick and snare. Loops cleanly."""
    step = 60 / 150 / 4
    low_e = 40
    bar1 = [low_e, low_e, low_e + 3, low_e, low_e, low_e, low_e + 6, low_e + 5, low_e, low_e, low_e + 3, low_e, low_e, low_e, low_e - 2, low_e - 1]
    bar2 = [low_e, low_e, low_e + 3, low_e, low_e, low_e, low_e + 6, low_e + 5, low_e, low_e, low_e + 7, low_e + 6, low_e + 5, low_e + 3, low_e + 2, low_e]
    notes = bar1 + bar2 + bar1 + bar2
    sample_count = int(RATE * step * len(notes))
    out = [0.0] * sample_count
    rnd = random.Random(5)
    for note_number, midi in enumerate(notes):
        start = int(note_number * step * RATE)
        accent = midi != low_e
        length = int(RATE * step * (0.95 if accent else 0.55))
        pitch, phase = _note_freq(midi), 0.0
        for sample_in_note in range(length):
            if start + sample_in_note >= sample_count: break
            seconds = sample_in_note / RATE
            phase += pitch / RATE
            saw = 2 * (phase % 1) - 1 + 0.6 * (2 * ((phase * 2.005) % 1) - 1)
            env = min(1, seconds * 400) * math.exp(-seconds * (6 if accent else 22))
            out[start + sample_in_note] += math.tanh(3.2 * saw) * 0.32 * env
    for beat in range(len(notes) // 4):                      # kick on every beat, snare on 2 and 4
        start = int(beat * 4 * step * RATE)
        for sample_in_note in range(int(RATE * 0.18)):
            if start + sample_in_note >= sample_count: break
            seconds = sample_in_note / RATE
            out[start + sample_in_note] += math.sin(2 * math.pi * (110 - 260 * seconds) * seconds) * math.exp(-seconds * 22) * 0.75
        if beat % 2 == 1:
            for sample_in_note in range(int(RATE * 0.16)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                out[start + sample_in_note] += rnd.uniform(-1, 1) * math.exp(-seconds * 26) * 0.35
    smooth = _lowpass(out, 0.35)
    return _wav([max(-1, min(1, sample)) * 0.9 for sample in smooth])

def thud():
    rnd = random.Random(31); out = []
    for sample_number in range(int(RATE * 0.45)):
        seconds = sample_number / RATE
        out.append(math.sin(2 * math.pi * (70 - 50 * seconds) * seconds) * math.exp(-seconds * 9) * 1.1 + rnd.uniform(-1, 1) * math.exp(-seconds * 40) * 0.5)
    return _wav(_lowpass(out, 0.3))

def melt():
    rnd = random.Random(32); sample_count = int(RATE * 1.2); out, smoothed = [], 0.0
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        smoothing = 0.25 * (1 - seconds / 1.2) + 0.02
        smoothed += smoothing * (rnd.uniform(-1, 1) - smoothed)
        out.append(smoothed * 3 * min(1, seconds * 20) * (1 - seconds / 1.2) + math.sin(2 * math.pi * (180 - 120 * seconds) * seconds) * 0.15 * (1 - seconds / 1.2))
    return _wav(out)
