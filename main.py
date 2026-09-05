"""Air Instrument — main entry point."""

import time
import cv2
import config
from hand_tracker import HandTracker
from gesture_engine import GestureEngine
from audio_engine import AudioEngine
from ui_renderer import UIRenderer


def main():
    cap = cv2.VideoCapture(config.CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    if not cap.isOpened():
        print("Error: Cannot open camera.")
        return

    tracker = HandTracker()
    gesture = GestureEngine()
    audio = AudioEngine()
    ui = UIRenderer()
    instrument = config.DEFAULT_INSTRUMENT
    start_time = time.time()

    print("Air Instrument running. Press Q to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        timestamp_ms = int((time.time() - start_time) * 1000)
        hands = tracker.process(frame, timestamp_ms)
        gesture.update(hands)

        if gesture.current_note:
            audio.play(gesture.current_note["name"])
        else:
            audio.stop()

        display = ui.draw(frame, hands, gesture.current_note,
                          gesture.is_pinching, instrument,
                          finger_count=gesture.finger_count)
        cv2.imshow("Air Music", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            instrument = "harmonium"
            audio.switch_instrument(instrument)
        elif key == ord('2'):
            instrument = "sitar"
            audio.switch_instrument(instrument)

    audio.stop()
    audio.cleanup()
    tracker.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
