#!/usr/bin/env python3
"""
Rhythm Trainer - Mode CLI
Entrainement aux signatures rythmiques impaires depuis le terminal.

Usage:
    python3 cli.py list-patterns [--level N]
    python3 cli.py list-levels
    python3 cli.py calibrate
    python3 cli.py progress
"""

import argparse
import sys
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from src.core.progression import ProgressionSystem
from src.core.rhythm_engine import RhythmEngine


def cmd_list_levels(args):
    """Affiche les niveaux de progression"""
    ps = ProgressionSystem()

    print(f"{'Lvl':>3} {'Nom':<30} {'Complexite':>10} {'Score req':>10}")
    print("-" * 56)
    for level in ps.levels:
        unlocked = "OUI" if level.id in ps.user_progress.get('unlocked_levels', [1]) else "NON"
        print(f"{level.id:>3} {level.name:<30} {level.complexity:>10} {level.required_score:>10}   {unlocked}")

    print(f"\n{len(ps.levels)} niveau(x)")


def cmd_list_patterns(args):
    """Liste les patterns rythmiques disponibles"""
    engine = RhythmEngine()
    patterns = engine.get_all_patterns()

    if args.level:
        ps = ProgressionSystem()
        level = next((l for l in ps.levels if l.id == args.level), None)
        if level:
            patterns = [p for p in patterns if p.id in level.patterns]

    if not patterns:
        print("Aucun pattern trouve.")
        return

    print(f"{'ID':<20} {'Signature':<12} {'Groupements':<20} {'BPM':<10}")
    print("-" * 65)
    for p in patterns:
        sig = f"{p.numerator}/{p.denominator}" if hasattr(p, 'numerator') else str(getattr(p, 'time_signature', '?'))
        groupings = str(getattr(p, 'groupings', getattr(p, 'subdivisions', '')))
        bpm = str(getattr(p, 'default_bpm', getattr(p, 'bpm', '')))
        print(f"{p.id:<20} {sig:<12} {groupings:<20} {bpm:<10}")

    print(f"\n{len(patterns)} pattern(s)")


def cmd_calibrate(args):
    """Lance la calibration de la latence audio"""
    from src.audio.calibration import LatencyCalibrator

    print("Calibration de la latence audio...")
    print("Tapez sur la touche Entree en rythme avec les clics du metronome.\n")

    calibrator = LatencyCalibrator()
    try:
        latency = calibrator.calibrate()
        print(f"\nLatence detectee: {latency:.1f} ms")
        print("Calibration enregistree.")
    except Exception as e:
        print(f"Erreur de calibration: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_progress(args):
    """Affiche la progression de l'utilisateur"""
    ps = ProgressionSystem()
    progress = ps.user_progress

    print("=== Progression ===\n")
    print(f"  Niveau actuel:      {progress.get('current_level', 1)}")
    print(f"  Sessions:           {progress.get('sessions_count', 0)}")
    print(f"  Temps total:        {progress.get('total_practice_time', 0)}s")
    print()

    unlocked = progress.get('unlocked_levels', [1])
    for level in ps.levels:
        status = "Debloque" if level.id in unlocked else "Verrouille"
        print(f"  Niveau {level.id}: {level.name} [{status}]")

    scores = progress.get('pattern_scores', {})
    if scores:
        print(f"\n  Scores par pattern:")
        for pid, score in sorted(scores.items()):
            print(f"    {pid}: {score}")


def main():
    parser = argparse.ArgumentParser(
        description="Rhythm Trainer - CLI",
        prog="cli.py"
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # list-levels
    sub.add_parser('list-levels', help='Afficher les niveaux')

    # list-patterns
    p_patterns = sub.add_parser('list-patterns', help='Lister les patterns rythmiques')
    p_patterns.add_argument('--level', type=int, help='Filtrer par niveau')

    # calibrate
    sub.add_parser('calibrate', help='Calibrer la latence audio')

    # progress
    sub.add_parser('progress', help='Voir la progression')

    args = parser.parse_args()
    commands = {
        'list-levels': cmd_list_levels,
        'list-patterns': cmd_list_patterns,
        'calibrate': cmd_calibrate,
        'progress': cmd_progress,
    }
    commands[args.command](args)


if __name__ == '__main__':
    main()
