"""
Détection des taps audio en temps réel.
Utilise sounddevice pour une latence minimale.
"""

import numpy as np
import sounddevice as sd
from collections import deque
from threading import Lock
import time
import logging

logger = logging.getLogger('rhythm-trainer.tap_detector')


class TapDetector:
    """Détecte les taps (frappes) dans le flux audio en temps réel."""

    def __init__(self,
                 sample_rate: int = 44100,
                 block_size: int = 128,
                 threshold: float = 0.3,
                 min_tap_interval: float = 0.05,
                 device_id: int = None):
        """
        Args:
            sample_rate: Fréquence d'échantillonnage
            block_size: Taille du buffer (plus petit = moins de latence)
            threshold: Seuil de détection (0-1)
            min_tap_interval: Intervalle minimum entre 2 taps (secondes)
            device_id: ID du périphérique audio (None = défaut système)
        """
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.threshold = threshold
        self.min_tap_interval = min_tap_interval
        self.device_id = device_id

        self.stream = None
        self.is_running = False
        self.latency_compensation = 0.0  # ms, défini par calibration

        # Buffer des taps détectés (timestamps)
        self.taps = deque(maxlen=1000)
        self.taps_lock = Lock()

        # Pour éviter les doubles détections
        self.last_tap_time = 0

        # Callback pour notifier les nouveaux taps
        self.on_tap_callback = None

    def set_threshold(self, threshold: float):
        """Ajuste le seuil de détection (0-1)."""
        self.threshold = max(0.01, min(1.0, threshold))

    def set_latency_compensation(self, latency_ms: float):
        """Définit la compensation de latence (depuis calibration)."""
        self.latency_compensation = latency_ms

    def set_device(self, device_id: int):
        """Change le périphérique audio (nécessite restart)."""
        self.device_id = device_id

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback appelé pour chaque bloc audio."""
        if status:
            logger.warning(f"Audio input status: {status}")

        # Calculer l'amplitude RMS
        amplitude = np.sqrt(np.mean(indata ** 2))

        # Détection de pic
        if amplitude > self.threshold:
            current_time = time.perf_counter()

            # Éviter les doubles détections
            if current_time - self.last_tap_time > self.min_tap_interval:
                # Timestamp corrigé de la latence
                tap_time = current_time - (self.latency_compensation / 1000.0)

                with self.taps_lock:
                    self.taps.append(tap_time)

                self.last_tap_time = current_time

                # Notifier via callback
                if self.on_tap_callback:
                    self.on_tap_callback(tap_time)

    def start(self):
        """Démarre la capture audio."""
        if self.is_running:
            return

        try:
            # Utiliser le sample rate natif du périphérique
            actual_sr = self.sample_rate
            try:
                device_info = sd.query_devices(self.device_id, kind='input')
                actual_sr = int(device_info['default_samplerate'])
                if actual_sr != self.sample_rate:
                    logger.info(f"Sample rate ajuste: {self.sample_rate} -> {actual_sr} "
                                f"(natif du peripherique)")
                    self.sample_rate = actual_sr
            except Exception as e:
                logger.warning(f"Impossible de lire le sample rate natif: {e}")

            self.stream = sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=1,
                dtype='float32',
                latency='low',
                callback=self._audio_callback
            )
            self.stream.start()
            self.is_running = True
            device_name = get_device_name(self.device_id) if self.device_id is not None else "defaut"
            logger.info(f"TapDetector demarre sur '{device_name}' "
                        f"(device_id={self.device_id}, "
                        f"latence={self.stream.latency * 1000:.1f}ms, "
                        f"sr={self.sample_rate}, blocksize={self.block_size})")
        except Exception as e:
            logger.error(f"Erreur demarrage TapDetector: {e}", exc_info=True)
            raise

    def stop(self):
        """Arrête la capture audio."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.is_running = False

    def get_taps(self, since: float = None) -> list:
        """
        Retourne les taps détectés.

        Args:
            since: Timestamp minimum (None = tous)

        Returns:
            Liste des timestamps des taps
        """
        with self.taps_lock:
            if since is None:
                return list(self.taps)
            return [t for t in self.taps if t >= since]

    def clear_taps(self):
        """Efface l'historique des taps."""
        with self.taps_lock:
            self.taps.clear()
        self.last_tap_time = 0

    def get_input_latency(self) -> float:
        """Retourne la latence d'entrée en ms."""
        if self.stream:
            return self.stream.latency * 1000
        return 0.0

    def set_on_tap(self, callback):
        """Définit le callback appelé à chaque tap détecté."""
        self.on_tap_callback = callback


def list_audio_devices():
    """Liste les périphériques audio disponibles."""
    print("Périphériques audio disponibles:")
    print(sd.query_devices())
    return sd.query_devices()


def get_input_devices() -> list:
    """
    Retourne la liste des périphériques d'entrée audio.

    Returns:
        Liste de tuples (device_id, device_name)
    """
    devices = sd.query_devices()
    input_devices = []

    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append((i, device['name']))

    return input_devices


def get_device_name(device_id: int) -> str:
    """Retourne le nom d'un périphérique par son ID."""
    try:
        device = sd.query_devices(device_id)
        return device['name']
    except Exception:
        return f"Device {device_id}"


if __name__ == "__main__":
    # Test simple
    print("Test du détecteur de taps")
    print("Tapez sur la table pendant 10 secondes...")

    detector = TapDetector(threshold=0.2)
    detector.set_on_tap(lambda t: print(f"TAP à {t:.3f}"))

    detector.start()
    time.sleep(10)
    detector.stop()

    taps = detector.get_taps()
    print(f"\n{len(taps)} taps détectés")
