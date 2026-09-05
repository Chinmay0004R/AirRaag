"""Note Manager — single source of truth for musical notes and frequencies."""

# Full 12-swara system used by the app.
# The first 11 are mapped to the 0..10 fingers visible in the camera.
# The 12th swara is a special Upper Sa triggered by a right-hand thumb-only gesture.
SWARS = [
    {"name": "Sa", "western": "C", "sargam": "Sa", "semitone": 0, "hint": "Root"},
    {"name": "Komal Re", "western": "C#", "sargam": "Komal Re", "semitone": 1, "hint": "Flat 2nd"},
    {"name": "Re", "western": "D", "sargam": "Re", "semitone": 2, "hint": "2nd"},
    {"name": "Komal Ga", "western": "D#", "sargam": "Komal Ga", "semitone": 3, "hint": "Flat 3rd"},
    {"name": "Ga", "western": "E", "sargam": "Ga", "semitone": 4, "hint": "3rd"},
    {"name": "Ma", "western": "F", "sargam": "Ma", "semitone": 5, "hint": "4th"},
    {"name": "Tivra Ma", "western": "F#", "sargam": "Tivra Ma", "semitone": 6, "hint": "Sharp 4th"},
    {"name": "Pa", "western": "G", "sargam": "Pa", "semitone": 7, "hint": "5th"},
    {"name": "Komal Dha", "western": "G#", "sargam": "Komal Dha", "semitone": 8, "hint": "Flat 6th"},
    {"name": "Dha", "western": "A", "sargam": "Dha", "semitone": 9, "hint": "6th"},
    {"name": "Komal Ni", "western": "A#", "sargam": "Komal Ni", "semitone": 10, "hint": "Flat 7th"},
    {"name": "Ni", "western": "B", "sargam": "Ni", "semitone": 11, "hint": "7th"},
]

# Chromatic scale starting at octave 4.
# Keep the Western note names for audio and sample file lookup.
NOTES = [{"name": swar["western"], "semitone": swar["semitone"]} for swar in SWARS]

# 0..10 visible fingers map to 11 swaras on the screen.
# The final visible swara is Ni, while Upper Sa is the special 12th note.
FINGER_NOTES = [
    {"fingers": 0, "name": "C", "sargam": "Sa", "semitone": 0, "hint": "0 fingers"},
    {"fingers": 1, "name": "C#", "sargam": "Komal Re", "semitone": 1, "hint": "1 finger"},
    {"fingers": 2, "name": "D", "sargam": "Re", "semitone": 2, "hint": "2 fingers"},
    {"fingers": 3, "name": "D#", "sargam": "Komal Ga", "semitone": 3, "hint": "3 fingers"},
    {"fingers": 4, "name": "E", "sargam": "Ga", "semitone": 4, "hint": "4 fingers"},
    {"fingers": 5, "name": "F", "sargam": "Ma", "semitone": 5, "hint": "5 fingers"},
    {"fingers": 6, "name": "F#", "sargam": "Tivra Ma", "semitone": 6, "hint": "6 fingers"},
    {"fingers": 7, "name": "G", "sargam": "Pa", "semitone": 7, "hint": "7 fingers"},
    {"fingers": 8, "name": "G#", "sargam": "Komal Dha", "semitone": 8, "hint": "8 fingers"},
    {"fingers": 9, "name": "A", "sargam": "Dha", "semitone": 9, "hint": "9 fingers"},
    {"fingers": 10, "name": "B", "sargam": "Ni", "semitone": 11, "hint": "10 fingers"},
]

UPPER_SA = {
    "fingers": 12,
    "name": "C",
    "sargam": "Upper Sa",
    "western": "C",
    "semitone": 0,
    "hint": "Right thumb only",
}

# A4 = 440 Hz, C4 = 261.63 Hz (A4 is 9 semitones above C4)
A4_FREQ = 440.0
A4_SEMITONE = 9  # A is the 9th semitone in the octave (0-indexed from C)


def _normalize_note_name(note_name):
    """Resolve both Western and swara names to the matching Western pitch."""
    if note_name is None:
        return None

    key = note_name.strip()
    if not key:
        return None

    # Exact Western-name match.
    for note in NOTES:
        if note["name"].lower() == key.lower():
            return note["name"]

    # Match swara names like "Sa", "Komal Re", "Tivra Ma".
    for swar in SWARS:
        aliases = {
            swar["name"],
            swar["sargam"],
            swar["western"],
        }
        if key.lower() in {value.lower() for value in aliases}:
            return swar["western"]

    return key


def get_frequency(note_name, octave=4):
    """Get frequency in Hz for a note name and octave."""
    resolved_name = _normalize_note_name(note_name)
    if resolved_name is None:
        return 0.0

    for note in NOTES:
        if note["name"] == resolved_name:
            distance = (octave - 4) * 12 + note["semitone"] - A4_SEMITONE
            return A4_FREQ * (2 ** (distance / 12.0))
    return 0.0


def get_note_for_fingers(finger_count):
    """Map a finger count (0-10) to a swara dict."""
    if finger_count < 0:
        return None
    if finger_count < len(FINGER_NOTES):
        return FINGER_NOTES[finger_count]
    return None


def get_upper_sa():
    """Return the 12th swara, accessed by the right thumb-only gesture."""
    return dict(UPPER_SA)


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
    resolved_name = _normalize_note_name(note_name)
    for i, note in enumerate(NOTES):
        if note["name"] == resolved_name:
            return i
    return -1


def get_wav_filename(note_name, octave=4):
    """Get the wav filename for a note, e.g. 'C4.wav' or 'Csharp4.wav'."""
    resolved_name = _normalize_note_name(note_name)
    safe = resolved_name.replace("#", "sharp")
    return f"{safe}{octave}.wav"
