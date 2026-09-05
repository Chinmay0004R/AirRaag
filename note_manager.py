"""Note Manager — single source of truth for musical notes and frequencies."""

# Chromatic scale starting at octave 4
NOTES = [
    {"name": "C",  "semitone": 0},
    {"name": "C#", "semitone": 1},
    {"name": "D",  "semitone": 2},
    {"name": "D#", "semitone": 3},
    {"name": "E",  "semitone": 4},
    {"name": "F",  "semitone": 5},
    {"name": "F#", "semitone": 6},
    {"name": "G",  "semitone": 7},
    {"name": "G#", "semitone": 8},
    {"name": "A",  "semitone": 9},
    {"name": "A#", "semitone": 10},
    {"name": "B",  "semitone": 11},
]

# Finger-count → note mapping (sargam-style for easy switching)
# fingers=1 → Sa(C), 2 → Re(D), 3 → Ga(E), 4 → Ma(F), 5 → Pa(G),
# fist(0) → Dha(A), open-palm-spread(6+) → Ni(B)
FINGER_NOTES = [
    {"fingers": 0, "name": "A",  "sargam": "Dha", "semitone": 9,  "hint": "Fist"},
    {"fingers": 1, "name": "C",  "sargam": "Sa",  "semitone": 0,  "hint": "1 finger"},
    {"fingers": 2, "name": "D",  "sargam": "Re",  "semitone": 2,  "hint": "2 fingers"},
    {"fingers": 3, "name": "E",  "sargam": "Ga",  "semitone": 4,  "hint": "3 fingers"},
    {"fingers": 4, "name": "F",  "sargam": "Ma",  "semitone": 5,  "hint": "4 fingers"},
    {"fingers": 5, "name": "G",  "sargam": "Pa",  "semitone": 7,  "hint": "5 fingers"},
]

# A4 = 440 Hz, C4 = 261.63 Hz (A4 is 9 semitones above C4)
A4_FREQ = 440.0
A4_SEMITONE = 9  # A is the 9th semitone in the octave (0-indexed from C)


def get_frequency(note_name, octave=4):
    """Get frequency in Hz for a note name and octave."""
    for note in NOTES:
        if note["name"] == note_name:
            # semitones from A4
            distance = (octave - 4) * 12 + note["semitone"] - A4_SEMITONE
            return A4_FREQ * (2 ** (distance / 12.0))
    return 0.0


def get_note_for_fingers(finger_count):
    """Map a finger count (0-5) to a FINGER_NOTES dict.

    Returns the note dict or None if out of range.
    """
    for fn in FINGER_NOTES:
        if fn["fingers"] == finger_count:
            return fn
    return None


def get_note_for_x(x_normalized, num_notes=12):
    """Map a normalized x position (0.0–1.0) to a note dict.

    Returns the note dict or None if out of range.
    """
    if x_normalized < 0 or x_normalized > 1:
        return None
    index = int(x_normalized * num_notes)
    if index >= num_notes:
        index = num_notes - 1
    return NOTES[index]


def get_note_index(note_name):
    """Get the index (0–11) of a note by name."""
    for i, note in enumerate(NOTES):
        if note["name"] == note_name:
            return i
    return -1


def get_wav_filename(note_name, octave=4):
    """Get the wav filename for a note, e.g. 'C4.wav' or 'Csharp4.wav'."""
    safe = note_name.replace("#", "sharp")
    return f"{safe}{octave}.wav"
