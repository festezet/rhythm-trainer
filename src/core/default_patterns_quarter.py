"""
Default rhythm patterns for quarter-note time signatures (3/4, 4/4, 5/4, 7/4).
Split from default_patterns.py for modularity.
"""

from src.core.rhythm_engine import RhythmPattern


def get_3_4_patterns():
    """Returns default patterns for 3/4 time signature."""
    return [
        RhythmPattern(
            id='3_4_basic',
            name='3/4 - Noires simples',
            signature=(3, 4),
            hits=[0.0, 1/3, 2/3],
            complexity=1,
            description='3 noires regulieres (valse)'
        ),
        RhythmPattern(
            id='3_4_eighth_all',
            name='3/4 - Toutes croches',
            signature=(3, 4),
            hits=[i/6 for i in range(6)],
            complexity=2,
            description='6 croches regulieres'
        ),
        RhythmPattern(
            id='3_4_triplets',
            name='3/4 - Triolets',
            signature=(3, 4),
            hits=[i/9 for i in range(9)],
            complexity=2,
            description='Triolets de croches (3 par temps)'
        ),
        RhythmPattern(
            id='3_4_sixteenth_1',
            name='3/4 - Doubles croches T1',
            signature=(3, 4),
            hits=[0.0, 1/12, 2/12, 3/12, 1/3, 2/3],
            complexity=3,
            description='4 doubles croches sur temps 1, puis noires'
        ),
        RhythmPattern(
            id='3_4_sixteenth_all',
            name='3/4 - Toutes doubles croches',
            signature=(3, 4),
            hits=[i/12 for i in range(12)],
            complexity=4,
            description='12 doubles croches regulieres'
        ),
    ]


def _get_4_4_basic():
    """Returns basic 4/4 patterns (complexity 1-2)."""
    return [
        RhythmPattern(
            id='4_4_basic',
            name='4/4 - Noires simples',
            signature=(4, 4),
            hits=[0.0, 0.25, 0.5, 0.75],
            complexity=1,
            description='4 noires regulieres (temps commun)'
        ),
        RhythmPattern(
            id='4_4_eighth_all',
            name='4/4 - Toutes croches',
            signature=(4, 4),
            hits=[i/8 for i in range(8)],
            complexity=2,
            description='8 croches regulieres'
        ),
        RhythmPattern(
            id='4_4_triplets',
            name='4/4 - Triolets',
            signature=(4, 4),
            hits=[i/12 for i in range(12)],
            complexity=2,
            description='Triolets de croches (3 par temps)'
        ),
        RhythmPattern(
            id='4_4_backbeat',
            name='4/4 - Backbeat',
            signature=(4, 4),
            hits=[0.25, 0.75],
            complexity=2,
            description='Backbeat rock (temps 2 et 4)'
        ),
    ]


def _get_4_4_advanced():
    """Returns advanced 4/4 patterns (complexity 3-4)."""
    return [
        RhythmPattern(
            id='4_4_sixteenth_1',
            name='4/4 - Doubles croches T1',
            signature=(4, 4),
            hits=[0.0, 0.0625, 0.125, 0.1875, 0.25, 0.5, 0.75],
            complexity=3,
            description='4 doubles croches sur temps 1, puis noires'
        ),
        RhythmPattern(
            id='4_4_syncopated',
            name='4/4 - Syncopes',
            signature=(4, 4),
            hits=[0.125, 0.375, 0.625, 0.875],
            complexity=3,
            description='Croches sur les contretemps'
        ),
        RhythmPattern(
            id='4_4_sixteenth_all',
            name='4/4 - Toutes doubles croches',
            signature=(4, 4),
            hits=[i/16 for i in range(16)],
            complexity=4,
            description='16 doubles croches regulieres'
        ),
        RhythmPattern(
            id='4_4_sextuplets',
            name='4/4 - Sextolets',
            signature=(4, 4),
            hits=[i/24 for i in range(24)],
            complexity=4,
            description='Sextolets (6 notes par temps)'
        ),
    ]


def get_4_4_patterns():
    """Returns default patterns for 4/4 time signature."""
    return _get_4_4_basic() + _get_4_4_advanced()


def _get_5_4_basic():
    """Returns basic 5/4 patterns (complexity 1-3)."""
    return [
        RhythmPattern(
            id='5_4_basic_1',
            name='5/4 - Noires simples',
            signature=(5, 4),
            hits=[0.0, 0.2, 0.4, 0.6, 0.8],
            complexity=1,
            description='5 noires regulieres'
        ),
        RhythmPattern(
            id='5_4_eighth_1',
            name='5/4 - Croches temps 1-2',
            signature=(5, 4),
            hits=[0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8],
            complexity=2,
            description='Croches sur temps 1-2, noires sur 3-4-5'
        ),
        RhythmPattern(
            id='5_4_eighth_all',
            name='5/4 - Toutes croches',
            signature=(5, 4),
            hits=[i * 0.1 for i in range(10)],
            complexity=2,
            description='10 croches regulieres'
        ),
        RhythmPattern(
            id='5_4_3plus2',
            name='5/4 - Pattern 3+2',
            signature=(5, 4),
            hits=[0.0, 0.6],
            complexity=3,
            description='Groupement 3+2 (style Take Five)'
        ),
        RhythmPattern(
            id='5_4_syncopated',
            name='5/4 - Syncopes',
            signature=(5, 4),
            hits=[0.1, 0.3, 0.5, 0.7, 0.9],
            complexity=3,
            description='Croches sur les contretemps'
        ),
    ]


def _get_5_4_advanced():
    """Returns advanced 5/4 patterns (complexity 3-5)."""
    return [
        RhythmPattern(
            id='5_4_mixed_1',
            name='5/4 - Mixte (C-C-N-N)',
            signature=(5, 4),
            hits=[0.0, 0.1, 0.2, 0.4, 0.6],
            complexity=3,
            description='Croche+Croche+Noire+Noire+Noire'
        ),
        RhythmPattern(
            id='5_4_sixteenth_1',
            name='5/4 - Doubles croches T1',
            signature=(5, 4),
            hits=[0.0, 0.05, 0.1, 0.15, 0.2, 0.4, 0.6, 0.8],
            complexity=4,
            description='4 doubles croches sur temps 1, puis noires'
        ),
        RhythmPattern(
            id='5_4_complex_syncopation',
            name='5/4 - Syncope complexe',
            signature=(5, 4),
            hits=[0.0, 0.15, 0.3, 0.5, 0.65, 0.8],
            complexity=4,
            description='Syncopes avec doubles croches'
        ),
        RhythmPattern(
            id='5_4_sixteenth_all',
            name='5/4 - Toutes doubles croches',
            signature=(5, 4),
            hits=[i * 0.05 for i in range(20)],
            complexity=5,
            description='20 doubles croches regulieres'
        ),
    ]


def get_5_4_patterns():
    """Returns default patterns for 5/4 time signature."""
    return _get_5_4_basic() + _get_5_4_advanced()


def _get_7_4_basic():
    """Returns basic 7/4 patterns (complexity 1-3)."""
    return [
        RhythmPattern(
            id='7_4_basic_1',
            name='7/4 - Noires simples',
            signature=(7, 4),
            hits=[0.0, 1/7, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=1,
            description='7 noires regulieres'
        ),
        RhythmPattern(
            id='7_4_eighth_all',
            name='7/4 - Toutes croches',
            signature=(7, 4),
            hits=[i/14 for i in range(14)],
            complexity=2,
            description='14 croches regulieres'
        ),
        RhythmPattern(
            id='7_4_4plus3',
            name='7/4 - Pattern 4+3',
            signature=(7, 4),
            hits=[0.0, 4/7],
            complexity=3,
            description='Groupement 4+3 (style Money - Pink Floyd)'
        ),
        RhythmPattern(
            id='7_4_3plus2plus2',
            name='7/4 - Pattern 3+2+2',
            signature=(7, 4),
            hits=[0.0, 3/7, 5/7],
            complexity=3,
            description='Groupement 3+2+2'
        ),
    ]


def _get_7_4_advanced():
    """Returns advanced 7/4 patterns (complexity 3-5)."""
    return [
        RhythmPattern(
            id='7_4_syncopated',
            name='7/4 - Syncopes',
            signature=(7, 4),
            hits=[i/14 + 1/28 for i in range(7)],
            complexity=3,
            description='Croches sur les contretemps'
        ),
        RhythmPattern(
            id='7_4_sixteenth_1',
            name='7/4 - Doubles croches T1-2',
            signature=(7, 4),
            hits=[0.0, 1/28, 2/28, 3/28, 1/7, 5/28, 6/28, 7/28, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=4,
            description='Doubles croches sur temps 1-2, puis noires'
        ),
        RhythmPattern(
            id='7_4_complex_syncopation',
            name='7/4 - Syncope complexe',
            signature=(7, 4),
            hits=[0.0, 1/14, 3/14, 5/14, 7/14, 9/14, 11/14, 13/14],
            complexity=5,
            description='Pattern syncope avec contretemps'
        ),
    ]


def get_7_4_patterns():
    """Returns default patterns for 7/4 time signature."""
    return _get_7_4_basic() + _get_7_4_advanced()
