"""
Affichage timeline lineaire des patterns rythmiques.
Widget CustomTkinter pour visualiser les beats et les taps.
"""

import customtkinter as ctk
from typing import List, Tuple
import time

from src.gui.notation_renderer import NotationRenderer, analyze_rhythm_structure


class TimelineDisplay(ctk.CTkCanvas):
    """Widget d'affichage timeline pour les patterns rythmiques."""

    # Couleurs (eviter les emojis dans CustomTkinter!)
    COLORS = {
        'background': '#1a1a2e',
        'timeline': '#16213e',
        'beat_line': '#e94560',
        'beat_accent': '#ff6b6b',
        'hit_expected': '#4ecdc4',
        'hit_played': '#95e1d3',
        'hit_missed': '#ff4757',
        'hit_good': '#2ed573',
        'cursor': '#ffd93d',
        'text': '#eaeaea'
    }

    def __init__(self, master, width: int = 800, height: int = 150, **kwargs):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=self.COLORS['background'],
            highlightthickness=0,
            **kwargs
        )

        self.display_width = width
        self.display_height = height

        # Etat
        self.pattern_hits = []
        self.played_hits = []
        self.signature = (4, 4)
        self.num_measures = 4

        # Animation
        self.cursor_position = 0.0
        self.is_playing = False
        self.start_time = None
        self.measure_duration = 2.0

        # Marges
        self.margin_left = 50
        self.margin_right = 20
        self.margin_top = 75
        self.margin_bottom = 50

        # Notation renderer
        self._notation = NotationRenderer(self, self.margin_left, self.COLORS)

        # Redimensionnement automatique
        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """Adapte le dessin a la taille reelle du canvas."""
        if event.width > 100 and event.height > 100:
            if event.width != self.display_width or event.height != self.display_height:
                self.display_width = event.width
                self.display_height = event.height
                if not self.is_playing:
                    self.draw()

    def set_pattern(self, hits: List[float], signature: Tuple[int, int]):
        """Definit le pattern a afficher."""
        self.pattern_hits = hits
        self.signature = signature
        self.played_hits = []
        self.draw()

    def set_measure_duration(self, duration: float):
        """Definit la duree d'une mesure en secondes."""
        self.measure_duration = duration

    def add_played_hit(self, position: float):
        """Ajoute un tap joue a la position donnee (0-1)."""
        self.played_hits.append(position)
        self.draw()

    def clear_played_hits(self):
        """Efface les taps joues."""
        self.played_hits = []
        self.cursor_position = 0.0
        self.draw()

    def reset(self):
        """Reset complet : efface les taps, stop l'animation, redessine."""
        self.played_hits = []
        self.is_playing = False
        self.cursor_position = 0.0
        self.start_time = None
        self.draw()

    def start_playback(self):
        """Demarre l'animation du curseur."""
        self.is_playing = True
        self.start_time = time.perf_counter()
        self.cursor_position = 0.0
        self._animate()

    def stop_playback(self):
        """Arrete l'animation."""
        self.is_playing = False

    def _animate(self):
        """Boucle d'animation du curseur."""
        if not self.is_playing:
            return

        elapsed = time.perf_counter() - self.start_time
        total_duration = self.measure_duration * self.num_measures

        self.cursor_position = (elapsed % total_duration) / total_duration

        self.draw()
        self.after(16, self._animate)

    def draw(self):
        """Dessine la timeline complete (dispatcher)."""
        self.delete('all')

        draw_width = self.display_width - self.margin_left - self.margin_right
        draw_height = self.display_height - self.margin_top - self.margin_bottom
        beats, beat_value = self.signature

        # Fond de la timeline
        self.create_rectangle(
            self.margin_left, self.margin_top,
            self.display_width - self.margin_right,
            self.display_height - self.margin_bottom,
            fill=self.COLORS['timeline'],
            outline=''
        )

        # Sous-sections
        self._draw_measures(draw_width, beats)
        self._draw_end_bar(draw_width)
        self._draw_notation_section(draw_width, beats)
        self._draw_separator_line(draw_width)
        self._draw_expected_hits(draw_width, draw_height)
        self._draw_played_hits(draw_width, draw_height)
        self._draw_legend_bottom(self.display_height - self.margin_bottom + 35)
        self._draw_cursor(draw_width)
        self._draw_signature_label(beats, beat_value)

    def _draw_measures(self, draw_width: float, beats: int):
        """Dessine les mesures avec beats et subdivisions."""
        for measure in range(self.num_measures):
            measure_start = measure / self.num_measures
            measure_width = 1.0 / self.num_measures
            self._draw_single_measure(draw_width, beats, measure, measure_start, measure_width)

    def _draw_single_measure(self, draw_width, beats, measure, measure_start, measure_width):
        """Dessine une mesure individuelle."""
        x = self.margin_left + measure_start * draw_width
        self.create_line(
            x, self.margin_top,
            x, self.display_height - self.margin_bottom,
            fill=self.COLORS['beat_accent'],
            width=2
        )

        self.create_text(
            x + 10, self.margin_top - 55,
            text=f"M{measure + 1}",
            fill=self.COLORS['text'],
            font=('Helvetica', 10),
            anchor='w'
        )

        for beat in range(beats):
            beat_pos = measure_start + (beat / beats) * measure_width
            self._draw_beat(draw_width, beats, beat, beat_pos, measure_width)

    def _draw_beat(self, draw_width, beats, beat, beat_pos, measure_width):
        """Dessine un beat avec ses subdivisions."""
        x = self.margin_left + beat_pos * draw_width
        width = 2 if beat == 0 else 1
        color = self.COLORS['beat_accent'] if beat == 0 else self.COLORS['beat_line']

        self.create_line(
            x, self.margin_top + 10,
            x, self.display_height - self.margin_bottom - 10,
            fill=color,
            width=width,
            dash=(4, 2) if beat != 0 else None
        )

        self.create_text(
            x, self.display_height - self.margin_bottom + 15,
            text=str(beat + 1),
            fill=self.COLORS['text'],
            font=('Helvetica', 9)
        )

        self._draw_subdivisions(beats, beat, beat_pos, measure_width, draw_width)

    def _draw_subdivisions(self, beats, beat, beat_pos, measure_width, draw_width):
        """Dessine les subdivisions (croches et doubles croches) d'un beat."""
        # Croches
        if beat < beats - 1:
            subdivision_pos = beat_pos + (0.5 / beats) * measure_width
            x_sub = self.margin_left + subdivision_pos * draw_width
            self.create_line(
                x_sub, self.margin_top + 20,
                x_sub, self.display_height - self.margin_bottom - 20,
                fill=self.COLORS['beat_line'],
                width=1,
                dash=(2, 3)
            )

        # Doubles croches
        for sub in [0.25, 0.75]:
            if beat < beats - 1 or sub < 0.5:
                subsubdivision_pos = beat_pos + (sub / beats) * measure_width
                x_subsub = self.margin_left + subsubdivision_pos * draw_width
                self.create_line(
                    x_subsub, self.margin_top + 25,
                    x_subsub, self.display_height - self.margin_bottom - 25,
                    fill='#444466',
                    width=1,
                    dash=(1, 4)
                )

    def _draw_end_bar(self, draw_width: float):
        """Dessine la barre de fin apres la derniere mesure."""
        x_end = self.margin_left + draw_width - 1
        self.create_line(
            x_end, self.margin_top,
            x_end, self.display_height - self.margin_bottom,
            fill=self.COLORS['beat_accent'],
            width=3
        )

    def _draw_notation_section(self, draw_width: float, beats: int):
        """Dessine la zone de notation musicale au-dessus de la timeline."""
        y_staff = self.margin_top - 25
        self._notation.draw_staff(y_staff, draw_width)

        self.create_text(
            5, y_staff - 5,
            text="Rythme:",
            fill=self.COLORS['text'],
            font=('Helvetica', 10),
            anchor='w'
        )

        rhythm_elements = analyze_rhythm_structure(self.pattern_hits, beats)
        for measure in range(self.num_measures):
            self._draw_notation_for_measure(rhythm_elements, measure, y_staff, draw_width)

    def _draw_notation_for_measure(self, rhythm_elements, measure, y_staff, draw_width):
        """Dessine la notation musicale pour une mesure donnee."""
        groups = {}
        singles = []
        color = self.COLORS['hit_expected']

        for elem in rhythm_elements:
            elem_position = (elem['position'] + measure) / self.num_measures

            if elem['type'] == 'rest':
                x = self.margin_left + elem_position * draw_width
                self._notation.draw_rest(x, y_staff, elem['duration'], color)
            elif elem['type'] == 'note':
                if elem['group_id'] is not None:
                    group_key = f"{measure}_{elem['group_id']}"
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append({
                        'position': elem_position,
                        'duration': elem['duration']
                    })
                else:
                    singles.append({
                        'position': elem_position,
                        'duration': elem['duration']
                    })

        self._draw_grouped_notes(groups, y_staff, draw_width, color)
        self._draw_single_notes(singles, y_staff, draw_width, color)

    def _draw_grouped_notes(self, groups, y_staff, draw_width, color):
        """Dessine les groupes de notes avec ligatures."""
        for group_notes in groups.values():
            if len(group_notes) >= 2:
                self._notation.draw_note_group(group_notes, y_staff, draw_width, color)
            elif len(group_notes) == 1:
                x = self.margin_left + group_notes[0]['position'] * draw_width
                self._notation.draw_single_note(x, y_staff, group_notes[0]['duration'], color)

    def _draw_single_notes(self, singles, y_staff, draw_width, color):
        """Dessine les notes individuelles."""
        for note_data in singles:
            x = self.margin_left + note_data['position'] * draw_width
            self._notation.draw_single_note(x, y_staff, note_data['duration'], color)

    def _draw_separator_line(self, draw_width: float):
        """Dessine la ligne de separation entre notation et zone de precision."""
        separator_y = self.margin_top + 5
        self.create_line(
            self.margin_left, separator_y,
            self.display_width - self.margin_right, separator_y,
            fill='#333355',
            width=1,
            dash=(5, 3)
        )

    def _draw_expected_hits(self, draw_width: float, draw_height: float):
        """Dessine les hits attendus (cercles)."""
        y_expected = self.margin_top + draw_height * 0.35
        expected_radius = 7.2
        for hit in self.pattern_hits:
            for measure in range(self.num_measures):
                pos = (measure + hit) / self.num_measures
                x = self.margin_left + pos * draw_width
                self.create_oval(
                    x - expected_radius, y_expected - expected_radius,
                    x + expected_radius, y_expected + expected_radius,
                    fill=self.COLORS['hit_expected'],
                    outline=''
                )

    def _draw_played_hits(self, draw_width: float, draw_height: float):
        """Dessine les hits joues avec coloration selon la precision."""
        y_played = self.margin_top + draw_height * 0.65
        for hit_pos in self.played_hits:
            x = self.margin_left + hit_pos * draw_width
            color = self._get_played_hit_color(hit_pos)
            self.create_oval(
                x - 6, y_played - 6,
                x + 6, y_played + 6,
                fill=color,
                outline=''
            )

    def _get_played_hit_color(self, hit_pos: float) -> str:
        """Determine la couleur d'un hit joue selon sa proximite."""
        for expected in self.pattern_hits:
            for measure in range(self.num_measures):
                expected_pos = (measure + expected) / self.num_measures
                if abs(hit_pos - expected_pos) < 0.02:
                    return self.COLORS['hit_good']
        return self.COLORS['hit_played']

    def _draw_cursor(self, draw_width: float):
        """Dessine le curseur de lecture si en cours."""
        if self.is_playing:
            cursor_x = self.margin_left + self.cursor_position * draw_width
            self.create_line(
                cursor_x, self.margin_top,
                cursor_x, self.display_height - self.margin_bottom,
                fill=self.COLORS['cursor'],
                width=3
            )

    def _draw_signature_label(self, beats: int, beat_value: int):
        """Dessine le label de la signature rythmique."""
        self.create_text(
            15, self.display_height / 2,
            text=f"{beats}/{beat_value}",
            fill=self.COLORS['text'],
            font=('Helvetica', 14, 'bold'),
            anchor='w'
        )

    def _draw_legend_bottom(self, y: float):
        """Dessine la legende en bas, horizontalement."""
        legend_x_start = self.display_width / 2 - 80

        self.create_oval(
            legend_x_start, y - 4,
            legend_x_start + 8, y + 4,
            fill=self.COLORS['hit_expected'],
            outline=''
        )
        self.create_text(
            legend_x_start + 15, y,
            text="Attendu",
            fill=self.COLORS['text'],
            font=('Helvetica', 9),
            anchor='w'
        )

        legend_x_played = legend_x_start + 90
        self.create_oval(
            legend_x_played, y - 4,
            legend_x_played + 8, y + 4,
            fill=self.COLORS['hit_played'],
            outline=''
        )
        self.create_text(
            legend_x_played + 15, y,
            text="Joue",
            fill=self.COLORS['text'],
            font=('Helvetica', 9),
            anchor='w'
        )


if __name__ == "__main__":
    # Test du widget
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.title("Test Timeline")
    root.geometry("900x300")

    timeline = TimelineDisplay(root, width=850, height=180)
    timeline.pack(pady=20, padx=20)

    # Pattern 7/8 avec groupement 2+2+3
    timeline.set_pattern([0.0, 2/7, 4/7], (7, 8))

    # Simuler quelques taps
    timeline.add_played_hit(0.01)
    timeline.add_played_hit(0.15)
    timeline.add_played_hit(0.29)

    # Bouton de lecture
    def toggle_play():
        if timeline.is_playing:
            timeline.stop_playback()
            btn.configure(text="Play")
        else:
            timeline.start_playback()
            btn.configure(text="Stop")

    btn = ctk.CTkButton(root, text="Play", command=toggle_play)
    btn.pack(pady=10)

    root.mainloop()
