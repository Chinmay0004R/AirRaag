import unittest

import note_manager
from gesture_engine import GestureEngine


def make_hand(finger_count):
    if finger_count <= 0:
        return [(0.50, 0.80)] + [(0.50, 0.75)] * 20

    points = [
        (0.50, 0.80),
        (0.58, 0.70),
        (0.62, 0.62),
        (0.64, 0.54),
        (0.70, 0.35),
        (0.65, 0.82),
        (0.67, 0.70),
        (0.68, 0.58),
        (0.70, 0.46),
        (0.56, 0.82),
        (0.56, 0.70),
        (0.56, 0.58),
        (0.56, 0.44),
        (0.46, 0.82),
        (0.45, 0.70),
        (0.44, 0.58),
        (0.43, 0.46),
        (0.36, 0.82),
        (0.35, 0.70),
        (0.34, 0.58),
        (0.33, 0.48),
    ]

    if finger_count < 5:
        closed_mask = {8, 12, 16, 20}
        for idx in list(closed_mask)[:5 - finger_count]:
            points[idx] = (points[idx][0], points[idx][1] + 0.18)

    return points


class TestNoteManager(unittest.TestCase):
    def test_has_twelve_swaras(self):
        self.assertEqual(len(note_manager.SWARS), 12)
        self.assertEqual([swar["name"] for swar in note_manager.SWARS], [
            "Sa", "Komal Re", "Re", "Komal Ga", "Ga", "Ma",
            "Tivra Ma", "Pa", "Komal Dha", "Dha", "Komal Ni", "Ni"
        ])

    def test_frequency_lookup_for_swaras(self):
        self.assertAlmostEqual(note_manager.get_frequency("C", octave=4), 261.63, places=1)
        self.assertAlmostEqual(note_manager.get_frequency("A", octave=4), 440.00, places=1)
        self.assertGreater(note_manager.get_frequency("C", octave=5), note_manager.get_frequency("C", octave=4))

    def test_get_note_for_fingers_handles_zero_to_ten(self):
        self.assertIsNotNone(note_manager.get_note_for_fingers(0))
        self.assertIsNotNone(note_manager.get_note_for_fingers(5))
        self.assertIsNotNone(note_manager.get_note_for_fingers(10))
        self.assertEqual(note_manager.get_note_for_fingers(10)["sargam"], "Ni")

    def test_upper_sa_uses_thumb_only_right_hand(self):
        self.assertEqual(note_manager.get_upper_sa()["sargam"], "Upper Sa")

    def test_two_hands_sum_to_ten_fingers(self):
        engine = GestureEngine()
        left = {"landmarks": make_hand(5), "handedness": "Left"}
        right = {"landmarks": make_hand(5), "handedness": "Right"}

        engine.update([left, right])

        self.assertEqual(engine.finger_count, 10)
        self.assertEqual(engine.current_note["sargam"], "Ni")


if __name__ == "__main__":
    unittest.main()
