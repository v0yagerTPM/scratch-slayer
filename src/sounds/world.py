"""Sounds of the world: doors, switches, pickups, explosions, secrets, getting hurt
and running out of breath."""
import math, random
from sounds.synth import RATE, make_wav, smooth_samples

def player_hurt():
    sample_count, phase, out = int(RATE * 0.22), 0.0, []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        phase += (150 - 200 * seconds) / RATE
        square_wave = 1 if (phase % 1) < 0.5 else -1
        out.append(square_wave * min(1, seconds * 80) * (1 - seconds / 0.22))
    return make_wav([sample * 1.2 for sample in smooth_samples(out, 0.12)])

def door():
    rnd = random.Random(5); sample_count = int(RATE * 0.55)
    noise = smooth_samples([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.05)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        sample = noise[sample_number] * 3.5 * min(1, seconds * 20) * (1 - seconds / 0.55)
        sample += math.sin(2 * math.pi * (60 + 40 * seconds) * seconds) * 0.35 * (1 - seconds / 0.55)
        if seconds > 0.47: sample += math.sin(2 * math.pi * 80 * seconds) * math.exp(-(seconds - 0.47) * 40)
        out.append(sample)
    return make_wav(out)

def switch():
    out = []
    for sample_number in range(int(RATE * 0.45)):
        seconds = sample_number / RATE
        sample = (1 if seconds < 0.01 else 0) * 0.8
        pitch = 440 if seconds < 0.15 else 660
        if seconds > 0.04: sample += (1 if math.sin(2 * math.pi * pitch * seconds) > 0 else -1) * 0.3 * math.exp(-(seconds % 0.15) * 8)
        out.append(sample)
    return make_wav(smooth_samples(out, 0.4))

def locked():
    out = [(1 if (sample_number * 110 / RATE) % 1 < 0.5 else -1) * 0.5 * (1 - sample_number / (RATE * 0.3)) for sample_number in range(int(RATE * 0.3))]
    return make_wav(smooth_samples(out, 0.2))

def item():
    out, phase = [], 0.0
    for sample_number in range(int(RATE * 0.16)):
        seconds = sample_number / RATE; phase += (600 + 4000 * seconds) / RATE
        out.append((1 if phase % 1 < 0.5 else -1) * 0.35 * (1 - seconds / 0.16))
    return make_wav(smooth_samples(out, 0.5))

def key():
    out = []
    for note_number, pitch in enumerate((523, 659, 784, 1047)):
        for sample_number in range(int(RATE * 0.08)):
            seconds = sample_number / RATE
            out.append((1 if math.sin(2 * math.pi * pitch * seconds) > 0 else -1) * 0.3 * (1 - seconds / 0.08))
    return make_wav(smooth_samples(out, 0.5))

def explosion():
    rnd = random.Random(13); sample_count = int(RATE * 1.1)
    noise = smooth_samples([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.08)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        sample = noise[sample_number] * 5 * math.exp(-seconds * 3.5) * min(1, seconds * 300)
        sample += math.sin(2 * math.pi * (60 - 25 * seconds) * seconds) * math.exp(-seconds * 4) * 0.9
        out.append(sample)
    return make_wav(out)

def secret():
    rnd = random.Random(14); sample_count = int(RATE * 0.9)
    noise = smooth_samples([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.03)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        sample = noise[sample_number] * 4 * (1 - seconds / 0.9) * min(1, seconds * 10)
        if seconds > 0.55:
            for pitch in (523, 784):
                sample += math.sin(2 * math.pi * pitch * seconds) * 0.15 * math.exp(-(seconds - 0.55) * 6)
        out.append(sample)
    return make_wav(out)

def out_of_breath():
    """Two ragged breaths: filtered noise swells."""
    rnd = random.Random(71); sample_count = int(RATE * 1.1); out, smoothed = [], 0.0
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        phase = (seconds % 0.55) / 0.55
        env = math.sin(math.pi * min(1, phase / 0.8)) ** 2 if phase < 0.8 else 0
        smoothed += 0.12 * (rnd.uniform(-1, 1) - smoothed)
        out.append(smoothed * 3.2 * env * (1 if seconds < 0.55 else 0.8))
    return make_wav(out)

def weapon_pickup():
    """Two metal clacks, then a bright ring."""
    rnd = random.Random(84); out = []
    for sample_number in range(int(RATE * 0.5)):
        seconds = sample_number / RATE; sample = 0.0
        for click_time in (0.0, 0.11):
            if click_time <= seconds < click_time + 0.04:
                sample += rnd.uniform(-1, 1) * 0.8 * math.exp(-(seconds - click_time) * 90)
        if seconds > 0.2:
            sample += (math.sin(2 * math.pi * 1320 * seconds) + 0.5 * math.sin(2 * math.pi * 1980 * seconds)) * 0.25 * math.exp(-(seconds - 0.2) * 9)
        out.append(sample)
    return make_wav(out)
