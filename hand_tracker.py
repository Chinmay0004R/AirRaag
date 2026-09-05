"""Hand Tracker — MediaPipe Tasks API HandLandmarker wrapper."""

import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import config


class HandTracker:
    def __init__(self):
        self._ensure_model()
        base_options = mp_python.BaseOptions(model_asset_path=config.MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def _ensure_model(self):
        """Download model file if missing."""
        if os.path.exists(config.MODEL_PATH):
            return
        os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)
        print(f"Downloading hand_landmarker model...")
        urllib.request.urlretrieve(config.MODEL_URL, config.MODEL_PATH)
        print("Model downloaded.")

    def process(self, frame, timestamp_ms):
        """Detect hand landmarks in a BGR frame.

        Returns list of 21 (x, y) tuples normalized 0–1, or None if no hand.
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.hand_landmarks:
            return None
        hand = result.hand_landmarks[0]
        return [(lm.x, lm.y) for lm in hand]

    def close(self):
        self.landmarker.close()
