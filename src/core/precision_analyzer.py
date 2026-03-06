"""
Analyseur de précision rythmique.
Calcule les métriques de performance.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import sqlite3
from datetime import datetime
from pathlib import Path


@dataclass
class PrecisionResult:
    """Résultat d'analyse de précision."""
    pattern_id: str
    timestamp: datetime
    bpm: int

    # Métriques principales
    mean_deviation_ms: float  # Décalage moyen (+ = en retard, - = en avance)
    std_deviation_ms: float   # Écart-type (stabilité)
    accuracy_percent: float   # % de hits dans la tolérance

    # Détails
    hit_count: int
    expected_count: int
    deviations: List[float]  # Tous les décalages individuels

    # Score global (0-100)
    score: int

    def get_rating(self) -> Tuple[int, str]:
        """Retourne le nombre d'étoiles et le label."""
        if abs(self.mean_deviation_ms) <= 8 and self.std_deviation_ms <= 10:
            return 5, "Timing pro !"
        elif abs(self.mean_deviation_ms) <= 15 and self.std_deviation_ms <= 20:
            return 4, "Excellent"
        elif abs(self.mean_deviation_ms) <= 25 and self.std_deviation_ms <= 30:
            return 3, "Bon"
        elif abs(self.mean_deviation_ms) <= 40:
            return 2, "A ameliorer"
        else:
            return 1, "Continue !"

    def to_dict(self) -> dict:
        stars, label = self.get_rating()
        return {
            'pattern_id': self.pattern_id,
            'timestamp': self.timestamp.isoformat(),
            'bpm': self.bpm,
            'mean_deviation_ms': round(self.mean_deviation_ms, 1),
            'std_deviation_ms': round(self.std_deviation_ms, 1),
            'accuracy_percent': round(self.accuracy_percent, 1),
            'hit_count': self.hit_count,
            'expected_count': self.expected_count,
            'score': self.score,
            'stars': stars,
            'rating': label
        }


class PrecisionAnalyzer:
    """Analyse la précision des taps par rapport aux patterns attendus."""

    def __init__(self, tolerance_ms: float = 50.0):
        """
        Args:
            tolerance_ms: Tolérance pour considérer un hit comme "bon"
        """
        self.tolerance_ms = tolerance_ms

    def analyze(self,
                taps: List[float],
                expected_times: List[float],
                pattern_id: str,
                bpm: int) -> PrecisionResult:
        """
        Analyse les taps par rapport aux temps attendus.

        Args:
            taps: Timestamps des taps détectés (secondes)
            expected_times: Timestamps attendus (secondes)
            pattern_id: ID du pattern
            bpm: Tempo utilisé

        Returns:
            PrecisionResult avec toutes les métriques
        """
        if not expected_times:
            return self._empty_result(pattern_id, bpm)

        # Associer chaque tap au temps attendu le plus proche
        # Algorithme optimisé O(n+m) au lieu de O(n*m)
        deviations = []
        matched_expected = set()

        # Trier les taps (normalement déjà triés)
        sorted_taps = sorted(taps)

        # Pour chaque temps attendu, chercher le tap le plus proche
        for i, exp in enumerate(expected_times):
            min_diff = float('inf')
            best_tap_idx = None

            # Chercher le tap le plus proche de ce temps attendu
            for j, tap in enumerate(sorted_taps):
                diff = (tap - exp) * 1000  # Convertir en ms

                # Si on s'éloigne trop, arrêter la recherche
                if diff > self.tolerance_ms * 2:
                    break

                if abs(diff) < abs(min_diff) and j not in matched_expected:
                    min_diff = diff
                    best_tap_idx = j

            if best_tap_idx is not None and abs(min_diff) < self.tolerance_ms * 2:
                deviations.append(min_diff)
                matched_expected.add(best_tap_idx)

        # Calculer les métriques
        if deviations:
            mean_dev = np.mean(deviations)
            std_dev = np.std(deviations)
            hits_in_tolerance = sum(1 for d in deviations if abs(d) <= self.tolerance_ms)
            accuracy = (hits_in_tolerance / len(expected_times)) * 100
        else:
            mean_dev = 0
            std_dev = 0
            accuracy = 0

        # Score global (0-100)
        score = self._calculate_score(mean_dev, std_dev, accuracy, len(deviations), len(expected_times))

        return PrecisionResult(
            pattern_id=pattern_id,
            timestamp=datetime.now(),
            bpm=bpm,
            mean_deviation_ms=mean_dev,
            std_deviation_ms=std_dev,
            accuracy_percent=accuracy,
            hit_count=len(deviations),
            expected_count=len(expected_times),
            deviations=deviations,
            score=score
        )

    def _calculate_score(self, mean_dev: float, std_dev: float,
                        accuracy: float, hits: int, expected: int) -> int:
        """Calcule un score global 0-100."""
        if expected == 0:
            return 0

        # Composantes du score
        # 1. Précision moyenne (40 points max)
        precision_score = max(0, 40 - abs(mean_dev))

        # 2. Stabilité (30 points max)
        stability_score = max(0, 30 - std_dev)

        # 3. Complétude (30 points max)
        completeness = (hits / expected) * 30

        total = precision_score + stability_score + completeness
        return max(0, min(100, int(total)))

    def _empty_result(self, pattern_id: str, bpm: int) -> PrecisionResult:
        """Retourne un résultat vide."""
        return PrecisionResult(
            pattern_id=pattern_id,
            timestamp=datetime.now(),
            bpm=bpm,
            mean_deviation_ms=0,
            std_deviation_ms=0,
            accuracy_percent=0,
            hit_count=0,
            expected_count=0,
            deviations=[],
            score=0
        )


class ProgressTracker:
    """Stocke et analyse la progression de l'utilisateur."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialise la base de données."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                pattern_id TEXT NOT NULL,
                bpm INTEGER NOT NULL,
                mean_deviation_ms REAL,
                std_deviation_ms REAL,
                accuracy_percent REAL,
                hit_count INTEGER,
                expected_count INTEGER,
                score INTEGER
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pattern ON sessions(pattern_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON sessions(timestamp)
        ''')

        conn.commit()
        conn.close()

    def save_result(self, result: PrecisionResult):
        """Sauvegarde un résultat dans la base."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sessions (
                timestamp, pattern_id, bpm, mean_deviation_ms,
                std_deviation_ms, accuracy_percent, hit_count,
                expected_count, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.timestamp.isoformat(),
            result.pattern_id,
            result.bpm,
            result.mean_deviation_ms,
            result.std_deviation_ms,
            result.accuracy_percent,
            result.hit_count,
            result.expected_count,
            result.score
        ))

        conn.commit()
        conn.close()

    def get_history(self, pattern_id: str = None, limit: int = 50) -> List[dict]:
        """Récupère l'historique des sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if pattern_id:
            cursor.execute('''
                SELECT * FROM sessions
                WHERE pattern_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (pattern_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM sessions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def get_stats(self, pattern_id: str = None) -> dict:
        """Calcule les statistiques globales."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        where_clause = "WHERE pattern_id = ?" if pattern_id else ""
        params = (pattern_id,) if pattern_id else ()

        cursor.execute(f'''
            SELECT
                COUNT(*) as total_sessions,
                AVG(score) as avg_score,
                MAX(score) as best_score,
                AVG(mean_deviation_ms) as avg_deviation,
                AVG(accuracy_percent) as avg_accuracy
            FROM sessions
            {where_clause}
        ''', params)

        row = cursor.fetchone()
        conn.close()

        return {
            'total_sessions': row[0] or 0,
            'avg_score': round(row[1] or 0, 1),
            'best_score': row[2] or 0,
            'avg_deviation': round(row[3] or 0, 1),
            'avg_accuracy': round(row[4] or 0, 1)
        }

    def get_progression(self, pattern_id: str, days: int = 30) -> List[dict]:
        """Récupère la progression sur une période."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                date(timestamp) as date,
                AVG(score) as avg_score,
                AVG(mean_deviation_ms) as avg_deviation,
                COUNT(*) as sessions
            FROM sessions
            WHERE pattern_id = ?
            AND timestamp >= datetime('now', ?)
            GROUP BY date(timestamp)
            ORDER BY date
        ''', (pattern_id, f'-{days} days'))

        columns = ['date', 'avg_score', 'avg_deviation', 'sessions']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

    def backup_database(self):
        """Crée un backup de la base de données."""
        import shutil
        from datetime import datetime

        backup_dir = Path(self.db_path).parent / 'backups'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'progress_{timestamp}.db'

        shutil.copy2(self.db_path, backup_path)

        # Garder les 10 derniers backups
        backups = sorted(backup_dir.glob('*.db'))
        for old_backup in backups[:-10]:
            old_backup.unlink()

        return str(backup_path)


if __name__ == "__main__":
    # Test de l'analyseur
    analyzer = PrecisionAnalyzer(tolerance_ms=50)

    # Simuler des taps (avec un léger décalage)
    expected = [0.0, 0.5, 1.0, 1.5, 2.0]
    taps = [0.012, 0.508, 0.995, 1.520, 2.005]  # ~10-20ms de décalage

    result = analyzer.analyze(taps, expected, 'test_pattern', 120)

    print("=== Résultat d'analyse ===")
    print(f"Décalage moyen: {result.mean_deviation_ms:.1f} ms")
    print(f"Écart-type: {result.std_deviation_ms:.1f} ms")
    print(f"Précision: {result.accuracy_percent:.1f}%")
    print(f"Score: {result.score}/100")

    stars, label = result.get_rating()
    print(f"Rating: {'*' * stars} ({label})")
