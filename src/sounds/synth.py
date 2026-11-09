"""Tools for making sounds from numbers: the sample rate, turning samples into a WAV file,
smoothing (a low-pass filter) and note pitches."""
import io, struct, wave

# A sound is a list of numbers between -1 and 1 (samples): how far the speaker is pushed out or
# pulled in at each moment. RATE samples make one second of sound.
RATE = 22050

def make_wav(samples):
    """Pack samples into a WAV file (16-bit, mono). Returns the file's bytes and the sample count."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1); wav_file.setsampwidth(2); wav_file.setframerate(RATE)
        wav_file.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, sample)) * 30000)) for sample in samples))
    return buffer.getvalue(), len(samples)

def smooth_samples(samples, smoothing):
    """A low-pass filter: each sample moves only part of the way (smoothing, 0 to 1) toward the
    next one, which rounds off sharp edges. Small smoothing = a duller, deeper sound."""
    smoothed, out = 0.0, []
    for sample in samples:
        smoothed += smoothing * (sample - smoothed); out.append(smoothed)
    return out

def note_frequency(midi):
    """The pitch (vibrations per second) of a note numbered like a MIDI keyboard: 69 is the A
    that orchestras tune to (440), and each step up is one semitone (12 steps = an octave)."""
    return 440 * 2 ** ((midi - 69) / 12)
