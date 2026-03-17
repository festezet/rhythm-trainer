"""
Default rhythm patterns data.
Thin wrapper that delegates to specialized modules by time signature category.
Split from a single 509-line file into quarter and eighth sub-modules.
"""

from src.core.default_patterns_quarter import (
    get_3_4_patterns,
    get_4_4_patterns,
    get_5_4_patterns,
    get_7_4_patterns,
)
from src.core.default_patterns_eighth import (
    get_5_8_patterns,
    get_7_8_patterns,
    get_9_8_patterns,
)


def get_all_default_patterns():
    """Returns all default patterns across all time signatures."""
    patterns = []
    patterns.extend(get_3_4_patterns())
    patterns.extend(get_4_4_patterns())
    patterns.extend(get_5_4_patterns())
    patterns.extend(get_7_4_patterns())
    patterns.extend(get_5_8_patterns())
    patterns.extend(get_7_8_patterns())
    patterns.extend(get_9_8_patterns())
    return patterns
