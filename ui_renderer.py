"""UI Renderer — draws all visual overlays on the camera frame."""

import cv2
import config
import note_manager


class UIRenderer:
    def draw(self, frame, hands, current_note, is_pinching, instrument,
             finger_count=0):
        """Draw all UI elements on the frame. Returns the modified frame."""
        h, w = frame.shape[:2]
        frame = cv2.flip(frame, 1)

        self._draw_header(frame, w, instrument)
        self._draw_note_strip(frame, w, h, current_note, is_pinching, finger_count)
        self._draw_status(frame, w, h, current_note, is_pinching, instrument, finger_count)
        if hands:
            for hand in hands:
                landmarks = hand.get("landmarks") if isinstance(hand, dict) else hand
                if landmarks:
                    self._draw_hand(frame, landmarks, w, h, is_pinching)
        return frame

    def _draw_header(self, frame, w, instrument):
        """Dark header bar with title."""
        cv2.rectangle(frame, (0, 0), (w, config.HEADER_HEIGHT), config.COLOR_HEADER, -1)
        cv2.putText(frame, "AIR MUSIC", (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, config.COLOR_TEXT, 2)
        # Instrument label on right
        label = f"[{instrument.upper()}]"
        sz = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        cv2.putText(frame, label, (w - sz[0] - 15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.COLOR_NOTE_ACTIVE, 2)

    def _draw_note_strip(self, frame, w, h, current_note, is_pinching,
                         finger_count):
        """Bottom strip showing finger-count note cards."""
        strip_y = h - config.NOTE_STRIP_HEIGHT - config.STATUS_HEIGHT
        notes = note_manager.FINGER_NOTES
        num = len(notes)
        col_w = w // num
        pad = 4  # inner padding

        for i, fn in enumerate(notes):
            x1 = i * col_w + pad
            x2 = (i + 1) * col_w - pad
            y1 = strip_y + pad
            y2 = strip_y + config.NOTE_STRIP_HEIGHT - pad

            is_active = current_note and fn["name"] == current_note["name"]

            if is_active and is_pinching:
                bg = config.COLOR_PINCH
            elif is_active:
                bg = config.COLOR_NOTE_ACTIVE
            else:
                bg = config.COLOR_NOTE_INACTIVE

            # Rounded-feel rectangle
            cv2.rectangle(frame, (x1, y1), (x2, y2), bg, -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), config.COLOR_NOTE_BORDER, 1)

            # --- Finger count number (big, top) ---
            fc_text = str(fn["fingers"])
            fc_sz = cv2.getTextSize(fc_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            fc_x = x1 + (x2 - x1 - fc_sz[0]) // 2
            fc_y = y1 + fc_sz[1] + 8
            fc_color = config.COLOR_BG if is_active else config.COLOR_TEXT_DIM
            cv2.putText(frame, fc_text, (fc_x, fc_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, fc_color, 2)

            # --- Sargam label (middle, main) ---
            sar_text = fn["sargam"]
            sar_sz = cv2.getTextSize(sar_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            sar_x = x1 + (x2 - x1 - sar_sz[0]) // 2
            sar_y = fc_y + sar_sz[1] + 10
            sar_color = config.COLOR_BG if is_active else config.COLOR_TEXT
            cv2.putText(frame, sar_text, (sar_x, sar_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, sar_color, 2)

            # --- Western name (bottom, small) ---
            west_text = fn["name"]
            west_sz = cv2.getTextSize(west_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
            west_x = x1 + (x2 - x1 - west_sz[0]) // 2
            west_y = sar_y + west_sz[1] + 8
            west_color = config.COLOR_BG if is_active else config.COLOR_TEXT_DIM
            cv2.putText(frame, west_text, (west_x, west_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, west_color, 1)

    def _draw_status(self, frame, w, h, current_note, is_pinching, instrument,
                     finger_count):
        """Bottom status bar: note, finger count, state, controls."""
        y = h - config.STATUS_HEIGHT
        cv2.rectangle(frame, (0, y), (w, h), config.COLOR_HEADER, -1)

        note_text = current_note["sargam"] if current_note else "---"
        state = "PLAYING" if (is_pinching and current_note) else "READY"
        info = (f"FINGERS: {finger_count}   |   NOTE: {note_text}   |   "
                f"{state}   |   1=Harmonium  2=Sitar  Q=Quit")

        cv2.putText(frame, info, (15, y + 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, config.COLOR_TEXT, 1)

    def _draw_hand(self, frame, landmarks, w, h, is_pinching):
        """Draw hand skeleton and finger tips."""
        points = [(int((1.0 - lm[0]) * w), int(lm[1] * h)) for lm in landmarks]

        # Connections
        for a, b in config.HAND_CONNECTIONS:
            if a < len(points) and b < len(points):
                cv2.line(frame, points[a], points[b], config.COLOR_SKELETON, 2)

        # Joints
        for i, pt in enumerate(points):
            radius = 6 if i in (config.THUMB_TIP, config.INDEX_TIP) else 3
            color = config.COLOR_PINCH if (is_pinching and i in (config.THUMB_TIP, config.INDEX_TIP)) else config.COLOR_JOINT
            cv2.circle(frame, pt, radius, color, -1)

        # Pinch line
        if is_pinching:
            cv2.line(frame, points[config.THUMB_TIP], points[config.INDEX_TIP], config.COLOR_PINCH, 3)
