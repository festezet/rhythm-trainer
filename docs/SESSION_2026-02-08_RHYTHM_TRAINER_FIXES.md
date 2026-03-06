# Session 2026-02-08 - Rhythm Trainer Fixes Audio/Micro/Patterns

**Date** : 2026-02-08
**Projet** : PRJ-036 (rhythm-trainer)
**Objectif** : Corriger les bugs bloquants et rendre l'application utilisable

## Contexte

Le projet avait été créé le 2026-01-31 avec toute l'architecture en place mais plusieurs bugs empêchaient une utilisation normale : pas de son pendant les exercices, micro non fonctionnel, patterns groupés incorrects, sélection de pattern cassée.

## Corrections

### 1. Patterns groupés (5/4 3+2, 7/4 4+3)
- **Problème** : Les hits de `5_4_3plus2` et `7_4_4plus3` étaient identiques aux patterns basiques (toutes les noires)
- **Fix** : Remplacés par les accents de groupement uniquement
  - `5_4_3plus2` : `[0.0, 0.2, 0.4, 0.6, 0.8]` -> `[0.0, 0.6]`
  - `7_4_4plus3` : `[0.0, 1/7, ..., 6/7]` -> `[0.0, 4/7]`
- **Fichiers** : `src/core/rhythm_engine.py`, `data/patterns.json`

### 2. Sélection de pattern cassée
- **Problème** : `settings_panel` stockait le `name` du pattern dans `pattern_id` quand l'utilisateur changeait via dropdown, mais l'ID réel au set initial. De plus `_on_settings_changed` appelait `_update_patterns_list` à chaque changement de n'importe quel setting, ce qui reset la sélection au premier pattern.
- **Fix** :
  - Ajout mapping `_pattern_name_to_id` dans SettingsPanel
  - `_on_pattern_change` résout maintenant le nom vers l'ID
  - `_update_patterns_list` appelé uniquement quand la signature change réellement
- **Fichiers** : `src/gui/settings_panel.py`, `src/gui/main_window.py`

### 3. Erreur sample rate micro (C270 webcam)
- **Problème** : `PortAudioError: Invalid sample rate` - le TapDetector forçait 44100 Hz, mais la C270 est à 48000 Hz
- **Fix** : Le TapDetector détecte automatiquement le sample rate natif du périphérique via `sd.query_devices()`
- **Fichier** : `src/audio/tap_detector.py`

### 4. Pas de son pendant l'exercice
- **Problème** : Le métronome utilisait `sd.play()` (fonction de convenance qui crée/détruit un stream temporaire) depuis un thread. En conflit avec le `InputStream` du tap detector ouvert en parallèle.
- **Fix** : Remplacement par un `OutputStream` persistant. Pré-calcul de buffers complets par beat (click + silence) écrits en mode bloquant = timing naturel sans drift.
- **Fichier** : `src/audio/metronome.py`

### 5. Seuil micro trop élevé
- **Problème** : Seuil de détection à 0.3, mais le peak max de la C270 pour un tap est ~0.26
- **Fix** : Seuil par défaut abaissé à 0.02. Ajout d'un slider "Sensibilité" dans le panneau settings pour ajustement en temps réel.
- **Fichiers** : `src/gui/main_window.py`, `src/gui/settings_panel.py`

### 6. Système de logging + erreurs copiables
- **Ajout** : `logging` dans `main.py`, `tap_detector.py`, `metronome.py`, `main_window.py`
- **Log fichier** : `data/rhythm_trainer.log`
- **Diagnostic audio** au démarrage (liste des périphériques)
- **ErrorDialog** : popup avec texte copiable (tk.Text + bouton Copier) pour les erreurs micro
- **Fichiers** : `main.py`, `src/gui/main_window.py`

### 7. Auto-stop fantôme au restart
- **Problème** : Le timer `self.after()` de l'exercice précédent n'était jamais annulé, stoppant le nouvel exercice en plein milieu
- **Fix** : Ajout `_exercise_id` (compteur), `after_cancel()` au stop/restart, vérification d'ID dans `_auto_stop_exercise()`
- **Fichier** : `src/gui/main_window.py`

### 8. Changement de signature pendant exercice
- **Fix** : `_on_settings_changed` stoppe l'exercice en cours si la signature change
- **Fichier** : `src/gui/main_window.py`

### 9. Timeline pleine largeur
- **Fix** : Canvas responsive via `<Configure>` event + `fill='x', expand=True`
- **Fichier** : `src/gui/timeline_display.py`

### 10. Lanceur HomeHub-v2
- Mise à jour de `projects.db` : `launcher_path = /data/projects/rhythm-trainer/scripts/start.sh`
- L'app apparaît dans l'onglet Applications de HomeHub

### 11. Nettoyage
- Suppression du répertoire `gui/` vide à la racine (tout est dans `src/gui/`)

## Bug connu non corrigé

- **Points "attendu"/"joué" parasites** : des marqueurs verts persistent visuellement (zone M4 beat 2-3) entre les exercices malgré le `reset()`. A investiguer.

## Fichiers modifiés

| Fichier | Type |
|---------|------|
| `main.py` | Logging + diagnostic audio |
| `src/audio/metronome.py` | OutputStream persistant + buffers pré-calculés |
| `src/audio/tap_detector.py` | Auto-detect sample rate + logging |
| `src/core/rhythm_engine.py` | Fix patterns groupés |
| `src/gui/main_window.py` | Fix sélection pattern, restart, logging, ErrorDialog |
| `src/gui/settings_panel.py` | Mapping name->id, slider sensibilité |
| `src/gui/timeline_display.py` | Timeline responsive, reset() |
| `data/patterns.json` | Fix patterns groupés |

## Validation

- Import complet sans erreur
- Patterns groupés distincts des basiques (vérifié)
- Micro C270 détecte les taps (vérifié, peak ~0.04 RMS)
- Métronome audible pendant exercice (vérifié)
- Changement de signature stoppe l'exercice (vérifié)
