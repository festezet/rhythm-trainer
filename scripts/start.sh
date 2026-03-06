#!/bin/bash
# Script de lancement de Rhythm Trainer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Vérifier les dépendances
python3 -c "import customtkinter, sounddevice, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installation des dépendances..."
    pip3 install -r requirements.txt
fi

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
