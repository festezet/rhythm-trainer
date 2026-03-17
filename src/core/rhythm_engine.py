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
        """Crée les patterns par défaut (charge depuis default_patterns.py)."""
        from src.core.default_patterns import get_all_default_patterns
        self.patterns = get_all_default_patterns()

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
