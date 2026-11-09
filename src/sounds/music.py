"""Original music: the title riff, the death sting, the victory theme and the two
in-game loops."""
import math, random, wave
from sounds.synth import RATE, make_wav, note_frequency, smooth_samples

def title_riff():
    """An original chugging riff: 2 bars of sixteenths at 150 BPM, with kick and snare. Loops cleanly."""
    step = 60 / 150 / 4
    low_e = 40
    bar1 = [low_e, low_e, low_e + 3, low_e, low_e, low_e, low_e + 6, low_e + 5, low_e, low_e, low_e + 3, low_e, low_e, low_e, low_e - 2, low_e - 1]
    bar2 = [low_e, low_e, low_e + 3, low_e, low_e, low_e, low_e + 6, low_e + 5, low_e, low_e, low_e + 7, low_e + 6, low_e + 5, low_e + 3, low_e + 2, low_e]
    notes = bar1 + bar2 + bar1 + bar2
    sample_count = int(RATE * step * len(notes))
    out = [0.0] * sample_count
    rnd = random.Random(5)
    for note_number, midi in enumerate(notes):
        start = int(note_number * step * RATE)
        accent = midi != low_e
        length = int(RATE * step * (0.95 if accent else 0.55))
        pitch, phase = note_frequency(midi), 0.0
        for sample_in_note in range(length):
            if start + sample_in_note >= sample_count: break
            seconds = sample_in_note / RATE
            phase += pitch / RATE
            saw = 2 * (phase % 1) - 1 + 0.6 * (2 * ((phase * 2.005) % 1) - 1)
            env = min(1, seconds * 400) * math.exp(-seconds * (6 if accent else 22))
            out[start + sample_in_note] += math.tanh(3.2 * saw) * 0.32 * env
    for beat in range(len(notes) // 4):                      # kick on every beat, snare on 2 and 4
        start = int(beat * 4 * step * RATE)
        for sample_in_note in range(int(RATE * 0.18)):
            if start + sample_in_note >= sample_count: break
            seconds = sample_in_note / RATE
            out[start + sample_in_note] += math.sin(2 * math.pi * (110 - 260 * seconds) * seconds) * math.exp(-seconds * 22) * 0.75
        if beat % 2 == 1:
            for sample_in_note in range(int(RATE * 0.16)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                out[start + sample_in_note] += rnd.uniform(-1, 1) * math.exp(-seconds * 26) * 0.35
    smooth = smooth_samples(out, 0.35)
    return make_wav([max(-1, min(1, sample)) * 0.9 for sample in smooth])

def death_sting():
    """A low, falling minor chord with a distorted edge."""
    sample_count = int(RATE * 2.0); out = [0.0] * sample_count
    for midi, delay in ((52, 0.0), (48, 0.0), (45, 0.0), (40, 0.12)):
        start_pitch, phase = 440 * 2 ** ((midi - 69) / 12), 0.0
        for sample_number in range(int(delay * RATE), sample_count):
            seconds = sample_number / RATE - delay
            pitch = start_pitch * (1 - 0.18 * min(1, seconds / 1.6))
            phase += pitch / RATE
            saw = 2 * (phase % 1) - 1
            out[sample_number] += math.tanh(2.5 * saw) * 0.22 * min(1, seconds * 40) * math.exp(-seconds * 1.4)
    return make_wav([max(-1, min(1, sample)) for sample in smooth_samples(out, 0.2)])

def victory_theme():
    """An original upbeat power-chord loop in E major with drums (about 3.4 seconds)."""
    step = 60 / 140 / 2
    low_e = 52
    notes = [low_e, low_e, low_e + 7, low_e + 5, low_e + 4, low_e + 5, low_e + 7, low_e + 12,
             low_e + 9, low_e + 9, low_e + 7, low_e + 5, low_e + 4, low_e + 2, low_e + 4, low_e]
    sample_count = int(RATE * step * len(notes)); out = [0.0] * sample_count
    rnd = random.Random(9)
    for note_number, midi in enumerate(notes):
        start = int(note_number * step * RATE)
        for interval in (0, 7):                         # power chord: root + fifth
            pitch, phase = 440 * 2 ** ((midi + interval - 69) / 12), 0.0
            for sample_in_note in range(int(RATE * step * 0.95)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                phase += pitch / RATE
                saw = 2 * (phase % 1) - 1
                out[start + sample_in_note] += math.tanh(2.4 * saw) * 0.18 * min(1, seconds * 300) * math.exp(-seconds * 3)
    for beat in range(len(notes)):
        start = int(beat * step * RATE)
        if beat % 2 == 0:
            for sample_in_note in range(int(RATE * 0.16)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += math.sin(2 * math.pi * (100 - 220 * seconds) * seconds) * math.exp(-seconds * 22) * 0.6
        if beat % 4 == 2:
            for sample_in_note in range(int(RATE * 0.14)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += rnd.uniform(-1, 1) * math.exp(-seconds * 28) * 0.3
    return make_wav([max(-1, min(1, sample)) * 0.9 for sample in smooth_samples(out, 0.4)])

def _music(bpm, riff, root, kick_pattern, snare_pattern, seed, dark=False):
    """Mix an original loop: a distorted guitar riff (with a power-chord fifth on accents),
    a bass an octave down, and kick + snare + hi-hat drums. 'riff' = semitones above 'root'
    (None = rest), one per sixteenth note."""
    step = 60 / bpm / 4
    sample_count = int(RATE * step * len(riff)); out = [0.0] * sample_count
    rnd = random.Random(seed)
    for step_number, semi in enumerate(riff):
        if semi is None:
            continue
        start = int(step_number * step * RATE)
        accent = semi != 0
        length = int(RATE * step * (1.9 if accent else 0.6))
        for interval, gain in ((0, 0.26), (7, 0.16 if accent else 0), (-12, 0.22)):
            if not gain:
                continue
            pitch, phase = note_frequency(root + semi + interval), 0.0
            for sample_in_note in range(length):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                phase += pitch / RATE
                wave = (2 * (phase % 1) - 1) if interval != -12 else math.sin(2 * math.pi * phase)
                env = min(1, seconds * 300) * math.exp(-seconds * (4 if accent else 18))
                shaped = math.tanh((3.5 if not dark else 2.5) * wave) if interval != -12 else wave
                out[start + sample_in_note] += shaped * gain * env
    for s16 in range(len(riff)):
        start = int(s16 * step * RATE)
        if kick_pattern[s16 % len(kick_pattern)] == "x":
            for sample_in_note in range(int(RATE * 0.2)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += math.sin(2 * math.pi * (105 - 240 * seconds) * seconds) * math.exp(-seconds * 20) * 0.8
        if snare_pattern[s16 % len(snare_pattern)] == "x":
            for sample_in_note in range(int(RATE * 0.18)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE
                out[start + sample_in_note] += (rnd.uniform(-1, 1) * 0.42 + math.sin(2 * math.pi * 190 * seconds) * 0.2) * math.exp(-seconds * 22)
        if s16 % 2 == 0:
            for sample_in_note in range(int(RATE * 0.04)):
                if start + sample_in_note >= sample_count: break
                seconds = sample_in_note / RATE; out[start + sample_in_note] += rnd.uniform(-1, 1) * 0.07 * math.exp(-seconds * 90)
    smooth = smooth_samples(out, 0.3 if dark else 0.38)
    peak = max(abs(sample) for sample in smooth) or 1
    return make_wav([sample / peak * 0.85 for sample in smooth])

def episode_1_theme():
    """Original: a brooding, mid-tempo chug in E minor (about 8.7 seconds, loops cleanly)."""
    bar_a = [0, 0, None, 0, 0, None, 3, None, 0, 0, None, 0, 5, None, 3, None]
    bar_b = [0, 0, None, 0, 0, None, 3, None, 0, 0, None, 0, 7, 6, 5, 3]
    bar_c = [0, 0, None, 0, 0, None, 3, None, 0, 0, None, 0, 1, None, -2, None]
    riff = bar_a + bar_b + bar_a + bar_c
    return _music(110, riff, 40, "x.......x.x.....", "....x.......x...", 91, dark=True)

def episode_2_theme():
    """Original: a faster, heavier gallop in D minor (about 7.4 seconds, loops cleanly)."""
    gallop = [0, 0, 0, None, 0, 0, 0, None]
    bar_a = gallop + [0, 0, 3, None, 5, None, 3, None]
    bar_b = gallop + [0, 0, 6, None, 5, None, 3, 1]
    bar_c = gallop + [8, None, 7, None, 5, None, 3, None]
    riff = bar_a + bar_b + bar_a + bar_c
    return _music(130, riff, 38, "x.x...x.x.x...x.", "....x.......x...", 92)
