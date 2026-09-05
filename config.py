"""All constants for Air Instrument."""

# Camera
CAM_INDEX = 0
CAM_WIDTH = 1280
CAM_HEIGHT = 720

# MediaPipe model
MODEL_PATH = "models/hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

# Landmark indices
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
WRIST = 0

# Hand skeleton connections for drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),       # index
    (0, 9), (9, 10), (10, 11), (11, 12),   # middle
    (0, 13), (13, 14), (14, 15), (15, 16), # ring
    (0, 17), (17, 18), (18, 19), (19, 20), # pinky
    (5, 9), (9, 13), (13, 17),             # palm
]

# Finger landmark PIP joints (used for finger-up detection)
INDEX_PIP = 6
MIDDLE_PIP = 10
RING_PIP = 14
PINKY_PIP = 18
INDEX_MCP = 5
THUMB_IP = 3

# Gesture thresholds
PINCH_THRESHOLD_ON = 0.045   # distance to START pinch (tighter)
PINCH_THRESHOLD_OFF = 0.065  # distance to RELEASE pinch (wider = hysteresis)
FINGER_SMOOTHING_FRAMES = 4  # frames a finger count must be stable before switching

# Audio
SAMPLE_RATE = 44100
SAMPLE_DURATION = 2.0  # seconds per note
AUDIO_DIR = "audio"
DEFAULT_INSTRUMENT = "harmonium"
INSTRUMENTS = ["harmonium", "sitar"]

# UI Colors (BGR for OpenCV)
COLOR_BG = (24, 28, 32)
COLOR_HEADER = (29, 36, 42)
COLOR_HEADER_EDGE = (64, 172, 211)
COLOR_NOTE_INACTIVE = (39, 47, 53)
COLOR_NOTE_ACTIVE = (65, 205, 34)
COLOR_NOTE_BORDER = (82, 96, 105)
COLOR_TEXT = (239, 244, 246)
COLOR_TEXT_DIM = (156, 171, 179)
COLOR_SKELETON = (31, 193, 232)
COLOR_JOINT = (245, 250, 252)
COLOR_PINCH = (35, 235, 154)
COLOR_FINGERTIP = (41, 198, 242)
COLOR_ACCENT = (65, 205, 34)
COLOR_WARNING = (45, 187, 248)

# UI Layout
HEADER_HEIGHT = 62
NOTE_STRIP_HEIGHT = 126
STATUS_HEIGHT = 68
