"""
Moteur de gestion des patterns rythmiques.
Définit les signatures et patterns disponibles.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Tuple
from pathlib import Path


@dataclass
class RhythmPattern:
    """Représente un pattern rythmique."""
    id: str
    name: str
    signature: Tuple[int, int]  # (beats, beat_value)
    hits: List[float]  # Positions des frappes (0.0 à 1.0)
    complexity: int  # 1-5 (noires=1, croches=2, syncopes=3, etc.)
    description: str = ""

    def get_hit_times(self, measure_duration: float) -> List[float]:
        """
        Convertit les positions en temps réels.

        Args:
            measure_duration: Durée d'une mesure en secondes

        Returns:
            Liste des temps de frappe en secondes
        """
        return [h * measure_duration for h in self.hits]

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'signature': list(self.signature),
            'hits': self.hits,
            'complexity': self.complexity,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RhythmPattern':
        return cls(
            id=data['id'],
            name=data['name'],
            signature=tuple(data['signature']),
            hits=data['hits'],
            complexity=data['complexity'],
            description=data.get('description', '')
        )


class RhythmEngine:
    """Gère les patterns et signatures rythmiques."""

    # Signatures supportées
    SIGNATURES = {
        '3/4': (3, 4),
        '4/4': (4, 4),
        '5/4': (5, 4),
        '7/4': (7, 4),
        '5/8': (5, 8),
        '7/8': (7, 8),
        '9/8': (9, 8),
    }

    def __init__(self, patterns_file: str = None):
        self.patterns: List[RhythmPattern] = []
        self.patterns_file = patterns_file

        if patterns_file and Path(patterns_file).exists():
            self.load_patterns(patterns_file)
        else:
            self._create_default_patterns()

    def _create_default_patterns(self):
        """Crée les patterns par défaut."""
        self.patterns = []

        # === 3/4 ===
        # Complexité 1: Noires simples
        self.patterns.append(RhythmPattern(
            id='3_4_basic',
            name='3/4 - Noires simples',
            signature=(3, 4),
            hits=[0.0, 1/3, 2/3],  # 3 noires
            complexity=1,
            description='3 noires régulières (valse)'
        ))

        # Complexité 2: Toutes croches
        self.patterns.append(RhythmPattern(
            id='3_4_eighth_all',
            name='3/4 - Toutes croches',
            signature=(3, 4),
            hits=[i/6 for i in range(6)],  # 6 croches
            complexity=2,
            description='6 croches régulières'
        ))

        # Complexité 2: Triolets (3 notes par temps)
        self.patterns.append(RhythmPattern(
            id='3_4_triplets',
            name='3/4 - Triolets',
            signature=(3, 4),
            hits=[i/9 for i in range(9)],  # 9 notes (3 triolets par temps × 3 temps)
            complexity=2,
            description='Triolets de croches (3 par temps)'
        ))

        # Complexité 3: Doubles croches sur premier temps
        self.patterns.append(RhythmPattern(
            id='3_4_sixteenth_1',
            name='3/4 - Doubles croches T1',
            signature=(3, 4),
            hits=[0.0, 1/12, 2/12, 3/12, 1/3, 2/3],
            complexity=3,
            description='4 doubles croches sur temps 1, puis noires'
        ))

        # Complexité 4: Toutes doubles croches
        self.patterns.append(RhythmPattern(
            id='3_4_sixteenth_all',
            name='3/4 - Toutes doubles croches',
            signature=(3, 4),
            hits=[i/12 for i in range(12)],  # 12 doubles croches
            complexity=4,
            description='12 doubles croches régulières'
        ))

        # === 4/4 ===
        # Complexité 1: Noires simples
        self.patterns.append(RhythmPattern(
            id='4_4_basic',
            name='4/4 - Noires simples',
            signature=(4, 4),
            hits=[0.0, 0.25, 0.5, 0.75],  # 4 noires
            complexity=1,
            description='4 noires régulières (temps commun)'
        ))

        # Complexité 2: Toutes croches
        self.patterns.append(RhythmPattern(
            id='4_4_eighth_all',
            name='4/4 - Toutes croches',
            signature=(4, 4),
            hits=[i/8 for i in range(8)],  # 8 croches
            complexity=2,
            description='8 croches régulières'
        ))

        # Complexité 2: Triolets (3 notes par temps)
        self.patterns.append(RhythmPattern(
            id='4_4_triplets',
            name='4/4 - Triolets',
            signature=(4, 4),
            hits=[i/12 for i in range(12)],  # 12 notes (3 triolets par temps × 4 temps)
            complexity=2,
            description='Triolets de croches (3 par temps)'
        ))

        # Complexité 2: Backbeat (accents temps 2 et 4)
        self.patterns.append(RhythmPattern(
            id='4_4_backbeat',
            name='4/4 - Backbeat',
            signature=(4, 4),
            hits=[0.25, 0.75],  # Temps 2 et 4
            complexity=2,
            description='Backbeat rock (temps 2 et 4)'
        ))

        # Complexité 3: Doubles croches sur premier temps
        self.patterns.append(RhythmPattern(
            id='4_4_sixteenth_1',
            name='4/4 - Doubles croches T1',
            signature=(4, 4),
            hits=[0.0, 0.0625, 0.125, 0.1875, 0.25, 0.5, 0.75],
            complexity=3,
            description='4 doubles croches sur temps 1, puis noires'
        ))

        # Complexité 3: Syncopes
        self.patterns.append(RhythmPattern(
            id='4_4_syncopated',
            name='4/4 - Syncopes',
            signature=(4, 4),
            hits=[0.125, 0.375, 0.625, 0.875],  # Entre les temps
            complexity=3,
            description='Croches sur les contretemps'
        ))

        # Complexité 4: Toutes doubles croches
        self.patterns.append(RhythmPattern(
            id='4_4_sixteenth_all',
            name='4/4 - Toutes doubles croches',
            signature=(4, 4),
            hits=[i/16 for i in range(16)],  # 16 doubles croches
            complexity=4,
            description='16 doubles croches régulières'
        ))

        # Complexité 4: Sextuplets (6 notes par temps sur 2 temps)
        self.patterns.append(RhythmPattern(
            id='4_4_sextuplets',
            name='4/4 - Sextolets',
            signature=(4, 4),
            hits=[i/24 for i in range(24)],  # 24 notes (6 par temps × 4 temps)
            complexity=4,
            description='Sextolets (6 notes par temps)'
        ))

        # === 5/4 ===
        # Complexité 1: Noires simples
        self.patterns.append(RhythmPattern(
            id='5_4_basic_1',
            name='5/4 - Noires simples',
            signature=(5, 4),
            hits=[0.0, 0.2, 0.4, 0.6, 0.8],  # 5 noires
            complexity=1,
            description='5 noires régulières'
        ))

        # Complexité 2: Avec croches
        self.patterns.append(RhythmPattern(
            id='5_4_eighth_1',
            name='5/4 - Croches temps 1-2',
            signature=(5, 4),
            hits=[0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8],
            complexity=2,
            description='Croches sur temps 1-2, noires sur 3-4-5'
        ))

        # Complexité 2: Toutes les croches
        self.patterns.append(RhythmPattern(
            id='5_4_eighth_all',
            name='5/4 - Toutes croches',
            signature=(5, 4),
            hits=[i * 0.1 for i in range(10)],  # 10 croches
            complexity=2,
            description='10 croches régulières'
        ))

        # Complexité 3: Pattern 3+2 (accents de groupement uniquement)
        self.patterns.append(RhythmPattern(
            id='5_4_3plus2',
            name='5/4 - Pattern 3+2',
            signature=(5, 4),
            hits=[0.0, 0.6],  # Accent sur beat 1 et beat 4 (groupe 3+2)
            complexity=3,
            description='Groupement 3+2 (style Take Five)'
        ))

        # Complexité 3: Syncopes (contretemps)
        self.patterns.append(RhythmPattern(
            id='5_4_syncopated',
            name='5/4 - Syncopes',
            signature=(5, 4),
            hits=[0.1, 0.3, 0.5, 0.7, 0.9],  # Entre les temps
            complexity=3,
            description='Croches sur les contretemps'
        ))

        # Complexité 3: Pattern mixte croche-noire
        self.patterns.append(RhythmPattern(
            id='5_4_mixed_1',
            name='5/4 - Mixte (C-C-N-N)',
            signature=(5, 4),
            hits=[0.0, 0.1, 0.2, 0.4, 0.6],
            complexity=3,
            description='Croche+Croche+Noire+Noire+Noire'
        ))

        # Complexité 4: Doubles croches temps 1
        self.patterns.append(RhythmPattern(
            id='5_4_sixteenth_1',
            name='5/4 - Doubles croches T1',
            signature=(5, 4),
            hits=[0.0, 0.05, 0.1, 0.15, 0.2, 0.4, 0.6, 0.8],
            complexity=4,
            description='4 doubles croches sur temps 1, puis noires'
        ))

        # Complexité 4: Pattern syncopé complexe
        self.patterns.append(RhythmPattern(
            id='5_4_complex_syncopation',
            name='5/4 - Syncopé complexe',
            signature=(5, 4),
            hits=[0.0, 0.15, 0.3, 0.5, 0.65, 0.8],
            complexity=4,
            description='Syncopes avec doubles croches'
        ))

        # Complexité 5: Toutes doubles croches
        self.patterns.append(RhythmPattern(
            id='5_4_sixteenth_all',
            name='5/4 - Toutes doubles croches',
            signature=(5, 4),
            hits=[i * 0.05 for i in range(20)],  # 20 doubles croches
            complexity=5,
            description='20 doubles croches régulières'
        ))

        # === 7/4 ===
        self.patterns.append(RhythmPattern(
            id='7_4_basic_1',
            name='7/4 - Noires simples',
            signature=(7, 4),
            hits=[0.0, 1/7, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=1,
            description='7 noires régulières'
        ))

        # Complexité 2: Toutes croches
        self.patterns.append(RhythmPattern(
            id='7_4_eighth_all',
            name='7/4 - Toutes croches',
            signature=(7, 4),
            hits=[i/14 for i in range(14)],  # 14 croches
            complexity=2,
            description='14 croches régulières'
        ))

        self.patterns.append(RhythmPattern(
            id='7_4_4plus3',
            name='7/4 - Pattern 4+3',
            signature=(7, 4),
            hits=[0.0, 4/7],  # Accent sur beat 1 et beat 5 (groupe 4+3)
            complexity=3,
            description='Groupement 4+3 (style Money - Pink Floyd)'
        ))

        # Complexité 3: Pattern 3+2+2
        self.patterns.append(RhythmPattern(
            id='7_4_3plus2plus2',
            name='7/4 - Pattern 3+2+2',
            signature=(7, 4),
            hits=[0.0, 3/7, 5/7],
            complexity=3,
            description='Groupement 3+2+2'
        ))

        # Complexité 3: Syncopes
        self.patterns.append(RhythmPattern(
            id='7_4_syncopated',
            name='7/4 - Syncopes',
            signature=(7, 4),
            hits=[i/14 + 1/28 for i in range(7)],  # Entre les temps
            complexity=3,
            description='Croches sur les contretemps'
        ))

        # Complexité 4: Doubles croches sur premiers temps
        self.patterns.append(RhythmPattern(
            id='7_4_sixteenth_1',
            name='7/4 - Doubles croches T1-2',
            signature=(7, 4),
            hits=[0.0, 1/28, 2/28, 3/28, 1/7, 5/28, 6/28, 7/28, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=4,
            description='Doubles croches sur temps 1-2, puis noires'
        ))

        # Complexité 5: Pattern très syncopé
        self.patterns.append(RhythmPattern(
            id='7_4_complex_syncopation',
            name='7/4 - Syncopé complexe',
            signature=(7, 4),
            hits=[0.0, 1/14, 3/14, 5/14, 7/14, 9/14, 11/14, 13/14],
            complexity=5,
            description='Pattern syncopé avec contretemps'
        ))

        # === 5/8 ===
        self.patterns.append(RhythmPattern(
            id='5_8_basic_1',
            name='5/8 - Croches simples',
            signature=(5, 8),
            hits=[0.0, 0.2, 0.4, 0.6, 0.8],
            complexity=1,
            description='5 croches régulières'
        ))

        self.patterns.append(RhythmPattern(
            id='5_8_2plus3',
            name='5/8 - Pattern 2+3',
            signature=(5, 8),
            hits=[0.0, 0.4],  # Accent sur 1 et 3
            complexity=2,
            description='Groupement 2+3'
        ))

        self.patterns.append(RhythmPattern(
            id='5_8_3plus2',
            name='5/8 - Pattern 3+2',
            signature=(5, 8),
            hits=[0.0, 0.6],  # Accent sur 1 et 4
            complexity=2,
            description='Groupement 3+2'
        ))

        # Complexité 3: Doubles croches sur croche 1
        self.patterns.append(RhythmPattern(
            id='5_8_sixteenth_1',
            name='5/8 - Doubles croches C1',
            signature=(5, 8),
            hits=[0.0, 0.1, 0.2, 0.4, 0.6, 0.8],
            complexity=3,
            description='2 doubles croches sur croche 1, puis croches'
        ))

        # Complexité 3: Syncopes (entre les croches)
        self.patterns.append(RhythmPattern(
            id='5_8_syncopated',
            name='5/8 - Syncopes',
            signature=(5, 8),
            hits=[0.1, 0.3, 0.5, 0.7, 0.9],
            complexity=3,
            description='Doubles croches sur contretemps'
        ))

        # Complexité 4: Toutes doubles croches
        self.patterns.append(RhythmPattern(
            id='5_8_sixteenth_all',
            name='5/8 - Toutes doubles croches',
            signature=(5, 8),
            hits=[i * 0.1 for i in range(10)],  # 10 doubles croches
            complexity=4,
            description='10 doubles croches régulières'
        ))

        # Complexité 4: Pattern syncopé complexe 2+3
        self.patterns.append(RhythmPattern(
            id='5_8_complex_2plus3',
            name='5/8 - Syncopé 2+3',
            signature=(5, 8),
            hits=[0.0, 0.1, 0.3, 0.4, 0.5, 0.7],
            complexity=4,
            description='Pattern 2+3 avec subdivisions'
        ))

        # Complexité 5: Triolets sur 5/8
        self.patterns.append(RhythmPattern(
            id='5_8_triplets',
            name='5/8 - Triolets',
            signature=(5, 8),
            hits=[0.0, 0.067, 0.133, 0.2, 0.267, 0.333, 0.4, 0.467, 0.533, 0.6, 0.667, 0.733, 0.8, 0.867, 0.933],
            complexity=5,
            description='Triolets de doubles croches (3 par croche)'
        ))

        # === 7/8 ===
        self.patterns.append(RhythmPattern(
            id='7_8_basic_1',
            name='7/8 - Croches simples',
            signature=(7, 8),
            hits=[0.0, 1/7, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=1,
            description='7 croches régulières'
        ))

        self.patterns.append(RhythmPattern(
            id='7_8_2plus2plus3',
            name='7/8 - Pattern 2+2+3',
            signature=(7, 8),
            hits=[0.0, 2/7, 4/7],  # Accents
            complexity=2,
            description='Groupement 2+2+3 (style balkanique)'
        ))

        self.patterns.append(RhythmPattern(
            id='7_8_3plus2plus2',
            name='7/8 - Pattern 3+2+2',
            signature=(7, 8),
            hits=[0.0, 3/7, 5/7],
            complexity=2,
            description='Groupement 3+2+2'
        ))

        # Complexité 3: Pattern 3+4
        self.patterns.append(RhythmPattern(
            id='7_8_3plus4',
            name='7/8 - Pattern 3+4',
            signature=(7, 8),
            hits=[0.0, 3/7],
            complexity=2,
            description='Groupement 3+4'
        ))

        # Complexité 3: Doubles croches sur première croche
        self.patterns.append(RhythmPattern(
            id='7_8_sixteenth_1',
            name='7/8 - Doubles croches C1',
            signature=(7, 8),
            hits=[0.0, 1/14, 1/7, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=3,
            description='2 doubles croches sur croche 1, puis croches'
        ))

        # Complexité 3: Syncopes (entre croches)
        self.patterns.append(RhythmPattern(
            id='7_8_syncopated',
            name='7/8 - Syncopes',
            signature=(7, 8),
            hits=[1/14, 3/14, 5/14, 7/14, 9/14, 11/14, 13/14],
            complexity=3,
            description='Doubles croches sur contretemps'
        ))

        # Complexité 4: Toutes doubles croches
        self.patterns.append(RhythmPattern(
            id='7_8_sixteenth_all',
            name='7/8 - Toutes doubles croches',
            signature=(7, 8),
            hits=[i/14 for i in range(14)],  # 14 doubles croches
            complexity=4,
            description='14 doubles croches régulières'
        ))

        # Complexité 4: Pattern 2+2+3 avec subdivisions
        self.patterns.append(RhythmPattern(
            id='7_8_complex_2plus2plus3',
            name='7/8 - Syncopé 2+2+3',
            signature=(7, 8),
            hits=[0.0, 1/14, 2/7, 3/14 + 2/7, 4/7, 5/14 + 4/7],
            complexity=4,
            description='Pattern 2+2+3 avec doubles croches'
        ))

        # Complexité 5: Aksak complexe
        self.patterns.append(RhythmPattern(
            id='7_8_aksak_complex',
            name='7/8 - Aksak complexe',
            signature=(7, 8),
            hits=[0.0, 1/21, 2/21, 1/7, 4/21, 5/21, 2/7, 7/21, 3/7, 10/21, 4/7, 13/21],
            complexity=5,
            description='Rythme aksak avec triolets'
        ))

        # === 9/8 ===
        self.patterns.append(RhythmPattern(
            id='9_8_basic_1',
            name='9/8 - Croches simples',
            signature=(9, 8),
            hits=[i/9 for i in range(9)],
            complexity=1,
            description='9 croches régulières'
        ))

        self.patterns.append(RhythmPattern(
            id='9_8_3plus3plus3',
            name='9/8 - Pattern 3+3+3',
            signature=(9, 8),
            hits=[0.0, 3/9, 6/9],
            complexity=2,
            description='Groupement ternaire classique'
        ))

        self.patterns.append(RhythmPattern(
            id='9_8_2plus2plus2plus3',
            name='9/8 - Pattern 2+2+2+3',
            signature=(9, 8),
            hits=[0.0, 2/9, 4/9, 6/9],
            complexity=3,
            description='Groupement aksak 2+2+2+3'
        ))

        # Complexité 2: Pattern 2+2+5
        self.patterns.append(RhythmPattern(
            id='9_8_2plus2plus5',
            name='9/8 - Pattern 2+2+5',
            signature=(9, 8),
            hits=[0.0, 2/9, 4/9],
            complexity=2,
            description='Groupement 2+2+5'
        ))

        # Complexité 3: Doubles croches sur première croche
        self.patterns.append(RhythmPattern(
            id='9_8_sixteenth_1',
            name='9/8 - Doubles croches C1',
            signature=(9, 8),
            hits=[0.0, 1/18, 1/9, 2/9, 3/9, 4/9, 5/9, 6/9, 7/9, 8/9],
            complexity=3,
            description='2 doubles croches sur croche 1, puis croches'
        ))

        # Complexité 3: Syncopes (entre croches)
        self.patterns.append(RhythmPattern(
            id='9_8_syncopated',
            name='9/8 - Syncopes',
            signature=(9, 8),
            hits=[1/18, 3/18, 5/18, 7/18, 9/18, 11/18, 13/18, 15/18, 17/18],
            complexity=3,
            description='Doubles croches sur contretemps'
        ))

        # Complexité 4: Toutes doubles croches
        self.patterns.append(RhythmPattern(
            id='9_8_sixteenth_all',
            name='9/8 - Toutes doubles croches',
            signature=(9, 8),
            hits=[i/18 for i in range(18)],  # 18 doubles croches
            complexity=4,
            description='18 doubles croches régulières'
        ))

        # Complexité 4: Pattern 3+3+3 avec subdivisions
        self.patterns.append(RhythmPattern(
            id='9_8_complex_3plus3plus3',
            name='9/8 - Syncopé 3+3+3',
            signature=(9, 8),
            hits=[0.0, 1/18, 3/9, 1/18 + 3/9, 6/9, 1/18 + 6/9],
            complexity=4,
            description='Pattern ternaire avec doubles croches'
        ))

        # Complexité 5: Pattern très complexe avec triolets
        self.patterns.append(RhythmPattern(
            id='9_8_triplet_complex',
            name='9/8 - Triolets complexes',
            signature=(9, 8),
            hits=[0.0, 1/27, 2/27, 3/27, 5/27, 7/27, 9/27, 11/27, 13/27, 15/27, 17/27, 19/27, 21/27, 23/27, 25/27],
            complexity=5,
            description='Triolets de doubles croches (variations)'
        ))

        # Complexité 5: Aksak asymétrique
        self.patterns.append(RhythmPattern(
            id='9_8_aksak_asymmetric',
            name='9/8 - Aksak asymétrique',
            signature=(9, 8),
            hits=[0.0, 1/18, 2/9, 4/9, 1/18 + 4/9, 6/9, 7/9, 1/18 + 7/9],
            complexity=5,
            description='Pattern aksak avec contretemps'
        ))

    def get_patterns_by_signature(self, signature: Tuple[int, int]) -> List[RhythmPattern]:
        """Retourne les patterns pour une signature donnée."""
        return [p for p in self.patterns if p.signature == signature]

    def get_patterns_by_complexity(self, max_complexity: int) -> List[RhythmPattern]:
        """Retourne les patterns jusqu'à un niveau de complexité."""
        return [p for p in self.patterns if p.complexity <= max_complexity]

    def get_pattern(self, pattern_id: str) -> RhythmPattern:
        """Retourne un pattern par son ID."""
        for p in self.patterns:
            if p.id == pattern_id:
                return p
        return None

    def get_measure_duration(self, bpm: int, signature: Tuple[int, int]) -> float:
        """
        Calcule la durée d'une mesure.

        Args:
            bpm: Tempo en BPM
            signature: (beats, beat_value)

        Returns:
            Durée en secondes
        """
        beats, beat_value = signature
        beat_duration = 60.0 / bpm

        # Note: on ne divise plus par 2 pour les signatures en /8
        # Le BPM représente directement les temps (croches en /8)

        return beat_duration * beats

    def save_patterns(self, filepath: str):
        """Sauvegarde les patterns dans un fichier JSON."""
        data = [p.to_dict() for p in self.patterns]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_patterns(self, filepath: str):
        """Charge les patterns depuis un fichier JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.patterns = [RhythmPattern.from_dict(d) for d in data]

    def list_signatures(self) -> List[str]:
        """Liste les signatures disponibles."""
        return list(self.SIGNATURES.keys())


if __name__ == "__main__":
    engine = RhythmEngine()

    print("=== Patterns disponibles ===")
    for sig_name, sig in engine.SIGNATURES.items():
        patterns = engine.get_patterns_by_signature(sig)
        print(f"\n{sig_name} ({len(patterns)} patterns):")
        for p in patterns:
            print(f"  - {p.name} (complexité {p.complexity})")

    # Sauvegarder pour référence
    engine.save_patterns('/data/projects/rhythm-trainer/data/patterns.json')
    print("\nPatterns sauvegardés dans data/patterns.json")
