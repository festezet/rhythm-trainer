"""
Calibration de la latence audio.
Mesure le délai entre l'émission d'un son et sa détection.
"""

import numpy as np
import sounddevice as sd
import time
from threading import Event


class LatencyCalibrator:
    """Calibre la latence du système audio."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.measured_latency = None

        # Son de calibration
        self.calibration_click = self._generate_calibration_click()

    def _generate_calibration_click(self) -> np.ndarray:
        """Génère un click fort pour la calibration."""
        duration = 0.02
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)

        wave = 0.9 * np.sin(2 * np.pi * 1000 * t)
        envelope = np.exp(-t * 50)

        return (wave * envelope).astype(np.float32)

    def calibrate(self, num_samples: int = 5, threshold: float = 0.3) -> float:
        """
        Effectue la calibration de latence.

        Le système émet un son et mesure quand il est détecté en entrée.
        Nécessite que le micro capte le son émis (boucle audio).

        Args:
            num_samples: Nombre de mesures à moyenner
            threshold: Seuil de détection

        Returns:
            Latence mesurée en millisecondes
        """
        print("Calibration de latence...")
        print("Assurez-vous que le micro peut capter le son émis.")

        latencies = []

        for i in range(num_samples):
            latency = self._measure_single_latency(threshold)
            if latency is not None:
                latencies.append(latency)
                print(f"  Mesure {i+1}: {latency:.1f} ms")
            else:
                print(f"  Mesure {i+1}: échec (pas de détection)")
            time.sleep(0.5)

        if not latencies:
            print("Calibration échouée - aucune mesure valide")
            return 0.0

        # Moyenne en excluant les valeurs aberrantes
        latencies.sort()
        if len(latencies) >= 3:
            # Exclure min et max
            latencies = latencies[1:-1]

        self.measured_latency = np.mean(latencies)
        print(f"\nLatence mesurée: {self.measured_latency:.1f} ms")

        return self.measured_latency

    def _measure_single_latency(self, threshold: float) -> float:
        """Mesure une seule latence."""
        detected_event = Event()
        detection_time = [None]

        def audio_callback(indata, frames, time_info, status):
            amplitude = np.sqrt(np.mean(indata ** 2))
            if amplitude > threshold and detection_time[0] is None:
                detection_time[0] = time.perf_counter()
                detected_event.set()

        try:
            # Ouvrir le stream d'entrée
            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=64,
                channels=1,
                dtype='float32',
                latency='low',
                callback=audio_callback
            ):
                time.sleep(0.1)  # Laisser le stream se stabiliser

                # Émettre le click et noter le timestamp
                emit_time = time.perf_counter()
                sd.play(self.calibration_click, self.sample_rate, blocking=False)

                # Attendre la détection (timeout 500ms)
                if detected_event.wait(timeout=0.5):
                    latency_ms = (detection_time[0] - emit_time) * 1000
                    return latency_ms

        except Exception as e:
            print(f"Erreur calibration: {e}")

        return None

    def estimate_latency(self) -> float:
        """
        Estime la latence sans mesure réelle.
        Basé sur les paramètres audio typiques.

        Returns:
            Latence estimée en millisecondes
        """
        # Estimation basée sur buffer size typique
        # Input latency + Output latency + Processing

        try:
            # Obtenir les latences par défaut du système
            device_info = sd.query_devices(kind='input')
            input_latency = device_info.get('default_low_input_latency', 0.01)

            device_info = sd.query_devices(kind='output')
            output_latency = device_info.get('default_low_output_latency', 0.01)

            # Total en ms + marge de sécurité
            estimated = (input_latency + output_latency) * 1000 + 5

            print(f"Latence estimée: {estimated:.1f} ms")
            return estimated

        except Exception as e:
            print(f"Erreur estimation: {e}")
            return 20.0  # Valeur par défaut raisonnable

    def get_system_info(self) -> dict:
        """Retourne les infos du système audio."""
        info = {
            'devices': [],
            'default_input': None,
            'default_output': None,
        }

        try:
            devices = sd.query_devices()
            info['devices'] = [
                {'name': d['name'], 'inputs': d['max_input_channels'],
                 'outputs': d['max_output_channels']}
                for d in devices
            ]

            default_input = sd.query_devices(kind='input')
            info['default_input'] = {
                'name': default_input['name'],
                'low_latency': default_input.get('default_low_input_latency', 0) * 1000
            }

            default_output = sd.query_devices(kind='output')
            info['default_output'] = {
                'name': default_output['name'],
                'low_latency': default_output.get('default_low_output_latency', 0) * 1000
            }

        except Exception as e:
            print(f"Erreur info système: {e}")

        return info


if __name__ == "__main__":
    calibrator = LatencyCalibrator()

    print("=== Informations système audio ===")
    info = calibrator.get_system_info()
    print(f"Entrée: {info['default_input']}")
    print(f"Sortie: {info['default_output']}")

    print("\n=== Estimation de latence ===")
    calibrator.estimate_latency()

    print("\n=== Calibration réelle ===")
    print("(Nécessite une boucle audio micro -> haut-parleur)")
    # calibrator.calibrate()
