"""The title screen: the logo, the sky backdrop, the embers, and the pulsing prompts
(the Prompt Text sprite's costumes, also used on the death and victory screens)."""
import random
from pictures.drawing import FIRE_STOPS, gradient, svg
from pictures.lettering import block_text, text_width

# ---------------- title logo ----------------
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

# ---------------- title sky (stage backdrop) ----------------
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

def prompt(text, color):
    box_width = 11 * len(text) + 40
    return svg(box_width, 30, f'<rect x="0" y="1" width="{box_width}" height="28" rx="14" fill="#000" opacity="0.6"/>'
                      f'<text x="{box_width / 2}" y="21" font-family="Sans Serif" font-size="15" font-weight="bold" fill="{color}" '
                      f'text-anchor="middle" letter-spacing="1.5">{text}</text>')

PROMPT_RETRY = prompt("PRESS SPACE TO RETRY", "#ffe14d")

PROMPT_AGAIN = prompt("CLICK THE GREEN FLAG TO PLAY AGAIN", "#ffe14d")
