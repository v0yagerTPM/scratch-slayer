"""Round 5 art + audio: animated death screen and victory screen."""
import math, random
from assets import svg, _wav, _lowpass, RATE
import assets2, assets4
from assets4 import block_text, text_width, gradient

assets4.LETTERS.update({
    "I": "01110 00100 00100 00100 00100 00100 01110", "O": "01110 10001 10001 10001 10001 10001 01110",
    "U": "10001 10001 10001 10001 10001 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
})
BLOOD_STOPS = [(0, "#ff6a5a"), (0.4, "#e01818"), (1, "#5a0000")]
GOLD_STOPS = [(0, "#fffbe0"), (0.35, "#ffe066"), (0.75, "#f0a800"), (1, "#a05a00")]

# =============================== DEATH SCREEN ===============================
def _you_died():
    unit, text = 9, "YOU DIED"
    picture_width = text_width(text, unit) + 16
    body = "<defs>" + gradient("blood", 4, 4 + 7 * unit, BLOOD_STOPS) + "</defs>" + block_text(text, unit, 6, 4, "blood")
    rnd = random.Random(41)
    bottom_pixels = [6 + (letter_number * 6 + col) * unit for letter_number, character in enumerate(text)
                     for col, bit in enumerate(assets4.LETTERS[character].split()[-1]) if bit == "1"]
    for drip_x in rnd.sample(bottom_pixels, 9):  # drips hanging under real letter pixels
        drip_x += unit / 2 - 3
        drip_length = rnd.uniform(8, 22)
        body += (f'<path d="M{drip_x:.0f} {4 + 7 * unit} h6 v{drip_length:.0f} a3 3 0 0 1 -6 0 Z" fill="#a00000" stroke="#000" stroke-width="1.5"/>')
    return svg(picture_width, 7 * unit + 34, body)
YOU_DIED = _you_died()
YOU_DIED_CENTER = ((text_width("YOU DIED", 9) + 16) // 2, (7 * 9 + 34) // 2)

DEATH_OVERLAY = svg(480, 360,
    '<defs><radialGradient id="vig" cx="0.5" cy="0.45" r="0.75">'
    '<stop offset="0" stop-color="#5a0000" stop-opacity="0.55"/><stop offset="0.7" stop-color="#2a0000" stop-opacity="0.85"/>'
    '<stop offset="1" stop-color="#000000" stop-opacity="0.97"/></radialGradient></defs>'
    '<rect width="480" height="360" fill="url(#vig)"/>')

BLOOD_DROP = svg(10, 20, '<path d="M5 0 Q10 12 9 15 A4.2 4.2 0 0 1 1 15 Q0 12 5 0 Z" fill="#b30000" stroke="#3a0000" stroke-width="1"/>'
                         '<ellipse cx="3.6" cy="13" rx="1.2" ry="2" fill="#ff8a8a" opacity="0.7"/>')

KILLERS = {
    "imp": ("KILLED BY AN IMP", "Tip: back up while you shoot. Imps have to reach you to hurt you."),
    "spitter": ("KILLED BY A SPITTER", "Tip: strafe with A and D to dodge the acid, and duck behind walls."),
    "golem": ("KILLED BY A GOLEM", "Tip: golems are slow. Keep moving, and lure them next to a barrel."),
    "warden": ("KILLED BY THE WARDEN", "Tip: the fireballs come in threes. Strafe sideways, then strike back."),
    "barrel": ("BLOWN UP BY A BARREL", "Tip: step back before you shoot a barrel!"),
    "monster": ("KILLED BY A MONSTER", "Tip: keep moving, and keep your shells topped up."),
}

def killed_by(title, tip):
    return svg(440, 50,
        '<rect x="0" y="0" width="440" height="50" rx="10" fill="#000" opacity="0.6"/>'
        f'<text x="220" y="21" font-family="Sans Serif" font-size="17" font-weight="bold" fill="#ff4040" '
        f'text-anchor="middle" letter-spacing="2">{title}</text>'
        f'<text x="220" y="40" font-family="Sans Serif" font-size="12" fill="#e0d0c0" text-anchor="middle">{tip}</text>')
KILLED_BY = {name: killed_by(*text) for name, text in KILLERS.items()}

def prompt(text, color):
    box_width = 11 * len(text) + 40
    return svg(box_width, 30, f'<rect x="0" y="1" width="{box_width}" height="28" rx="14" fill="#000" opacity="0.6"/>'
                      f'<text x="{box_width / 2}" y="21" font-family="Sans Serif" font-size="15" font-weight="bold" fill="{color}" '
                      f'text-anchor="middle" letter-spacing="1.5">{text}</text>')
PROMPT_RETRY = prompt("PRESS SPACE TO RETRY", "#ffe14d")
PROMPT_AGAIN = prompt("CLICK THE GREEN FLAG TO PLAY AGAIN", "#ffe14d")

# =============================== VICTORY SCREEN ===============================
def _victory_sky():
    rnd = random.Random(51)
    picture = ('<defs><linearGradient id="dawn" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#1a1440"/><stop offset="0.45" stop-color="#7a3a6a"/>'
         '<stop offset="0.75" stop-color="#ff8a4a"/><stop offset="1" stop-color="#ffd27a"/></linearGradient>'
         '<radialGradient id="sun"><stop offset="0" stop-color="#fff6d0"/><stop offset="0.45" stop-color="#ffd25a"/>'
         '<stop offset="1" stop-color="#ffb030" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="field" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#3a2418"/><stop offset="1" stop-color="#120a06"/></linearGradient></defs>'
         '<rect width="480" height="250" fill="url(#dawn)"/>')
    picture += "".join(f'<circle cx="{rnd.uniform(0, 480):.0f}" cy="{rnd.uniform(0, 70):.0f}" r="{rnd.choice([0.7, 1])}" '
                 f'fill="#fff" opacity="{rnd.uniform(0.2, 0.6):.2f}"/>' for _ in range(25))
    for ray_number in range(16):                              # sun rays
        ray_angle = math.radians(180 + ray_number * 12 + 6)
        ray_start_x, ray_start_y = 240 + 60 * math.cos(ray_angle), 205 + 60 * math.sin(ray_angle)
        ray_end_x, ray_end_y = 240 + 330 * math.cos(ray_angle), 205 + 330 * math.sin(ray_angle)
        picture += f'<line x1="{ray_start_x:.0f}" y1="{ray_start_y:.0f}" x2="{ray_end_x:.0f}" y2="{ray_end_y:.0f}" stroke="#fff2b0" stroke-width="10" opacity="0.10"/>'
    picture += '<circle cx="240" cy="205" r="120" fill="url(#sun)"/><circle cx="240" cy="205" r="42" fill="#fff0b8"/>'
    picture += '<path d="M0 215 L50 192 L95 205 L150 180 L200 200 L240 186 L290 202 L340 178 L390 198 L440 186 L480 196 L480 250 L0 250 Z" fill="#5a2a3a" opacity="0.8"/>'
    fort = "M60 250 V196 H72 V184 H80 V196 H96 V170 H104 V160 H112 V170 H120 V196 H150 V176 H164 V196 H330 V180 H344 V196 H360 V166 H368 V150 H376 V166 H384 V196 H404 V186 H414 V196 H420 V250 Z"
    picture += f'<path d="{fort}" fill="#2a1420"/>'
    picture += '<rect y="236" width="480" height="124" fill="url(#field)"/>'
    for grass_x, grass_y in ((110, 290), (380, 300), (240, 335), (40, 330), (440, 340)):
        picture += f'<path d="M{grass_x} {grass_y} q4 -10 8 0 q4 -10 8 0" stroke="#6a8a3a" stroke-width="2" fill="none"/>'
    return svg(480, 360, picture)
VICTORY_SKY = _victory_sky()

def _victory_logo():
    unit, text = 10, "VICTORY"
    logo_width = text_width(text, unit) + 16
    logo_height = 7 * unit + 40
    body = "<defs>" + gradient("gold", 4, 4 + 7 * unit, GOLD_STOPS) + "</defs>"
    body += f'<ellipse cx="{logo_width / 2}" cy="{4 + 3.5 * unit}" rx="{logo_width / 2}" ry="{4.5 * unit}" fill="#fff2a0" opacity="0.18"/>'
    body += block_text(text, unit, 6, 4, "gold")
    body += (f'<text x="{logo_width / 2}" y="{logo_height - 6}" font-family="Sans Serif" font-size="15" font-weight="bold" fill="#fff6d8" '
             f'stroke="#3a1a00" stroke-width="3" paint-order="stroke" text-anchor="middle" letter-spacing="3">'
             'YOU ESCAPED THE FORTRESS</text>')
    return svg(logo_width, logo_height, body)
VICTORY_LOGO = _victory_logo()
VICTORY_CENTER = ((text_width("VICTORY", 10) + 16) // 2, (7 * 10 + 40) // 2)

STATS_PANEL = svg(300, 76,
    '<rect x="0" y="0" width="300" height="76" rx="12" fill="#000" opacity="0.62"/>'
    '<rect x="1.5" y="1.5" width="297" height="73" rx="11" fill="none" stroke="#ffd25a" stroke-opacity="0.6" stroke-width="2"/>'
    + assets2._label(16, 27, "TOTAL KILLS", size=15, fill="#ffe9b0")
    + assets2._label(16, 61, "SECRETS FOUND", size=15, fill="#ffe9b0")
    + '<text x="227" y="65" font-family="Sans Serif" font-weight="bold" font-size="24" fill="#ff4a24" text-anchor="middle">/</text>')

ROCKET = svg(8, 18, '<path d="M4 0 L7 10 L4 18 L1 10 Z" fill="#fff4c0"/><circle cx="4" cy="6" r="2.5" fill="#ffffff"/>')
SPARK_COLORS = {"gold": "#ffd23f", "red": "#ff4a4a", "cyan": "#4ae0ff", "green": "#6aff6a", "pink": "#ff6ad8"}
SPARKS = {name: svg(12, 12, f'<circle cx="6" cy="6" r="5.5" fill="{color}" opacity="0.35"/><circle cx="6" cy="6" r="3" fill="{color}"/>'
                            '<circle cx="6" cy="6" r="1.3" fill="#ffffff"/>') for name, color in SPARK_COLORS.items()}

# =============================== SOUNDS ===============================
def death_sting():
    """A low, falling minor chord with a distorted edge."""
    sample_count = int(RATE * 2.0); out = [0.0] * sample_count
    for midi, delay in ((52, 0.0), (48, 0.0), (45, 0.0), (40, 0.12)):
        start_pitch, phase = 440 * 2 ** ((midi - 69) / 12), 0.0
        for sample_number in range(int(delay * RATE), sample_count):
            seconds = sample_number / RATE - delay
            pitch = start_pitch * (1 - 0.18 * min(1, seconds / 1.6))
            phase += pitch / RATE
            saw = 2 * (phase % 1) - 1
            out[sample_number] += math.tanh(2.5 * saw) * 0.22 * min(1, seconds * 40) * math.exp(-seconds * 1.4)
    return _wav([max(-1, min(1, sample)) for sample in _lowpass(out, 0.2)])

def victory_theme():
    """An original upbeat power-chord loop in E major with drums (about 3.4 seconds)."""
    step = 60 / 140 / 2
    low_e = 52
    notes = [low_e, low_e, low_e + 7, low_e + 5, low_e + 4, low_e + 5, low_e + 7, low_e + 12,
             low_e + 9, low_e + 9, low_e + 7, low_e + 5, low_e + 4, low_e + 2, low_e + 4, low_e]
    sample_count = int(RATE * step * len(notes)); out = [0.0] * sample_count
    rnd = random.Random(9)
    for note_number, midi in enumerate(notes):
        start = int(note_number * step * RATE)
        for interval in (0, 7):                         # power chord: root + fifth
            pitch, phase = 440 * 2 ** ((midi + interval - 69) / 12), 0.0
            for sample_in_note in range(int(RATE * step * 0.95)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                phase += pitch / RATE
                saw = 2 * (phase % 1) - 1
                out[start + sample_in_note] += math.tanh(2.4 * saw) * 0.18 * min(1, seconds * 300) * math.exp(-seconds * 3)
    for beat in range(len(notes)):
        start = int(beat * step * RATE)
        if beat % 2 == 0:
            for sample_in_note in range(int(RATE * 0.16)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += math.sin(2 * math.pi * (100 - 220 * seconds) * seconds) * math.exp(-seconds * 22) * 0.6
        if beat % 4 == 2:
            for sample_in_note in range(int(RATE * 0.14)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += rnd.uniform(-1, 1) * math.exp(-seconds * 28) * 0.3
    return _wav([max(-1, min(1, sample)) * 0.9 for sample in _lowpass(out, 0.4)])

def firework_pop():
    rnd = random.Random(61); out = []
    for sample_number in range(int(RATE * 0.6)):
        seconds = sample_number / RATE
        sample = rnd.uniform(-1, 1) * math.exp(-seconds * 30) * 0.9
        if seconds > 0.08 and rnd.random() < 0.004 * math.exp(-seconds * 4) * 40: sample += rnd.uniform(-1, 1) * 0.6   # crackle
        sample += math.sin(2 * math.pi * 70 * seconds) * math.exp(-seconds * 18) * 0.5
        out.append(sample)
    return _wav(_lowpass(out, 0.5))

# =============================== SPRINT ===============================
SPRINT_FRAME = ('<rect x="6" y="268" width="124" height="15" rx="4" fill="#000" fill-opacity="0.5"/>'
                '<text x="14" y="279" font-family="Sans Serif" font-weight="bold" font-size="9" fill="#d8d8d8" '
                'letter-spacing="1.5">SPRINT (HOLD Q)</text>'
                '<rect x="12" y="285" width="112" height="9" rx="3" fill="none" stroke="#d8d8d8" stroke-opacity="0.8" stroke-width="1.2"/>')

def hud_with_sprint(hud_svg):
    """The HUD frame plus the sprint bar's label and outline. The bar's fill is drawn with the pen."""
    return hud_svg.replace("</svg>", SPRINT_FRAME + "</svg>")

def out_of_breath():
    """Two ragged breaths: filtered noise swells."""
    rnd = random.Random(71); sample_count = int(RATE * 1.1); out, smoothed = [], 0.0
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        phase = (seconds % 0.55) / 0.55
        env = math.sin(math.pi * min(1, phase / 0.8)) ** 2 if phase < 0.8 else 0
        smoothed += 0.12 * (rnd.uniform(-1, 1) - smoothed)
        out.append(smoothed * 3.2 * env * (1 if seconds < 0.55 else 0.8))
    return _wav(out)
