"""Audio Engine — Pygame-based low-latency sound playback."""

import os
import pygame
import config
import note_manager


class AudioEngine:
    def __init__(self, instrument=config.DEFAULT_INSTRUMENT):
        pygame.mixer.pre_init(config.SAMPLE_RATE, -16, 2, 512)
        pygame.mixer.init()
        self.sounds = {}
        self.current_instrument = ""
        self.playing_note = None
        self.channel = pygame.mixer.Channel(0)
        self.switch_instrument(instrument)

    def switch_instrument(self, instrument):
        """Load all wav files for the given instrument."""
        if instrument == self.current_instrument:
            return
        self.stop()
        self.sounds.clear()
        self.current_instrument = instrument
        folder = os.path.join(config.AUDIO_DIR, instrument)
        if not os.path.isdir(folder):
            print(f"Warning: audio folder '{folder}' not found")
            return
        for note in note_manager.NOTES:
            filename = note_manager.get_wav_filename(note["name"])
            path = os.path.join(folder, filename)
            if os.path.isfile(path):
                self.sounds[note["name"]] = pygame.mixer.Sound(path)

    def play(self, note_name):
        """Play a note. Avoids re-triggering the same note."""
        if note_name == self.playing_note:
            return
        self.stop()
        sound = self.sounds.get(note_name)
        if sound:
            self.channel.play(sound, loops=-1)
            self.playing_note = note_name

    def stop(self):
        """Stop current playback."""
        if self.playing_note:
            self.channel.stop()
            self.playing_note = None

    def cleanup(self):
        pygame.mixer.quit()
