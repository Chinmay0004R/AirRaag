"""Gesture Engine — interprets hand landmarks into musical actions.

Uses finger counting for note selection and pinch gesture for play/stop.
"""

import math
from collections import deque
import config
import note_manager


class GestureEngine:
    def __init__(self):
        self.current_note = None   # FINGER_NOTES dict or None
        self.is_pinching = False
        self.pinch_distance = 1.0  # normalized
        self.finger_count = 0

        # Smoothing: keep last N finger counts, only switch when stable
        self._finger_history = deque(maxlen=config.FINGER_SMOOTHING_FRAMES)
        self._stable_fingers = 0

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------
    def update(self, landmarks):
        """Update gesture state from 21 normalized (x,y) landmarks.

        landmarks can be None (no hand detected).
        """
        if landmarks is None:
            self.current_note = None
            self.is_pinching = False
            self.pinch_distance = 1.0
            self.finger_count = 0
            self._finger_history.clear()
            return

        # --- Pinch detection with hysteresis ---
        thumb = landmarks[config.THUMB_TIP]
        index = landmarks[config.INDEX_TIP]
        dx = thumb[0] - index[0]
        dy = thumb[1] - index[1]
        self.pinch_distance = math.sqrt(dx * dx + dy * dy)

        if self.is_pinching:
            # Must exceed the wider "off" threshold to release
            if self.pinch_distance > config.PINCH_THRESHOLD_OFF:
                self.is_pinching = False
        else:
            # Must go below the tighter "on" threshold to start
            if self.pinch_distance < config.PINCH_THRESHOLD_ON:
                self.is_pinching = True

        # --- Finger counting ---
        raw_count = self._count_fingers(landmarks)
        self._finger_history.append(raw_count)

        # Only accept a new finger count when it's been stable for all
        # recent frames (prevents accidental note jumps)
        if len(self._finger_history) == config.FINGER_SMOOTHING_FRAMES:
            if all(f == raw_count for f in self._finger_history):
                self._stable_fingers = raw_count

        self.finger_count = self._stable_fingers
        self.current_note = note_manager.get_note_for_fingers(self.finger_count)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _count_fingers(self, landmarks):
        """Count how many fingers are raised (0-5).

        Thumb: uses angle-based detection (works for both left & right hand).
        Other fingers: tip must be above (lower y) its PIP joint.
        """
        count = 0

        # Thumb — compare tip to IP joint, using wrist→index_mcp as
        # reference direction to determine "open" regardless of hand side
        thumb_tip = landmarks[config.THUMB_TIP]
        thumb_ip = landmarks[config.THUMB_IP]
        wrist = landmarks[config.WRIST]
        index_mcp = landmarks[config.INDEX_MCP]

        # Thumb is "up" if the tip is farther from the palm center than
        # the IP joint. We measure horizontal distance from the
        # wrist-to-index_mcp line.
        palm_dx = index_mcp[0] - wrist[0]
        # thumb sticks out sideways — measure x-distance from palm axis
        thumb_tip_dist = abs(thumb_tip[0] - wrist[0])
        thumb_ip_dist = abs(thumb_ip[0] - wrist[0])
        if thumb_tip_dist > thumb_ip_dist:
            count += 1

        # Index finger
        if landmarks[config.INDEX_TIP][1] < landmarks[config.INDEX_PIP][1]:
            count += 1

        # Middle finger
        if landmarks[config.MIDDLE_TIP][1] < landmarks[config.MIDDLE_PIP][1]:
            count += 1

        # Ring finger
        if landmarks[config.RING_TIP][1] < landmarks[config.RING_PIP][1]:
            count += 1

        # Pinky finger
        if landmarks[config.PINKY_TIP][1] < landmarks[config.PINKY_PIP][1]:
            count += 1

        return count
