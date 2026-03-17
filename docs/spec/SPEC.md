# SPEC - Rhythm Trainer (PRJ-036)

> Specification technique generee par analyse du code source.
> Derniere mise a jour : 2026-03-13

---

## 1. Vue d'ensemble

### Description
Rhythm Trainer est une application desktop Python d'entrainement aux signatures rythmiques impaires et composees. Elle detecte en temps reel les frappes de l'utilisateur (taps sur table avec un crayon) via le microphone, compare leur timing aux patterns rythmiques attendus, et fournit des metriques de precision detaillees avec un systeme de progression.

### Objectifs
- Permettre l'entrainement aux signatures rythmiques inhabituelles (5/4, 7/4, 5/8, 7/8, 9/8) avec retour de precision en temps reel.
- Mesurer la precision temporelle des frappes en millisecondes et fournir un score objectif.
- Proposer un systeme de progression adaptatif avec 5 niveaux de difficulte et 49 patterns.
- Offrir une visualisation musicale claire avec notation sur portee et timeline animee.

### Stack technique
| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage | Python | 3.10+ |
| GUI | CustomTkinter | >= 5.2.0 |
| Audio I/O | sounddevice (PortAudio) | >= 0.4.6 |
| Traitement numerique | numpy | >= 1.24.0 |
| Graphiques (optionnel) | matplotlib | >= 3.7.0 |
| Base de donnees | SQLite3 | stdlib |
| OS cible | Linux (Ubuntu 22.04) | - |

### Identifiants
- **ID projet** : PRJ-036
- **Version** : 1.1.0
- **Date de creation** : 2026-01-31

---

## 2. Architecture technique

### Structure des fichiers

```
rhythm-trainer/
├── main.py                          # Point d'entree GUI, logging, diagnostic audio
├── cli.py                           # Interface CLI (argparse, 4 commandes)
├── requirements.txt                 # Dependances Python
├── scripts/
│   └── start.sh                     # Script de lancement (check deps, xdotool focus)
├── src/
│   ├── __init__.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── tap_detector.py          # Detection taps en temps reel (RMS amplitude)
│   │   ├── metronome.py             # Metronome + PatternPlayer (synthese audio)
│   │   └── calibration.py           # Calibration latence audio
│   ├── core/
│   │   ├── __init__.py
│   │   ├── rhythm_engine.py         # Gestion patterns et signatures rythmiques
│   │   ├── precision_analyzer.py    # Analyse precision + ProgressTracker (SQLite)
│   │   └── progression.py           # Systeme de niveaux et deblocage
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py           # Fenetre principale (1200x750, dark theme)
│       ├── timeline_display.py      # Timeline musicale + notation sur portee
│       ├── settings_panel.py        # Panneau de configuration + CalibrationDialog
│       └── stats_view.py            # Vue statistiques (3 onglets)
├── data/
│   ├── patterns.json                # 49 patterns serialises en JSON
│   ├── user_progress.json           # Progression utilisateur (niveaux, scores)
│   ├── progress.db                  # Historique sessions SQLite
│   └── backups/                     # Backups automatiques de la DB
├── tests/                           # Tests (repertoire present, contenu minimal)
├── docs/
│   └── PATTERNS.md                  # Documentation des patterns
├── CHANGELOG.md
├── ROADMAP.md
└── README.md
```

### Diagramme des composants

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (entry point)                     │
│                   Logging + Audio diagnostic                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌─────────▼─────────┐
│    cli.py      │                    │  gui/main_window  │
│  4 commandes   │                    │  Orchestrateur    │
│  (argparse)    │                    │  principal        │
└───────┬────────┘                    └──┬──────┬──────┬──┘
        │                               │      │      │
        │              ┌─────────────────┘      │      └─────────────────┐
        │              │                        │                        │
        │    ┌─────────▼──────────┐  ┌──────────▼──────────┐  ┌─────────▼──────────┐
        │    │ gui/settings_panel │  │ gui/timeline_display │  │   gui/stats_view   │
        │    │ Config, calibration│  │ Notation musicale    │  │ 3 onglets stats    │
        │    │ microphone select  │  │ Animation ~60 FPS    │  │ Graphe progression │
        │    └─────────┬──────────┘  │ ResultsOverlay       │  └─────────┬──────────┘
        │              │             └──────────────────────┘            │
        │              │                                                │
┌───────▼──────────────▼────────────────────────────────────────────────▼──┐
│                           CORE LAYER                                      │
│  ┌─────────────────────┐  ┌──────────────────────┐  ┌─────────────────┐  │
│  │ core/rhythm_engine   │  │ core/precision_      │  │ core/progression│  │
│  │ 49 patterns          │  │      analyzer        │  │ 5 niveaux       │  │
│  │ 7 signatures         │  │ O(n+m) matching      │  │ auto-unlock     │  │
│  │ JSON persistence     │  │ Score 0-100          │  │ JSON persistence│  │
│  └─────────────────────┘  │ SQLite tracking       │  └─────────────────┘  │
│                           └──────────────────────┘                        │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼───────────────────────────────────────┐
│                           AUDIO LAYER                                     │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐ │
│  │ audio/tap_detector│  │ audio/metronome   │  │ audio/calibration      │ │
│  │ InputStream       │  │ OutputStream      │  │ emit-then-detect       │ │
│  │ RMS detection     │  │ Click synthesis   │  │ 5 samples, trim outlier│ │
│  │ 44100Hz/128 block │  │ PatternPlayer     │  │ estimate_latency()     │ │
│  └──────────────────┘  └───────────────────┘  └────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │   sounddevice          │
                        │   (PortAudio backend)  │
                        └────────────────────────┘
```

### Flux de donnees principal (exercice)

```
1. Utilisateur configure (signature, pattern, BPM, mode audio)
        │
2. MainWindow.start_exercise()
   ├── Prep countdown (1 mesure de metronome)
   ├── TapDetector.start() → InputStream (thread audio)
   ├── Metronome.play_measure() en boucle (OutputStream)
   └── Timeline animation ~60 FPS (cursor + beat lines)
        │
3. Pendant l'exercice :
   ├── TapDetector callback : RMS > threshold → timestamp dans deque
   ├── Metronome : on_beat_callback → sync avec timeline
   └── MainWindow : filtre taps < 30ms des beats metronome (anti-self-detect)
        │
4. Fin exercice (auto-stop apres N mesures) :
   ├── TapDetector.stop()
   ├── Metronome.stop()
   ├── PrecisionAnalyzer.analyze(expected_times, tap_times)
   │   └── Matching O(n+m), calcul score, rating
   ├── ProgressTracker.save_session() → SQLite
   ├── ProgressionSystem.update_score() → JSON
   └── ResultsOverlay.show() sur timeline
```

### Dependances entre modules

- `main_window.py` importe et orchestre : `SettingsPanel`, `TimelineDisplay`, `TapDetector`, `Metronome`, `PatternPlayer`, `PrecisionAnalyzer`, `ProgressTracker`, `ProgressionSystem`, `RhythmEngine`
- `cli.py` importe : `ProgressionSystem`, `RhythmEngine`
- `timeline_display.py` est autonome (Canvas Tkinter pur, pas de dependance core)
- `precision_analyzer.py` contient aussi `ProgressTracker` (acces SQLite)
- `progression.py` est autonome (lecture/ecriture JSON)

---

## 3. Fonctionnalites detaillees

### 3.1 Signatures rythmiques

7 signatures supportees, definies dans `RhythmEngine.SIGNATURES` :

| Signature | Numerateur | Denominateur | Type |
|-----------|-----------|--------------|------|
| 3/4 | 3 | 4 | Simple |
| 4/4 | 4 | 4 | Simple |
| 5/4 | 5 | 4 | Impaire |
| 7/4 | 7 | 4 | Impaire |
| 5/8 | 5 | 8 | Impaire |
| 7/8 | 7 | 8 | Impaire |
| 9/8 | 9 | 8 | Impaire |

Le BPM represente directement les battements (pas de division par 2 pour les signatures en /8).

### 3.2 Patterns rythmiques

49 patterns au total, repartis sur 5 niveaux de complexite :

| Niveau | Complexite | Description | Exemples |
|--------|-----------|-------------|----------|
| 1 | Noires basiques | Noires regulieres sur chaque temps | `5_4_quarter_notes`, `7_8_basic` |
| 2 | Groupements | Croches + groupements asymetriques | `7_8_2_2_3`, `5_8_3_2` |
| 3 | Syncopes | Contretemps, subdivisions mixtes | `5_4_syncopated`, `7_8_offbeat` |
| 4 | Doubles croches | Patterns rapides, subdivisions fines | `5_4_sixteenths`, `9_8_complex` |
| 5 | Expert | Triolets, aksak avance | `7_8_aksak_advanced`, `9_8_triplets` |

Chaque pattern est un `RhythmPattern` (dataclass) :
- `id` : identifiant unique (str)
- `name` : nom affichable (str)
- `signature` : tuple (numerateur, denominateur)
- `hits` : liste de floats 0.0-1.0 representant les positions des frappes dans la mesure
- `complexity` : niveau 1-5 (int)
- `description` : texte descriptif (str)

Les patterns sont stockes en dur dans `rhythm_engine.py` et serialises dans `data/patterns.json`.

### 3.3 Detection de taps

Implementation dans `TapDetector` (`src/audio/tap_detector.py`) :

| Parametre | Valeur par defaut | Plage configurable |
|-----------|------------------|--------------------|
| Sample rate | 44100 Hz | Adaptatif (device native) |
| Block size | 128 samples (~2.9ms) | Fixe |
| Threshold (RMS) | 0.3 | 0.005 - 0.2 (slider GUI) |
| Min tap interval | 50 ms | Fixe |
| Buffer taps | deque(maxlen=1000) | Fixe |

Algorithme de detection :
1. InputStream sounddevice en mode callback (thread separe)
2. Calcul RMS de chaque bloc de 128 samples
3. Si RMS > threshold ET temps depuis dernier tap > min_interval → enregistrer timestamp
4. Compensation de latence appliquee au timestamp (`time.time() - latency_compensation`)
5. Buffer thread-safe (deque) pour collecte non-bloquante

### 3.4 Metronome

Implementation dans `Metronome` (`src/audio/metronome.py`) :

| Parametre | Valeur |
|-----------|--------|
| Click accent (temps 1) | 1800 Hz, 35 ms, enveloppe exponentielle |
| Click normal | 900 Hz, 25 ms, enveloppe exponentielle |
| BPM range | 30 - 300 |
| Output | OutputStream blocking write |

Le `PatternPlayer` joue le pattern rythmique avec un son distinct :
- Frequences : 1000 Hz + 1500 Hz melangees
- Duree : 60 ms
- Son de type "wood block"

### 3.5 Analyse de precision

Implementation dans `PrecisionAnalyzer` (`src/core/precision_analyzer.py`) :

**Algorithme de matching** (optimise O(n+m)) :
1. Trier les temps attendus et les taps
2. Pour chaque tap, trouver le temps attendu le plus proche
3. Si ecart < tolerance (50ms) → match valide
4. Chaque temps attendu ne peut etre matche qu'une fois

**Calcul du score** (0-100 points) :
| Composante | Poids | Calcul |
|-----------|-------|--------|
| Precision | 40 pts max | `40 - abs(mean_deviation_ms)` (min 0) |
| Stabilite | 30 pts max | `30 - std_deviation_ms` (min 0) |
| Completude | 30 pts max | `(hits_matches / expected_count) * 30` |

**Systeme de rating** (etoiles) :
| Etoiles | Mean deviation | Std deviation |
|---------|---------------|---------------|
| 5 | <= 8 ms | <= 10 ms |
| 4 | <= 15 ms | <= 20 ms |
| 3 | <= 25 ms | <= 30 ms |
| 2 | <= 40 ms | (any) |
| 1 | > 40 ms | (any) |

**Resultat** (`PrecisionResult` dataclass) :
- `mean_deviation_ms` : decalage moyen en millisecondes
- `std_deviation_ms` : ecart-type (stabilite)
- `accuracy_percent` : pourcentage de taps dans la tolerance
- `score` : score global 0-100
- `rating` : etoiles 1-5
- `matched_count` : nombre de taps matches
- `expected_count` : nombre de frappes attendues
- `deviations` : liste des ecarts individuels en ms

### 3.6 Systeme de progression

Implementation dans `ProgressionSystem` (`src/core/progression.py`) :

5 niveaux avec deblocage progressif :

| Niveau | Nom | Score requis | Patterns inclus |
|--------|-----|-------------|-----------------|
| 1 | Debutant - Noires | 0 | Patterns complexite 1 |
| 2 | Groupements basiques | 60 | Patterns complexite 2 |
| 3 | Croches completes | 65 | Patterns complexite 3 |
| 4 | Syncopes et subdivisions | 70 | Patterns complexite 4 |
| 5 | Expert | 75 | Patterns complexite 5 |

**Mecanique de deblocage** :
- Moyenne des scores des patterns du niveau courant >= `required_score` du niveau suivant
- Deblocage automatique, pas de validation manuelle
- Progression stockee dans `data/user_progress.json`

### 3.7 Calibration

Implementation dans `LatencyCalibrator` (`src/audio/calibration.py`) :

**Mode mesure** :
1. Emettre un click audio via OutputStream
2. Detecter le click via InputStream simultanement
3. Mesurer le delta temporel
4. Repeter 5 fois, exclure min et max (outliers)
5. Moyenner les 3 valeurs restantes

**Mode estimation** :
- Lire la latence par defaut du device (`default_low_input_latency`)
- Ajouter 5 ms de marge
- Fallback : 20 ms si aucune info device

**CalibrationDialog** (GUI) :
- Phase preparation : 4 clicks de mise en route
- Phase mesure : 4 clicks avec calcul
- Affichage du resultat et application automatique

### 3.8 Interface graphique

**Fenetre principale** (`MainWindow`, 1200x750, theme sombre) :
- Panneau gauche : `SettingsPanel` (configuration complete)
- Zone centrale : `TimelineDisplay` (1050x305, notation musicale animee)
- Overlay de resultats apres chaque exercice

**Timeline musicale** (`TimelineDisplay`) :
- Portee avec cle de sol rendue sur Canvas Tkinter
- Notation musicale : tetes de notes, hampes, ligatures, crochets, silences
- Analyse de structure rythmique : detecte triolets, croches, doubles croches
- Animation du curseur a ~60 FPS pendant l'exercice
- Code couleur : attendu=teal, joue=vert, joue hors tolerance=rouge
- Labels de mesure (M1, M2, M3, M4) au-dessus de la portee

**Panneau de configuration** (`SettingsPanel`) :
- Selection signature (boutons radio)
- Menu deroulant patterns (filtre par signature selectionnee)
- Slider BPM : 40-180 (increment 1)
- Slider threshold : 0.005-0.200
- Entree latence manuelle + bouton auto-calibration
- Mode audio : Metronome seul / Metronome + Pattern / Silencieux
- Nombre de mesures : 2, 4, ou 8
- Selection microphone avec bouton refresh

**Vue statistiques** (`StatsView`, 3 onglets) :
- Resume : score moyen, meilleur score, sessions totales
- Historique : tableau scrollable des sessions passees (widget reuse optimise)
- Progression : graphe Canvas score/temps

### 3.9 Interface CLI

4 commandes disponibles via `cli.py` (argparse) :

| Commande | Description | Options |
|----------|------------|---------|
| `list-levels` | Affiche les 5 niveaux avec statut de deblocage | - |
| `list-patterns` | Liste les patterns disponibles | `--level N` (filtre par niveau) |
| `calibrate` | Lance la calibration latence interactive | - |
| `progress` | Affiche la progression utilisateur | - |

---

## 4. Modele de donnees

### 4.1 Base SQLite (`data/progress.db`)

**Table `sessions`** :

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| timestamp | TEXT | ISO 8601 datetime |
| pattern_id | TEXT | ID du pattern joue |
| signature | TEXT | Ex: "7/8" |
| bpm | INTEGER | Tempo utilise |
| score | REAL | Score 0-100 |
| mean_deviation_ms | REAL | Decalage moyen |
| std_deviation_ms | REAL | Ecart-type |
| accuracy_percent | REAL | % de taps dans la tolerance |
| rating | INTEGER | Etoiles 1-5 |
| matched_count | INTEGER | Taps correctement matches |
| expected_count | INTEGER | Nombre de frappes attendues |
| num_measures | INTEGER | Nombre de mesures jouees |

**Backup automatique** :
- Declenche au demarrage de `ProgressTracker`
- Rotation : garde les 10 derniers fichiers `.bak`
- Emplacement : `data/backups/`
- Format : `progress.db.TIMESTAMP.bak`

### 4.2 Fichier JSON progression (`data/user_progress.json`)

```json
{
  "current_level": 1,
  "unlocked_levels": [1],
  "pattern_scores": {
    "5_4_quarter_notes": 78,
    "7_8_2_2_3": 65
  },
  "total_practice_time": 3600,
  "sessions_count": 42
}
```

### 4.3 Fichier JSON patterns (`data/patterns.json`)

Tableau de 49 objets :

```json
[
  {
    "id": "5_4_quarter_notes",
    "name": "5/4 - Noires",
    "signature": [5, 4],
    "hits": [0.0, 0.2, 0.4, 0.6, 0.8],
    "complexity": 1,
    "description": "Noires regulieres en 5/4"
  }
]
```

Les `hits` sont des positions normalisees dans la mesure (0.0 = debut, 1.0 = fin).

### 4.4 Structures de donnees en memoire

**`RhythmPattern`** (dataclass, `rhythm_engine.py`) :
```python
@dataclass
class RhythmPattern:
    id: str
    name: str
    signature: tuple  # (numerator, denominator)
    hits: list        # [0.0, 0.2, 0.4, ...]
    complexity: int   # 1-5
    description: str
```

**`PrecisionResult`** (dataclass, `precision_analyzer.py`) :
```python
@dataclass
class PrecisionResult:
    mean_deviation_ms: float
    std_deviation_ms: float
    accuracy_percent: float
    score: float        # 0-100
    rating: int         # 1-5
    matched_count: int
    expected_count: int
    deviations: list    # [ms, ms, ...]
```

**`Level`** (dataclass, `progression.py`) :
```python
@dataclass
class Level:
    id: int
    name: str
    complexity: int
    description: str
    required_score: int
    patterns: list      # [pattern_id, ...]
```

---

## 5. API et interfaces

### 5.1 API interne Python

**RhythmEngine** :
| Methode | Signature | Description |
|---------|-----------|-------------|
| `get_all_patterns()` | `() -> list[RhythmPattern]` | Tous les patterns |
| `get_patterns_by_signature(sig)` | `(tuple) -> list[RhythmPattern]` | Patterns filtres par signature |
| `get_pattern_by_id(id)` | `(str) -> RhythmPattern | None` | Pattern par ID |
| `get_measure_duration(bpm, sig)` | `(int, tuple) -> float` | Duree mesure en secondes |
| `save_patterns(path)` | `(str) -> None` | Export JSON |
| `load_patterns(path)` | `(str) -> None` | Import JSON |

**TapDetector** :
| Methode | Signature | Description |
|---------|-----------|-------------|
| `start()` | `() -> None` | Demarre l'ecoute microphone |
| `stop()` | `() -> None` | Arrete l'ecoute |
| `get_taps()` | `() -> list[float]` | Timestamps des taps detectes |
| `clear_taps()` | `() -> None` | Vide le buffer |
| `set_threshold(v)` | `(float) -> None` | Ajuste le seuil de detection |
| `set_latency_compensation(v)` | `(float) -> None` | Ajuste la compensation latence |

**Metronome** :
| Methode | Signature | Description |
|---------|-----------|-------------|
| `play_measure(bpm, sig, callback)` | `(int, tuple, callable) -> None` | Joue une mesure |
| `stop()` | `() -> None` | Arrete le metronome |
| `set_bpm(bpm)` | `(int) -> None` | Change le tempo |

**PatternPlayer** :
| Methode | Signature | Description |
|---------|-----------|-------------|
| `play_pattern(pattern, bpm)` | `(RhythmPattern, int) -> None` | Joue le pattern |
| `stop()` | `() -> None` | Arrete la lecture |

**PrecisionAnalyzer** :
| Methode | Signature | Description |
|---------|-----------|-------------|
| `analyze(expected, taps)` | `(list[float], list[float]) -> PrecisionResult` | Analyse de precision |

**ProgressTracker** :
| Methode | Signature | Description |
|---------|-----------|-------------|
| `save_session(result, pattern_id, ...)` | `(...) -> None` | Enregistre en SQLite |
| `get_history(limit)` | `(int) -> list[dict]` | Dernieres sessions |
| `get_stats()` | `() -> dict` | Statistiques globales |
| `backup_database()` | `() -> None` | Backup avec rotation |

**ProgressionSystem** :
| Methode | Signature | Description |
|---------|-----------|-------------|
| `update_score(pattern_id, score)` | `(str, float) -> None` | Met a jour le score |
| `check_level_unlock()` | `() -> bool` | Verifie deblocage niveau |
| `get_current_level()` | `() -> Level` | Niveau actuel |

### 5.2 Interface CLI

```bash
# Lister les niveaux
python3 cli.py list-levels

# Lister les patterns (optionnel: filtrer par niveau)
python3 cli.py list-patterns
python3 cli.py list-patterns --level 2

# Calibrer la latence audio
python3 cli.py calibrate

# Voir la progression
python3 cli.py progress
```

### 5.3 Script de lancement

```bash
./scripts/start.sh
```

Fonctionnement :
1. Verifie les dependances (`customtkinter`, `sounddevice`, `numpy`)
2. Lance `main.py` en arriere-plan
3. Utilise `xdotool` pour donner le focus a la fenetre (si disponible)

---

## 6. Configuration et deploiement

### 6.1 Installation

```bash
cd /data/projects/rhythm-trainer
pip3 install -r requirements.txt
```

Dependances systeme requises :
- `portaudio19-dev` (backend de sounddevice)
- `python3-tk` (backend Tkinter)
- Microphone fonctionnel (ALSA/PulseAudio)

### 6.2 Parametres configurables (runtime)

Tous les parametres sont ajustables via l'interface GUI :

| Parametre | Defaut | Plage | Emplacement |
|-----------|--------|-------|-------------|
| BPM | 80 | 40-180 | SettingsPanel slider |
| Threshold detection | 0.3 | 0.005-0.200 | SettingsPanel slider |
| Latence compensation | 15 ms | 0-200 ms | SettingsPanel entry / auto-calibration |
| Mode audio | Metronome seul | 3 modes | SettingsPanel radio buttons |
| Nombre de mesures | 4 | 2, 4, 8 | SettingsPanel segmented button |
| Microphone | Device par defaut | Devices disponibles | SettingsPanel dropdown |

### 6.3 Parametres hardcodes (constants)

| Parametre | Valeur | Fichier |
|-----------|--------|---------|
| Sample rate | 44100 Hz | tap_detector.py |
| Block size | 128 samples | tap_detector.py |
| Min tap interval | 50 ms | tap_detector.py |
| Tap buffer max | 1000 | tap_detector.py |
| Tolerance matching | 50 ms | precision_analyzer.py |
| Click accent freq | 1800 Hz / 35 ms | metronome.py |
| Click normal freq | 900 Hz / 25 ms | metronome.py |
| Wood block freq | 1000+1500 Hz / 60 ms | metronome.py |
| BPM internal range | 30-300 | metronome.py |
| Metronome filter | 30 ms | main_window.py |
| Fenetre | 1200x750 | main_window.py |
| Timeline | 1050x305 | main_window.py |
| Animation FPS | ~60 | timeline_display.py |
| Backup rotation | 10 fichiers max | precision_analyzer.py |
| Calibration samples | 5 (trim 2) | calibration.py |
| Estimation marge | 5 ms | calibration.py |
| Estimation fallback | 20 ms | calibration.py |

### 6.4 Logging

Configure dans `main.py` :
- Fichier : `data/rhythm_trainer.log` (mode append)
- Console : stderr
- Niveau : INFO
- Format : `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Diagnostic audio au demarrage (liste des devices, device par defaut)

### 6.5 Lancement

```bash
# Mode GUI (principal)
python3 main.py

# Mode CLI
python3 cli.py <commande>

# Via script
./scripts/start.sh
```

---

## 7. Securite et gestion des erreurs

### 7.1 Gestion des erreurs audio

- **Pas de microphone** : `ErrorDialog` modal avec message explicatif et texte copiable
- **Device audio indisponible** : fallback vers le device par defaut du systeme
- **Echec calibration** : fallback vers `estimate_latency()` (mode estimation)
- **Sample rate incompatible** : ajustement automatique au sample rate natif du device
- **Exception dans callback audio** : log de l'erreur, pas de crash (callback silencieux)

### 7.2 Gestion des erreurs donnees

- **DB corrompue** : backup automatique au demarrage, restauration manuelle possible
- **JSON invalide** : valeurs par defaut utilisees (`user_progress.json`, `patterns.json`)
- **Fichiers manquants** : creation automatique au premier lancement
- **Dossier `data/` absent** : creation automatique

### 7.3 Robustesse de l'exercice

- **Exercise ID system** : chaque exercice a un ID unique pour empecher les callbacks fantomes de timers precedents
- **Filtre anti-self-detection** : les taps dans les 30 ms suivant un beat de metronome sont ignores (evite que le metronome declenche le detecteur)
- **Auto-stop** : l'exercice s'arrete automatiquement apres le nombre de mesures configure
- **Thread safety** : `deque` avec `maxlen` pour le buffer de taps (thread-safe en CPython)

### 7.4 Donnees sensibles

- Pas de donnees personnelles stockees (pas de comptes utilisateur)
- `.gitignore` exclut : `data/*.db`, `data/*.sqlite`, `.env`, `secrets.json`, `.claude/`
- Toutes les donnees sont locales (pas de reseau, pas d'API externe)

---

## 8. Limitations connues et dette technique

### 8.1 Limitations fonctionnelles

| Limitation | Impact | Piste d'amelioration |
|-----------|--------|---------------------|
| Mono-utilisateur | Un seul profil de progression | Mode multi-joueur (ROADMAP) |
| Pas de calibration instrument | Seuil de detection generique | Calibration par enregistrement (ROADMAP priorite haute) |
| Pas d'export stats | Donnees consultables uniquement in-app | Export CSV/PDF (ROADMAP) |
| Pas de MIDI | Pas de synchronisation materielle | Support MIDI (ROADMAP) |
| Pas de polyrythmes | Limites aux signatures simples | Polyrythmes 3:4, etc. (ROADMAP) |
| Linux uniquement | Pas teste sur macOS/Windows | Portage possible (dependencies cross-platform) |

### 8.2 Limitations techniques

| Limitation | Detail |
|-----------|--------|
| Threshold fixe par session | Le seuil ne s'adapte pas dynamiquement au bruit ambiant |
| Block size 128 fixe | Resolution temporelle de ~2.9ms, non configurable |
| Tolerance 50ms hardcodee | Pas ajustable par l'utilisateur |
| GUI Tkinter single-thread | L'animation peut saccader sur machines lentes |
| ProgressTracker dans precision_analyzer.py | Responsabilite mixte (analyse + persistence) |
| 49 patterns hardcodes | Pas d'import de patterns personnalises |

### 8.3 Dette technique identifiee

| Element | Description | Severite |
|---------|-------------|----------|
| `ProgressTracker` dans `precision_analyzer.py` | Devrait etre dans un module dedie (`persistence.py` ou similaire) | Faible |
| Patterns dupliques (Python + JSON) | Les 49 patterns sont definis en dur dans `rhythm_engine.py` ET serialises dans `patterns.json` - source de verite ambigue | Moyenne |
| Pas de tests unitaires | Le repertoire `tests/` existe mais est vide/minimal | Moyenne |
| Constantes magiques | Threshold 0.3, tolerance 50ms, etc. non centralises dans un fichier de configuration | Faible |
| `StatsView` importe mais plus utilisee dans `main_window.py` | La vue stats a ete deplacee dans le ResultsOverlay mais le module existe encore | Faible |

---

## 9. Evolution prevue

### 9.1 Court terme (ROADMAP priorite haute)

**Calibration instrument par enregistrement audio** :
- Ajouter un dialogue de calibration dans `settings_panel.py`
- Enregistrer 5-10 secondes de frappes de l'instrument utilise
- Analyser : amplitude moyenne des pics, spectre frequentiel dominant, enveloppe temporelle (attack/decay)
- Ajuster automatiquement : threshold, min_interval, filtres frequentiels
- Sauvegarder dans `data/instrument_profiles.json` (profils par instrument)
- Fichiers a modifier : `tap_detector.py`, `settings_panel.py`, `main_window.py`

### 9.2 Moyen terme (ROADMAP priorite moyenne)

**Mode multi-joueur** :
- Selection du joueur au demarrage
- Statistiques et historique separes par joueur
- Progression personnalisee independante
- Modification du schema SQLite (ajout colonne `player_id`)

### 9.3 Long terme (ROADMAP futur)

**Interface** :
- Animations de transition entre les ecrans
- Theme clair/sombre configurable
- Graphiques de progression plus detailles
- Export des statistiques (CSV, PDF)

**Audio** :
- Sons de metronome differents (selectionnable)
- Volume configurable independamment (metronome vs pattern)
- Support MIDI pour synchronisation avec materiel externe

**Pedagogie** :
- Mode entrainement progressif (augmentation automatique du BPM)
- Exercices guides par niveau
- Defis et objectifs quotidiens
- Feedback visuel en temps reel pendant l'exercice (coloration immediate des notes)

**Technique** :
- Support des signatures composees (ex: 3+2+3/8)
- Polyrythmes (3 contre 4, 5 contre 3)
- Import de patterns personnalises (format JSON)
- Adaptation dynamique du seuil au bruit ambiant

---

*Specification generee par analyse du code source le 2026-03-13.*
*Version du projet analysee : 1.1.0*
