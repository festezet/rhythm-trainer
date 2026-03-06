# Amélioration des Patterns Rythmiques

**Date** : 2026-02-23

## Résumé des changements

L'application propose maintenant **43 patterns** au lieu de 14, avec une progression de complexité beaucoup plus riche.

### Avant / Après

| Signature | Avant | Après | Nouveaux patterns |
|-----------|-------|-------|-------------------|
| **5/4**   | 3     | 9     | +6 (croches complètes, syncopes, doubles croches, triolets) |
| **7/4**   | 2     | 7     | +5 (croches complètes, syncopes, groupements variés) |
| **5/8**   | 3     | 8     | +5 (doubles croches, syncopes, triolets) |
| **7/8**   | 3     | 9     | +6 (groupements multiples, syncopes, aksak complexe) |
| **9/8**   | 3     | 10    | +7 (syncopes, doubles croches, triolets, aksak) |
| **TOTAL** | **14** | **43** | **+29 patterns** |

---

## Nouveaux types de patterns

### 1. Subdivisions complètes
**Avant** : Seulement quelques croches
**Après** : Toutes les croches, toutes les doubles croches

**Exemple 5/4** :
- Avant : `0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8` (7 notes)
- Après : `0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9` (10 croches complètes)

### 2. Syncopes (Contretemps)
**Nouveau** : Notes qui tombent ENTRE les temps

**Exemple 5/4 syncopes** :
```
Temps réguliers :  1 . 2 . 3 . 4 . 5 .
Syncopes        :  . 1 . 2 . 3 . 4 . 5
Positions       :  0.1, 0.3, 0.5, 0.7, 0.9
```

### 3. Doubles croches
**Nouveau** : Subdivisions 2x plus rapides que les croches

**Exemple 5/4** :
- Croches : 10 notes (une tous les 0.1)
- Doubles croches : 20 notes (une tous les 0.05)

### 4. Patterns mixtes
**Nouveau** : Combinaisons de différentes durées

**Exemple "Mixte C-C-N-N"** :
```
Croche + Croche + Noire + Noire + Noire
0.0    + 0.1    + 0.2   + 0.4   + 0.6
```

### 5. Triolets
**Nouveau** : Division du temps en 3 (au lieu de 2 ou 4)

**Exemple 5/8** :
- Croches normales : 5 notes espacées de 0.2
- Triolets : 15 notes espacées de ~0.067

### 6. Patterns aksak complexes
**Nouveau** : Rythmes balkaniques très asymétriques avec subdivisions

**Exemple 7/8 aksak** :
- Groupement 2+2+3 avec doubles croches intercalées
- Mélange de syncopes et de triolets

---

## Progression de complexité étendue

### Niveau 1 : Basique
**Avant** : Noires simples
**Après** : Noires + croches basiques

### Niveau 2 : Intermédiaire
**Avant** : Quelques croches
**Après** : Toutes croches + groupements simples

### Niveau 3 : Avancé
**Avant** : Groupements (3+2, 4+3)
**Après** : Syncopes + Subdivisions mixtes + Doubles croches

### Niveau 4 : Expert (NOUVEAU)
Doubles croches complètes + patterns syncopés complexes

### Niveau 5 : Maître (NOUVEAU)
Triolets + Aksak très asymétriques + Patterns ultra-complexes

---

## Impact sur l'entraînement

### Courbe d'apprentissage améliorée
1. **Débutant** : Niveaux 1-2 (comprendre la signature rythmique)
2. **Intermédiaire** : Niveau 3 (maîtriser les syncopes)
3. **Avancé** : Niveau 4 (vitesse et précision)
4. **Expert** : Niveau 5 (patterns professionnels)

### Nouveaux défis
- **Syncopes** : Développe le sens du contretemps
- **Doubles croches** : Améliore la rapidité et la précision
- **Triolets** : Force à penser en division ternaire
- **Patterns mixtes** : Entraîne la flexibilité rythmique

### Variété
- Avant : ~3 patterns par signature (risque d'ennui)
- Après : 7-10 patterns par signature (progression riche)

---

## Exemples musicaux

Ces nouveaux patterns correspondent à des rythmes utilisés dans :

### Syncopes
- Jazz (swing, bebop)
- Funk (groove syncopé)
- Drum & Bass (contretemps)

### Doubles croches
- Metal (double bass drum)
- Drum & Bass (breakbeats rapides)
- Jazz fusion (fills complexes)

### Triolets
- Blues shuffle
- Jazz swing
- Progressive rock

### Aksak complexe (niveau 5)
- Musique balkanique traditionnelle
- Math rock
- Progressive metal (Tool, Meshuggah)

---

## Fichiers modifiés

1. **src/core/rhythm_engine.py** : Ajout de 29 nouveaux patterns
2. **data/patterns.json** : Régénéré avec les 43 patterns
3. **docs/PATTERNS.md** : Guide complet des patterns (nouveau)
4. **docs/CHANGELOG_PATTERNS.md** : Ce fichier
5. **README.md** : Mis à jour avec les nouvelles fonctionnalités

---

## Prochaines étapes possibles

### Fonctionnalités suggérées
1. **Mode aléatoire** : Générer des patterns aléatoires dans une complexité donnée
2. **Patterns personnalisés** : Permettre à l'utilisateur de créer ses propres patterns
3. **Variations dynamiques** : Alterner automatiquement entre patterns de même complexité
4. **Défis progressifs** : Augmenter automatiquement la complexité selon la performance
5. **Quintuplets** : Ajouter des subdivisions en 5 (encore plus rare et complexe)

### Nouvelles signatures possibles
- **11/8** : Signatures très longues
- **13/8** : Signatures ultra-complexes
- **15/16** : Signatures avec noire pointée comme unité

---

*Créé le 2026-02-23*
