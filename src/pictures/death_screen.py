"""The death screen: YOU DIED, the blood, and a tip card for whatever killed you."""
import random
from pictures.drawing import BLOOD_STOPS, gradient, svg
from pictures.lettering import LETTERS, block_text, text_width

def _you_died():
    unit, text = 9, "YOU DIED"
    picture_width = text_width(text, unit) + 16
    body = "<defs>" + gradient("blood", 4, 4 + 7 * unit, BLOOD_STOPS) + "</defs>" + block_text(text, unit, 6, 4, "blood")
    rnd = random.Random(41)
    bottom_pixels = [6 + (letter_number * 6 + col) * unit for letter_number, character in enumerate(text)
                     for col, bit in enumerate(LETTERS[character].split()[-1]) if bit == "1"]
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
    "charger": ("FLATTENED BY A CHARGER", "Tip: when it lowers its head, sidestep! It slams into walls."),
    "wraith": ("CAUGHT BY A WRAITH", "Tip: wraiths fade from far away. Keep your back to a wall."),
    "colossus": ("CRUSHED BY THE COLOSSUS", "Tip: hide behind the pillars, and save rockets for the boss."),
    "rocket": ("BLOWN UP BY YOUR OWN ROCKET", "Tip: don't fire rockets at monsters right next to you!"),
}

def killed_by(title, tip):
    return svg(440, 50,
        '<rect x="0" y="0" width="440" height="50" rx="10" fill="#000" opacity="0.6"/>'
        f'<text x="220" y="21" font-family="Sans Serif" font-size="17" font-weight="bold" fill="#ff4040" '
        f'text-anchor="middle" letter-spacing="2">{title}</text>'
        f'<text x="220" y="40" font-family="Sans Serif" font-size="12" fill="#e0d0c0" text-anchor="middle">{tip}</text>')

KILLED_BY = {name: killed_by(*text) for name, text in KILLERS.items()}
