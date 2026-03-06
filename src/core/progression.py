"""
Système de progression pédagogique.
Gère les niveaux de difficulté et le déblocage.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Level:
    """Représente un niveau de progression."""
    id: int
    name: str
    complexity: int  # 1-5
    description: str
    required_score: int  # Score minimum pour débloquer le suivant
    patterns: List[str]  # IDs des patterns de ce niveau


class ProgressionSystem:
    """Gère la progression de l'utilisateur."""

    # Niveaux de complexité
    COMPLEXITY_NAMES = {
        1: "Noires",
        2: "Croches",
        3: "Syncopes",
        4: "Patterns complexes",
        5: "Expert"
    }

    def __init__(self, progress_db_path: str = None):
        self.progress_db_path = progress_db_path
        self.levels = self._create_levels()
        self.user_progress = self._load_progress()

    def _create_levels(self) -> List[Level]:
        """Crée les niveaux de progression."""
        return [
            # Niveau 1: Noires simples
            Level(
                id=1,
                name="Debutant - Noires",
                complexity=1,
                description="Patterns simples avec noires regulieres",
                required_score=60,
                patterns=['5_4_basic_1', '7_4_basic_1', '5_8_basic_1',
                         '7_8_basic_1', '9_8_basic_1']
            ),

            # Niveau 2: Introduction aux groupements
            Level(
                id=2,
                name="Groupements basiques",
                complexity=2,
                description="Apprendre les groupements 2+3, 3+2, etc.",
                required_score=65,
                patterns=['5_8_2plus3', '5_8_3plus2', '7_8_2plus2plus3',
                         '7_8_3plus2plus2', '9_8_3plus3plus3']
            ),

            # Niveau 3: Croches et subdivisions
            Level(
                id=3,
                name="Croches",
                complexity=2,
                description="Patterns avec croches sur certains temps",
                required_score=70,
                patterns=['5_4_eighth_1', '9_8_2plus2plus2plus3']
            ),

            # Niveau 4: Syncopes
            Level(
                id=4,
                name="Syncopes",
                complexity=3,
                description="Patterns avec deplacements d'accents",
                required_score=75,
                patterns=['5_4_3plus2', '7_4_4plus3']
            ),

            # Niveau 5: Expert (tous les patterns)
            Level(
                id=5,
                name="Expert",
                complexity=4,
                description="Tous les patterns, tempos rapides",
                required_score=80,
                patterns=[]  # Tous les patterns disponibles
            ),
        ]

    def _load_progress(self) -> Dict:
        """Charge la progression de l'utilisateur."""
        default = {
            'current_level': 1,
            'unlocked_levels': [1],
            'pattern_scores': {},  # pattern_id -> best_score
            'total_practice_time': 0,
            'sessions_count': 0
        }

        if self.progress_db_path:
            progress_file = Path(self.progress_db_path).parent / 'user_progress.json'
            if progress_file.exists():
                try:
                    with open(progress_file, 'r') as f:
                        return {**default, **json.load(f)}
                except Exception:
                    pass

        return default

    def save_progress(self):
        """Sauvegarde la progression."""
        if self.progress_db_path:
            progress_file = Path(self.progress_db_path).parent / 'user_progress.json'
            with open(progress_file, 'w') as f:
                json.dump(self.user_progress, f, indent=2)

    def get_current_level(self) -> Level:
        """Retourne le niveau actuel."""
        level_id = self.user_progress['current_level']
        return self.levels[level_id - 1]

    def get_available_patterns(self) -> List[str]:
        """Retourne les patterns disponibles selon le niveau."""
        available = []
        for level_id in self.user_progress['unlocked_levels']:
            level = self.levels[level_id - 1]
            available.extend(level.patterns)
        return list(set(available))

    def get_recommended_pattern(self) -> Optional[str]:
        """Suggère un pattern à pratiquer."""
        level = self.get_current_level()
        scores = self.user_progress['pattern_scores']

        # Trouver le pattern avec le score le plus bas
        worst_pattern = None
        worst_score = 100

        for pattern_id in level.patterns:
            score = scores.get(pattern_id, 0)
            if score < worst_score:
                worst_score = score
                worst_pattern = pattern_id

        return worst_pattern

    def record_score(self, pattern_id: str, score: int):
        """Enregistre un score pour un pattern."""
        scores = self.user_progress['pattern_scores']

        # Mettre à jour le meilleur score
        if pattern_id not in scores or score > scores[pattern_id]:
            scores[pattern_id] = score

        self.user_progress['sessions_count'] += 1

        # Vérifier si on peut débloquer un niveau
        self._check_level_unlock()
        self.save_progress()

    def _check_level_unlock(self):
        """Vérifie si un nouveau niveau peut être débloqué."""
        current_level = self.get_current_level()
        scores = self.user_progress['pattern_scores']

        if current_level.id >= len(self.levels):
            return  # Déjà au max

        # Calculer le score moyen du niveau actuel
        level_scores = [
            scores.get(p, 0) for p in current_level.patterns
        ]

        if not level_scores:
            return

        avg_score = sum(level_scores) / len(level_scores)

        # Si score suffisant, débloquer le niveau suivant
        if avg_score >= current_level.required_score:
            next_level = current_level.id + 1
            if next_level not in self.user_progress['unlocked_levels']:
                self.user_progress['unlocked_levels'].append(next_level)
                self.user_progress['current_level'] = next_level
                print(f"Niveau {next_level} débloqué !")

    def is_pattern_unlocked(self, pattern_id: str) -> bool:
        """Vérifie si un pattern est débloqué."""
        return pattern_id in self.get_available_patterns()

    def get_level_progress(self, level_id: int) -> Dict:
        """Retourne la progression pour un niveau."""
        level = self.levels[level_id - 1]
        scores = self.user_progress['pattern_scores']

        pattern_progress = []
        for pattern_id in level.patterns:
            pattern_progress.append({
                'pattern_id': pattern_id,
                'score': scores.get(pattern_id, 0),
                'completed': scores.get(pattern_id, 0) >= level.required_score
            })

        completed = sum(1 for p in pattern_progress if p['completed'])

        return {
            'level': level.name,
            'complexity': level.complexity,
            'patterns': pattern_progress,
            'completed_count': completed,
            'total_count': len(level.patterns),
            'progress_percent': (completed / len(level.patterns) * 100) if level.patterns else 0,
            'unlocked': level_id in self.user_progress['unlocked_levels']
        }

    def get_stats_summary(self) -> Dict:
        """Retourne un résumé des statistiques."""
        scores = self.user_progress['pattern_scores']

        if scores:
            avg_score = sum(scores.values()) / len(scores)
            best_score = max(scores.values())
        else:
            avg_score = 0
            best_score = 0

        return {
            'current_level': self.get_current_level().name,
            'unlocked_levels': len(self.user_progress['unlocked_levels']),
            'total_levels': len(self.levels),
            'patterns_practiced': len(scores),
            'average_score': round(avg_score, 1),
            'best_score': best_score,
            'total_sessions': self.user_progress['sessions_count']
        }

    def reset_progress(self):
        """Réinitialise la progression (attention!)."""
        self.user_progress = {
            'current_level': 1,
            'unlocked_levels': [1],
            'pattern_scores': {},
            'total_practice_time': 0,
            'sessions_count': 0
        }
        self.save_progress()


if __name__ == "__main__":
    # Test du système de progression
    system = ProgressionSystem()

    print("=== Système de Progression ===")
    print(f"\nNiveau actuel: {system.get_current_level().name}")

    print("\nPatterns disponibles:")
    for pattern_id in system.get_available_patterns():
        print(f"  - {pattern_id}")

    print("\nProgression niveau 1:")
    progress = system.get_level_progress(1)
    print(f"  {progress['completed_count']}/{progress['total_count']} complétés")

    print("\nStatistiques:")
    stats = system.get_stats_summary()
    for key, value in stats.items():
        print(f"  {key}: {value}")
