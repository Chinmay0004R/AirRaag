"""Generate instrument audio samples — run once before first use."""

import os
import numpy as np
from scipy.io import wavfile
import note_manager
import config


def adsr_envelope(length, sr, attack=0.05, decay=0.1, sustain_level=0.7, release=0.3):
    """Generate an ADSR amplitude envelope."""
    env = np.ones(length)
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    # Attack
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    # Decay
    if d > 0:
        env[a:a + d] = np.linspace(1, sustain_level, d)
    # Sustain
    env[a + d: length - r] = sustain_level
    # Release
    if r > 0:
        env[length - r:] = np.linspace(sustain_level, 0, r)
    return env


def generate_harmonium(freq, duration, sr):
    """Additive synthesis — organ/harmonium timbre."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    wave = (
        0.50 * np.sin(2 * np.pi * freq * t) +
        0.25 * np.sin(2 * np.pi * freq * 2 * t) +
        0.12 * np.sin(2 * np.pi * freq * 3 * t) +
        0.06 * np.sin(2 * np.pi * freq * 4 * t) +
        0.03 * np.sin(2 * np.pi * freq * 6 * t)
    )
    env = adsr_envelope(len(wave), sr, attack=0.08, decay=0.1, sustain_level=0.75, release=0.4)
    return wave * env


def generate_sitar(freq, duration, sr):
    """Karplus-Strong plucked string synthesis — sitar-like timbre."""
    n_samples = int(sr * duration)
    period = int(sr / freq)
    if period < 2:
        period = 2
    # Initialize buffer with noise burst
    buf = np.random.uniform(-1, 1, period).astype(np.float64)
    output = np.zeros(n_samples)
    for i in range(n_samples):
        output[i] = buf[i % period]
        # Averaging filter with slight detuning for sitar buzz
        next_idx = (i + 1) % period
        buf[i % period] = 0.498 * (buf[i % period] + buf[next_idx])
    # Add sympathetic resonance (faint octave harmonic)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    output += 0.08 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-2 * t)
    # Envelope
    env = adsr_envelope(n_samples, sr, attack=0.005, decay=0.15, sustain_level=0.3, release=0.5)
    return output * env


def save_wav(data, path, sr):
    """Normalize and save as 16-bit WAV."""
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak
    audio_16 = (data * 32767 * 0.8).astype(np.int16)
    # Stereo
    stereo = np.column_stack((audio_16, audio_16))
    wavfile.write(path, sr, stereo)


def generate_all():
    sr = config.SAMPLE_RATE
    dur = config.SAMPLE_DURATION

    for instrument, synth_fn in [("harmonium", generate_harmonium), ("sitar", generate_sitar)]:
        folder = os.path.join(config.AUDIO_DIR, instrument)
        os.makedirs(folder, exist_ok=True)
        print(f"\nGenerating {instrument}...")
        for note in note_manager.NOTES:
            freq = note_manager.get_frequency(note["name"], octave=4)
            filename = note_manager.get_wav_filename(note["name"])
            path = os.path.join(folder, filename)
            wave = synth_fn(freq, dur, sr)
            save_wav(wave, path, sr)
            print(f"  {filename}  ({freq:.2f} Hz)")

    print("\nDone! All samples generated.")


if __name__ == "__main__":
    generate_all()
