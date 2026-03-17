"""
Fenetre principale de l'application Rhythm Trainer.
Integre tous les composants : timeline, settings, stats.
"""

import customtkinter as ctk
import sys
import logging
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gui.timeline_display import TimelineDisplay
from src.gui.results_overlay import ResultsOverlay
from src.gui.settings_panel import SettingsPanel
from src.gui.calibration_dialog import CalibrationDialog
from src.gui.exercise_controller import ExerciseController
from src.core.rhythm_engine import RhythmEngine
from src.core.precision_analyzer import PrecisionAnalyzer, ProgressTracker
from src.core.progression import ProgressionSystem
from src.audio.tap_detector import TapDetector
from src.audio.metronome import Metronome

logger = logging.getLogger('rhythm-trainer.gui')


class MainWindow(ctk.CTk):
    """Fenetre principale de l'application."""

    def __init__(self):
        super().__init__()

        self.title("Rhythm Trainer - Signatures Impaires")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Chemins
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)

        # Etat de l'exercice
        self.is_exercising = False
        self.exercise_start_time = None
        self.current_pattern = None
        self.expected_times = []
        self._current_signature = None
        self._auto_stop_timer = None
        self._exercise_id = 0

        # Calibration au premier lancement
        self.latency_compensation = 15.0

        # Initialiser les composants
        self._init_core_components()
        self._create_ui()
        self._load_initial_data()

        # Controleur d'exercice (delegue le cycle de vie)
        self.exercise_ctrl = ExerciseController(self)

    def _init_core_components(self):
        """Initialise les composants metier."""
        patterns_file = self.data_dir / 'patterns.json'
        self.rhythm_engine = RhythmEngine(str(patterns_file) if patterns_file.exists() else None)
        self.analyzer = PrecisionAnalyzer(tolerance_ms=50)

        db_path = self.data_dir / 'progress.db'
        self.tracker = ProgressTracker(str(db_path))
        self.progression = ProgressionSystem(str(db_path))

        self.tap_detector = TapDetector(threshold=0.02)
        self.metronome = Metronome()
        logger.info("Composants initialises")

    def _create_ui(self):
        """Cree l'interface utilisateur (dispatcher)."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.settings_panel = SettingsPanel(
            self,
            on_settings_changed=self._on_settings_changed,
            width=280
        )
        self.settings_panel.grid(row=0, column=0, sticky='nsw', padx=10, pady=10)

        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        self._create_timeline(center_frame)
        self._create_controls(center_frame)
        self._create_results_zone(center_frame)
        self._create_calibration_zone(center_frame)

    def _create_timeline(self, parent):
        """Cree la zone timeline."""
        timeline_frame = ctk.CTkFrame(parent)
        timeline_frame.grid(row=0, column=0, sticky='nsew', pady=(10, 5))
        timeline_frame.grid_columnconfigure(0, weight=1)
        timeline_frame.grid_rowconfigure(0, weight=1)

        self.timeline = TimelineDisplay(timeline_frame, width=1050, height=305)
        self.timeline.pack(pady=10, padx=10, fill='both', expand=True)

    def _create_controls(self, parent):
        """Cree les boutons de controle et l'indicateur de tap."""
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.grid(row=1, column=0, pady=20)

        self.start_btn = ctk.CTkButton(
            controls_frame,
            text="Demarrer l'exercice",
            command=self._toggle_exercise,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.start_btn.pack(pady=10)

        self.tap_indicator = ctk.CTkLabel(
            controls_frame,
            text="Pret",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        self.tap_indicator.pack(pady=5)

    def _create_results_zone(self, parent):
        """Cree la zone de resultats (cachee par defaut)."""
        self.results_frame = ctk.CTkFrame(parent)
        self.results_overlay = ResultsOverlay(
            self.results_frame, on_restart=self._restart_exercise
        )
        self.results_overlay.pack(padx=20, pady=20)

    def _create_calibration_zone(self, parent):
        """Cree le bouton calibration et le label latence."""
        calibration_frame = ctk.CTkFrame(parent, fg_color="transparent")
        calibration_frame.grid(row=2, column=0, sticky='s', pady=10)

        self.calibrate_btn = ctk.CTkButton(
            calibration_frame,
            text="Calibrer latence",
            command=self._show_calibration,
            width=120,
            height=30,
            fg_color=("gray70", "gray30")
        )
        self.calibrate_btn.pack()

        self.latency_label = ctk.CTkLabel(
            calibration_frame,
            text=f"Latence: {self.latency_compensation:.0f} ms",
            text_color=("gray50", "gray60")
        )
        self.latency_label.pack(pady=5)

    def _load_initial_data(self):
        """Charge les donnees initiales."""
        self._update_patterns_list('4/4')

    def _update_patterns_list(self, signature: str):
        """Met a jour la liste des patterns pour une signature."""
        sig_tuple = self.rhythm_engine.SIGNATURES.get(signature)
        if not sig_tuple:
            return

        patterns = self.rhythm_engine.get_patterns_by_signature(sig_tuple)
        available = self.progression.get_available_patterns()

        patterns_data = [
            {'id': p.id, 'name': p.name}
            for p in patterns
            if p.id in available or True
        ]

        self.settings_panel.set_patterns(patterns_data)

        if patterns:
            self._set_current_pattern(patterns[0])

    def _set_current_pattern(self, pattern):
        """Definit le pattern actuel."""
        self.current_pattern = pattern
        self.timeline.set_pattern(pattern.hits, pattern.signature)

    def _on_settings_changed(self, settings):
        """Callback quand les settings changent."""
        sig = settings.get('signature')
        if sig and sig != self._current_signature:
            if self.is_exercising:
                self.exercise_ctrl.stop()
            self._current_signature = sig
            self._update_patterns_list(sig)

        bpm = settings.get('bpm', 80)
        self.metronome.set_bpm(bpm)

        pattern_id = settings.get('pattern_id')
        if pattern_id and (not self.current_pattern or self.current_pattern.id != pattern_id):
            pattern = self.rhythm_engine.get_pattern(pattern_id)
            if pattern:
                self._set_current_pattern(pattern)
                logger.info(f"Pattern change: {pattern.id} ({pattern.name})")

        self._apply_audio_settings(settings)

    def _apply_audio_settings(self, settings):
        """Applique les settings audio, micro, latence et mesures."""
        audio_mode = settings.get('audio_mode', 'metronome')
        self.metronome.set_audio_enabled(audio_mode != 'silent')

        device_id = settings.get('input_device_id')
        if self.tap_detector.device_id != device_id:
            self.tap_detector.set_device(device_id)

        threshold = settings.get('threshold')
        if threshold is not None:
            self.tap_detector.set_threshold(threshold)

        latency_ms = settings.get('latency_ms', 0)
        if latency_ms > 0:
            self.latency_compensation = latency_ms
            self.latency_label.configure(text=f"Latence: {latency_ms:.0f} ms (manuel)")
            self.tap_detector.set_latency_compensation(latency_ms)

        num_measures = settings.get('num_measures', 4)
        if self.timeline.num_measures != num_measures:
            self.timeline.num_measures = num_measures
            if not self.is_exercising:
                self.timeline.draw()

    def _toggle_exercise(self):
        """Demarre ou arrete un exercice."""
        self.exercise_ctrl.toggle()

    def _restart_exercise(self):
        """Relance un exercice (depuis le bouton Recommencer)."""
        self.exercise_ctrl.restart()

    def _show_calibration(self):
        """Affiche le dialogue de calibration."""
        self.results_frame.grid_forget()
        dialog = CalibrationDialog(self, on_complete=self._on_calibration_complete)
        dialog.focus()

    def _on_calibration_complete(self, latency: float):
        """Callback fin de calibration."""
        settings = self.settings_panel.get_settings()
        latency_ms = settings.get('latency_ms', 0)

        if latency_ms == 0:
            self.latency_compensation = latency
            self.latency_label.configure(text=f"Latence: {latency:.0f} ms")
        else:
            self.latency_label.configure(
                text=f"Latence: {latency_ms:.0f} ms (manuel, calibration ignoree)"
            )

        self.results_frame.grid_forget()

    def on_closing(self):
        """Nettoyage a la fermeture."""
        if self.is_exercising:
            self.tap_detector.stop()
            self.metronome.stop()

        self.tracker.backup_database()
        self.destroy()


def main():
    """Point d'entree principal."""
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
