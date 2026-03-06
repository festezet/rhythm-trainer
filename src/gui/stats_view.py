"""
Vue des statistiques et de la progression.
Affiche l'historique et les graphiques de performance.
"""

import customtkinter as ctk
from typing import List, Dict
import tkinter as tk


class StatsView(ctk.CTkFrame):
    """Vue des statistiques de l'utilisateur."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._create_widgets()

    def _create_widgets(self):
        """Crée les widgets de la vue."""

        # Titre
        title = ctk.CTkLabel(
            self,
            text="Statistiques & Progression",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=15)

        # Onglets
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill='both', expand=True, padx=10, pady=10)

        self.tabview.add("Resume")
        self.tabview.add("Historique")
        self.tabview.add("Progression")

        self._create_summary_tab()
        self._create_history_tab()
        self._create_progression_tab()

    def _create_summary_tab(self):
        """Crée l'onglet résumé."""
        tab = self.tabview.tab("Resume")

        # Stats globales
        self.summary_frame = ctk.CTkFrame(tab)
        self.summary_frame.pack(fill='x', padx=20, pady=20)

        self.stats_labels = {}

        stats_config = [
            ('total_sessions', 'Sessions totales', '0'),
            ('avg_score', 'Score moyen', '0'),
            ('best_score', 'Meilleur score', '0'),
            ('avg_deviation', 'Decalage moyen', '-- ms'),
            ('patterns_mastered', 'Patterns maitrises', '0'),
            ('current_level', 'Niveau actuel', 'Debutant'),
        ]

        for i, (key, label, default) in enumerate(stats_config):
            row = i // 2
            col = i % 2

            frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
            frame.grid(row=row, column=col, padx=20, pady=10, sticky='w')

            ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray60")
            ).pack(anchor='w')

            self.stats_labels[key] = ctk.CTkLabel(
                frame,
                text=default,
                font=ctk.CTkFont(size=18, weight="bold")
            )
            self.stats_labels[key].pack(anchor='w')

        # Configurer la grille
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.summary_frame.grid_columnconfigure(1, weight=1)

    def _create_history_tab(self):
        """Crée l'onglet historique."""
        tab = self.tabview.tab("Historique")

        # Liste scrollable
        self.history_frame = ctk.CTkScrollableFrame(tab, height=300)
        self.history_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # En-tête
        header_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        header_frame.pack(fill='x', pady=(0, 10))

        headers = ['Date', 'Pattern', 'BPM', 'Score', 'Decalage']
        widths = [100, 150, 60, 60, 80]

        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                header_frame,
                text=header,
                width=width,
                font=ctk.CTkFont(weight="bold")
            ).pack(side='left', padx=5)

        # Placeholder pour les données
        self.history_rows_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_rows_frame.pack(fill='both', expand=True)

        self.no_data_label = ctk.CTkLabel(
            self.history_rows_frame,
            text="Aucun historique pour le moment.\nCommencez a vous entrainer !",
            text_color=("gray50", "gray60")
        )
        self.no_data_label.pack(pady=50)

        # Cache des widgets pour réutilisation
        self.history_row_cache = []

    def _create_progression_tab(self):
        """Crée l'onglet progression."""
        tab = self.tabview.tab("Progression")

        # Graphique placeholder (Canvas simple)
        self.graph_frame = ctk.CTkFrame(tab)
        self.graph_frame.pack(fill='both', expand=True, padx=20, pady=20)

        self.graph_canvas = tk.Canvas(
            self.graph_frame,
            height=250,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.graph_canvas.pack(fill='both', expand=True)

        # Légende
        legend_frame = ctk.CTkFrame(tab, fg_color="transparent")
        legend_frame.pack(pady=10)

        ctk.CTkLabel(
            legend_frame,
            text="Score moyen par jour (30 derniers jours)",
            text_color=("gray50", "gray60")
        ).pack()

        # Message si pas de données
        self._draw_empty_graph()

    def _draw_empty_graph(self):
        """Dessine un graphique vide."""
        self.graph_canvas.delete('all')

        width = self.graph_canvas.winfo_width() or 400
        height = self.graph_canvas.winfo_height() or 250

        # Axes
        margin = 40
        self.graph_canvas.create_line(
            margin, height - margin,
            width - margin, height - margin,
            fill='#4a4a6a', width=2
        )
        self.graph_canvas.create_line(
            margin, margin,
            margin, height - margin,
            fill='#4a4a6a', width=2
        )

        # Labels axes
        self.graph_canvas.create_text(
            width // 2, height - 10,
            text="Jours",
            fill='#8a8aaa'
        )
        self.graph_canvas.create_text(
            15, height // 2,
            text="Score",
            fill='#8a8aaa',
            angle=90
        )

        # Message
        self.graph_canvas.create_text(
            width // 2, height // 2,
            text="Pas encore de donnees",
            fill='#6a6a8a',
            font=('Helvetica', 14)
        )

    def update_summary(self, stats: Dict):
        """Met à jour le résumé des statistiques."""
        mappings = {
            'total_sessions': str(stats.get('total_sessions', 0)),
            'avg_score': str(round(stats.get('avg_score', 0))),
            'best_score': str(stats.get('best_score', 0)),
            'avg_deviation': f"{stats.get('avg_deviation', 0):.1f} ms",
            'patterns_mastered': str(stats.get('patterns_mastered', 0)),
            'current_level': stats.get('current_level', 'Debutant'),
        }

        for key, value in mappings.items():
            if key in self.stats_labels:
                self.stats_labels[key].configure(text=value)

    def update_history(self, history: List[Dict]):
        """Met à jour l'historique (optimisé pour réutiliser les widgets)."""
        # Masquer le label "pas de données"
        if hasattr(self, 'no_data_label') and self.no_data_label.winfo_exists():
            self.no_data_label.pack_forget()

        if not history:
            # Masquer toutes les lignes du cache
            for row_data in self.history_row_cache:
                row_data['frame'].pack_forget()

            # Afficher le message "pas de données"
            if not hasattr(self, 'no_data_label') or not self.no_data_label.winfo_exists():
                self.no_data_label = ctk.CTkLabel(
                    self.history_rows_frame,
                    text="Aucun historique pour le moment.",
                    text_color=("gray50", "gray60")
                )
            self.no_data_label.pack(pady=50)
            return

        # Limiter à 20 entrées
        history = history[:20]

        # Créer des widgets supplémentaires si nécessaire
        while len(self.history_row_cache) < len(history):
            row_frame = ctk.CTkFrame(self.history_rows_frame, fg_color="transparent")

            date_label = ctk.CTkLabel(row_frame, width=100)
            date_label.pack(side='left', padx=5)

            pattern_label = ctk.CTkLabel(row_frame, width=150)
            pattern_label.pack(side='left', padx=5)

            bpm_label = ctk.CTkLabel(row_frame, width=60)
            bpm_label.pack(side='left', padx=5)

            score_label = ctk.CTkLabel(row_frame, width=60)
            score_label.pack(side='left', padx=5)

            dev_label = ctk.CTkLabel(row_frame, width=80)
            dev_label.pack(side='left', padx=5)

            self.history_row_cache.append({
                'frame': row_frame,
                'date': date_label,
                'pattern': pattern_label,
                'bpm': bpm_label,
                'score': score_label,
                'dev': dev_label
            })

        # Mettre à jour les widgets existants
        for i, entry in enumerate(history):
            row_data = self.history_row_cache[i]

            # Date
            date_str = entry.get('timestamp', '')[:10]
            row_data['date'].configure(text=date_str)

            # Pattern
            pattern = entry.get('pattern_id', '')[:20]
            row_data['pattern'].configure(text=pattern)

            # BPM
            row_data['bpm'].configure(text=str(entry.get('bpm', '')))

            # Score
            score = entry.get('score', 0)
            score_color = '#2ed573' if score >= 70 else '#ffa502' if score >= 50 else '#ff4757'
            row_data['score'].configure(text=str(score), text_color=score_color)

            # Décalage
            dev = entry.get('mean_deviation_ms', 0)
            sign = '+' if dev > 0 else ''
            row_data['dev'].configure(text=f"{sign}{dev:.1f}ms")

            # Afficher la ligne
            row_data['frame'].pack(fill='x', pady=2)

        # Masquer les lignes excédentaires
        for i in range(len(history), len(self.history_row_cache)):
            self.history_row_cache[i]['frame'].pack_forget()

    def update_progression_graph(self, data: List[Dict]):
        """Met à jour le graphique de progression."""
        self.graph_canvas.delete('all')

        if not data:
            self._draw_empty_graph()
            return

        width = self.graph_canvas.winfo_width() or 400
        height = self.graph_canvas.winfo_height() or 250
        margin = 40

        # Extraire les valeurs
        scores = [d['avg_score'] for d in data]
        dates = [d['date'] for d in data]

        if not scores:
            self._draw_empty_graph()
            return

        # Normaliser
        max_score = max(scores) if scores else 100
        min_score = min(scores) if scores else 0

        # Dessiner les axes
        self.graph_canvas.create_line(
            margin, height - margin,
            width - margin, height - margin,
            fill='#4a4a6a', width=2
        )
        self.graph_canvas.create_line(
            margin, margin,
            margin, height - margin,
            fill='#4a4a6a', width=2
        )

        # Dessiner les points et lignes
        if len(scores) > 1:
            points = []
            graph_width = width - 2 * margin
            graph_height = height - 2 * margin

            for i, score in enumerate(scores):
                x = margin + (i / (len(scores) - 1)) * graph_width
                y = height - margin - ((score - min_score) / max(max_score - min_score, 1)) * graph_height
                points.extend([x, y])

            # Ligne
            if len(points) >= 4:
                self.graph_canvas.create_line(
                    *points,
                    fill='#4ecdc4',
                    width=2,
                    smooth=True
                )

            # Points
            for i in range(0, len(points), 2):
                x, y = points[i], points[i+1]
                self.graph_canvas.create_oval(
                    x-4, y-4, x+4, y+4,
                    fill='#4ecdc4',
                    outline=''
                )

        # Labels
        self.graph_canvas.create_text(
            margin - 25, margin,
            text=str(int(max_score)),
            fill='#8a8aaa'
        )
        self.graph_canvas.create_text(
            margin - 25, height - margin,
            text=str(int(min_score)),
            fill='#8a8aaa'
        )


if __name__ == "__main__":
    # Test
    ctk.set_appearance_mode("dark")

    root = ctk.CTk()
    root.title("Test Stats View")
    root.geometry("600x500")

    view = StatsView(root)
    view.pack(fill='both', expand=True)

    # Simuler des données
    view.update_summary({
        'total_sessions': 25,
        'avg_score': 72,
        'best_score': 91,
        'avg_deviation': 8.3,
        'patterns_mastered': 5,
        'current_level': 'Intermediaire'
    })

    test_history = [
        {'timestamp': '2026-01-31T10:30:00', 'pattern_id': '5_4_basic', 'bpm': 80, 'score': 85, 'mean_deviation_ms': 6.2},
        {'timestamp': '2026-01-30T14:15:00', 'pattern_id': '7_8_2plus2plus3', 'bpm': 90, 'score': 72, 'mean_deviation_ms': -12.1},
    ]
    view.update_history(test_history)

    root.mainloop()
