"""
Rendu de la notation musicale sur canvas.
Extrait de timeline_display.py pour modularite.
Dessine les notes, silences, portees, et analyse la structure rythmique.
"""

from typing import List


class NotationRenderer:
    """Dessine la notation musicale sur un canvas tkinter."""

    # Constants for note rendering
    NOTE_HEAD_RADIUS = 5
    STEM_HEIGHT = 25

    def __init__(self, canvas, margin_left: float, colors: dict):
        self.canvas = canvas
        self.margin_left = margin_left
        self.colors = colors

    def draw_staff(self, y_center: float, width: float):
        """
        Dessine une portee musicale simplifiee.

        Args:
            y_center: Position verticale du centre de la portee
            width: Largeur de la portee
        """
        staff_color = '#555577'
        line_spacing = 8

        for i in range(5):
            y = y_center - (2 - i) * line_spacing
            self.canvas.create_line(
                self.margin_left, y,
                self.margin_left + width, y,
                fill=staff_color,
                width=1
            )

        self.draw_treble_clef(self.margin_left + 5, y_center)

    def draw_treble_clef(self, x: float, y_center: float):
        """Dessine une cle de sol simplifiee."""
        clef_color = self.colors['text']

        self.canvas.create_oval(
            x - 3, y_center - 8,
            x + 3, y_center - 2,
            outline=clef_color,
            width=2,
            fill=''
        )

        self.canvas.create_line(
            x, y_center - 8,
            x, y_center + 12,
            fill=clef_color,
            width=2
        )

        self.canvas.create_arc(
            x - 5, y_center + 8,
            x + 5, y_center + 16,
            start=270,
            extent=180,
            outline=clef_color,
            width=2,
            style='arc'
        )

    def draw_rest(self, x: float, y_center: float, rest_type: str, color: str = None):
        """
        Dessine un silence (soupir, demi-soupir, quart de soupir).

        Args:
            x: Position horizontale
            y_center: Position verticale (centre de la portee)
            rest_type: Type de silence ('quarter', 'eighth', 'sixteenth', 'triplet')
            color: Couleur du silence
        """
        if color is None:
            color = self.colors['text']

        if rest_type == 'quarter':
            self._draw_quarter_rest(x, y_center, color)
        elif rest_type in ('eighth', 'triplet'):
            self._draw_eighth_rest(x, y_center, color)
        elif rest_type == 'sixteenth':
            self._draw_sixteenth_rest(x, y_center, color)

    def _draw_quarter_rest(self, x: float, y_center: float, color: str):
        """Dessine un soupir (silence de noire)."""
        points = [
            x - 3, y_center - 10,
            x + 4, y_center - 5,
            x - 2, y_center,
            x + 3, y_center + 5,
            x - 3, y_center + 10
        ]
        self.canvas.create_line(points, fill=color, width=2, smooth=False)

    def _draw_eighth_rest(self, x: float, y_center: float, color: str):
        """Dessine un demi-soupir (silence de croche)."""
        points = [
            x - 2, y_center - 5,
            x + 3, y_center - 5,
            x + 3, y_center,
        ]
        self.canvas.create_line(points, fill=color, width=2)
        self.canvas.create_oval(
            x + 1, y_center + 2,
            x + 4, y_center + 5,
            fill=color,
            outline=color
        )

    def _draw_sixteenth_rest(self, x: float, y_center: float, color: str):
        """Dessine un quart de soupir (silence de double croche)."""
        points = [
            x - 2, y_center - 8,
            x + 3, y_center - 8,
            x + 3, y_center - 2,
        ]
        self.canvas.create_line(points, fill=color, width=2)
        self.canvas.create_oval(
            x + 1, y_center,
            x + 4, y_center + 3,
            fill=color,
            outline=color
        )
        self.canvas.create_oval(
            x + 1, y_center + 5,
            x + 4, y_center + 8,
            fill=color,
            outline=color
        )

    def draw_note_group(self, notes_data: list, y_center: float, draw_width: float, color: str = None):
        """
        Dessine un groupe de notes reliees par une ligature.

        Args:
            notes_data: Liste de dicts avec 'position' (0-1) et 'duration'
            y_center: Position verticale (centre de la portee)
            draw_width: Largeur totale de la zone de dessin
            color: Couleur des notes
        """
        if color is None:
            color = self.colors['text']

        y_note = y_center

        x_positions = self._draw_note_heads_and_stems(
            notes_data, y_note, draw_width, color
        )

        self._draw_beams(x_positions, y_note, notes_data, color)

    def _draw_note_heads_and_stems(self, notes_data, y_note, draw_width, color):
        """Dessine les tetes de notes et hampes, retourne les positions X."""
        r = self.NOTE_HEAD_RADIUS
        sh = self.STEM_HEIGHT
        x_positions = []
        for note in notes_data:
            x = self.margin_left + note['position'] * draw_width
            x_positions.append(x)

            self.canvas.create_oval(
                x - r, y_note - r + 2,
                x + r, y_note + r - 2,
                fill=color,
                outline=color
            )

            self.canvas.create_line(
                x + r - 1, y_note,
                x + r - 1, y_note - sh,
                fill=color,
                width=1.5
            )
        return x_positions

    def _draw_beams(self, x_positions, y_note, notes_data, color):
        """Dessine les ligatures horizontales reliant les notes."""
        if len(x_positions) < 2:
            return

        r = self.NOTE_HEAD_RADIUS
        sh = self.STEM_HEIGHT
        x_start = x_positions[0] + r - 1
        x_end = x_positions[-1] + r - 1
        y_beam = y_note - sh

        self.canvas.create_rectangle(
            x_start, y_beam,
            x_end, y_beam + 3,
            fill=color,
            outline=color
        )

        if notes_data[0]['duration'] == 'sixteenth':
            self.canvas.create_rectangle(
                x_start, y_beam + 5,
                x_end, y_beam + 8,
                fill=color,
                outline=color
            )

        if notes_data[0]['duration'] == 'triplet':
            x_mid = (x_start + x_end) / 2
            self.canvas.create_text(
                x_mid, y_beam - 8,
                text="3",
                fill=color,
                font=('Helvetica', 10, 'bold')
            )

    def draw_single_note(self, x: float, y_center: float, note_type: str, color: str = None):
        """
        Dessine une note individuelle (noire ou avec crochet).

        Args:
            x: Position horizontale
            y_center: Position verticale (centre de la portee)
            note_type: Type de note ('quarter', 'eighth', 'sixteenth', 'triplet')
            color: Couleur de la note
        """
        if color is None:
            color = self.colors['text']

        note_head_radius = 5
        stem_height = 25
        y_note = y_center

        # Tete de note pleine
        self.canvas.create_oval(
            x - note_head_radius, y_note - note_head_radius + 2,
            x + note_head_radius, y_note + note_head_radius - 2,
            fill=color,
            outline=color
        )

        # Hampe vers le haut
        self.canvas.create_line(
            x + note_head_radius - 1, y_note,
            x + note_head_radius - 1, y_note - stem_height,
            fill=color,
            width=1.5
        )

        # Crochets
        if note_type in ('eighth', 'triplet'):
            self._draw_single_flag(x, y_note, note_head_radius, stem_height, color)
        elif note_type == 'sixteenth':
            self._draw_double_flag(x, y_note, note_head_radius, stem_height, color)

    def _draw_single_flag(self, x, y_note, radius, stem_h, color):
        """Dessine un crochet (croche)."""
        flag_points = [
            x + radius - 1, y_note - stem_h,
            x + radius + 8, y_note - stem_h + 5,
            x + radius + 6, y_note - stem_h + 8,
            x + radius - 1, y_note - stem_h + 5
        ]
        self.canvas.create_polygon(flag_points, fill=color, outline=color)

    def _draw_double_flag(self, x, y_note, radius, stem_h, color):
        """Dessine deux crochets (double croche)."""
        self._draw_single_flag(x, y_note, radius, stem_h, color)
        flag_points_2 = [
            x + radius - 1, y_note - stem_h + 6,
            x + radius + 8, y_note - stem_h + 11,
            x + radius + 6, y_note - stem_h + 14,
            x + radius - 1, y_note - stem_h + 11
        ]
        self.canvas.create_polygon(flag_points_2, fill=color, outline=color)


def analyze_rhythm_structure(hits: List[float], beats: int):
    """
    Analyse la structure rythmique du pattern pour determiner les notes et silences.

    Args:
        hits: Liste des positions des frappes (0.0 a 1.0 dans une mesure)
        beats: Nombre de temps dans la mesure

    Returns:
        Liste de dicts representant chaque element rythmique
    """
    if not hits:
        return []

    beat_duration = 1.0 / beats
    sorted_hits = sorted(hits)

    subdivision = _detect_subdivision(sorted_hits, beat_duration, beats)

    elements = []
    for beat_num in range(beats):
        beat_start = beat_num * beat_duration
        beat_end = (beat_num + 1) * beat_duration
        notes_in_beat = [h for h in hits if beat_start <= h < beat_end]

        if subdivision == 'triplet':
            _add_triplet_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat)
        elif subdivision == 'sixteenth':
            _add_sixteenth_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat)
        elif subdivision == 'eighth':
            _add_eighth_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat)
        else:
            _add_quarter_elements(elements, beat_num, beat_start, notes_in_beat)

    return elements


def _detect_subdivision(sorted_hits, beat_duration, beats):
    """Detecte le type de subdivision rythmique."""
    if len(sorted_hits) > 1:
        min_interval = min(
            sorted_hits[i+1] - sorted_hits[i]
            for i in range(len(sorted_hits) - 1)
        )
    else:
        min_interval = beat_duration

    # Verifier triolets
    if len(sorted_hits) % 3 == 0 and len(sorted_hits) > beats:
        triplet_interval = beat_duration / 3
        triplet_match = all(
            abs((sorted_hits[i+1] - sorted_hits[i]) - triplet_interval) < 0.01
            for i in range(len(sorted_hits) - 1)
            if (sorted_hits[i+1] - sorted_hits[i]) < beat_duration * 0.9
        )
        if triplet_match:
            return 'triplet'

    if min_interval < beat_duration * 0.3:
        return 'sixteenth'
    elif min_interval < beat_duration * 0.6:
        return 'eighth'
    return 'quarter'


def _add_quarter_elements(elements, beat_num, beat_start, notes_in_beat):
    """Ajoute les elements pour un temps en noires."""
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
        elements.append({
            'type': 'rest',
            'duration': 'quarter',
            'position': beat_start,
            'beat': beat_num,
            'group_id': None
        })


def _add_triplet_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat):
    """Ajoute les elements pour un temps en triolets."""
    triplet_interval = beat_duration / 3
    group_id = f'triplet_{beat_num}'

    for i in range(3):
        expected_pos = beat_start + i * triplet_interval
        found = _find_closest_note(notes_in_beat, expected_pos, triplet_interval * 0.4)
        if found is not None:
            elements.append({
                'type': 'note',
                'duration': 'triplet',
                'position': found,
                'beat': beat_num,
                'group_id': group_id
            })
        elif notes_in_beat:
            elements.append({
                'type': 'rest',
                'duration': 'triplet',
                'position': expected_pos,
                'beat': beat_num,
                'group_id': group_id
            })


def _add_eighth_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat):
    """Ajoute les elements pour un temps en croches."""
    eighth_interval = beat_duration / 2
    group_id = f'eighth_{beat_num}'

    for i in range(2):
        expected_pos = beat_start + i * eighth_interval
        found = _find_closest_note(notes_in_beat, expected_pos, eighth_interval * 0.4)
        if found is not None:
            elements.append({
                'type': 'note',
                'duration': 'eighth',
                'position': found,
                'beat': beat_num,
                'group_id': group_id
            })
        elif notes_in_beat:
            elements.append({
                'type': 'rest',
                'duration': 'eighth',
                'position': expected_pos,
                'beat': beat_num,
                'group_id': group_id
            })


def _add_sixteenth_elements(elements, beat_num, beat_start, beat_duration, notes_in_beat):
    """Ajoute les elements pour un temps en doubles croches."""
    sixteenth_interval = beat_duration / 4
    group_id = f'sixteenth_{beat_num}'

    for i in range(4):
        expected_pos = beat_start + i * sixteenth_interval
        found = _find_closest_note(notes_in_beat, expected_pos, sixteenth_interval * 0.4)
        if found is not None:
            elements.append({
                'type': 'note',
                'duration': 'sixteenth',
                'position': found,
                'beat': beat_num,
                'group_id': group_id
            })
        elif notes_in_beat:
            elements.append({
                'type': 'rest',
                'duration': 'sixteenth',
                'position': expected_pos,
                'beat': beat_num,
                'group_id': group_id
            })


def _find_closest_note(notes_in_beat, expected_pos, tolerance):
    """Cherche une note proche de la position attendue."""
    for note_pos in notes_in_beat:
        if abs(note_pos - expected_pos) < tolerance:
            return note_pos
    return None
