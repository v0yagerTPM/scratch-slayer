"""Menu and screen sounds: clicks, thuds, the screen melt, the tally and fireworks."""
import math, random
from sounds.synth import RATE, make_wav, smooth_samples

def thud():
    rnd = random.Random(31); out = []
    for sample_number in range(int(RATE * 0.45)):
        seconds = sample_number / RATE
        out.append(math.sin(2 * math.pi * (70 - 50 * seconds) * seconds) * math.exp(-seconds * 9) * 1.1 + rnd.uniform(-1, 1) * math.exp(-seconds * 40) * 0.5)
    return make_wav(smooth_samples(out, 0.3))

def melt():
    rnd = random.Random(32); sample_count = int(RATE * 1.2); out, smoothed = [], 0.0
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        smoothing = 0.25 * (1 - seconds / 1.2) + 0.02
        smoothed += smoothing * (rnd.uniform(-1, 1) - smoothed)
        out.append(smoothed * 3 * min(1, seconds * 20) * (1 - seconds / 1.2) + math.sin(2 * math.pi * (180 - 120 * seconds) * seconds) * 0.15 * (1 - seconds / 1.2))
    return make_wav(out)

def firework_pop():
    rnd = random.Random(61); out = []
    for sample_number in range(int(RATE * 0.6)):
        seconds = sample_number / RATE
        sample = rnd.uniform(-1, 1) * math.exp(-seconds * 30) * 0.9
        if seconds > 0.08 and rnd.random() < 0.004 * math.exp(-seconds * 4) * 40: sample += rnd.uniform(-1, 1) * 0.6   # crackle
        sample += math.sin(2 * math.pi * 70 * seconds) * math.exp(-seconds * 18) * 0.5
        out.append(sample)
    return make_wav(smooth_samples(out, 0.5))

def menu_click():
    out = [math.sin(2 * math.pi * 1500 * (sample_number / RATE)) * math.exp(-(sample_number / RATE) * 60) * 0.6 for sample_number in range(int(RATE * 0.06))]
    return make_wav(out)

def tally_tick():
    """A short metallic click while the numbers count up."""
    sample_count = int(RATE * 0.025)
    noise = random.Random(71)
    return make_wav([(math.sin(2 * math.pi * 2200 * (sample_number / RATE)) * 0.5 + noise.uniform(-0.3, 0.3))
                 * math.exp(-(sample_number / RATE) * 180) for sample_number in range(sample_count)])

def tally_done():
    """A low thump when the counting finishes."""
    sample_count = int(RATE * 0.25)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        pitch = 140 - 260 * seconds
        out.append(math.sin(2 * math.pi * pitch * seconds) * 0.9 * math.exp(-seconds * 14))
    return make_wav(out)
