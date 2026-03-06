# Changelog - Rhythm Trainer

## Session du 23 février 2026

### Améliorations de l'interface

#### 1. Optimisation des performances
- **Calcul des résultats** : Réduit de >1 seconde à quelques millisecondes
  - Algorithme de matching optimisé : O(n*m) → O(n+m) (src/core/precision_analyzer.py:94-127)
  - Mise à jour différée de l'historique (+100ms) (src/gui/main_window.py:507-509)
  - Réutilisation des widgets au lieu de les recréer (src/gui/stats_view.py:208-290)

#### 2. Réorganisation de l'interface
- **Suppression du panneau de droite** : Les statistiques sont maintenant intégrées dans le ResultsOverlay
- **Timeline agrandie** : 600px → 1050px de largeur
- **Fenêtre principale** : 1100x700 → 1200x750
- **Statistiques globales** : Affichées sous les stats de session avec la même police (14pt)
  - Sessions totales
  - Score moyen
  - Meilleur score
  - Décalage moyen

#### 3. Ajustements visuels
- **Position M1/M2/M3/M4** : Déplacée plus haut (margin_top - 55px) pour éviter la coupure
- **Barres de mesure** : Barre finale visible (x-1px, width=3)
- **Légende** : Éloignée des chiffres (+35px au lieu de +25px)
- **Marges** : margin_top=75px, margin_bottom=50px
- **Nombre de mesures par défaut** : 2 → 4 (aligné avec le sélecteur)

#### 4. Corrections de bugs
- **Redimensionnement du Canvas** :
  - Fix de `_on_resize()` qui ne mettait à jour que la largeur (src/gui/timeline_display.py:62-68)
  - Fix de `pack(fill='x')` → `pack(fill='both')` (src/gui/main_window.py:112)
  - Fix de `sticky='ew'` → `sticky='nsew'` (src/gui/main_window.py:108)
  - Ajout de `grid_rowconfigure(0, weight=1)` pour expansion verticale

### Fichiers modifiés

1. **src/gui/main_window.py**
   - Lignes 37-38: Dimensions de la fenêtre (1200x750)
   - Ligne 111: Timeline width=1050, height=305
   - Lignes 108-110: Configuration du grid pour expansion
   - Ligne 112: pack(fill='both') au lieu de fill='x'
   - Lignes 165-169: Suppression du panneau stats et de l'appel à _update_stats()
   - Lignes 473-491: Intégration des stats globales dans show_results()
   - Suppression de la méthode _update_stats() et de l'import StatsView

2. **src/gui/timeline_display.py**
   - Lignes 45: num_measures par défaut = 4
   - Lignes 56: margin_top = 75px
   - Ligne 57: margin_bottom = 50px
   - Lignes 62-68: Fix de _on_resize() pour mettre à jour width ET height
   - Ligne 165: Position M1/M2/M3/M4 à margin_top - 55
   - Lignes 226-231: Barre finale visible
   - Ligne 343: Position légende +35px
   - Lignes 896-939: Ajout des statistiques globales dans ResultsOverlay
   - Lignes 916-948: Méthode show_results() modifiée pour accepter global_stats

3. **src/core/precision_analyzer.py**
   - Lignes 94-127: Algorithme de matching optimisé

4. **src/gui/stats_view.py**
   - Lignes 120-124: Ajout du cache de widgets
   - Lignes 208-290: Méthode update_history() optimisée avec réutilisation

5. **src/gui/settings_panel.py**
   - Lignes 109-118: Font size=11 pour le menu des patterns

### Fonctionnalités futures

#### Enregistrement audio pour calibration de la détection
- **Objectif** : Permettre l'enregistrement du son de l'instrument de percussion pour améliorer la détection des taps
- **Bénéfices** :
  - Calibration automatique du seuil de détection
  - Adaptation aux différents instruments (djembé, cajon, pad électronique, etc.)
  - Amélioration de la précision de détection selon le timbre
- **Implémentation suggérée** :
  - Ajouter un bouton "Calibrer instrument" dans le panneau settings
  - Enregistrer 5-10 secondes de frappes de l'utilisateur
  - Analyser l'amplitude, le spectre fréquentiel et l'enveloppe temporelle
  - Ajuster automatiquement le threshold et les paramètres du TapDetector
  - Sauvegarder le profil instrument dans la configuration utilisateur

### Notes techniques

- **Gestion de la géométrie Tkinter** : Les Canvas avec dimensions explicites doivent utiliser `pack(fill='both')` ET `grid_rowconfigure(weight=1)` pour respecter les dimensions
- **Callback _on_resize** : Doit mettre à jour les deux dimensions (width ET height) pour un redimensionnement correct
- **Performance** : La réutilisation de widgets existants au lieu de les détruire/recréer améliore drastiquement les performances (120+ widgets)
