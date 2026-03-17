"""
Controleur du cycle de vie d'un exercice rythmique.
Extrait de main_window.py pour modularite.
Gere : demarrage, preparation, enregistrement, detection taps, arret, analyse, resultats.
"""

import time
import traceback
import logging

from src.gui.error_dialog import ErrorDialog

logger = logging.getLogger('rhythm-trainer.gui')


class ExerciseController:
    """Gere le cycle de vie complet d'un exercice rythmique.

    Necessite un objet `window` (MainWindow) qui expose :
      - is_exercising, exercise_start_time, current_pattern, expected_times
      - _auto_stop_timer, _exercise_id, latency_compensation
      - settings_panel, rhythm_engine, timeline, tap_detector, metronome
      - analyzer, tracker, progression
      - results_frame, results_overlay, start_btn, tap_indicator, latency_label
      - after(), after_cancel() (methodes tkinter)
    """

    def __init__(self, window):
        self.w = window

    def toggle(self):
        """Demarre ou arrete un exercice."""
        if self.w.is_exercising:
            self.stop()
        else:
            self.start()

    def start(self):
        """Demarre un exercice avec decompte de preparation."""
        if not self.w.current_pattern:
            logger.warning("Pas de pattern selectionne")
            return

        self._sync_pattern_with_settings()
        self._cancel_previous_timer()
        self._stop_previous_exercise()

        self.w.results_frame.grid_forget()
        self.w.is_exercising = True
        self.w.start_btn.configure(text="Arreter")

        settings = self.w.settings_panel.get_settings()
        self._configure_exercise(settings)

        if not self._start_tap_detector(settings):
            return

        self._start_preparation_countdown(settings)

    def stop(self):
        """Arrete l'exercice et affiche les resultats."""
        self.w.is_exercising = False
        self.w.start_btn.configure(text="Demarrer l'exercice")

        if self.w._auto_stop_timer is not None:
            self.w.after_cancel(self.w._auto_stop_timer)
            self.w._auto_stop_timer = None

        self.w.tap_detector.stop()
        self.w.metronome.stop()
        self.w.timeline.stop_playback()

        result = self._analyze_exercise()
        self._display_exercise_results(result)

    def restart(self):
        """Relance un exercice (depuis le bouton Recommencer)."""
        self.w.results_frame.grid_forget()
        self.w.timeline.clear_played_hits()
        self.w.tap_indicator.configure(text="Pret")
        self.start()

    def auto_stop(self, exercise_id=None):
        """Arrete automatiquement l'exercice. Ignore si l'ID ne correspond plus."""
        if exercise_id is not None and exercise_id != self.w._exercise_id:
            logger.debug(f"Auto-stop ignore (id={exercise_id}, actuel={self.w._exercise_id})")
            return
        if self.w.is_exercising:
            self.w._auto_stop_timer = None
            self.stop()

    # --- Preparation ---

    def _sync_pattern_with_settings(self):
        """Synchronise le pattern courant avec les settings."""
        settings = self.w.settings_panel.get_settings()
        pattern_id = settings.get('pattern_id')
        if pattern_id and self.w.current_pattern.id != pattern_id:
            pattern = self.w.rhythm_engine.get_pattern(pattern_id)
            if pattern:
                logger.warning(
                    f"Pattern desynchronise ! Actuel: {self.w.current_pattern.id}, "
                    f"Settings: {pattern_id}. Correction en cours..."
                )
                self.w._set_current_pattern(pattern)

    def _cancel_previous_timer(self):
        """Annule tout timer auto-stop precedent."""
        if self.w._auto_stop_timer is not None:
            self.w.after_cancel(self.w._auto_stop_timer)
            self.w._auto_stop_timer = None
        self.w._exercise_id += 1

    def _stop_previous_exercise(self):
        """Arrete proprement un exercice en cours (cas restart)."""
        if self.w.is_exercising:
            self.w.tap_detector.stop()
            self.w.metronome.stop()
            self.w.timeline.stop_playback()

    def _configure_exercise(self, settings):
        """Configure le metronome, timeline et calcule les temps attendus."""
        bpm = settings.get('bpm', 80)
        num_measures = settings.get('num_measures', 4)

        beats, beat_value = self.w.current_pattern.signature
        self.w.metronome.set_time_signature(beats, beat_value)
        self.w.metronome.set_bpm(bpm)
        logger.info(
            f"Exercice: pattern={self.w.current_pattern.id}, "
            f"sig={beats}/{beat_value}, bpm={bpm}, "
            f"mesures={num_measures}, audio={settings.get('audio_mode')}, "
            f"mic_device={settings.get('input_device_id')}"
        )

        measure_duration = self.w.rhythm_engine.get_measure_duration(
            bpm, self.w.current_pattern.signature
        )
        self.w.timeline.set_measure_duration(measure_duration)
        self.w.timeline.num_measures = num_measures
        self.w._current_measure_duration = measure_duration
        self.w._current_num_measures = num_measures

        self.w.expected_times = []
        for m in range(num_measures):
            for hit in self.w.current_pattern.hits:
                self.w.expected_times.append(
                    m * measure_duration + hit * measure_duration
                )

    def _start_tap_detector(self, settings) -> bool:
        """Demarre le detecteur de taps. Retourne False si erreur."""
        device_id = settings.get('input_device_id')
        self.w.tap_detector.set_device(device_id)
        self.w.tap_detector.set_latency_compensation(self.w.latency_compensation)
        self.w.tap_detector.clear_taps()
        self.w.tap_detector.set_on_tap(self.on_tap_detected)
        try:
            self.w.tap_detector.start()
            return True
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Erreur demarrage micro: {error_detail}")
            self.w.tap_indicator.configure(text="Erreur micro (voir popup)")
            self.w.is_exercising = False
            self.w.start_btn.configure(text="Demarrer l'exercice")
            ErrorDialog(self.w, "Erreur Microphone", error_detail)
            return False

    # --- Decompte de preparation ---

    def _start_preparation_countdown(self, settings):
        """Demarre le decompte de preparation du metronome."""
        beats, _ = self.w.current_pattern.signature
        bpm = settings.get('bpm', 80)

        self.w.tap_indicator.configure(text="Preparation...")
        self.w.timeline.reset()
        self._prep_beat_count = 0
        self._prep_total = beats

        self.w.metronome.start()

        beat_interval = 60.0 / bpm
        self._beat_interval_ms = int(beat_interval * 1000)
        self._update_prep_countdown()

    def _update_prep_countdown(self):
        """Met a jour le decompte de preparation."""
        if not self.w.is_exercising:
            return

        self._prep_beat_count += 1

        if self._prep_beat_count <= self._prep_total:
            remaining = self._prep_total - self._prep_beat_count + 1
            self.w.tap_indicator.configure(text=f"Preparation... {remaining}")
            self.w.after(self._beat_interval_ms, self._update_prep_countdown)
        else:
            self._begin_recording()

    def _begin_recording(self):
        """Demarre l'enregistrement apres le decompte."""
        if not self.w.is_exercising:
            return

        self.w.tap_indicator.configure(text="C'est parti ! Tapez en rythme !")
        self.w.tap_detector.clear_taps()

        self.w.exercise_start_time = time.perf_counter()
        self.w.timeline.start_playback()

        total_duration = self.w._current_measure_duration * self.w._current_num_measures
        current_id = self.w._exercise_id
        self.w._auto_stop_timer = self.w.after(
            int(total_duration * 1000) + 500,
            lambda: self.auto_stop(current_id)
        )

    # --- Detection de taps ---

    def on_tap_detected(self, tap_time: float):
        """Callback quand un tap est detecte."""
        if not self.w.is_exercising or not self.w.exercise_start_time:
            return

        relative_time = tap_time - self.w.exercise_start_time
        settings = self.w.settings_panel.get_settings()
        num_measures = settings.get('num_measures', 4)
        measure_duration = self.w.rhythm_engine.get_measure_duration(
            settings.get('bpm', 80),
            self.w.current_pattern.signature
        )
        total_duration = measure_duration * num_measures

        if relative_time < 0 or relative_time > total_duration:
            return

        if self._is_metronome_bleed(relative_time, settings, measure_duration, num_measures):
            logger.debug(f"Tap ignore (probablement metronome) a t={relative_time:.3f}")
            return

        position = relative_time / total_duration
        self.w.timeline.add_played_hit(position)

        self.w.tap_indicator.configure(text="TAP!")
        self.w.after(100, lambda: self.w.tap_indicator.configure(text="Continuez..."))

    def _is_metronome_bleed(self, relative_time, settings, measure_duration, num_measures):
        """Verifie si un tap est probablement du au son du metronome capte par le micro."""
        audio_mode = settings.get('audio_mode', 'metronome')
        if audio_mode != 'metronome':
            return False

        beats, _ = self.w.current_pattern.signature
        beat_duration = measure_duration / beats

        for m in range(num_measures):
            for b in range(beats):
                beat_time = m * measure_duration + b * beat_duration
                if abs(relative_time - beat_time) < 0.030:
                    return True
        return False

    # --- Analyse et resultats ---

    def _analyze_exercise(self):
        """Analyse les taps enregistres et sauvegarde le resultat."""
        taps = self.w.tap_detector.get_taps(since=self.w.exercise_start_time)
        relative_taps = [t - self.w.exercise_start_time for t in taps]

        settings = self.w.settings_panel.get_settings()
        result = self.w.analyzer.analyze(
            relative_taps,
            self.w.expected_times,
            self.w.current_pattern.id,
            settings.get('bpm', 80)
        )

        self.w.tracker.save_result(result)
        self.w.progression.record_score(self.w.current_pattern.id, result.score)
        return result

    def _display_exercise_results(self, result):
        """Affiche les resultats et met a jour les stats."""
        stats = self.w.tracker.get_stats()
        global_stats = {
            'total_sessions': stats.get('total_sessions', 0),
            'avg_score': stats.get('avg_score', 0),
            'best_score': stats.get('best_score', 0),
            'avg_deviation': stats.get('avg_deviation', 0)
        }

        self.w.results_overlay.show_results(result, global_stats)
        self.w.results_frame.grid(row=1, column=0, pady=10)

        stars, label = result.get_rating()
        self.w.tap_indicator.configure(text=f"{'*' * stars} {label}")

        self.w.settings_panel.update_stats(
            stats.get('total_sessions', 0),
            stats.get('best_score', 0),
            stats.get('avg_deviation', 0)
        )
