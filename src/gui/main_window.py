"""
Fenêtre principale de l'application Rhythm Trainer.
Intègre tous les composants : timeline, settings, stats.
"""

import customtkinter as ctk
import tkinter as tk
import sys
import os
import time
import traceback
import logging
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gui.timeline_display import TimelineDisplay, ResultsOverlay
from src.gui.settings_panel import SettingsPanel, CalibrationDialog
from src.core.rhythm_engine import RhythmEngine
from src.core.precision_analyzer import PrecisionAnalyzer, ProgressTracker
from src.core.progression import ProgressionSystem
from src.audio.tap_detector import TapDetector
from src.audio.metronome import Metronome

logger = logging.getLogger('rhythm-trainer.gui')


class MainWindow(ctk.CTk):
    """Fenêtre principale de l'application."""

    def __init__(self):
        super().__init__()

        self.title("Rhythm Trainer - Signatures Impaires")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Chemins
        self.data_dir = Path(__file__).parent.parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)

        # État de l'exercice
        self.is_exercising = False
        self.exercise_start_time = None
        self.current_pattern = None
        self.expected_times = []
        self._current_signature = None  # Pour détecter les vrais changements
        self._auto_stop_timer = None    # ID du timer auto-stop
        self._exercise_id = 0           # Compteur pour invalider les anciens timers

        # Calibration au premier lancement
        self.latency_compensation = 15.0  # Valeur par défaut

        # Initialiser les composants
        self._init_core_components()
        self._create_ui()
        self._load_initial_data()

    def _init_core_components(self):
        """Initialise les composants métier."""
        # Moteur de patterns
        patterns_file = self.data_dir / 'patterns.json'
        self.rhythm_engine = RhythmEngine(str(patterns_file) if patterns_file.exists() else None)

        # Analyseur de précision
        self.analyzer = PrecisionAnalyzer(tolerance_ms=50)

        # Tracker de progression
        db_path = self.data_dir / 'progress.db'
        self.tracker = ProgressTracker(str(db_path))

        # Système de progression
        self.progression = ProgressionSystem(str(db_path))

        # Audio (créés mais pas démarrés)
        self.tap_detector = TapDetector(threshold=0.02)
        self.metronome = Metronome()
        logger.info("Composants initialises")

    def _create_ui(self):
        """Crée l'interface utilisateur."""
        # Layout principal: gauche (settings) | centre (timeline)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === Panneau gauche: Settings ===
        self.settings_panel = SettingsPanel(
            self,
            on_settings_changed=self._on_settings_changed,
            width=280
        )
        self.settings_panel.grid(row=0, column=0, sticky='nsw', padx=10, pady=10)

        # === Zone centrale ===
        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        # Timeline (pleine largeur)
        timeline_frame = ctk.CTkFrame(center_frame)
        timeline_frame.grid(row=0, column=0, sticky='nsew', pady=(10, 5))
        timeline_frame.grid_columnconfigure(0, weight=1)
        timeline_frame.grid_rowconfigure(0, weight=1)

        self.timeline = TimelineDisplay(timeline_frame, width=1050, height=305)
        self.timeline.pack(pady=10, padx=10, fill='both', expand=True)

        # Boutons de contrôle
        controls_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
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

        # Indicateur de tap
        self.tap_indicator = ctk.CTkLabel(
            controls_frame,
            text="Pret",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray60")
        )
        self.tap_indicator.pack(pady=5)

        # Zone de résultats (cachée par défaut)
        self.results_frame = ctk.CTkFrame(center_frame)
        self.results_overlay = ResultsOverlay(self.results_frame, on_restart=self._restart_exercise)
        self.results_overlay.pack(padx=20, pady=20)

        # Bouton calibration
        calibration_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
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
        """Charge les données initiales."""
        # Charger les patterns pour la signature par défaut
        self._update_patterns_list('4/4')

    def _update_patterns_list(self, signature: str):
        """Met à jour la liste des patterns pour une signature."""
        sig_tuple = self.rhythm_engine.SIGNATURES.get(signature)
        if not sig_tuple:
            return

        patterns = self.rhythm_engine.get_patterns_by_signature(sig_tuple)
        available = self.progression.get_available_patterns()

        # Filtrer par patterns débloqués
        patterns_data = [
            {'id': p.id, 'name': p.name}
            for p in patterns
            if p.id in available or True  # Pour le moment, tous accessibles
        ]

        self.settings_panel.set_patterns(patterns_data)

        # Mettre à jour la timeline avec le premier pattern
        if patterns:
            self._set_current_pattern(patterns[0])

    def _set_current_pattern(self, pattern):
        """Définit le pattern actuel."""
        self.current_pattern = pattern
        self.timeline.set_pattern(pattern.hits, pattern.signature)

    def _on_settings_changed(self, settings):
        """Callback quand les settings changent."""
        # Mise à jour signature (seulement si elle change vraiment)
        sig = settings.get('signature')
        if sig and sig != self._current_signature:
            # Stopper l'exercice en cours si on change de signature
            if self.is_exercising:
                self._stop_exercise()
            self._current_signature = sig
            self._update_patterns_list(sig)

        # Mise à jour tempo
        bpm = settings.get('bpm', 80)
        self.metronome.set_bpm(bpm)

        # Mise à jour pattern sélectionné
        pattern_id = settings.get('pattern_id')
        if pattern_id and (not self.current_pattern or self.current_pattern.id != pattern_id):
            pattern = self.rhythm_engine.get_pattern(pattern_id)
            if pattern:
                self._set_current_pattern(pattern)
                logger.info(f"Pattern change: {pattern.id} ({pattern.name})")

        # Mise à jour mode audio
        audio_mode = settings.get('audio_mode', 'metronome')
        self.metronome.set_audio_enabled(audio_mode != 'silent')

        # Mise à jour périphérique audio (micro)
        device_id = settings.get('input_device_id')
        if self.tap_detector.device_id != device_id:
            self.tap_detector.set_device(device_id)

        # Mise à jour sensibilité micro
        threshold = settings.get('threshold')
        if threshold is not None:
            self.tap_detector.set_threshold(threshold)

        # Mise à jour latence manuelle
        latency_ms = settings.get('latency_ms', 0)
        if latency_ms > 0:
            # Mode manuel : utiliser la latence spécifiée
            self.latency_compensation = latency_ms
            self.latency_label.configure(text=f"Latence: {latency_ms:.0f} ms (manuel)")
            self.tap_detector.set_latency_compensation(latency_ms)
        # Sinon mode auto, la latence sera mise à jour par la calibration

        # Mise à jour nombre de mesures
        num_measures = settings.get('num_measures', 4)
        if self.timeline.num_measures != num_measures:
            self.timeline.num_measures = num_measures
            if not self.is_exercising:
                self.timeline.draw()

    def _toggle_exercise(self):
        """Démarre ou arrête un exercice."""
        if self.is_exercising:
            self._stop_exercise()
        else:
            self._start_exercise()

    def _start_exercise(self):
        """Démarre un exercice avec décompte de préparation."""
        if not self.current_pattern:
            logger.warning("Pas de pattern selectionne")
            return

        # S'assurer que le pattern sélectionné est bien celui affiché
        settings = self.settings_panel.get_settings()
        pattern_id = settings.get('pattern_id')
        if pattern_id and self.current_pattern.id != pattern_id:
            # Le pattern sélectionné dans les settings ne correspond pas au pattern actuel
            pattern = self.rhythm_engine.get_pattern(pattern_id)
            if pattern:
                logger.warning(f"Pattern désynchronisé ! Actuel: {self.current_pattern.id}, "
                              f"Settings: {pattern_id}. Correction en cours...")
                self._set_current_pattern(pattern)

        # Annuler tout timer auto-stop précédent
        if self._auto_stop_timer is not None:
            self.after_cancel(self._auto_stop_timer)
            self._auto_stop_timer = None
        self._exercise_id += 1

        # Arrêter proprement un exercice en cours (cas restart)
        if self.is_exercising:
            self.tap_detector.stop()
            self.metronome.stop()
            self.timeline.stop_playback()

        # Cacher les résultats précédents
        self.results_frame.grid_forget()

        self.is_exercising = True
        self.start_btn.configure(text="Arreter")

        # Configuration
        settings = self.settings_panel.get_settings()
        bpm = settings.get('bpm', 80)
        num_measures = settings.get('num_measures', 4)

        # Configurer le métronome
        beats, beat_value = self.current_pattern.signature
        self.metronome.set_time_signature(beats, beat_value)
        self.metronome.set_bpm(bpm)
        logger.info(f"Exercice: pattern={self.current_pattern.id}, "
                     f"sig={beats}/{beat_value}, bpm={bpm}, "
                     f"mesures={num_measures}, audio={settings.get('audio_mode')}, "
                     f"mic_device={settings.get('input_device_id')}")

        # Calculer les temps attendus
        measure_duration = self.rhythm_engine.get_measure_duration(bpm, self.current_pattern.signature)
        self.timeline.set_measure_duration(measure_duration)
        self.timeline.num_measures = num_measures
        self._current_measure_duration = measure_duration
        self._current_num_measures = num_measures

        self.expected_times = []
        for m in range(num_measures):
            for hit in self.current_pattern.hits:
                self.expected_times.append(m * measure_duration + hit * measure_duration)

        # Préparer l'audio avec le bon périphérique
        device_id = settings.get('input_device_id')
        self.tap_detector.set_device(device_id)
        self.tap_detector.set_latency_compensation(self.latency_compensation)
        self.tap_detector.clear_taps()
        self.tap_detector.set_on_tap(self._on_tap_detected)
        try:
            self.tap_detector.start()
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Erreur demarrage micro: {error_detail}")
            self.tap_indicator.configure(text="Erreur micro (voir popup)")
            self.is_exercising = False
            self.start_btn.configure(text="Demarrer l'exercice")
            ErrorDialog(self, "Erreur Microphone", error_detail)
            return

        # Phase 1: Décompte de préparation (4 clics du métronome)
        self.tap_indicator.configure(text="Preparation...")
        self.timeline.reset()
        self._prep_beat_count = 0
        self._prep_total = beats  # 1 mesure complète de préparation

        # Démarrer le métronome pour la préparation
        self.metronome.start()

        # Calculer le temps d'un beat
        beat_interval = 60.0 / bpm
        # Note: on ne divise plus par 2 pour les signatures en /8

        # Timer pour le décompte
        self._beat_interval_ms = int(beat_interval * 1000)
        self._update_prep_countdown()

    def _update_prep_countdown(self):
        """Met à jour le décompte de préparation."""
        if not self.is_exercising:
            return

        self._prep_beat_count += 1

        if self._prep_beat_count <= self._prep_total:
            remaining = self._prep_total - self._prep_beat_count + 1
            self.tap_indicator.configure(text=f"Preparation... {remaining}")
            self.after(self._beat_interval_ms, self._update_prep_countdown)
        else:
            # Phase 2: Lancer l'exercice réel
            self._begin_recording()

    def _begin_recording(self):
        """Démarre l'enregistrement après le décompte."""
        if not self.is_exercising:
            return

        self.tap_indicator.configure(text="C'est parti ! Tapez en rythme !")
        self.tap_detector.clear_taps()  # Ignorer les taps de la préparation

        # Démarrer l'animation et l'enregistrement
        self.exercise_start_time = time.perf_counter()
        self.timeline.start_playback()

        # Timer pour arrêter automatiquement (avec ID d'exercice pour éviter les fantômes)
        total_duration = self._current_measure_duration * self._current_num_measures
        current_id = self._exercise_id
        self._auto_stop_timer = self.after(
            int(total_duration * 1000) + 500,
            lambda: self._auto_stop_exercise(current_id)
        )

    def _on_tap_detected(self, tap_time: float):
        """Callback quand un tap est détecté."""
        if not self.is_exercising or not self.exercise_start_time:
            return

        # Position relative dans l'exercice
        relative_time = tap_time - self.exercise_start_time
        settings = self.settings_panel.get_settings()
        num_measures = settings.get('num_measures', 4)
        measure_duration = self.rhythm_engine.get_measure_duration(
            settings.get('bpm', 80),
            self.current_pattern.signature
        )
        total_duration = measure_duration * num_measures

        if 0 <= relative_time <= total_duration:
            # Filtrer les taps qui correspondent exactement aux beats du métronome
            # (pour éviter de détecter le son du métronome si le micro capte les haut-parleurs)
            beats, beat_value = self.current_pattern.signature
            beat_duration = measure_duration / beats

            # Vérifier si le tap arrive exactement sur un beat (avec tolérance de 30ms)
            is_metronome_beat = False
            for m in range(num_measures):
                for b in range(beats):
                    beat_time = m * measure_duration + b * beat_duration
                    if abs(relative_time - beat_time) < 0.030:  # 30ms de tolérance
                        is_metronome_beat = True
                        break
                if is_metronome_beat:
                    break

            # Si le tap est exactement sur un beat et que le métronome est actif,
            # c'est probablement le son du métronome qui a été capté
            audio_mode = settings.get('audio_mode', 'metronome')
            if is_metronome_beat and audio_mode == 'metronome':
                # Ignorer ce tap (probablement le métronome)
                logger.debug(f"Tap ignoré (probablement métronome) à t={relative_time:.3f}")
                return

            position = relative_time / total_duration
            self.timeline.add_played_hit(position)

            # Feedback visuel
            self.tap_indicator.configure(text="TAP!")
            self.after(100, lambda: self.tap_indicator.configure(text="Continuez..."))

    def _auto_stop_exercise(self, exercise_id=None):
        """Arrête automatiquement l'exercice. Ignore si l'ID ne correspond plus."""
        if exercise_id is not None and exercise_id != self._exercise_id:
            logger.debug(f"Auto-stop ignore (id={exercise_id}, actuel={self._exercise_id})")
            return
        if self.is_exercising:
            self._auto_stop_timer = None
            self._stop_exercise()

    def _stop_exercise(self):
        """Arrête l'exercice et affiche les résultats."""
        self.is_exercising = False
        self.start_btn.configure(text="Demarrer l'exercice")

        # Annuler le timer auto-stop
        if self._auto_stop_timer is not None:
            self.after_cancel(self._auto_stop_timer)
            self._auto_stop_timer = None

        # Arrêter l'audio
        self.tap_detector.stop()
        self.metronome.stop()
        self.timeline.stop_playback()

        # Récupérer les taps
        taps = self.tap_detector.get_taps(since=self.exercise_start_time)
        relative_taps = [t - self.exercise_start_time for t in taps]

        # Analyser
        settings = self.settings_panel.get_settings()
        result = self.analyzer.analyze(
            relative_taps,
            self.expected_times,
            self.current_pattern.id,
            settings.get('bpm', 80)
        )

        # Sauvegarder
        self.tracker.save_result(result)
        self.progression.record_score(self.current_pattern.id, result.score)

        # Récupérer les stats globales
        stats = self.tracker.get_stats()
        global_stats = {
            'total_sessions': stats.get('total_sessions', 0),
            'avg_score': stats.get('avg_score', 0),
            'best_score': stats.get('best_score', 0),
            'avg_deviation': stats.get('avg_deviation', 0)
        }

        # Afficher les résultats avec stats globales
        self.results_overlay.show_results(result, global_stats)
        self.results_frame.grid(row=1, column=0, pady=10)

        stars, label = result.get_rating()
        self.tap_indicator.configure(text=f"{'*' * stars} {label}")

        # Mettre à jour les stats du panneau settings
        self.settings_panel.update_stats(
            stats.get('total_sessions', 0),
            stats.get('best_score', 0),
            stats.get('avg_deviation', 0)
        )


    def _show_calibration(self):
        """Affiche le dialogue de calibration."""
        # Cacher les résultats pour voir le bouton
        self.results_frame.grid_forget()
        dialog = CalibrationDialog(self, on_complete=self._on_calibration_complete)
        dialog.focus()

    def _on_calibration_complete(self, latency: float):
        """Callback fin de calibration."""
        # Ne mettre à jour que si on est en mode auto (pas de latence manuelle)
        settings = self.settings_panel.get_settings()
        latency_ms = settings.get('latency_ms', 0)

        if latency_ms == 0:
            # Mode auto : utiliser la latence calibrée
            self.latency_compensation = latency
            self.latency_label.configure(text=f"Latence: {latency:.0f} ms")
        else:
            # Mode manuel : ignorer la calibration
            self.latency_label.configure(text=f"Latence: {latency_ms:.0f} ms (manuel, calibration ignorée)")

        # S'assurer que le bouton est visible
        self.results_frame.grid_forget()

    def _restart_exercise(self):
        """Relance un exercice (depuis le bouton Recommencer)."""
        self.results_frame.grid_forget()
        self.timeline.clear_played_hits()
        self.tap_indicator.configure(text="Pret")
        self._start_exercise()

    def on_closing(self):
        """Nettoyage à la fermeture."""
        if self.is_exercising:
            self.tap_detector.stop()
            self.metronome.stop()

        # Backup de la base
        self.tracker.backup_database()
        self.destroy()


class ErrorDialog(ctk.CTkToplevel):
    """Dialog avec texte d'erreur copiable."""

    def __init__(self, master, title: str, message: str):
        super().__init__(master)
        self.title(title)
        self.geometry("600x300")
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        self.transient(master)

        ctk.CTkLabel(
            self, text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ff4757"
        ).pack(pady=(15, 5))

        # Zone de texte copiable (tk.Text, pas CTk)
        text_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#1f2937"))
        text_frame.pack(fill='both', expand=True, padx=15, pady=10)

        self.text_widget = tk.Text(
            text_frame, wrap='word', font=('Consolas', 11),
            bg='#1f2937', fg='#eaeaea', insertbackground='#eaeaea',
            selectbackground='#4ecdc4', relief='flat', padx=10, pady=10
        )
        self.text_widget.pack(fill='both', expand=True)
        self.text_widget.insert('1.0', message)
        self.text_widget.configure(state='normal')  # Garder editable pour copier

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text="Copier", width=100,
            command=self._copy_to_clipboard
        ).pack(side='left', padx=5)

        ctk.CTkButton(
            btn_frame, text="Fermer", width=100,
            fg_color=("gray70", "gray30"),
            command=self.destroy
        ).pack(side='left', padx=5)

        self.after(100, lambda: self.grab_set())

    def _copy_to_clipboard(self):
        """Copie le texte dans le presse-papier."""
        self.clipboard_clear()
        self.clipboard_append(self.text_widget.get('1.0', 'end').strip())


def main():
    """Point d'entrée principal."""
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
