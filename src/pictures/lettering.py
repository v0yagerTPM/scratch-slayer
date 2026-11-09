"""The chunky block-letter font (5 x 7 squares per letter) used for logos and headings,
and the pixel shapes of the digits 0-9."""


# ---------------- big pixel digits for the HUD (20x28, anchored right-middle) ----------------
GLYPHS = {
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
}

# ---------------- block-letter font (5 x 7 pixels per letter) ----------------
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

LETTERS.update(GLYPHS)

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
