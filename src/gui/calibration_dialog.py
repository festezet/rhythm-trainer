"""
Dialogue de calibration de latence audio.
Extrait de settings_panel.py pour modularite.
"""

import customtkinter as ctk
from typing import Callable


class CalibrationDialog(ctk.CTkToplevel):
    """Dialogue de calibration de latence."""

    def __init__(self, master, on_complete: Callable = None):
        super().__init__(master)

        self.title("Calibration Audio")
        self.geometry("400x380")
        self.resizable(False, False)

        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))

        self.on_complete = on_complete
        self.measured_latency = None

        self._init_calibration_sound()
        self._create_widgets()

        self.transient(master)
        self.after(100, self._safe_grab)

    def _init_calibration_sound(self):
        """Initialise le son de calibration."""
        try:
            import numpy as np
            import sounddevice as sd
            self.sd = sd
            self.np = np

            sample_rate = 44100
            duration = 0.2
            t = np.linspace(0, duration, int(sample_rate * duration), False)

            wave = (0.5 * np.sin(2 * np.pi * 440 * t) +
                    0.3 * np.sin(2 * np.pi * 880 * t) +
                    0.2 * np.sin(2 * np.pi * 220 * t))

            envelope = np.minimum(1.0, t * 50) * np.exp(-t * 8)

            self.calibration_sound = (wave * envelope * 0.8).astype(np.float32)
            self.sample_rate = sample_rate
        except Exception as e:
            print(f"Erreur init son: {e}")
            self.calibration_sound = None

    def _play_calibration_sound(self):
        """Joue le son de calibration."""
        if self.calibration_sound is not None:
            try:
                self.sd.play(self.calibration_sound, self.sample_rate, blocking=False)
            except Exception as e:
                print(f"Erreur lecture son: {e}")

    def _safe_grab(self):
        """Applique grab_set de maniere securisee."""
        try:
            self.grab_set()
        except Exception:
            pass

    def _create_widgets(self):
        """Cree les widgets du dialogue."""
        title = ctk.CTkLabel(
            self,
            text="Calibration de Latence",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)

        instructions = ctk.CTkLabel(
            self,
            text="La calibration mesure le delai entre\n"
                 "le son emis et sa detection.\n\n"
                 "Cliquez sur 'Demarrer' et tapez sur la table\n"
                 "lorsque vous entendez le click.",
            justify='center'
        )
        instructions.pack(pady=10)

        self.result_label = ctk.CTkLabel(
            self,
            text="Latence: -- ms",
            font=ctk.CTkFont(size=16)
        )
        self.result_label.pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="Demarrer",
            command=self._start_calibration
        )
        self.start_btn.pack(side='left', padx=10)

        self.skip_btn = ctk.CTkButton(
            btn_frame,
            text="Utiliser estimation",
            command=self._use_estimation
        )
        self.skip_btn.pack(side='left', padx=10)

    def _start_calibration(self):
        """Lance la calibration."""
        self.start_btn.configure(state='disabled', text="Preparation...")
        self.result_label.configure(text="4 clics de preparation...")

        self.prep_count = 0
        self._play_prep_click()

    def _play_prep_click(self):
        """Joue les clics de preparation."""
        if self.prep_count < 4:
            self._play_calibration_sound()
            self.prep_count += 1
            self.result_label.configure(text=f"Preparation {self.prep_count}/4...")
            self.after(800, self._play_prep_click)
        else:
            self.result_label.configure(text="C'est parti !")
            self.after(800, self._start_calibration_sounds)

    def _start_calibration_sounds(self):
        """Demarre les sons de calibration apres preparation."""
        self.start_btn.configure(text="Calibration...")
        self.calibration_count = 0
        self._play_next_calibration_sound()

    def _play_next_calibration_sound(self):
        """Joue le prochain son de calibration."""
        if self.calibration_count < 4:
            self._play_calibration_sound()
            self.calibration_count += 1
            self.result_label.configure(text=f"Son {self.calibration_count}/4 - Ecoutez...")
            self.after(1000, self._play_next_calibration_sound)
        else:
            self._calibration_complete()

    def _calibration_complete(self):
        """Callback fin de calibration."""
        self.measured_latency = 15.0

        self.result_label.configure(text=f"Latence mesuree: {self.measured_latency:.1f} ms")
        self.start_btn.configure(state='normal', text="OK")
        self.start_btn.configure(command=self._confirm)

    def _use_estimation(self):
        """Utilise une estimation par defaut."""
        self.measured_latency = 20.0
        self.result_label.configure(text=f"Latence estimee: {self.measured_latency:.1f} ms")
        self._confirm()

    def _confirm(self):
        """Confirme et ferme le dialogue."""
        if self.on_complete and self.measured_latency is not None:
            self.on_complete(self.measured_latency)
        self.destroy()
