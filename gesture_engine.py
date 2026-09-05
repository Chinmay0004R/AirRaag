"""Gesture Engine — interprets hand landmarks into musical actions.

The app now tracks both hands so 0–10 visible fingers map to the 11 basic swaras.
A right-thumb-only gesture triggers the 12th swara: Upper Sa.
"""

import math
from collections import deque
import config
import note_manager


class GestureEngine:
    def __init__(self):
        self.current_note = None
        self.is_pinching = False
        self.pinch_distance = 1.0
        self.finger_count = 0
        self._finger_history = deque(maxlen=config.FINGER_SMOOTHING_FRAMES)
        self._stable_fingers = 0
        self._right_thumb_only = False

    def update(self, hands):
        """Update gesture state from one or two hands.

        The current app provides either a single hand or a list of hands.
        """
        if hands is None or (isinstance(hands, list) and len(hands) == 0):
            self.current_note = None
            self.is_pinching = False
            self.pinch_distance = 1.0
            self.finger_count = 0
            self._right_thumb_only = False
            self._finger_history.clear()
            return

        if isinstance(hands, dict):
            hand_entries = [hands]
        elif isinstance(hands, list) and hands and isinstance(hands[0], tuple):
            hand_entries = [{"landmarks": hands, "handedness": "Right"}]
        else:
            hand_entries = list(hands)

        hand_list = []
        for entry in hand_entries:
            if isinstance(entry, dict):
                landmarks = entry.get("landmarks")
                handedness = entry.get("handedness")
            else:
                landmarks = entry
                handedness = None
            if landmarks is not None:
                hand_list.append((landmarks, handedness))

        if not hand_list:
            self.current_note = None
            self.is_pinching = False
            self.pinch_distance = 1.0
            self.finger_count = 0
            self._right_thumb_only = False
            self._finger_history.clear()
            return

        # Upper Sa has priority over normal finger counting.
        for landmarks, handedness in hand_list:
            if handedness and handedness.lower() == "right" and self._is_right_thumb_only(landmarks):
                self._right_thumb_only = True
                break

        # Normal notes use the total number of raised fingers across both hands.
        raw_count = min(sum(self._count_fingers(landmarks) for landmarks, _ in hand_list), 10)
        self._finger_history.append(raw_count)
        if len(self._finger_history) == config.FINGER_SMOOTHING_FRAMES:
            if all(f == raw_count for f in self._finger_history):
                self._stable_fingers = raw_count

        self.finger_count = self._stable_fingers if len(self._finger_history) == config.FINGER_SMOOTHING_FRAMES else raw_count
        self.is_pinching = self._right_thumb_only
        self.pinch_distance = 0.0

        if self._right_thumb_only:
            self.current_note = note_manager.get_upper_sa()
        elif self.finger_count <= 10:
            self.current_note = note_manager.get_note_for_fingers(self.finger_count)
        else:
            self.current_note = None

    def _count_fingers(self, landmarks):
        """Count how many fingers are raised in one hand (0-5)."""
        count = 0
        thumb_tip = landmarks[config.THUMB_TIP]
        thumb_ip = landmarks[config.THUMB_IP]
        wrist = landmarks[config.WRIST]

        thumb_tip_dist = abs(thumb_tip[0] - wrist[0])
        thumb_ip_dist = abs(thumb_ip[0] - wrist[0])
        if thumb_tip_dist > thumb_ip_dist:
            count += 1

        if landmarks[config.INDEX_TIP][1] < landmarks[config.INDEX_PIP][1]:
            count += 1
        if landmarks[config.MIDDLE_TIP][1] < landmarks[config.MIDDLE_PIP][1]:
            count += 1
        if landmarks[config.RING_TIP][1] < landmarks[config.RING_PIP][1]:
            count += 1
        if landmarks[config.PINKY_TIP][1] < landmarks[config.PINKY_PIP][1]:
            count += 1

        return count

    def _is_right_thumb_only(self, landmarks):
        """Detect the special Upper Sa gesture: right thumb up, all other fingers closed."""
        thumb_tip = landmarks[config.THUMB_TIP]
        thumb_ip = landmarks[config.THUMB_IP]
        wrist = landmarks[config.WRIST]
        thumb_extended = abs(thumb_tip[0] - wrist[0]) > abs(thumb_ip[0] - wrist[0]) + 0.02

        index_closed = landmarks[config.INDEX_TIP][1] > landmarks[config.INDEX_PIP][1]
        middle_closed = landmarks[config.MIDDLE_TIP][1] > landmarks[config.MIDDLE_PIP][1]
        ring_closed = landmarks[config.RING_TIP][1] > landmarks[config.RING_PIP][1]
        pinky_closed = landmarks[config.PINKY_TIP][1] > landmarks[config.PINKY_PIP][1]

        return thumb_extended and index_closed and middle_closed and ring_closed and pinky_closed
