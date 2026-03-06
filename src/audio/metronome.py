"""
Métronome avec support des signatures rythmiques impaires.
Génère des clicks avec accent sur le temps 1.
Utilise un OutputStream persistant pour cohabiter avec le TapDetector.
"""

import numpy as np
import sounddevice as sd
from threading import Thread, Event
import time
import logging

logger = logging.getLogger('rhythm-trainer.metronome')


class Metronome:
    """Métronome avec accents pour signatures rythmiques variées."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.bpm = 80
        self.time_signature = (4, 4)  # (beats, beat_value)

        self.is_running = False
        self.stop_event = Event()
        self.thread = None
        self.output_stream = None

        # Sons du métronome
        self.click_accent = self._generate_accent_click()    # Beat 1 - son distinct
        self.click_normal = self._generate_normal_click()    # Autres beats

        # Callback pour synchronisation
        self.on_beat_callback = None

        # Mode audio
        self.audio_enabled = True

    def _generate_accent_click(self) -> np.ndarray:
        """Son du beat 1 : 'DING' aigu, court, sec, distinct."""
        duration = 0.035
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Fréquence haute pour se distinguer
        wave = 0.9 * np.sin(2 * np.pi * 1800 * t)

        # Enveloppe ultra-sèche (pas de résonance)
        envelope = np.exp(-t * 120)

        result = wave * envelope
        return np.clip(result, -1.0, 1.0).astype(np.float32)

    def _generate_normal_click(self) -> np.ndarray:
        """Son des autres beats : 'TOC' court, sec, identique partout."""
        duration = 0.025
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Fréquence plus basse
        wave = 0.6 * np.sin(2 * np.pi * 900 * t)

        # Enveloppe ultra-sèche
        envelope = np.exp(-t * 150)

        result = wave * envelope
        return np.clip(result, -1.0, 1.0).astype(np.float32)

    def set_bpm(self, bpm: int):
        """Définit le tempo en BPM."""
        self.bpm = max(30, min(300, bpm))

    def set_time_signature(self, beats: int, beat_value: int):
        """Définit la signature rythmique."""
        self.time_signature = (beats, beat_value)

    def set_audio_enabled(self, enabled: bool):
        """Active/désactive le son du métronome."""
        self.audio_enabled = enabled

    def _build_beat_buffers(self, beat_interval: float):
        """Pré-calcule les buffers complets (click + silence) par beat."""
        beat_samples = int(beat_interval * self.sample_rate)

        accent_buf = np.zeros(beat_samples, dtype=np.float32)
        accent_buf[:len(self.click_accent)] = self.click_accent

        normal_buf = np.zeros(beat_samples, dtype=np.float32)
        normal_buf[:len(self.click_normal)] = self.click_normal

        silence_buf = np.zeros(beat_samples, dtype=np.float32)

        return accent_buf, normal_buf, silence_buf

    def _metronome_loop(self):
        """Boucle principale du métronome. Écrit des buffers complets par beat."""
        beats, beat_value = self.time_signature

        beat_interval = 60.0 / self.bpm
        # Note: on ne divise plus par 2 pour les signatures en /8
        # Le BPM représente directement les temps (croches en /8)

        accent_buf, normal_buf, silence_buf = self._build_beat_buffers(beat_interval)

        current_beat = 0

        while not self.stop_event.is_set():
            # Choisir le buffer : accent (beat 1) ou normal
            if current_beat == 0:
                buf = accent_buf
            else:
                buf = normal_buf

            # Écrire le buffer complet (bloquant = timing naturel)
            if self.audio_enabled and self.output_stream:
                try:
                    self.output_stream.write(buf)
                except Exception as e:
                    logger.error(f"Erreur ecriture beat: {e}")
                    break
            else:
                # Pas d'audio : sleep pour garder le timing
                time.sleep(beat_interval)

            # Notifier via callback
            if self.on_beat_callback:
                self.on_beat_callback(current_beat, time.perf_counter())

            current_beat = (current_beat + 1) % beats

    def start(self):
        """Démarre le métronome avec un OutputStream persistant."""
        if self.is_running:
            return

        # Ouvrir le stream de sortie dédié
        try:
            self.output_stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                latency='low',
            )
            self.output_stream.start()
            logger.info(f"OutputStream ouvert (sr={self.sample_rate}, "
                         f"latence={self.output_stream.latency * 1000:.1f}ms)")
        except Exception as e:
            logger.error(f"Erreur ouverture OutputStream: {e}", exc_info=True)
            self.output_stream = None

        self.stop_event.clear()
        self.is_running = True
        self.thread = Thread(target=self._metronome_loop, daemon=True)
        self.thread.start()

        beats, beat_value = self.time_signature
        beat_interval = 60.0 / self.bpm
        # Note: on ne divise plus par 2 pour les signatures en /8
        logger.info(f"Metronome demarre: {self.bpm} BPM, {beats}/{beat_value}, "
                     f"interval={beat_interval:.3f}s, audio_enabled={self.audio_enabled}")

    def stop(self):
        """Arrête le métronome et ferme le stream."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)
        self.is_running = False

        # Fermer le stream de sortie
        if self.output_stream:
            try:
                self.output_stream.stop()
                self.output_stream.close()
            except Exception as e:
                logger.warning(f"Erreur fermeture OutputStream: {e}")
            self.output_stream = None

    def set_on_beat(self, callback):
        """Définit le callback appelé à chaque temps."""
        self.on_beat_callback = callback

    def get_beat_interval(self) -> float:
        """Retourne l'intervalle entre temps en secondes."""
        _, beat_value = self.time_signature
        interval = 60.0 / self.bpm
        # Note: on ne divise plus par 2 pour les signatures en /8
        return interval


class PatternPlayer:
    """Joue un pattern rythmique en audio (mode apprentissage)."""

    def __init__(self, metronome: Metronome):
        self.metronome = metronome
        self.pattern = []  # Liste de positions (0.0 à 1.0 dans la mesure)
        self.is_playing = False

        # Son du pattern
        self.sample_rate = metronome.sample_rate
        self.pattern_click = self._generate_pattern_click()

    def _generate_pattern_click(self) -> np.ndarray:
        """Génère le son du pattern (différent du métronome)."""
        duration = 0.06
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        # Son plus "wood block"
        freq1, freq2 = 1000, 1500
        wave = 0.4 * (np.sin(2 * np.pi * freq1 * t) +
                      0.5 * np.sin(2 * np.pi * freq2 * t))
        envelope = np.exp(-t * 40)

        return (wave * envelope).astype(np.float32)

    def set_pattern(self, pattern: list):
        """Définit le pattern à jouer."""
        self.pattern = sorted(pattern)

    def play_pattern_sound(self):
        """Joue le son du pattern."""
        try:
            sd.play(self.pattern_click, self.sample_rate, blocking=False)
        except Exception as e:
            logger.error(f"Erreur pattern audio: {e}")


if __name__ == "__main__":
    # Test du métronome
    logging.basicConfig(level=logging.DEBUG)
    print("Test métronome 7/8 à 90 BPM pendant 10 secondes...")

    metro = Metronome()
    metro.set_bpm(90)
    metro.set_time_signature(7, 8)
    metro.set_on_beat(lambda beat, t: print(f"Beat {beat + 1}"))

    metro.start()
    time.sleep(10)
    metro.stop()

    print("Terminé")
