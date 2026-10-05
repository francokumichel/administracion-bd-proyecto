"""Funciones del módulo dashboard."""

from .common import *


class DashboardMixin:

    def show_dashboard(self):
        body = self.page("Dashboard", "Resumen operativo del taller", popup=False)
        stats = tk.Frame(body, bg=BG)
        stats.pack(fill="x")
        process = self.query("SELECT COUNT(*) n FROM ordenes_trabajo WHERE estado NOT IN ('Entregado','Cancelado')")[0]["n"]
        ready = self.query("SELECT COUNT(*) n FROM ordenes_trabajo WHERE estado='Listo para entregar'")[0]["n"]
        waiting = self.query("SELECT COUNT(*) n FROM ordenes_trabajo WHERE estado='Esperando repuesto'")[0]["n"]
        income = self.query("SELECT COALESCE(SUM(monto),0) total FROM pagos WHERE strftime('%Y-%m',fecha)=strftime('%Y-%m','now')")[0]["total"]
        self.card(stats, "Órdenes en proceso", process, BLUE)
        self.card(stats, "Listas para entregar", ready, GREEN)
        self.card(stats, "Esperando insumos", waiting, ORANGE)
        self.card(stats, "Ingresos del mes", self._money(income), PURPLE)

        # Zona inferior en GRID para garantizar que el panel de alertas conserve
        # su ancho y que la tabla de órdenes use solamente el espacio restante.
        lower = tk.Frame(body, bg=BG)
        lower.pack(fill="both", expand=True, pady=(18, 0))
        lower.grid_rowconfigure(0, weight=1)
        lower.grid_columnconfigure(0, weight=1)
        lower.grid_columnconfigure(1, weight=0, minsize=320)

        left = tk.Frame(lower, bg=WHITE, highlightthickness=1, highlightbackground="#E3EAF3")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(left, text="Órdenes de trabajo recientes", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=18, pady=14)

        table_wrap = tk.Frame(left, bg=WHITE)
        table_wrap.pack(fill="both", expand=True, padx=14, pady=(0,14))
        cols = ("ID","Cliente","Equipo","Problema","Estado","Ingreso")
        tree = ttk.Treeview(table_wrap, columns=cols, show="headings")
        widths = {"ID":60, "Cliente":150, "Equipo":145, "Problema":230, "Estado":165, "Ingreso":105}
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=widths[c], minwidth=55, stretch=(c in ("Cliente","Equipo","Problema","Estado")))
        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        rows = self.query("""
            SELECT o.id_orden,c.nombre||' '||c.apellido cliente,
                   trim(e.tipo||' '||COALESCE(e.marca,'')||' '||COALESCE(e.modelo,'')) equipo,
                   o.problema_informado,o.estado,substr(o.fecha_ingreso,1,10)
            FROM ordenes_trabajo o
            JOIN clientes c ON c.id_cliente=o.id_cliente
            JOIN equipos e ON e.id_equipo=o.id_equipo
            ORDER BY o.id_orden DESC LIMIT 8
        """)
        for r in rows:
            tree.insert("", "end", values=tuple(r))

        right = tk.Frame(lower, bg=WHITE, width=320, highlightthickness=1, highlightbackground="#E3EAF3")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_propagate(False)
        tk.Label(right, text="Alertas", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=18, pady=14)
        low = self.query("SELECT COUNT(*) n FROM insumos WHERE stock <= stock_minimo")[0]["n"]
        overdue = self.query("""SELECT COUNT(*) n FROM ordenes_trabajo
            WHERE fecha_estimada IS NOT NULL AND datetime(fecha_estimada)<datetime('now')
            AND estado NOT IN ('Entregado','Cancelado')""")[0]["n"]
        self.alert(right, "Insumos bajo mínimo", str(low), ORANGE)
        self.alert(right, "Órdenes demoradas", str(overdue), RED)

        tk.Label(right, text="Agenda", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=18, pady=(18,8))
        upcoming = self.query("""SELECT id_orden,fecha_estimada,estado FROM ordenes_trabajo
            WHERE fecha_estimada IS NOT NULL AND datetime(fecha_estimada)>=datetime('now')
            ORDER BY fecha_estimada LIMIT 5""")
        agenda = tk.Frame(right, bg=WHITE)
        agenda.pack(fill="both", expand=True, padx=12, pady=(0,12))
        if not upcoming:
            tk.Label(agenda, text="No hay actividades próximas.", bg=WHITE, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", padx=6, pady=6)
        else:
            for r in upcoming:
                item = tk.Frame(agenda, bg="#F8FAFD")
                item.pack(fill="x", pady=4)
                tk.Label(item, text=f"#{r['id_orden']:05d}", bg="#F8FAFD", fg=BLUE,
                         font=("Segoe UI", 9, "bold"), width=7, anchor="w").pack(side="left", padx=(8,2), pady=8)
                tk.Label(item, text=f"{r['fecha_estimada']}\n{r['estado']}",
                         bg="#F8FAFD", fg=MUTED, justify="left", anchor="w",
                         font=("Segoe UI", 8)).pack(side="left", fill="x", expand=True, padx=4, pady=6)
