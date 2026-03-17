"""
Default rhythm patterns for eighth-note time signatures (5/8, 7/8, 9/8).
Split from default_patterns.py for modularity.
"""

from src.core.rhythm_engine import RhythmPattern


def _get_5_8_basic():
    """Returns basic 5/8 patterns (complexity 1-3)."""
    return [
        RhythmPattern(
            id='5_8_basic_1',
            name='5/8 - Croches simples',
            signature=(5, 8),
            hits=[0.0, 0.2, 0.4, 0.6, 0.8],
            complexity=1,
            description='5 croches regulieres'
        ),
        RhythmPattern(
            id='5_8_2plus3',
            name='5/8 - Pattern 2+3',
            signature=(5, 8),
            hits=[0.0, 0.4],
            complexity=2,
            description='Groupement 2+3'
        ),
        RhythmPattern(
            id='5_8_3plus2',
            name='5/8 - Pattern 3+2',
            signature=(5, 8),
            hits=[0.0, 0.6],
            complexity=2,
            description='Groupement 3+2'
        ),
        RhythmPattern(
            id='5_8_sixteenth_1',
            name='5/8 - Doubles croches C1',
            signature=(5, 8),
            hits=[0.0, 0.1, 0.2, 0.4, 0.6, 0.8],
            complexity=3,
            description='2 doubles croches sur croche 1, puis croches'
        ),
    ]


def _get_5_8_advanced():
    """Returns advanced 5/8 patterns (complexity 3-5)."""
    return [
        RhythmPattern(
            id='5_8_syncopated',
            name='5/8 - Syncopes',
            signature=(5, 8),
            hits=[0.1, 0.3, 0.5, 0.7, 0.9],
            complexity=3,
            description='Doubles croches sur contretemps'
        ),
        RhythmPattern(
            id='5_8_sixteenth_all',
            name='5/8 - Toutes doubles croches',
            signature=(5, 8),
            hits=[i * 0.1 for i in range(10)],
            complexity=4,
            description='10 doubles croches regulieres'
        ),
        RhythmPattern(
            id='5_8_complex_2plus3',
            name='5/8 - Syncope 2+3',
            signature=(5, 8),
            hits=[0.0, 0.1, 0.3, 0.4, 0.5, 0.7],
            complexity=4,
            description='Pattern 2+3 avec subdivisions'
        ),
        RhythmPattern(
            id='5_8_triplets',
            name='5/8 - Triolets',
            signature=(5, 8),
            hits=[0.0, 0.067, 0.133, 0.2, 0.267, 0.333, 0.4, 0.467, 0.533, 0.6, 0.667, 0.733, 0.8, 0.867, 0.933],
            complexity=5,
            description='Triolets de doubles croches (3 par croche)'
        ),
    ]


def get_5_8_patterns():
    """Returns default patterns for 5/8 time signature."""
    return _get_5_8_basic() + _get_5_8_advanced()


def _get_7_8_basic():
    """Returns basic 7/8 patterns (complexity 1-3)."""
    return [
        RhythmPattern(
            id='7_8_basic_1',
            name='7/8 - Croches simples',
            signature=(7, 8),
            hits=[0.0, 1/7, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=1,
            description='7 croches regulieres'
        ),
        RhythmPattern(
            id='7_8_2plus2plus3',
            name='7/8 - Pattern 2+2+3',
            signature=(7, 8),
            hits=[0.0, 2/7, 4/7],
            complexity=2,
            description='Groupement 2+2+3 (style balkanique)'
        ),
        RhythmPattern(
            id='7_8_3plus2plus2',
            name='7/8 - Pattern 3+2+2',
            signature=(7, 8),
            hits=[0.0, 3/7, 5/7],
            complexity=2,
            description='Groupement 3+2+2'
        ),
        RhythmPattern(
            id='7_8_3plus4',
            name='7/8 - Pattern 3+4',
            signature=(7, 8),
            hits=[0.0, 3/7],
            complexity=2,
            description='Groupement 3+4'
        ),
    ]


def _get_7_8_advanced():
    """Returns advanced 7/8 patterns (complexity 3-5)."""
    return [
        RhythmPattern(
            id='7_8_sixteenth_1',
            name='7/8 - Doubles croches C1',
            signature=(7, 8),
            hits=[0.0, 1/14, 1/7, 2/7, 3/7, 4/7, 5/7, 6/7],
            complexity=3,
            description='2 doubles croches sur croche 1, puis croches'
        ),
        RhythmPattern(
            id='7_8_syncopated',
            name='7/8 - Syncopes',
            signature=(7, 8),
            hits=[1/14, 3/14, 5/14, 7/14, 9/14, 11/14, 13/14],
            complexity=3,
            description='Doubles croches sur contretemps'
        ),
        RhythmPattern(
            id='7_8_sixteenth_all',
            name='7/8 - Toutes doubles croches',
            signature=(7, 8),
            hits=[i/14 for i in range(14)],
            complexity=4,
            description='14 doubles croches regulieres'
        ),
        RhythmPattern(
            id='7_8_complex_2plus2plus3',
            name='7/8 - Syncope 2+2+3',
            signature=(7, 8),
            hits=[0.0, 1/14, 2/7, 3/14 + 2/7, 4/7, 5/14 + 4/7],
            complexity=4,
            description='Pattern 2+2+3 avec doubles croches'
        ),
        RhythmPattern(
            id='7_8_aksak_complex',
            name='7/8 - Aksak complexe',
            signature=(7, 8),
            hits=[0.0, 1/21, 2/21, 1/7, 4/21, 5/21, 2/7, 7/21, 3/7, 10/21, 4/7, 13/21],
            complexity=5,
            description='Rythme aksak avec triolets'
        ),
    ]


def get_7_8_patterns():
    """Returns default patterns for 7/8 time signature."""
    return _get_7_8_basic() + _get_7_8_advanced()


def _get_9_8_basic():
    """Returns basic 9/8 patterns (complexity 1-3)."""
    return [
        RhythmPattern(
            id='9_8_basic_1',
            name='9/8 - Croches simples',
            signature=(9, 8),
            hits=[i/9 for i in range(9)],
            complexity=1,
            description='9 croches regulieres'
        ),
        RhythmPattern(
            id='9_8_3plus3plus3',
            name='9/8 - Pattern 3+3+3',
            signature=(9, 8),
            hits=[0.0, 3/9, 6/9],
            complexity=2,
            description='Groupement ternaire classique'
        ),
        RhythmPattern(
            id='9_8_2plus2plus2plus3',
            name='9/8 - Pattern 2+2+2+3',
            signature=(9, 8),
            hits=[0.0, 2/9, 4/9, 6/9],
            complexity=3,
            description='Groupement aksak 2+2+2+3'
        ),
        RhythmPattern(
            id='9_8_2plus2plus5',
            name='9/8 - Pattern 2+2+5',
            signature=(9, 8),
            hits=[0.0, 2/9, 4/9],
            complexity=2,
            description='Groupement 2+2+5'
        ),
        RhythmPattern(
            id='9_8_sixteenth_1',
            name='9/8 - Doubles croches C1',
            signature=(9, 8),
            hits=[0.0, 1/18, 1/9, 2/9, 3/9, 4/9, 5/9, 6/9, 7/9, 8/9],
            complexity=3,
            description='2 doubles croches sur croche 1, puis croches'
        ),
    ]


def _get_9_8_advanced():
    """Returns advanced 9/8 patterns (complexity 3-5)."""
    return [
        RhythmPattern(
            id='9_8_syncopated',
            name='9/8 - Syncopes',
            signature=(9, 8),
            hits=[1/18, 3/18, 5/18, 7/18, 9/18, 11/18, 13/18, 15/18, 17/18],
            complexity=3,
            description='Doubles croches sur contretemps'
        ),
        RhythmPattern(
            id='9_8_sixteenth_all',
            name='9/8 - Toutes doubles croches',
            signature=(9, 8),
            hits=[i/18 for i in range(18)],
            complexity=4,
            description='18 doubles croches regulieres'
        ),
        RhythmPattern(
            id='9_8_complex_3plus3plus3',
            name='9/8 - Syncope 3+3+3',
            signature=(9, 8),
            hits=[0.0, 1/18, 3/9, 1/18 + 3/9, 6/9, 1/18 + 6/9],
            complexity=4,
            description='Pattern ternaire avec doubles croches'
        ),
        RhythmPattern(
            id='9_8_triplet_complex',
            name='9/8 - Triolets complexes',
            signature=(9, 8),
            hits=[0.0, 1/27, 2/27, 3/27, 5/27, 7/27, 9/27, 11/27, 13/27, 15/27, 17/27, 19/27, 21/27, 23/27, 25/27],
            complexity=5,
            description='Triolets de doubles croches (variations)'
        ),
        RhythmPattern(
            id='9_8_aksak_asymmetric',
            name='9/8 - Aksak asymetrique',
            signature=(9, 8),
            hits=[0.0, 1/18, 2/9, 4/9, 1/18 + 4/9, 6/9, 7/9, 1/18 + 7/9],
            complexity=5,
            description='Pattern aksak avec contretemps'
        ),
    ]


def get_9_8_patterns():
    """Returns default patterns for 9/8 time signature."""
    return _get_9_8_basic() + _get_9_8_advanced()
