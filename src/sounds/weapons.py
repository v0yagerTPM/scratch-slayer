"""Weapon sounds: punch, pistol, shotgun, chaingun and rocket launch."""
import math, random
from sounds.synth import RATE, make_wav, smooth_samples

def shotgun():
    rnd = random.Random(1)
    sample_count = int(RATE * 0.6)
    noise = smooth_samples([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.3)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        sample = noise[sample_number] * 2.2 * math.exp(-seconds * 10) * min(1, seconds * 400)
        sample += math.sin(2 * math.pi * 55 * seconds) * math.exp(-seconds * 16) * 0.9
        for click_time in (0.36, 0.45):  # pump click-clack
            if click_time <= seconds < click_time + 0.025:
                sample += rnd.uniform(-1, 1) * 0.5 * math.exp(-(seconds - click_time) * 120)
        out.append(sample * 0.8)
    return make_wav(out)

def punch():
    rnd = random.Random(7); out = []
    for sample_number in range(int(RATE * 0.18)):
        seconds = sample_number / RATE
        out.append(math.sin(2 * math.pi * 85 * seconds) * math.exp(-seconds * 25) + rnd.uniform(-1, 1) * 0.5 * math.exp(-seconds * 60))
    return make_wav(out)

def _crack(dur, thump_hz, decay, seed, gain=1.0):
    rnd = random.Random(seed)
    sample_count = int(RATE * dur)
    noise = smooth_samples([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.45)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        sample = noise[sample_number] * 2.0 * math.exp(-seconds * decay) * min(1, seconds * 600)
        sample += math.sin(2 * math.pi * thump_hz * seconds) * math.exp(-seconds * decay * 1.4) * 0.8
        out.append(sample * gain)
    return make_wav(out)

def pistol(): return _crack(0.25, 110, 30, 81)

def chaingun(): return _crack(0.13, 95, 42, 82, 0.9)

def rocket_launch():
    rnd = random.Random(83); sample_count = int(RATE * 0.7); out, smoothed = [], 0.0
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        smoothing = 0.05 + 0.3 * min(1, seconds / 0.15)
        smoothed += smoothing * (rnd.uniform(-1, 1) - smoothed)
        sample = smoothed * 2.4 * math.exp(-seconds * 4) + math.sin(2 * math.pi * 60 * seconds) * math.exp(-seconds * 14) * 0.9
        out.append(sample)
    return make_wav(out)
