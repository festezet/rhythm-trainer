# Roadmap - Rhythm Trainer

## Fonctionnalités prioritaires

### 1. Calibration de détection par enregistrement audio
**Statut** : À implémenter
**Priorité** : Haute
**Objectif** : Améliorer la précision de détection des taps en s'adaptant à l'instrument utilisé

**Étapes d'implémentation** :
1. Ajouter un dialogue de calibration instrument dans settings_panel.py
2. Implémenter la capture audio dans tap_detector.py
   - Enregistrer 5-10 secondes de frappes
   - Analyser l'amplitude moyenne des pics
   - Analyser le spectre fréquentiel dominant
   - Calculer l'enveloppe temporelle (attack/decay)
3. Créer un système de profils d'instruments
   - Sauvegarder les paramètres par type d'instrument
   - Permettre plusieurs profils (djembé, cajon, pad, etc.)
4. Ajuster automatiquement :
   - threshold (seuil de détection)
   - min_interval (intervalle minimum entre taps)
   - Filtres fréquentiels si nécessaire

**Fichiers à modifier** :
- src/audio/tap_detector.py : Ajout de la méthode calibrate_from_recording()
- src/gui/settings_panel.py : Ajout du bouton/dialogue de calibration
- src/gui/main_window.py : Intégration du workflow de calibration
- data/instrument_profiles.json : Stockage des profils

### 2. Mode joueur avec noms et statistiques personnelles
**Statut** : Noté pour le futur
**Priorité** : Moyenne
**Objectif** : Permettre à plusieurs utilisateurs d'utiliser l'application avec leurs propres statistiques

**Fonctionnalités** :
- Sélection du joueur au démarrage
- Statistiques séparées par joueur
- Historique individuel
- Progression personnalisée

### 3. Améliorations futures

#### Interface
- [ ] Ajouter des animations pour les transitions
- [ ] Thème clair/sombre configurable
- [ ] Graphiques de progression plus détaillés
- [ ] Export des statistiques (CSV, PDF)

#### Audio
- [ ] Support de différents sons de métronome
- [ ] Volume configurable indépendamment
- [ ] Modes de métronome (simple, accentué, muet)

#### Pédagogie
- [ ] Mode entraînement progressif (augmentation auto du BPM)
- [ ] Exercices guidés par niveau
- [ ] Défis et objectifs quotidiens
- [ ] Feedback visuel en temps réel pendant l'exercice

#### Technique
- [ ] Support des signatures composées (3+2+3/8, etc.)
- [ ] Polyrythmes (3 contre 4, etc.)
- [ ] Import de patterns personnalisés
- [ ] Synchronisation avec métronome externe (MIDI)

## Bugs connus

Aucun bug connu actuellement.

## Dernière mise à jour

Session du 23 février 2026
