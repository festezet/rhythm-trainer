# Rhythm Trainer

Application d'entraînement aux signatures rythmiques impaires (5/4, 7/4, 5/8, 7/8, 9/8).

## 🎯 Objectif

Application d'entrainement aux signatures rythmiques impaires (5/4, 7/4, 5/8, 7/8, 9/8) avec detection de precision et suivi de progression.

## 📂 Structure

```
rhythm-trainer/
├── main.py          # Point d'entree GUI
├── cli.py           # Interface CLI
├── src/             # Modules sources
├── data/            # Base de donnees et logs
├── scripts/         # Scripts utilitaires
└── tests/           # Tests
```

## 🚀 Démarrage

```bash
cd /data/projects/rhythm-trainer
python3 cli.py       # Mode CLI
python3 main.py      # Mode GUI
```

## Description

Rhythm Trainer permet de s'entraîner à jouer des rythmes dans des signatures inhabituelles. L'application :
- Affiche des patterns rythmiques sur une timeline visuelle
- Joue un métronome avec accents sur le temps 1
- Détecte vos taps (frappes sur table avec un crayon)
- Mesure votre précision temporelle en millisecondes
- Suit votre progression avec statistiques et historique

## Fonctionnalités

- **5 signatures rythmiques** : 5/4, 7/4, 5/8, 7/8, 9/8
- **43 patterns rythmiques** : Du basique au très complexe
  - Noires et croches régulières
  - Groupements variés (3+2, 2+3, 2+2+3, 4+3, etc.)
  - Syncopes (contretemps)
  - Doubles croches
  - Triolets
  - Patterns aksak complexes
- **5 niveaux de complexité** :
  1. Noires/Croches basiques
  2. Croches complètes + groupements
  3. Syncopes + subdivisions mixtes
  4. Doubles croches + patterns complexes
  5. Triolets + aksak avancé
- **3 modes audio** : Métronome seul / Métronome + Pattern / Silencieux
- **Métriques de précision** :
  - Décalage moyen (ms)
  - Stabilité (écart-type)
  - Score de précision (%)
- **Progression** : Système de niveaux adaptatif
- **Historique** : Base SQLite avec graphiques de progression

## Installation

```bash
cd /data/projects/rhythm-trainer
pip3 install -r requirements.txt
```

### Dépendances

- `customtkinter` : Interface graphique moderne
- `sounddevice` : Capture audio low-latency
- `numpy` : Traitement numérique
- `matplotlib` : Graphiques (optionnel)

## Utilisation

### Lancer l'application

```bash
# Via le script
./scripts/start.sh

# Ou directement
python3 main.py
```

### Mode CLI (pour tests)

```bash
# Tester la détection de taps
python3 -m src.audio.tap_detector

# Tester le métronome
python3 -m src.audio.metronome

# Voir les patterns disponibles
python3 -m src.core.rhythm_engine
```

### Workflow d'exercice

1. Choisir une signature rythmique (ex: 7/8)
2. Sélectionner un pattern (ex: 2+2+3)
3. Ajuster le tempo (40-180 BPM)
4. Choisir le mode audio
5. Cliquer "Démarrer l'exercice"
6. Taper en rythme avec un crayon sur la table
7. Voir les résultats et statistiques

## Architecture

```
rhythm-trainer/
├── src/
│   ├── audio/
│   │   ├── tap_detector.py     # Détection des frappes
│   │   ├── metronome.py        # Métronome avec accents
│   │   └── calibration.py      # Calibration latence
│   ├── core/
│   │   ├── rhythm_engine.py    # Gestion des patterns
│   │   ├── precision_analyzer.py  # Analyse de précision
│   │   └── progression.py      # Système de niveaux
│   └── gui/
│       ├── main_window.py      # Fenêtre principale
│       ├── timeline_display.py # Visualisation timeline
│       ├── settings_panel.py   # Configuration
│       └── stats_view.py       # Statistiques
├── data/
│   ├── patterns.json           # Bibliothèque de patterns
│   ├── progress.db             # Historique utilisateur
│   └── backups/                # Backups automatiques
├── scripts/
│   └── start.sh
├── main.py
└── requirements.txt
```

## Précision et Latence

### Références de précision humaine

| Niveau | Précision |
|--------|-----------|
| Batteur pro (élite) | ~5-6 ms |
| Musicien professionnel | ~10 ms |
| Musicien entraîné | 10-20 ms |
| Non-musicien | ~35 ms |

### Calibration

L'application inclut un système de calibration pour compenser la latence audio du système. La latence typique est de 10-30 ms selon le matériel.

### Système de scoring

| Précision | Score |
|-----------|-------|
| ≤ 8 ms | Timing pro |
| 9-15 ms | Excellent |
| 16-25 ms | Bon |
| 26-40 ms | A améliorer |
| > 40 ms | Continue |

## Documentation

### Guide des Patterns

Voir [docs/PATTERNS.md](docs/PATTERNS.md) pour :
- Description détaillée des 43 patterns
- Système de complexité expliqué
- Progression recommandée
- Glossaire musical
- Exemples célèbres

## Base de données

L'historique est stocké dans `data/progress.db` (SQLite).

### Restauration depuis backup

```bash
cp data/backups/progress_TIMESTAMP.db data/progress.db
```

## Technologies

- Python 3.10+
- CustomTkinter 5.2+
- sounddevice (PortAudio)
- SQLite3

## Status

- **Dernière mise à jour** : 2026-02-08
- **Version** : 1.1.0
- **ID Projet** : PRJ-036

---

*Créé le 2026-01-31*
