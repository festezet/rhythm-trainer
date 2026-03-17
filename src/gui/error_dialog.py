"""
Dialog d'erreur avec texte copiable.
Extrait de main_window.py pour modularite.
"""

import customtkinter as ctk
import tkinter as tk


class ErrorDialog(ctk.CTkToplevel):
    """Dialog avec texte d'erreur copiable."""

    def __init__(self, master, title: str, message: str):
        super().__init__(master)
        self.title(title)
        self.geometry("600x300")
        self.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        self.transient(master)

        ctk.CTkLabel(
            self, text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ff4757"
        ).pack(pady=(15, 5))

        # Zone de texte copiable (tk.Text, pas CTk)
        text_frame = ctk.CTkFrame(self, fg_color=("#ffffff", "#1f2937"))
        text_frame.pack(fill='both', expand=True, padx=15, pady=10)

        self.text_widget = tk.Text(
            text_frame, wrap='word', font=('Consolas', 11),
            bg='#1f2937', fg='#eaeaea', insertbackground='#eaeaea',
            selectbackground='#4ecdc4', relief='flat', padx=10, pady=10
        )
        self.text_widget.pack(fill='both', expand=True)
        self.text_widget.insert('1.0', message)
        self.text_widget.configure(state='normal')  # Garder editable pour copier

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text="Copier", width=100,
            command=self._copy_to_clipboard
        ).pack(side='left', padx=5)

        ctk.CTkButton(
            btn_frame, text="Fermer", width=100,
            fg_color=("gray70", "gray30"),
            command=self.destroy
        ).pack(side='left', padx=5)

        self.after(100, lambda: self.grab_set())

    def _copy_to_clipboard(self):
        """Copie le texte dans le presse-papier."""
        self.clipboard_clear()
        self.clipboard_append(self.text_widget.get('1.0', 'end').strip())
