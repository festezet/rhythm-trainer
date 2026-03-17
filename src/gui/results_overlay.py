"""
Overlay d'affichage des resultats apres un exercice.
Extrait de timeline_display.py pour modularity.
"""

import customtkinter as ctk


class ResultsOverlay(ctk.CTkFrame):
    """Overlay d'affichage des resultats apres un exercice."""

    def __init__(self, master, on_restart=None, **kwargs):
        super().__init__(master, fg_color=("#f0f0f0", "#1f2937"), **kwargs)

        self.on_restart = on_restart

        self._create_score_section()
        self._create_metrics_section()
        self._create_global_stats_section()
        self._create_restart_button()

    def _create_score_section(self):
        """Cree la section score principal et rating."""
        self.score_label = ctk.CTkLabel(
            self,
            text="--",
            font=ctk.CTkFont(size=48, weight="bold")
        )
        self.score_label.pack(pady=10)

        self.rating_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=18)
        )
        self.rating_label.pack()

    def _create_metrics_section(self):
        """Cree la section metriques detaillees."""
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(pady=15, fill='x', padx=20)

        self.deviation_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Decalage: -- ms",
            font=ctk.CTkFont(size=14)
        )
        self.deviation_label.pack()

        self.stability_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Stabilite: -- ms",
            font=ctk.CTkFont(size=14)
        )
        self.stability_label.pack()

        self.accuracy_label = ctk.CTkLabel(
            self.metrics_frame,
            text="Precision: --%",
            font=ctk.CTkFont(size=14)
        )
        self.accuracy_label.pack()

    def _create_global_stats_section(self):
        """Cree la section statistiques globales."""
        separator = ctk.CTkFrame(self, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill='x', padx=40, pady=15)

        stats_title = ctk.CTkLabel(
            self,
            text="Statistiques & Progression",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_title.pack(pady=(5, 10))

        self.global_stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.global_stats_frame.pack(pady=5, fill='x', padx=20)

        self.total_sessions_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Sessions totales: 0",
            font=ctk.CTkFont(size=14)
        )
        self.total_sessions_label.pack()

        self.avg_score_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Score moyen: 0",
            font=ctk.CTkFont(size=14)
        )
        self.avg_score_label.pack()

        self.best_score_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Meilleur score: 0",
            font=ctk.CTkFont(size=14)
        )
        self.best_score_label.pack()

        self.avg_deviation_label = ctk.CTkLabel(
            self.global_stats_frame,
            text="Decalage moyen: -- ms",
            font=ctk.CTkFont(size=14)
        )
        self.avg_deviation_label.pack()

    def _create_restart_button(self):
        """Cree le bouton recommencer."""
        self.restart_btn = ctk.CTkButton(
            self,
            text="Recommencer",
            command=self._on_restart_click,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.restart_btn.pack(pady=15)

    def _on_restart_click(self):
        """Callback du bouton recommencer."""
        if self.on_restart:
            self.on_restart()

    def set_on_restart(self, callback):
        """Definit le callback pour le bouton recommencer."""
        self.on_restart = callback

    def show_results(self, result, global_stats=None):
        """Affiche les resultats d'un exercice."""
        self.score_label.configure(text=f"{result.score}/100")

        stars, label = result.get_rating()
        self.rating_label.configure(text=f"{'*' * stars} {label}")

        sign = "+" if result.mean_deviation_ms > 0 else ""
        self.deviation_label.configure(
            text=f"Decalage moyen: {sign}{result.mean_deviation_ms:.1f} ms"
        )
        self.stability_label.configure(
            text=f"Stabilite: +/-{result.std_deviation_ms:.1f} ms"
        )
        self.accuracy_label.configure(
            text=f"Precision: {result.accuracy_percent:.0f}%"
        )

        if global_stats:
            self._update_global_stats(global_stats)

    def _update_global_stats(self, global_stats):
        """Met a jour les statistiques globales."""
        self.total_sessions_label.configure(
            text=f"Sessions totales: {global_stats.get('total_sessions', 0)}"
        )
        self.avg_score_label.configure(
            text=f"Score moyen: {global_stats.get('avg_score', 0):.0f}"
        )
        self.best_score_label.configure(
            text=f"Meilleur score: {global_stats.get('best_score', 0)}"
        )
        avg_dev = global_stats.get('avg_deviation', 0)
        sign_dev = "+" if avg_dev > 0 else ""
        self.avg_deviation_label.configure(
            text=f"Decalage moyen: {sign_dev}{avg_dev:.1f} ms"
        )
