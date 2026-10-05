"""Funciones del módulo ui_base."""

from .common import *


class UiBaseMixin:

    def configure_styles(self):
        self.style.configure("Treeview", background=WHITE, fieldbackground=WHITE,
                             foreground=TEXT, rowheight=32, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background="#EAF0F7", foreground=TEXT,
                             font=("Segoe UI Semibold", 10))
        self.style.map("Treeview", background=[("selected", "#DCEAFF")], foreground=[("selected", TEXT)])
        self.style.configure("TButton", font=("Segoe UI", 10), padding=8)
        self.style.configure("Primary.TButton", background=BLUE, foreground=WHITE)
        self.style.configure("TEntry", padding=7)

    def create_layout(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=255)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=18, pady=(18, 12))
        tk.Label(brand, text="⚙", bg=SIDEBAR, fg="#62A8FF", font=("Segoe UI", 27, "bold")).pack(side="left")
        brand_text = tk.Frame(brand, bg=SIDEBAR)
        brand_text.pack(side="left", padx=8)
        tk.Label(brand_text, text="SAINT REPAIRS", bg=SIDEBAR, fg=WHITE,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="Taller de Electrónica", bg=SIDEBAR, fg="#AFC0D6",
                 font=("Segoe UI", 9)).pack(anchor="w")

        nav_container = tk.Frame(self.sidebar, bg=SIDEBAR)
        nav_container.pack(fill="both", expand=True, padx=(0, 4))
        self.nav_canvas = tk.Canvas(nav_container, bg=SIDEBAR, bd=0, highlightthickness=0, width=250)
        nav_scroll = ttk.Scrollbar(nav_container, orient="vertical", command=self.nav_canvas.yview)
        self.nav_frame = tk.Frame(self.nav_canvas, bg=SIDEBAR)
        self.nav_window = self.nav_canvas.create_window((0, 0), window=self.nav_frame, anchor="nw")
        self.nav_canvas.configure(yscrollcommand=nav_scroll.set)
        self.nav_canvas.pack(side="left", fill="both", expand=True)
        nav_scroll.pack(side="right", fill="y")

        def update_scrollregion(event=None):
            self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))
            self.nav_canvas.itemconfigure(self.nav_window, width=self.nav_canvas.winfo_width())

        self.nav_frame.bind("<Configure>", update_scrollregion)
        self.nav_canvas.bind("<Configure>", update_scrollregion)

        items = [
            ("Dashboard", self.show_dashboard, False),
            ("Órdenes de Trabajo", self.show_orders, True),
            ("Clientes", self.show_clients, True),
            ("Equipos", self.show_equipos, True),
            ("Insumos", self.show_insumos, True),
            ("Servicios", self.show_services, True),
            ("Presupuestos", self.show_budgets, True),
            ("Pagos", self.show_pagos, True),
            ("Entregas", self.show_deliveries, True),
            ("Garantías", self.show_garantias, True),
            ("Reportes", self.show_reports, True),
            ("Calendario", self.show_calendar, True),
        ]
        for label, command, popup in items:
            self._nav_button(
                self.nav_frame, label,
                (lambda cmd=command, label=label: self._safe_action(lambda: self.open_module(cmd), label))
                if popup else (lambda cmd=command, label=label: self._safe_action(cmd, label))
            )

        admin = tk.Frame(self.sidebar, bg="#041329")
        admin.pack(fill="x", side="bottom", pady=(4, 0))
        tk.Label(admin, text="ADMINISTRACIÓN", bg="#041329", fg="#7F96B4",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=18, pady=(7, 3))
        self._nav_button(admin, "Usuarios", lambda: self._safe_action(lambda: self.open_module(self.show_users), "Usuarios"), compact=True)

        session = tk.Frame(self.sidebar, bg=SIDEBAR)
        session.pack(fill="x", side="bottom", padx=10, pady=(5, 9))
        tk.Label(session, text=f"Usuario: {self.current_user_name}", bg=SIDEBAR, fg="#AFC0D6",
                 font=("Segoe UI", 8)).pack(side="left", padx=8)
        tk.Button(session, text="Salir", command=self.destroy, bd=0, relief="flat",
                  bg=SIDEBAR, fg="#FFB4B4", activebackground="#123A6A",
                  activeforeground=WHITE, font=("Segoe UI", 8, "bold"), cursor="hand2").pack(side="right", padx=5)

        self.nav_canvas.bind_all("<MouseWheel>", self._scroll_nav)
        self.nav_canvas.bind_all("<Button-4>", lambda e: self.nav_canvas.yview_scroll(-1, "units"))
        self.nav_canvas.bind_all("<Button-5>", lambda e: self.nav_canvas.yview_scroll(1, "units"))
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

    def _nav_button(self, parent, label, command, compact=False):
        button = tk.Button(parent, text="  " + label, command=command, anchor="w", bd=0,
                           relief="flat", bg=parent.cget("bg"), fg=WHITE,
                           activebackground="#123A6A", activeforeground=WHITE,
                           font=("Segoe UI", 9 if compact else 10), padx=16,
                           pady=7 if compact else 9, cursor="hand2")
        button.pack(fill="x", padx=7 if compact else 8, pady=1)
        return button

    def _scroll_nav(self, event):
        try:
            x = self.winfo_pointerx() - self.winfo_rootx()
            y = self.winfo_pointery() - self.winfo_rooty()
            if 0 <= x <= self.sidebar.winfo_width() and 70 <= y <= self.sidebar.winfo_height() - 80:
                delta = -1 if getattr(event, "delta", 0) > 0 else 1
                self.nav_canvas.yview_scroll(delta, "units")
        except tk.TclError:
            pass

    def _safe_action(self, action, label="Acción"):
        """Ejecuta una acción de interfaz y muestra cualquier error al usuario.

        Antes, una excepción dentro de un callback Tkinter podía quedar solamente
        en la consola y desde la interfaz parecía que el botón no hacía nada.
        """
        try:
            return action()
        except Exception as exc:
            messagebox.showerror(
                f"Error en {label}",
                f"La acción no pudo completarse.\n\n{type(exc).__name__}: {exc}",
                parent=self._active_module_window if self._active_module_window and self._active_module_window.winfo_exists() else self
            )
            return None

    def _new_window(self, title, geometry, parent=None, minsize=None):
        """Crea una ventana hija delante del módulo que la abrió."""
        owner = parent or (self._active_module_window if self._active_module_window and self._active_module_window.winfo_exists() else self)
        win = tk.Toplevel(owner)
        win.title(title)
        win.geometry(geometry)
        win.transient(owner)
        if minsize:
            win.minsize(*minsize)
        win.lift()
        win.focus_force()
        return win

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def header(self, title, subtitle=""):
        top = tk.Frame(self.content, bg=WHITE, height=74)
        top.pack(fill="x")
        tk.Label(top, text=title, bg=WHITE, fg=TEXT, font=("Segoe UI", 22, "bold")).pack(side="left", padx=28, pady=18)
        if subtitle:
            tk.Label(top, text=subtitle, bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(side="left", pady=25)

    def open_module(self, builder):
        builder()

    def page(self, title, subtitle="", popup=True):
        if popup:
            win = tk.Toplevel(self)
            win.title(f"SAINT REPAIRS | {title}")
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            ww, wh = min(1180, max(900, int(sw*0.82))), min(720, max(580, int(sh*0.78)))
            win.geometry(f"{ww}x{wh}+{max(0,(sw-ww)//2)}+{max(0,(sh-wh)//2)}")
            win.resizable(True, True)
            win.minsize(900, 580)
            win.configure(bg=BG)
            win.transient(self)
            win.lift()
            win.focus_force()
            self._active_module_window = win
            container = tk.Frame(win, bg=BG)
            container.pack(fill="both", expand=True)
            self._window_header(container, title, subtitle)
            body = tk.Frame(container, bg=BG)
            body.pack(fill="both", expand=True, padx=22, pady=20)
            return body
        self.clear()
        self.header(title, subtitle)
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=20)
        return body

    def _window_header(self, parent, title, subtitle=""):
        top = tk.Frame(parent, bg=WHITE, height=74)
        top.pack(fill="x")
        tk.Label(top, text=title, bg=WHITE, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(side="left", padx=28, pady=18)
        if subtitle:
            tk.Label(top, text=subtitle, bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(side="left", pady=24)
        tk.Button(top, text="Cerrar", command=parent.winfo_toplevel().destroy, bd=0, relief="flat",
                  bg=WHITE, fg=RED, activebackground="#F7E8E8", activeforeground=RED,
                  font=("Segoe UI", 9, "bold"), cursor="hand2").pack(side="right", padx=18, pady=20)

    def card(self, parent, title, value, color):
        f = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground="#E3EAF3")
        f.pack(side="left", fill="both", expand=True, padx=7)
        tk.Label(f, text=title, bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(16,4))
        tk.Label(f, text=value, bg=WHITE, fg=color, font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=18, pady=(0,16))

    def query(self, sql, params=()):
        with get_connection() as c:
            return c.execute(sql, params).fetchall()

    def execute(self, sql, params=()):
        with get_connection() as c:
            cur = c.execute(sql, params)
            c.commit()
            return cur.lastrowid

    def _money(self, value):
        return f"$ {float(value or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _date(self):
        return date.today().isoformat()

    def _require_selection(self, tree, title="Selección"):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning(title, "Seleccione un registro de la tabla antes de continuar.", parent=self)
            return None
        return sel[0]

    def _refresh_current_module(self, title, builder):
        """Recarga el módulo actual sin perder la ventana activa."""
        if builder:
            builder()

    def table_page(self, title, columns, rows, add_command=None, extra_buttons=None):
        body = self.page(title)
        bar = tk.Frame(body, bg=BG)
        bar.pack(fill="x", pady=(0,10))
        if add_command:
            ttk.Button(bar, text="+ Nuevo registro", command=lambda cmd=add_command, title=title: self._safe_action(cmd, title + " — Nuevo")).pack(side="left")
        if extra_buttons:
            for text, cmd in extra_buttons:
                ttk.Button(bar, text=text, command=lambda cmd=cmd, text=text, title=title: self._safe_action(cmd, title + " — " + text)).pack(side="left", padx=5)
        frame = tk.Frame(body, bg=WHITE)
        frame.pack(fill="both", expand=True)
        x = ttk.Scrollbar(frame, orient="horizontal")
        y = ttk.Scrollbar(frame, orient="vertical")
        tree = ttk.Treeview(frame, columns=columns, show="headings", xscrollcommand=x.set, yscrollcommand=y.set, selectmode="browse")
        x.configure(command=tree.xview); y.configure(command=tree.yview)
        wide = {"ID":70,"Orden":80,"Cliente":190,"Equipo":230,"Problema":300,"Estado":190,"Prioridad":110,
                "Ingreso":125,"Técnico":170,"Nombre":190,"Apellido":170,"Teléfono":145,"Email":240,"Documento":130,
                "Alta":125,"Tipo":150,"Marca":130,"Modelo":150,"N° Serie":190,"Estado físico":170,"Código":130,
                "Categoría":150,"Stock":90,"Mínimo":90,"Precio":125,"Costo":125,"Ubicación":120,"Descripción":300,
                "Cantidad":100,"Método":140,"Total":135,"Subtotal":135,"Fecha":150,"Recibido por":180,"Observaciones":320,
                "Activo":90,"Rol":150,"Motivo":220,"Movimiento":120,"Origen":130,"Condiciones":300}
        for c in columns:
            tree.heading(c, text=c)
            tree.column(c, width=wide.get(c,150), minwidth=80, stretch=False, anchor="w")
        tree.tag_configure("even", background="#FFFFFF"); tree.tag_configure("odd", background="#F7FAFD")
        tree.pack(side="top", fill="both", expand=True, padx=(10,0), pady=(10,0))
        y.pack(side="right", fill="y", pady=(10,0)); x.pack(side="bottom", fill="x", padx=10, pady=(0,10))
        for idx, r in enumerate(rows):
            tree.insert("", "end", values=tuple(r), tags=("even" if idx % 2 == 0 else "odd",))
        return tree

    def alert(self, parent, title, value, color):
        f = tk.Frame(parent, bg="#F8FAFD")
        f.pack(fill="x", padx=14, pady=6)
        tk.Label(f, text=value, bg="#F8FAFD", fg=color, font=("Segoe UI", 18, "bold")).pack(side="left", padx=12, pady=10)
        tk.Label(f, text=title, bg="#F8FAFD", fg=TEXT, font=("Segoe UI", 9)).pack(side="left")
