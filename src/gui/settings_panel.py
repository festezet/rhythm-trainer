"""
Panneau de configuration pour les exercices.
Permet de choisir signature, pattern, tempo, mode audio, microphone.
"""

import customtkinter as ctk
from typing import Callable, Dict, List
import sys
from pathlib import Path

# Import du module audio pour lister les périphériques
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from src.audio.tap_detector import get_input_devices
except ImportError:
    def get_input_devices():
        return []

# Re-export pour compatibilite avec les imports existants
from src.gui.calibration_dialog import CalibrationDialog  # noqa: F401


class SettingsPanel(ctk.CTkFrame):
    """Panneau de configuration des exercices."""

    def __init__(self, master, on_settings_changed: Callable = None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_settings_changed = on_settings_changed

        # Configuration actuelle
        self.current_settings = {
            'signature': '4/4',
            'pattern_id': None,
            'bpm': 80,
            'audio_mode': 'metronome',  # metronome, pattern, silent
            'num_measures': 4,
            'input_device_id': None,  # None = défaut système
            'latency_ms': 0  # 0 = auto, sinon valeur manuelle en ms
        }

        # Mapping nom → id pour les patterns
        self._pattern_name_to_id = {}

        # Liste des périphériques
        self.input_devices = []  # [(id, name), ...]

        self._create_widgets()

    def _create_widgets(self):
        """Cree les widgets du panneau (dispatcher)."""
        ctk.CTkLabel(
            self,
            text="Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 15))

        self._create_microphone_section()
        self._create_signature_section()
        self._create_pattern_section()
        self._create_tempo_section()
        self._create_sensitivity_section()
        self._create_latency_section()
        self._create_audio_mode_section()
        self._create_measures_section()
        self._create_stats_section()

    def _create_microphone_section(self):
        """Cree la section microphone."""
        mic_frame = ctk.CTkFrame(self, fg_color="transparent")
        mic_frame.pack(fill='x', padx=15, pady=5)

        ctk.CTkLabel(mic_frame, text="Micro:").pack(side='left')

        self.mic_var = ctk.StringVar(value='Defaut systeme')
        self.mic_menu = ctk.CTkOptionMenu(
            mic_frame,
            values=['Defaut systeme'],
            variable=self.mic_var,
            command=self._on_mic_change,
            width=180
        )
        self.mic_menu.pack(side='right')

        self.refresh_btn = ctk.CTkButton(
            mic_frame,
            text="[R]",
            command=self._refresh_devices,
            width=30,
            height=28
        )
        self.refresh_btn.pack(side='right', padx=5)

        self._refresh_devices()

    def _create_signature_section(self):
        """Cree la section signature rythmique."""
        sig_frame = ctk.CTkFrame(self, fg_color="transparent")
        sig_frame.pack(fill='x', padx=15, pady=5)

        ctk.CTkLabel(sig_frame, text="Signature:").pack(side='left')

        self.signature_var = ctk.StringVar(value='4/4')
        self.signature_menu = ctk.CTkOptionMenu(
            sig_frame,
            values=['3/4', '4/4', '5/4', '7/4', '5/8', '7/8', '9/8'],
            variable=self.signature_var,
            command=self._on_signature_change,
            width=100
        )
        self.signature_menu.pack(side='right')

    def _create_pattern_section(self):
        """Cree la section pattern."""
        pattern_frame = ctk.CTkFrame(self, fg_color="transparent")
        pattern_frame.pack(fill='x', padx=15, pady=5)

        ctk.CTkLabel(pattern_frame, text="Pattern:").pack(side='left')

        self.pattern_var = ctk.StringVar(value='')
        self.pattern_menu = ctk.CTkOptionMenu(
            pattern_frame,
            values=[''],
            variable=self.pattern_var,
            command=self._on_pattern_change,
            width=180,
            font=ctk.CTkFont(size=11)
        )
        self.pattern_menu.pack(side='right')

    def _create_tempo_section(self):
        """Cree la section tempo."""
        tempo_frame = ctk.CTkFrame(self, fg_color="transparent")
        tempo_frame.pack(fill='x', padx=15, pady=10)

        ctk.CTkLabel(tempo_frame, text="Tempo:").pack(side='left')

        self.bpm_label = ctk.CTkLabel(tempo_frame, text="80 BPM", width=70)
        self.bpm_label.pack(side='right')

        self.bpm_slider = ctk.CTkSlider(
            tempo_frame,
            from_=40,
            to=180,
            number_of_steps=140,
            command=self._on_bpm_change,
            width=150
        )
        self.bpm_slider.set(80)
        self.bpm_slider.pack(side='right', padx=10)

    def _create_sensitivity_section(self):
        """Cree la section sensibilite micro."""
        sens_frame = ctk.CTkFrame(self, fg_color="transparent")
        sens_frame.pack(fill='x', padx=15, pady=5)

        ctk.CTkLabel(sens_frame, text="Sensibilite micro:").pack(side='left')

        self.threshold_label = ctk.CTkLabel(sens_frame, text="0.020", width=50)
        self.threshold_label.pack(side='right')

        self.threshold_slider = ctk.CTkSlider(
            sens_frame,
            from_=0.005,
            to=0.2,
            number_of_steps=39,
            command=self._on_threshold_change,
            width=130
        )
        self.threshold_slider.set(0.02)
        self.threshold_slider.pack(side='right', padx=10)

        ctk.CTkLabel(
            self,
            text="Regle le seuil de detection du micro\n"
                 "Valeur basse = plus sensible (sons faibles)\n"
                 "Valeur haute = moins sensible (sons forts uniquement)",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60"),
            justify='left'
        ).pack(fill='x', padx=20, pady=(0, 10))

    def _create_latency_section(self):
        """Cree la section latence manuelle."""
        latency_frame = ctk.CTkFrame(self, fg_color="transparent")
        latency_frame.pack(fill='x', padx=15, pady=5)

        ctk.CTkLabel(latency_frame, text="Latence (ms):").pack(side='left')

        self.latency_entry = ctk.CTkEntry(
            latency_frame,
            width=80,
            placeholder_text="Auto"
        )
        self.latency_entry.pack(side='right')
        self.latency_entry.bind('<Return>', lambda e: self._on_latency_change())
        self.latency_entry.bind('<FocusOut>', lambda e: self._on_latency_change())

        ctk.CTkLabel(
            latency_frame,
            text="(0=auto)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side='right', padx=5)

    def _create_audio_mode_section(self):
        """Cree la section mode audio."""
        audio_frame = ctk.CTkFrame(self, fg_color="transparent")
        audio_frame.pack(fill='x', padx=15, pady=10)

        ctk.CTkLabel(audio_frame, text="Audio:").pack(anchor='w')

        self.audio_var = ctk.StringVar(value='metronome')

        modes = [
            ('metronome', 'Metronome seul'),
            ('pattern', 'Metronome + Pattern'),
            ('silent', 'Silencieux')
        ]

        for value, text in modes:
            ctk.CTkRadioButton(
                audio_frame,
                text=text,
                variable=self.audio_var,
                value=value,
                command=self._on_audio_change
            ).pack(anchor='w', pady=2)

    def _create_measures_section(self):
        """Cree la section nombre de mesures."""
        measures_frame = ctk.CTkFrame(self, fg_color="transparent")
        measures_frame.pack(fill='x', padx=15, pady=10)

        ctk.CTkLabel(measures_frame, text="Mesures:").pack(side='left')

        self.measures_var = ctk.StringVar(value='4')
        self.measures_menu = ctk.CTkOptionMenu(
            measures_frame,
            values=['2', '4', '8'],
            variable=self.measures_var,
            command=self._on_measures_change,
            width=80
        )
        self.measures_menu.pack(side='right')

    def _create_stats_section(self):
        """Cree la section statistiques rapides."""
        ctk.CTkFrame(self, height=2, fg_color=("gray70", "gray30")).pack(
            fill='x', padx=15, pady=15
        )

        ctk.CTkLabel(
            self,
            text="Stats de session",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 10))

        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill='x', padx=15)

        self.session_count_label = ctk.CTkLabel(
            self.stats_frame, text="Exercices: 0"
        )
        self.session_count_label.pack(anchor='w')

        self.best_score_label = ctk.CTkLabel(
            self.stats_frame, text="Meilleur score: --"
        )
        self.best_score_label.pack(anchor='w')

        self.avg_deviation_label = ctk.CTkLabel(
            self.stats_frame, text="Decalage moyen: --"
        )
        self.avg_deviation_label.pack(anchor='w')

    def _on_signature_change(self, value):
        """Callback changement de signature."""
        self.current_settings['signature'] = value
        self._notify_change()

    def _on_pattern_change(self, value):
        """Callback changement de pattern."""
        # Résoudre le nom affiché vers l'ID réel
        self.current_settings['pattern_id'] = self._pattern_name_to_id.get(value, value)
        self._notify_change()

    def _on_threshold_change(self, value):
        """Callback changement de sensibilité micro."""
        threshold = round(float(value), 3)
        self.current_settings['threshold'] = threshold
        self.threshold_label.configure(text=f"{threshold:.3f}")
        self._notify_change()

    def _on_latency_change(self):
        """Callback changement de latence manuelle."""
        try:
            value_str = self.latency_entry.get().strip()
            if not value_str or value_str == "0":
                # Mode auto
                self.current_settings['latency_ms'] = 0
                self.latency_entry.delete(0, 'end')
            else:
                # Valeur manuelle
                latency = float(value_str)
                if latency < 0:
                    latency = 0
                elif latency > 1000:
                    latency = 1000
                self.current_settings['latency_ms'] = latency
                self.latency_entry.delete(0, 'end')
                self.latency_entry.insert(0, f"{latency:.1f}")
            self._notify_change()
        except ValueError:
            # Valeur invalide, restaurer la valeur précédente
            self.latency_entry.delete(0, 'end')
            if self.current_settings['latency_ms'] > 0:
                self.latency_entry.insert(0, f"{self.current_settings['latency_ms']:.1f}")

    def _on_bpm_change(self, value):
        """Callback changement de tempo."""
        bpm = int(value)
        self.current_settings['bpm'] = bpm
        self.bpm_label.configure(text=f"{bpm} BPM")
        self._notify_change()

    def _on_audio_change(self):
        """Callback changement de mode audio."""
        self.current_settings['audio_mode'] = self.audio_var.get()
        self._notify_change()

    def _on_measures_change(self, value):
        """Callback changement du nombre de mesures."""
        self.current_settings['num_measures'] = int(value)
        self._notify_change()

    def _on_mic_change(self, value):
        """Callback changement de microphone."""
        if value == 'Defaut systeme':
            self.current_settings['input_device_id'] = None
        else:
            # Trouver l'ID correspondant au nom
            for device_id, device_name in self.input_devices:
                if device_name == value or value.startswith(device_name[:30]):
                    self.current_settings['input_device_id'] = device_id
                    break
        self._notify_change()

    def _refresh_devices(self):
        """Rafraîchit la liste des périphériques audio."""
        try:
            self.input_devices = get_input_devices()
        except Exception as e:
            print(f"Erreur liste périphériques: {e}")
            self.input_devices = []

        # Construire la liste pour le menu
        device_names = ['Defaut systeme']
        for device_id, device_name in self.input_devices:
            # Tronquer les noms trop longs
            display_name = device_name[:35] + '...' if len(device_name) > 35 else device_name
            device_names.append(display_name)

        self.mic_menu.configure(values=device_names)

        # Garder la sélection si possible
        current = self.mic_var.get()
        if current not in device_names:
            self.mic_var.set('Defaut systeme')
            self.current_settings['input_device_id'] = None

    def _notify_change(self):
        """Notifie le parent des changements."""
        if self.on_settings_changed:
            self.on_settings_changed(self.current_settings)

    def set_patterns(self, patterns: List[Dict]):
        """Met à jour la liste des patterns disponibles."""
        if not patterns:
            self.pattern_menu.configure(values=['Aucun pattern'])
            self._pattern_name_to_id = {}
            return

        names = [p['name'] for p in patterns]
        self._pattern_name_to_id = {p['name']: p['id'] for p in patterns}
        self.pattern_menu.configure(values=names)

        if names:
            self.pattern_var.set(names[0])
            self.current_settings['pattern_id'] = patterns[0]['id']

    def update_stats(self, session_count: int, best_score: int, avg_deviation: float):
        """Met à jour les statistiques affichées."""
        self.session_count_label.configure(text=f"Exercices: {session_count}")
        self.best_score_label.configure(text=f"Meilleur score: {best_score}")

        sign = "+" if avg_deviation > 0 else ""
        self.avg_deviation_label.configure(
            text=f"Decalage moyen: {sign}{avg_deviation:.1f} ms"
        )

    def get_settings(self) -> Dict:
        """Retourne les paramètres actuels."""
        return self.current_settings.copy()


if __name__ == "__main__":
    # Test
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.title("Test Settings Panel")
    root.geometry("300x600")

    def on_change(settings):
        print(f"Settings changed: {settings}")

    panel = SettingsPanel(root, on_settings_changed=on_change)
    panel.pack(fill='both', expand=True, padx=10, pady=10)

    # Simuler des patterns
    test_patterns = [
        {'id': 'p1', 'name': '5/4 - Noires simples'},
        {'id': 'p2', 'name': '5/4 - Croches'},
    ]
    panel.set_patterns(test_patterns)
    panel.update_stats(5, 82, 12.3)

    root.mainloop()
