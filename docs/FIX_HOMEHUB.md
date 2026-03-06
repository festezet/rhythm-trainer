# Fix : Lancement depuis HomeHub

**Date** : 2026-02-23

## Problème

L'application Rhythm Trainer se lançait depuis HomeHub mais **la fenêtre n'apparaissait pas au premier plan**. Elle restait cachée en arrière-plan.

## Cause

Quand une application GUI (interface graphique) est lancée depuis un script ou un launcher comme HomeHub :
- Le processus Python démarre correctement
- La fenêtre CustomTkinter s'ouvre
- **Mais** la fenêtre ne se met pas automatiquement au premier plan
- L'utilisateur pense que l'application a crashé alors qu'elle est juste cachée

## Solution

Modifié le script `/data/projects/rhythm-trainer/scripts/start.sh` pour :

### Avant
```bash
# Lancer l'application
echo "Demarrage de Rhythm Trainer..."
python3 -m src.gui.main_window
```

### Après
```bash
# Lancer l'application
echo "Demarrage de Rhythm Trainer..."
python3 main.py &

# Attendre que la fenêtre apparaisse et la mettre au premier plan
sleep 2
WINDOW_ID=$(xdotool search --name "Rhythm Trainer" 2>/dev/null | head -1)
if [ -n "$WINDOW_ID" ]; then
    xdotool windowactivate "$WINDOW_ID" 2>/dev/null
fi

# Attendre la fin du processus Python
wait
```

## Ce Que Ça Fait

1. **Lance Python en arrière-plan** avec `&` (libère le terminal)
2. **Attend 2 secondes** que la fenêtre apparaisse
3. **Cherche la fenêtre** avec `xdotool search --name "Rhythm Trainer"`
4. **Active la fenêtre** au premier plan avec `xdotool windowactivate`
5. **Attend la fin** du processus avec `wait` (pour que le script ne se termine pas immédiatement)

## Commandes Utilisées

### xdotool
Outil pour manipuler les fenêtres X11 (Linux).

```bash
# Chercher une fenêtre par son nom
xdotool search --name "Rhythm Trainer"

# Activer une fenêtre (la mettre au premier plan)
xdotool windowactivate <WINDOW_ID>
```

### Installation de xdotool
Si xdotool n'est pas installé :
```bash
sudo apt install xdotool
```

## Test

Pour tester le nouveau script :
```bash
cd /data/projects/rhythm-trainer
bash scripts/start.sh
```

La fenêtre devrait maintenant :
1. S'ouvrir
2. Se mettre **automatiquement au premier plan**
3. Être immédiatement visible

## HomeHub

Le script est enregistré dans la base HomeHub :
- **Projet** : PRJ-036 (rhythm-trainer)
- **Launcher** : `/data/projects/rhythm-trainer/scripts/start.sh`
- **Type** : bash
- **Status** : active

Quand tu cliques sur "Rhythm Trainer" dans HomeHub, il exécute ce script.

## Autres Changements (Rappel)

En même temps que ce fix, j'ai aussi :
1. Ajouté **29 nouveaux patterns rythmiques** (de 14 à 43)
2. Créé **5 niveaux de complexité** (au lieu de 3)
3. Ajouté des **syncopes, doubles croches, triolets**
4. Créé la documentation complète dans `docs/`

Voir :
- `docs/PATTERNS.md` : Guide des 43 patterns
- `docs/EXPLICATION_SIMPLE.md` : Explication pour débutants
- `docs/CHANGELOG_PATTERNS.md` : Historique des changements

---

## ⚠️ MISE À JOUR FINALE (2026-02-23)

Le problème n'était **PAS** seulement dans le script `start.sh` de Rhythm Trainer.

### Vrai Problème

Le problème était dans **HomeHub v2** lui-même :
- La fonction `get_x11_env()` ne capturait que `DISPLAY` + `XAUTHORITY`
- Il **manquait** les variables critiques :
  - `DBUS_SESSION_BUS_ADDRESS` (bus D-Bus session)
  - `XDG_RUNTIME_DIR` (répertoire runtime)
  - `XDG_SESSION_TYPE` (type de session)

Sans ces variables, **AUCUNE** application GUI ne pouvait se lancer depuis HomeHub.

### Solution Finale

Modifié `/data/projects/homehub-v2/backend/app.py` :
- Fonction `get_x11_env()` lit maintenant l'environnement complet depuis `/proc/<systemd-user-pid>/environ`
- Logs visibles dans `/tmp/homehub_PRJ-036_*.log`

**Résultat** : ✅ Rhythm Trainer se lance correctement depuis HomeHub

### Scripts

Le script `start.sh` avec xdotool fonctionne mais n'était **pas nécessaire**.
La vraie solution était de fixer HomeHub pour qu'il passe le bon environnement.

Cependant, le script actuel fonctionne bien et peut rester tel quel.

---

**Documentation complète** : `/data/projects/homehub-v2/docs/LESSONS_LEARNED.md`

*Problème définitivement résolu le 2026-02-23*
