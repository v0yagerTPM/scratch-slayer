"""Basic drawing helpers for every picture: the svg() wrapper, text labels, the full-screen
panel, and color gradients.

Every picture in the game is SVG: a drawing written as text, like
'<circle cx="10" cy="10" r="8" fill="#ffd23f"/>'. Scratch reads SVG costumes directly."""


def svg(width, height, body):
    """Wrap SVG shapes into a complete picture, width x height pixels."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">{body}</svg>')

# ---------------- text labels (used on the HUD, screens and menus) ----------------
def text_label(text_x, text_y, text, anchor="start", size=13, fill="#d8d8d8"):
    return (f'<text x="{text_x}" y="{text_y}" font-family="Sans Serif" font-weight="bold" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="2">{text}</text>')

# ---------------- full-screen overlays ----------------
def full_screen(title, color, lines, extra="", opacity=0.72):
    body = (f'<rect width="480" height="360" fill="#000" fill-opacity="{opacity}"/>'
            f'<text x="240" y="100" font-family="Pixel" font-size="40" fill="{color}" stroke="#000" '
            f'stroke-width="2" text-anchor="middle">{title}</text>')
    for txt, text_y, size, fill in lines:
        body += (f'<text x="240" y="{text_y}" font-family="Sans Serif" font-size="{size}" fill="{fill}" '
                 f'text-anchor="middle">{txt}</text>')
    return svg(480, 360, body + extra)

def gradient(grad_id, y_top, y_bottom, stops):
    """A top-to-bottom color fade. stops = [(how far down, 0 to 1, color), ...]."""
    stop_tags = "".join(f'<stop offset="{offset}" stop-color="{color}"/>' for offset, color in stops)
    return (f'<linearGradient id="{grad_id}" gradientUnits="userSpaceOnUse" x1="0" y1="{y_top}" x2="0" y2="{y_bottom}">'
            f'{stop_tags}</linearGradient>')

# Color fades for the block-letter logos: fire (title, options), blood (YOU DIED), gold (VICTORY).
FIRE_STOPS = [(0, "#fff3a0"), (0.35, "#ffc23a"), (0.7, "#ff6a00"), (1, "#c41400")]

BLOOD_STOPS = [(0, "#ff6a5a"), (0.4, "#e01818"), (1, "#5a0000")]

GOLD_STOPS = [(0, "#fffbe0"), (0.35, "#ffe066"), (0.75, "#f0a800"), (1, "#a05a00")]
