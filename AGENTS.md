# AGENTS.md

## Project Overview

**Rhythm Trainer** is a desktop application for practicing odd time signatures (5/4, 7/4, 5/8, 7/8, 9/8). It features real-time tap detection with millisecond precision, 43 rhythmic patterns across 5 complexity levels, and an adaptive progression system.

## Key Facts

- **Author**: Fabrice Estezet
- **Stack**: Python 3, CustomTkinter, sounddevice (PortAudio), NumPy, SQLite
- **License**: Personal use
- **Status**: Production (v1.1.0)

## Architecture

```
main.py                         → GUI entry point
cli.py                          → CLI interface
src/audio/tap_detector.py       → Real-time tap detection via microphone
src/audio/metronome.py          → Metronome with accent patterns
src/audio/calibration.py        → Audio latency calibration
src/core/rhythm_engine.py       → Pattern management and time signatures
src/core/precision_analyzer.py  → Timing precision analysis
src/core/progression.py         → Adaptive level progression
src/gui/                        → CustomTkinter UI components
```

## Features

- 5 time signatures: 5/4, 7/4, 5/8, 7/8, 9/8
- 43 rhythmic patterns (basic to aksak)
- Real-time audio tap detection
- Precision scoring (millisecond accuracy)
- Adaptive difficulty progression
- SQLite-backed progress history

## Skills Demonstrated

- Real-time audio processing with sounddevice/PortAudio
- Signal processing and timing analysis with NumPy
- Desktop GUI development with CustomTkinter
- Music theory implementation (time signatures, subdivisions, aksak patterns)
- Adaptive learning algorithm design
- Low-latency audio calibration
