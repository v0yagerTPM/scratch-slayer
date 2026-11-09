"""Monster sounds: growls, spit, fireballs and the wraith's blink."""
import math, random
from sounds.synth import RATE, make_wav, smooth_samples

def _growl(dur, start_pitch, end_pitch, vib, seed):
    rnd = random.Random(seed)
    sample_count, phase, out = int(RATE * dur), 0.0, []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        pitch = start_pitch + (end_pitch - start_pitch) * (seconds / dur)
        pitch *= 1 + 0.08 * math.sin(2 * math.pi * vib * seconds)
        phase += pitch / RATE
        saw = 2 * (phase % 1) - 1
        env = min(1, seconds * 60) * (1 - seconds / dur) ** 1.5
        out.append((saw * 0.7 + rnd.uniform(-1, 1) * 0.3) * env)
    return make_wav([sample * 1.4 for sample in smooth_samples(out, 0.18)])

def monster_pain(): return _growl(0.22, 260, 150, 30, 2)

def monster_death(): return _growl(0.85, 170, 45, 14, 3)

def spit():
    rnd = random.Random(11); sample_count = int(RATE * 0.3)
    noise = smooth_samples([rnd.uniform(-1, 1) for _ in range(sample_count)], 0.25)
    out = []
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        out.append(noise[sample_number] * 2.2 * math.exp(-seconds * 14) + math.sin(2 * math.pi * (500 - 900 * seconds) * seconds) * 0.3 * math.exp(-seconds * 10))
    return make_wav(out)

def fireball():
    rnd = random.Random(12); sample_count = int(RATE * 0.5)
    noise = [rnd.uniform(-1, 1) for _ in range(sample_count)]
    out, smoothed = [], 0.0
    for sample_number in range(sample_count):
        seconds = sample_number / RATE
        smoothing = 0.05 + 0.25 * min(1, seconds / 0.2)
        smoothed += smoothing * (noise[sample_number] - smoothed)
        out.append(smoothed * 2.5 * min(1, seconds * 30) * (1 - seconds / 0.5) + math.sin(2 * math.pi * 90 * seconds) * 0.3 * (1 - seconds / 0.5))
    return make_wav(out)

def wraith_blink():
    out = []
    for sample_number in range(int(RATE * 0.45)):
        seconds = sample_number / RATE
        pitch = 900 - 1400 * seconds
        sample = math.sin(2 * math.pi * pitch * seconds) * 0.35 + math.sin(2 * math.pi * pitch * 1.5 * seconds) * 0.2
        out.append(sample * math.sin(math.pi * seconds / 0.45) * (0.6 + 0.4 * math.sin(2 * math.pi * 30 * seconds)))
    return make_wav(out)
