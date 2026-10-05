"""Autenticación de usuarios."""

import tkinter as tk
from tkinter import messagebox, ttk

from .common import WHITE, BLUE, TEXT, MUTED, SIDEBAR, get_connection


class Login(tk.Tk):
    def __init__(self):
        super().__init__()
        self.authenticated = False
        self.user_id = None
        self.user_name = None
        self.title("SAINT REPAIRS | Acceso")
        self.geometry("430x430")
        self.resizable(False, False)
        self.configure(bg=SIDEBAR)

        card = tk.Frame(self, bg=WHITE)
        card.pack(fill="both", expand=True, padx=28, pady=28)
        tk.Label(card, text="⚙", bg=WHITE, fg=BLUE, font=("Segoe UI", 40, "bold")).pack(pady=(25, 0))
        tk.Label(card, text="SAINT REPAIRS", bg=WHITE, fg=TEXT, font=("Segoe UI", 19, "bold")).pack()
        tk.Label(card, text="Acceso al sistema", bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(pady=(0, 22))
        tk.Label(card, text="Usuario", bg=WHITE, fg=TEXT).pack(anchor="w", padx=45)
        self.user = ttk.Entry(card, width=32)
        self.user.pack(pady=(5, 12))
        tk.Label(card, text="Contraseña", bg=WHITE, fg=TEXT).pack(anchor="w", padx=45)
        self.password = ttk.Entry(card, width=32, show="•")
        self.password.pack(pady=(5, 20))
        ttk.Button(card, text="Ingresar", command=self.login).pack(ipadx=25, ipady=3)
        tk.Label(card, text="Usuario inicial: admin / admin", bg=WHITE, fg=MUTED, font=("Segoe UI", 8)).pack(pady=18)
        self.bind("<Return>", lambda e: self.login())
        self.user.focus_set()

    def login(self):
        u = self.user.get().strip()
        p = self.password.get()
        if not u or not p:
            messagebox.showwarning("Acceso", "Ingrese usuario y contraseña.", parent=self)
            return
        with get_connection() as c:
            row = c.execute(
                "SELECT id_usuario,nombre FROM usuarios WHERE usuario=? AND contrasena_hash=? AND activo=1",
                (u, p)
            ).fetchone()
        if row:
            self.authenticated = True
            self.user_id = row["id_usuario"]
            self.user_name = row["nombre"]
            self.destroy()
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.", parent=self)
