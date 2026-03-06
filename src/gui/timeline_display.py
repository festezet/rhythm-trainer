"""
Affichage timeline linéaire des patterns rythmiques.
Widget CustomTkinter pour visualiser les beats et les taps.
"""

import customtkinter as ctk
from typing import List, Tuple, Optional
import time


class TimelineDisplay(ctk.CTkCanvas):
    """Widget d'affichage timeline pour les patterns rythmiques."""

    # Couleurs (éviter les emojis dans CustomTkinter!)
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

        # État
        self.pattern_hits = []  # Positions attendues (0-1)
        self.played_hits = []   # Positions jouées (0-1)
        self.signature = (4, 4)
        self.num_measures = 4   # Nombre de mesures affichées par défaut

        # Animation
        self.cursor_position = 0.0  # Position du curseur (0-1 sur l'ensemble)
        self.is_playing = False
        self.start_time = None
        self.measure_duration = 2.0  # secondes

        # Marges
        self.margin_left = 50
        self.margin_right = 20
        self.margin_top = 75  # Augmenté pour M1/M2/M3/M4 et la portée musicale
        self.margin_bottom = 50

        # Redimensionnement automatique
        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """Adapte le dessin à la taille réelle du canvas."""
        if event.width > 100 and event.height > 100:
            if event.width != self.display_width or event.height != self.display_height:
                self.display_width = event.width
                self.display_height = event.height
                if not self.is_playing:
                    self.draw()

    def set_pattern(self, hits: List[float], signature: Tuple[int, int]):
        """
        Définit le pattern à afficher.

        Args:
            hits: Positions des frappes (0.0 à 1.0 dans une mesure)
            signature: (beats, beat_value)
        """
        self.pattern_hits = hits
        self.signature = signature
        self.played_hits = []
        self.draw()

    def set_measure_duration(self, duration: float):
        """Définit la durée d'une mesure en secondes."""
        self.measure_duration = duration

    def add_played_hit(self, position: float):
        """Ajoute un tap joué à la position donnée (0-1)."""
        self.played_hits.append(position)
        self.draw()

    def clear_played_hits(self):
        """Efface les taps joués."""
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
        """Démarre l'animation du curseur."""
        self.is_playing = True
        self.start_time = time.perf_counter()
        self.cursor_position = 0.0
        self._animate()

    def stop_playback(self):
        """Arrête l'animation."""
        self.is_playing = False

    def _animate(self):
        """Boucle d'animation du curseur."""
        if not self.is_playing:
            return

        elapsed = time.perf_counter() - self.start_time
        total_duration = self.measure_duration * self.num_measures

        self.cursor_position = (elapsed % total_duration) / total_duration

        self.draw()
        self.after(16, self._animate)  # ~60 FPS

    def draw(self):
        """Dessine la timeline complète."""
        self.delete('all')

        # Dimensions de la zone de dessin
        draw_width = self.display_width - self.margin_left - self.margin_right
        draw_height = self.display_height - self.margin_top - self.margin_bottom

        # Fond de la timeline
        self.create_rectangle(
            self.margin_left, self.margin_top,
            self.display_width - self.margin_right,
            self.display_height - self.margin_bottom,
            fill=self.COLORS['timeline'],
            outline=''
        )

        # Dessiner les mesures
        beats, beat_value = self.signature
        total_beats = beats * self.num_measures

        for measure in range(self.num_measures):
            measure_start = measure / self.num_measures
            measure_width = 1.0 / self.num_measures

            # Ligne de début de mesure
            x = self.margin_left + measure_start * draw_width
            self.create_line(
                x, self.margin_top,
                x, self.display_height - self.margin_bottom,
                fill=self.COLORS['beat_accent'],
                width=2
            )

            # Numéro de mesure (au-dessus de la portée)
            self.create_text(
                x + 10, self.margin_top - 55,
                text=f"M{measure + 1}",
                fill=self.COLORS['text'],
                font=('Helvetica', 10),
                anchor='w'
            )

            # Lignes de beats dans la mesure
            for beat in range(beats):
                beat_pos = measure_start + (beat / beats) * measure_width
                x = self.margin_left + beat_pos * draw_width

                # Trait plus épais pour temps 1
                width = 2 if beat == 0 else 1
                color = self.COLORS['beat_accent'] if beat == 0 else self.COLORS['beat_line']

                self.create_line(
                    x, self.margin_top + 10,
                    x, self.display_height - self.margin_bottom - 10,
                    fill=color,
                    width=width,
                    dash=(4, 2) if beat != 0 else None
                )

                # Numéro du beat
                self.create_text(
                    x, self.display_height - self.margin_bottom + 15,
                    text=str(beat + 1),
                    fill=self.COLORS['text'],
                    font=('Helvetica', 9)
                )

                # Barres de subdivision (croches)
                # Pour chaque temps, ajouter une ligne de subdivision au milieu
                if beat < beats - 1:  # Pas après le dernier temps
                    subdivision_pos = beat_pos + (0.5 / beats) * measure_width
                    x_sub = self.margin_left + subdivision_pos * draw_width
                    self.create_line(
                        x_sub, self.margin_top + 20,
                        x_sub, self.display_height - self.margin_bottom - 20,
                        fill=self.COLORS['beat_line'],
                        width=1,
                        dash=(2, 3)  # Pointillé plus léger
                    )

                # Barres de sous-subdivision (doubles croches)
                # Diviser chaque temps en 4
                for sub in [0.25, 0.75]:  # Quarts de temps
                    if beat < beats - 1 or sub < 0.5:
                        subsubdivision_pos = beat_pos + (sub / beats) * measure_width
                        x_subsub = self.margin_left + subsubdivision_pos * draw_width
                        self.create_line(
                            x_subsub, self.margin_top + 25,
                            x_subsub, self.display_height - self.margin_bottom - 25,
                            fill='#444466',  # Couleur encore plus légère
                            width=1,
                            dash=(1, 4)  # Pointillé très léger
                        )

        # Barre de fin (après la dernière mesure)
        # Dessiner légèrement avant le bord pour qu'elle soit visible
        x_end = self.margin_left + draw_width - 1
        self.create_line(
            x_end, self.margin_top,
            x_end, self.display_height - self.margin_bottom,
            fill=self.COLORS['beat_accent'],
            width=3
        )

        # Zone de notation musicale (au-dessus)
        y_staff = self.margin_top - 25
        self._draw_staff(y_staff, draw_width)

        # Label pour la notation musicale (déplacé plus à gauche et plus haut)
        self.create_text(
            5, y_staff - 5,
            text="Rythme:",
            fill=self.COLORS['text'],
            font=('Helvetica', 10),
            anchor='w'
        )

        # Analyser la structure rythmique du pattern
        rhythm_elements = self._analyze_rhythm_structure(self.pattern_hits, beats)

        # Dessiner la notation musicale pour chaque mesure
        for measure in range(self.num_measures):
            # Grouper les éléments par groupe_id pour dessiner les ligatures
            groups = {}
            singles = []

            for elem in rhythm_elements:
                measure_offset = measure / self.num_measures
                elem_position = (elem['position'] + measure) / self.num_measures

                if elem['type'] == 'rest':
                    # Dessiner le silence
                    x = self.margin_left + elem_position * draw_width
                    self._draw_rest(x, y_staff, elem['duration'], self.COLORS['hit_expected'])

                elif elem['type'] == 'note':
                    if elem['group_id'] is not None:
                        # Note fait partie d'un groupe
                        group_key = f"{measure}_{elem['group_id']}"
                        if group_key not in groups:
                            groups[group_key] = []
                        groups[group_key].append({
                            'position': elem_position,
                            'duration': elem['duration']
                        })
                    else:
                        # Note individuelle (noire)
                        singles.append({
                            'position': elem_position,
                            'duration': elem['duration']
                        })

            # Dessiner les groupes avec ligatures
            for group_notes in groups.values():
                if len(group_notes) >= 2:
                    self._draw_note_group(group_notes, y_staff, draw_width, self.COLORS['hit_expected'])
                elif len(group_notes) == 1:
                    # Un seul élément dans le groupe, dessiner comme note individuelle
                    x = self.margin_left + group_notes[0]['position'] * draw_width
                    self._draw_single_note(x, y_staff, group_notes[0]['duration'], self.COLORS['hit_expected'])

            # Dessiner les notes individuelles (noires)
            for note_data in singles:
                x = self.margin_left + note_data['position'] * draw_width
                self._draw_single_note(x, y_staff, note_data['duration'], self.COLORS['hit_expected'])

        # Ligne de séparation entre notation musicale et zone de précision
        separator_y = self.margin_top + 5
        self.create_line(
            self.margin_left, separator_y,
            self.display_width - self.margin_right, separator_y,
            fill='#333355',
            width=1,
            dash=(5, 3)
        )

        # Dessiner les hits attendus (ancien système - barres de précision)
        y_expected = self.margin_top + draw_height * 0.35
        expected_radius = 7.2  # Réduit de 10% (8 * 0.9 = 7.2)
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

        # Dessiner les hits joués
        y_played = self.margin_top + draw_height * 0.65
        for hit_pos in self.played_hits:
            x = self.margin_left + hit_pos * draw_width

            # Trouver le hit attendu le plus proche pour colorer
            color = self.COLORS['hit_played']
            for expected in self.pattern_hits:
                for measure in range(self.num_measures):
                    expected_pos = (measure + expected) / self.num_measures
                    if abs(hit_pos - expected_pos) < 0.02:  # ~2% de tolérance
                        color = self.COLORS['hit_good']
                        break

            self.create_oval(
                x - 6, y_played - 6,
                x + 6, y_played + 6,
                fill=color,
                outline=''
            )

        # Légende (en bas à droite, en dehors de la zone de dessin)
        legend_y = self.display_height - self.margin_bottom + 35
        self._draw_legend_bottom(legend_y)

        # Curseur de lecture
        if self.is_playing:
            cursor_x = self.margin_left + self.cursor_position * draw_width
            self.create_line(
                cursor_x, self.margin_top,
                cursor_x, self.display_height - self.margin_bottom,
                fill=self.COLORS['cursor'],
                width=3
            )

        # Signature rythmique
        self.create_text(
            15, self.display_height / 2,
            text=f"{beats}/{beat_value}",
            fill=self.COLORS['text'],
            font=('Helvetica', 14, 'bold'),
            anchor='w'
        )

    def _draw_legend_bottom(self, y: float):
        """Dessine la légende en bas, horizontalement."""
        # Centrer la légende horizontalement
        legend_x_start = self.display_width / 2 - 80

        # Attendu
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

        # Joué (à côté)
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

    def _analyze_rhythm_structure(self, hits: List[float], beats: int):
        """
        Analyse la structure rythmique du pattern pour déterminer les notes et silences.

        Args:
            hits: Liste des positions des frappes (0.0 à 1.0 dans une mesure)
            beats: Nombre de temps dans la mesure

        Returns:
            Liste de dictionnaires représentant chaque élément rythmique :
            {
                'type': 'note' ou 'rest',
                'duration': 'quarter', 'eighth', 'sixteenth', 'triplet',
                'position': position dans la mesure (0.0-1.0),
                'beat': numéro du temps (0 à beats-1),
                'group_id': identifiant de groupe pour les ligatures
            }
        """
        if not hits:
            return []

        beat_duration = 1.0 / beats
        elements = []

        # Déterminer la subdivision minimale
        sorted_hits = sorted(hits)
        if len(sorted_hits) > 1:
            min_interval = min(sorted_hits[i+1] - sorted_hits[i] for i in range(len(sorted_hits) - 1))
        else:
            min_interval = beat_duration

        # Détecter le type de subdivision
        is_triplet = False
        is_sixteenth = False
        is_eighth = False

        # Vérifier si c'est un triolet (3, 6, 9, 12 notes par mesure en divisions de 3)
        # Important: un triolet a des intervalles de 1/3 de TEMPS, pas 1 temps complet
        if len(hits) % 3 == 0 and len(hits) > beats:
            # Vérifier les intervalles réguliers de 1/3 de temps
            triplet_interval = beat_duration / 3
            triplet_match = all(
                abs((sorted_hits[i+1] - sorted_hits[i]) - triplet_interval) < 0.01
                for i in range(len(sorted_hits) - 1)
                if (sorted_hits[i+1] - sorted_hits[i]) < beat_duration * 0.9
            )
            if triplet_match:
                is_triplet = True

        if not is_triplet:
            if min_interval < beat_duration * 0.3:
                is_sixteenth = True
            elif min_interval < beat_duration * 0.6:
                is_eighth = True

        # Parcourir chaque temps et identifier les notes/silences
        for beat_num in range(beats):
            beat_start = beat_num * beat_duration
            beat_end = (beat_num + 1) * beat_duration

            # Trouver toutes les notes dans ce temps
            notes_in_beat = [h for h in hits if beat_start <= h < beat_end]

            if is_triplet:
                # Traiter comme triolets
                self._add_triplet_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat)
            elif is_sixteenth:
                # Traiter comme doubles croches
                self._add_sixteenth_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat)
            elif is_eighth:
                # Traiter comme croches
                self._add_eighth_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat)
            else:
                # Noires
                if notes_in_beat:
                    for note_pos in notes_in_beat:
                        elements.append({
                            'type': 'note',
                            'duration': 'quarter',
                            'position': note_pos,
                            'beat': beat_num,
                            'group_id': None
                        })
                else:
                    # Soupir (silence de noire)
                    elements.append({
                        'type': 'rest',
                        'duration': 'quarter',
                        'position': beat_start,
                        'beat': beat_num,
                        'group_id': None
                    })

        return elements

    def _add_triplet_elements(self, elements, beat_num, beat_start, beat_duration, notes_in_beat):
        """Ajoute les éléments pour un temps en triolets."""
        triplet_interval = beat_duration / 3
        group_id = f'triplet_{beat_num}'

        for i in range(3):
            expected_pos = beat_start + i * triplet_interval
            # Chercher une note proche de cette position
            found = False
            for note_pos in notes_in_beat:
                if abs(note_pos - expected_pos) < triplet_interval * 0.4:
                    elements.append({
                        'type': 'note',
                        'duration': 'triplet',
                        'position': note_pos,
                        'beat': beat_num,
                        'group_id': group_id
                    })
                    found = True
                    break
            if not found and notes_in_beat:
                # Silence de triolet
                elements.append({
                    'type': 'rest',
                    'duration': 'triplet',
                    'position': expected_pos,
                    'beat': beat_num,
                    'group_id': group_id
                })

    def _add_eighth_elements(self, elements, beat_num, beat_start, beat_duration, notes_in_beat):
        """Ajoute les éléments pour un temps en croches."""
        eighth_interval = beat_duration / 2
        group_id = f'eighth_{beat_num}'

        for i in range(2):
            expected_pos = beat_start + i * eighth_interval
            found = False
            for note_pos in notes_in_beat:
                if abs(note_pos - expected_pos) < eighth_interval * 0.4:
                    elements.append({
                        'type': 'note',
                        'duration': 'eighth',
                        'position': note_pos,
                        'beat': beat_num,
                        'group_id': group_id
                    })
                    found = True
                    break
            if not found and notes_in_beat:
                # Demi-soupir (silence de croche)
                elements.append({
                    'type': 'rest',
                    'duration': 'eighth',
                    'position': expected_pos,
                    'beat': beat_num,
                    'group_id': group_id
                })

    def _add_sixteenth_elements(self, elements, beat_num, beat_start, beat_duration, notes_in_beat):
        """Ajoute les éléments pour un temps en doubles croches."""
        sixteenth_interval = beat_duration / 4
        group_id = f'sixteenth_{beat_num}'

        for i in range(4):
            expected_pos = beat_start + i * sixteenth_interval
            found = False
            for note_pos in notes_in_beat:
                if abs(note_pos - expected_pos) < sixteenth_interval * 0.4:
                    elements.append({
                        'type': 'note',
                        'duration': 'sixteenth',
                        'position': note_pos,
                        'beat': beat_num,
                        'group_id': group_id
                    })
                    found = True
                    break
            if not found and notes_in_beat:
                # Quart de soupir (silence de double croche)
                elements.append({
                    'type': 'rest',
                    'duration': 'sixteenth',
                    'position': expected_pos,
                    'beat': beat_num,
                    'group_id': group_id
                })

    def _draw_staff(self, y_center: float, width: float):
        """
        Dessine une portée musicale simplifiée.

        Args:
            y_center: Position verticale du centre de la portée
            width: Largeur de la portée
        """
        staff_color = '#555577'
        line_spacing = 8  # Espacement entre les lignes de la portée

        # Dessiner 5 lignes horizontales (portée standard)
        for i in range(5):
            y = y_center - (2 - i) * line_spacing  # Centrer la portée autour de y_center
            self.create_line(
                self.margin_left, y,
                self.margin_left + width, y,
                fill=staff_color,
                width=1
            )

        # Dessiner une clé de sol simplifiée au début de la portée
        self._draw_treble_clef(self.margin_left + 5, y_center)

    def _draw_treble_clef(self, x: float, y_center: float):
        """
        Dessine une clé de sol simplifiée.

        Args:
            x: Position horizontale
            y_center: Centre de la portée
        """
        clef_color = self.COLORS['text']

        # Symbole simplifié de clé de sol (forme en S stylisée)
        # Cercle principal
        self.create_oval(
            x - 3, y_center - 8,
            x + 3, y_center - 2,
            outline=clef_color,
            width=2,
            fill=''
        )

        # Ligne verticale
        self.create_line(
            x, y_center - 8,
            x, y_center + 12,
            fill=clef_color,
            width=2
        )

        # Boucle en bas
        self.create_arc(
            x - 5, y_center + 8,
            x + 5, y_center + 16,
            start=270,
            extent=180,
            outline=clef_color,
            width=2,
            style='arc'
        )

    def _draw_rest(self, x: float, y_center: float, rest_type: str, color: str = None):
        """
        Dessine un silence (soupir, demi-soupir, quart de soupir).

        Args:
            x: Position horizontale
            y_center: Position verticale (centre de la portée)
            rest_type: Type de silence ('quarter', 'eighth', 'sixteenth', 'triplet')
            color: Couleur du silence
        """
        if color is None:
            color = self.COLORS['text']

        if rest_type == 'quarter':
            # Soupir (silence de noire) - forme en zigzag
            points = [
                x - 3, y_center - 10,
                x + 4, y_center - 5,
                x - 2, y_center,
                x + 3, y_center + 5,
                x - 3, y_center + 10
            ]
            self.create_line(points, fill=color, width=2, smooth=False)

        elif rest_type == 'eighth' or rest_type == 'triplet':
            # Demi-soupir (silence de croche) - forme en 7
            points = [
                x - 2, y_center - 5,
                x + 3, y_center - 5,
                x + 3, y_center,
            ]
            self.create_line(points, fill=color, width=2)
            # Petit point
            self.create_oval(
                x + 1, y_center + 2,
                x + 4, y_center + 5,
                fill=color,
                outline=color
            )

        elif rest_type == 'sixteenth':
            # Quart de soupir (silence de double croche) - forme en 7 avec deux points
            points = [
                x - 2, y_center - 8,
                x + 3, y_center - 8,
                x + 3, y_center - 2,
            ]
            self.create_line(points, fill=color, width=2)
            # Deux petits points
            self.create_oval(
                x + 1, y_center,
                x + 4, y_center + 3,
                fill=color,
                outline=color
            )
            self.create_oval(
                x + 1, y_center + 5,
                x + 4, y_center + 8,
                fill=color,
                outline=color
            )

    def _draw_note_group(self, notes_data: list, y_center: float, draw_width: float, color: str = None):
        """
        Dessine un groupe de notes reliées par une ligature horizontale.

        Args:
            notes_data: Liste de dictionnaires avec 'position' (0-1) et 'duration'
            y_center: Position verticale (centre de la portée)
            draw_width: Largeur totale de la zone de dessin
            color: Couleur des notes
        """
        if color is None:
            color = self.COLORS['text']

        note_head_radius = 5
        stem_height = 25
        stem_width = 1.5
        y_note = y_center

        # Dessiner toutes les têtes de notes et hampes
        x_positions = []
        for note in notes_data:
            x = self.margin_left + note['position'] * draw_width
            x_positions.append(x)

            # Tête de note pleine
            self.create_oval(
                x - note_head_radius, y_note - note_head_radius + 2,
                x + note_head_radius, y_note + note_head_radius - 2,
                fill=color,
                outline=color
            )

            # Hampe vers le haut
            self.create_line(
                x + note_head_radius - 1, y_note,
                x + note_head_radius - 1, y_note - stem_height,
                fill=color,
                width=stem_width
            )

        # Dessiner la ligature horizontale (barre reliant les notes)
        if len(x_positions) >= 2:
            x_start = x_positions[0] + note_head_radius - 1
            x_end = x_positions[-1] + note_head_radius - 1
            y_beam = y_note - stem_height

            # Première barre (pour toutes les croches/doubles croches)
            self.create_rectangle(
                x_start, y_beam,
                x_end, y_beam + 3,
                fill=color,
                outline=color
            )

            # Deuxième barre pour les doubles croches
            if notes_data[0]['duration'] == 'sixteenth':
                self.create_rectangle(
                    x_start, y_beam + 5,
                    x_end, y_beam + 8,
                    fill=color,
                    outline=color
                )

            # Ajouter un "3" au-dessus pour les triolets
            if notes_data[0]['duration'] == 'triplet':
                x_mid = (x_start + x_end) / 2
                self.create_text(
                    x_mid, y_beam - 8,
                    text="3",
                    fill=color,
                    font=('Helvetica', 10, 'bold')
                )

    def _draw_single_note(self, x: float, y_center: float, note_type: str, color: str = None):
        """
        Dessine une note individuelle (noire ou avec crochet individuel).

        Args:
            x: Position horizontale
            y_center: Position verticale (centre de la portée)
            note_type: Type de note ('quarter', 'eighth', 'sixteenth')
            color: Couleur de la note
        """
        if color is None:
            color = self.COLORS['text']

        note_head_radius = 5
        stem_height = 25
        stem_width = 1.5
        y_note = y_center

        # Tête de note pleine
        self.create_oval(
            x - note_head_radius, y_note - note_head_radius + 2,
            x + note_head_radius, y_note + note_head_radius - 2,
            fill=color,
            outline=color
        )

        # Hampe vers le haut
        self.create_line(
            x + note_head_radius - 1, y_note,
            x + note_head_radius - 1, y_note - stem_height,
            fill=color,
            width=stem_width
        )

        # Crochets pour les croches et doubles croches
        if note_type == 'eighth' or note_type == 'triplet':
            # Un crochet pour la croche
            flag_points = [
                x + note_head_radius - 1, y_note - stem_height,
                x + note_head_radius + 8, y_note - stem_height + 5,
                x + note_head_radius + 6, y_note - stem_height + 8,
                x + note_head_radius - 1, y_note - stem_height + 5
            ]
            self.create_polygon(flag_points, fill=color, outline=color)

        elif note_type == 'sixteenth':
            # Deux crochets pour la double croche
            flag_points_1 = [
                x + note_head_radius - 1, y_note - stem_height,
                x + note_head_radius + 8, y_note - stem_height + 5,
                x + note_head_radius + 6, y_note - stem_height + 8,
                x + note_head_radius - 1, y_note - stem_height + 5
            ]
            self.create_polygon(flag_points_1, fill=color, outline=color)
            flag_points_2 = [
                x + note_head_radius - 1, y_note - stem_height + 6,
                x + note_head_radius + 8, y_note - stem_height + 11,
                x + note_head_radius + 6, y_note - stem_height + 14,
                x + note_head_radius - 1, y_note - stem_height + 11
            ]
            self.create_polygon(flag_points_2, fill=color, outline=color)


class ResultsOverlay(ctk.CTkFrame):
    """Overlay d'affichage des résultats après un exercice."""

    def __init__(self, master, on_restart=None, **kwargs):
        super().__init__(master, fg_color=("#f0f0f0", "#1f2937"), **kwargs)

        self.on_restart = on_restart

        # Score principal
        self.score_label = ctk.CTkLabel(
            self,
            text="--",
            font=ctk.CTkFont(size=48, weight="bold")
        )
        self.score_label.pack(pady=10)

        # Rating (étoiles en texte)
        self.rating_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=18)
        )
        self.rating_label.pack()

        # Métriques détaillées
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(pady=15, fill='x', padx=20)

        self.deviation_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Decalage: -- ms",
            font=ctk.CTkFont(size=14)
        )
        self.deviation_label.pack()

        self.stability_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Stabilite: -- ms",
            font=ctk.CTkFont(size=14)
        )
        self.stability_label.pack()

        self.accuracy_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Precision: --%",
            font=ctk.CTkFont(size=14)
        )
        self.accuracy_label.pack()

        # Séparateur
        separator = ctk.CTkFrame(self, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill='x', padx=40, pady=15)

        # Statistiques globales
        stats_title = ctk.CTkLabel(
            self,
            text="Statistiques & Progression",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_title.pack(pady=(5, 10))

        self.global_stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.global_stats_frame.pack(pady=5, fill='x', padx=20)

        self.total_sessions_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Sessions totales: 0",
            font=ctk.CTkFont(size=14)
        )
        self.total_sessions_label.pack()

        self.avg_score_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Score moyen: 0",
            font=ctk.CTkFont(size=14)
        )
        self.avg_score_label.pack()

        self.best_score_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Meilleur score: 0",
            font=ctk.CTkFont(size=14)
        )
        self.best_score_label.pack()

        self.avg_deviation_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Decalage moyen: -- ms",
            font=ctk.CTkFont(size=14)
        )
        self.avg_deviation_label.pack()

        # Bouton Recommencer
        self.restart_btn = ctk.CTkButton(
            self,
            text="Recommencer",
            command=self._on_restart_click,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.restart_btn.pack(pady=15)

    def _on_restart_click(self):
        """Callback du bouton recommencer."""
        if self.on_restart:
            self.on_restart()

    def set_on_restart(self, callback):
        """Définit le callback pour le bouton recommencer."""
        self.on_restart = callback

    def show_results(self, result, global_stats=None):
        """Affiche les résultats d'un exercice."""
        self.score_label.configure(text=f"{result.score}/100")

        stars, label = result.get_rating()
        self.rating_label.configure(text=f"{'*' * stars} {label}")

        sign = "+" if result.mean_deviation_ms > 0 else ""
        self.deviation_label.configure(
            text=f"Decalage moyen: {sign}{result.mean_deviation_ms:.1f} ms"
        )
        self.stability_label.configure(
            text=f"Stabilite: +/-{result.std_deviation_ms:.1f} ms"
        )
        self.accuracy_label.configure(
            text=f"Precision: {result.accuracy_percent:.0f}%"
        )

        # Mettre à jour les stats globales si fournies
        if global_stats:
            self.total_sessions_label.configure(
                text=f"Sessions totales: {global_stats.get('total_sessions', 0)}"
            )
            self.avg_score_label.configure(
                text=f"Score moyen: {global_stats.get('avg_score', 0):.0f}"
            )
            self.best_score_label.configure(
                text=f"Meilleur score: {global_stats.get('best_score', 0)}"
            )
            avg_dev = global_stats.get('avg_deviation', 0)
            sign_dev = "+" if avg_dev > 0 else ""
            self.avg_deviation_label.configure(
                text=f"Decalage moyen: {sign_dev}{avg_dev:.1f} ms"
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
