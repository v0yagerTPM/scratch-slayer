"""Art + sound for round 2: pickups, keys, text labels, messages, the full-screen helper, digits,
door/switch sounds."""
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

# ---------------- big pixel digits for the HUD (20x28, anchored right-middle) ----------------
GLYPHS = {
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
}
def digit(character):
    rows = GLYPHS[character].split()
    lit_squares = [(column, row) for row, row_bits in enumerate(rows) for column, bit in enumerate(row_bits) if bit == "1"]
    shadow = "".join(f'<rect x="{column * 4 + 1}" y="{row * 4 + 1}" width="4" height="4" fill="#000"/>' for column, row in lit_squares)
    main = "".join(f'<rect x="{column * 4}" y="{row * 4}" width="4" height="4" fill="#ff4a24"/>' for column, row in lit_squares)
    return svg(21, 29, shadow + main)
DIGITS = {character: digit(character) for character in GLYPHS}

# ---------------- text labels (used on the HUD, screens and menus) ----------------
def _label(text_x, text_y, text, anchor="start", size=13, fill="#d8d8d8"):
    return (f'<text x="{text_x}" y="{text_y}" font-family="Sans Serif" font-weight="bold" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="2">{text}</text>')


# ---------------- messages along the top of the screen ----------------
def toast(text, color="#ffffff"):
    box_width = max(200, 11 * len(text) + 40)
    return svg(480, 360, f'<rect x="{240 - box_width / 2}" y="14" width="{box_width}" height="32" rx="8" fill="#000" fill-opacity="0.6"/>'
                         f'<text x="240" y="36" font-family="Sans Serif" font-weight="bold" font-size="16" '
                         f'fill="{color}" text-anchor="middle">{text}</text>')


# Every message the Message sprite can show, in costume order. The key is the costume name
# without "message " (so "door hint" is the costume "message door hint").
MESSAGES = {
    "door hint": toast("Press E to open the door", "#ffe14d"),
    "switch hint": toast("Press E to flip the EXIT switch", "#40ff70"),
    "need red key": toast("You need the RED key to open this door", "#ff6060"),
    "need blue key": toast("You need the BLUE key to open this door", "#70a0ff"),
    "picked up 1": toast("+25 HEALTH", "#60ff80"),
    "picked up 2": toast("+8 SHELLS", "#ffd23f"),
    "picked up 3": toast("Picked up the RED KEY", "#ff6060"),
    "picked up 4": toast("Picked up the BLUE KEY", "#70a0ff"),
    "exit activated": toast("EXIT ACTIVATED", "#40ff70"),
    "found secret": toast("You found a secret area!", "#ffd23f"),
    "out of breath": toast("Out of breath! Wait for the sprint bar", "#ffa040"),
    "picked up 5": toast("Got the SKULL KEY! The exit unseals", "#d8a0ff"),
    "picked up 6": toast("+20 BULLETS", "#ffd23f"),
    "picked up 7": toast("+4 ROCKETS", "#ffa040"),
    "picked up 8": toast("SHOTGUN!  Press 3", "#ffe14d"),
    "picked up 9": toast("CHAINGUN!  Press 4", "#ffe14d"),
    "picked up 10": toast("ROCKET LAUNCHER!  Press 5", "#ffe14d"),
    "need skull key": toast("SEALED! Beat the boss for the SKULL KEY", "#d8a0ff"),
    "out of ammo": toast("Out of ammo! Switching weapons", "#ffa040"),
    "boss awake warden": toast("THE WARDEN AWAKENS", "#ff4040"),
    "boss awake colossus": toast("THE COLOSSUS AWAKENS", "#ff4040"),
    "boss enraged colossus": toast("THE COLOSSUS IS ENRAGED!", "#ff4040"),
    "music on": toast("Music ON  (N to switch)", "#60ff80"),
    "music off": toast("Music OFF  (N to switch)", "#aaaaaa"),
}

# ---------------- full-screen overlays ----------------
def _screen(title, color, lines, extra="", opacity=0.72):
    body = (f'<rect width="480" height="360" fill="#000" fill-opacity="{opacity}"/>'
            f'<text x="240" y="100" font-family="Pixel" font-size="40" fill="{color}" stroke="#000" '
            f'stroke-width="2" text-anchor="middle">{title}</text>')
    for txt, text_y, size, fill in lines:
        body += (f'<text x="240" y="{text_y}" font-family="Sans Serif" font-size="{size}" fill="{fill}" '
                 f'text-anchor="middle">{txt}</text>')
    return svg(480, 360, body + extra)


# ---------------- sounds ----------------
def door():
    rnd = random.Random(5); sample_count = int(RATE * 0.55)
    noise = _lowpass([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.05)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        sample = noise[sample_number] * 3.5 * min(1, seconds * 20) * (1 - seconds / 0.55)
        sample += math.sin(2 * math.pi * (60 + 40 * seconds) * seconds) * 0.35 * (1 - seconds / 0.55)
        if seconds > 0.47: sample += math.sin(2 * math.pi * 80 * seconds) * math.exp(-(seconds - 0.47) * 40)
        out.append(sample)
    return _wav(out)

def switch():
    out = []
    for sample_number in range(int(RATE * 0.45)):
        seconds = sample_number / RATE
        sample = (1 if seconds < 0.01 else 0) * 0.8
        pitch = 440 if seconds < 0.15 else 660
        if seconds > 0.04: sample += (1 if math.sin(2 * math.pi * pitch * seconds) > 0 else -1) * 0.3 * math.exp(-(seconds % 0.15) * 8)
        out.append(sample)
    return _wav(_lowpass(out, 0.4))

def locked():
    out = [(1 if (sample_number * 110 / RATE) % 1 < 0.5 else -1) * 0.5 * (1 - sample_number / (RATE * 0.3)) for sample_number in range(int(RATE * 0.3))]
    return _wav(_lowpass(out, 0.2))

def punch():
    rnd = random.Random(7); out = []
    for sample_number in range(int(RATE * 0.18)):
        seconds = sample_number / RATE
        out.append(math.sin(2 * math.pi * 85 * seconds) * math.exp(-seconds * 25) + rnd.uniform(-1, 1) * 0.5 * math.exp(-seconds * 60))
    return _wav(out)

def item():
    out, phase = [], 0.0
    for sample_number in range(int(RATE * 0.16)):
        seconds = sample_number / RATE; phase += (600 + 4000 * seconds) / RATE
        out.append((1 if phase % 1 < 0.5 else -1) * 0.35 * (1 - seconds / 0.16))
    return _wav(_lowpass(out, 0.5))

def key():
    out = []
    for note_number, pitch in enumerate((523, 659, 784, 1047)):
        for sample_number in range(int(RATE * 0.08)):
            seconds = sample_number / RATE
            out.append((1 if math.sin(2 * math.pi * pitch * seconds) > 0 else -1) * 0.3 * (1 - seconds / 0.08))
    return _wav(_lowpass(out, 0.5))
