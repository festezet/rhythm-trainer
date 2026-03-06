#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rhythm Trainer - Application d'entrainement aux signatures rythmiques impaires.

Point d'entree principal.
"""

import sys
import logging
from pathlib import Path

# Ajouter le repertoire du projet au path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# Configurer le logging : console + fichier
LOG_FILE = PROJECT_DIR / 'data' / 'rhythm_trainer.log'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stderr),
    ]
)

logger = logging.getLogger('rhythm-trainer')

# Diagnostic audio au démarrage
def _audio_diagnostic():
    """Affiche les infos audio pour debug."""
    try:
        import sounddevice as sd
        logger.info(f"sounddevice {sd.__version__}, PortAudio {sd.get_portaudio_version()[1]}")
        default_in = sd.query_devices(kind='input')
        default_out = sd.query_devices(kind='output')
        logger.info(f"Input par defaut:  [{default_in['index']}] {default_in['name']} "
                     f"(channels={default_in['max_input_channels']}, "
                     f"sr={default_in['default_samplerate']})")
        logger.info(f"Output par defaut: [{default_out['index']}] {default_out['name']} "
                     f"(channels={default_out['max_output_channels']}, "
                     f"sr={default_out['default_samplerate']})")

        # Lister tous les périphériques d'entrée
        devices = sd.query_devices()
        input_devices = [(i, d['name']) for i, d in enumerate(devices) if d['max_input_channels'] > 0]
        logger.info(f"Peripheriques d'entree ({len(input_devices)}):")
        for idx, name in input_devices:
            logger.info(f"  [{idx}] {name}")
    except Exception as e:
        logger.error(f"Diagnostic audio echoue: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("=== Demarrage Rhythm Trainer ===")
    logger.info(f"Python {sys.version}")
    logger.info(f"Log fichier: {LOG_FILE}")
    _audio_diagnostic()

    from src.gui.main_window import main
    main()
