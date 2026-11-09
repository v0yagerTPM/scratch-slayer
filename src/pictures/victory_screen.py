"""The victory screen: the dawn sky, the VICTORY logo, the stats panel and fireworks."""
import math, random
from pictures.drawing import GOLD_STOPS, gradient, svg, text_label
from pictures.lettering import block_text, text_width

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
             'YOU DESTROYED THE CORE</text>')
    return svg(logo_width, logo_height, body)

VICTORY_LOGO = _victory_logo()

VICTORY_CENTER = ((text_width("VICTORY", 10) + 16) // 2, (7 * 10 + 40) // 2)

STATS_PANEL = svg(300, 76,
    '<rect x="0" y="0" width="300" height="76" rx="12" fill="#000" opacity="0.62"/>'
    '<rect x="1.5" y="1.5" width="297" height="73" rx="11" fill="none" stroke="#ffd25a" stroke-opacity="0.6" stroke-width="2"/>'
    + text_label(16, 27, "TOTAL KILLS", size=15, fill="#ffe9b0")
    + text_label(16, 61, "SECRETS FOUND", size=15, fill="#ffe9b0")
    + '<text x="227" y="65" font-family="Sans Serif" font-weight="bold" font-size="24" fill="#ff4a24" text-anchor="middle">/</text>')

ROCKET = svg(8, 18, '<path d="M4 0 L7 10 L4 18 L1 10 Z" fill="#fff4c0"/><circle cx="4" cy="6" r="2.5" fill="#ffffff"/>')

SPARK_COLORS = {"gold": "#ffd23f", "red": "#ff4a4a", "cyan": "#4ae0ff", "green": "#6aff6a", "pink": "#ff6ad8"}

SPARKS = {name: svg(12, 12, f'<circle cx="6" cy="6" r="5.5" fill="{color}" opacity="0.35"/><circle cx="6" cy="6" r="3" fill="{color}"/>'
                            '<circle cx="6" cy="6" r="1.3" fill="#ffffff"/>') for name, color in SPARK_COLORS.items()}
