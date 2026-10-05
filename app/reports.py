"""Funciones del módulo reports."""

from .common import *


class ReportsMixin:

    def show_calendar(self):
        rows=self.query("""SELECT o.id_orden,o.fecha_estimada,c.nombre||' '||c.apellido,o.estado,o.problema_informado
                          FROM ordenes_trabajo o JOIN clientes c ON c.id_cliente=o.id_cliente
                          WHERE o.fecha_estimada IS NOT NULL ORDER BY o.fecha_estimada""")
        self.table_page("Calendario",("Orden","Fecha","Cliente","Estado","Problema"),rows)

    def show_reports(self):
        body=self.page("Reportes","Consultas y exportación")
        for text,cmd in [("Órdenes por estado",self.report_status),("Ingresos del mes",self.report_income),("Stock bajo",self.report_stock),("Movimientos de insumos",self.report_movements),("Exportar órdenes CSV",self.export_orders)]:
            ttk.Button(body,text=text,command=cmd).pack(fill="x",pady=7,ipady=4)

    def report_status(self):self.report_window("Órdenes por estado",("Estado","Cantidad"),self.query("SELECT estado,COUNT(*) FROM ordenes_trabajo GROUP BY estado ORDER BY COUNT(*) DESC"))

    def report_income(self):self.report_window("Ingresos del mes",("Método","Operaciones","Total"),self.query("SELECT metodo_pago,COUNT(*),COALESCE(SUM(monto),0) FROM pagos WHERE strftime('%Y-%m',fecha)=strftime('%Y-%m','now') GROUP BY metodo_pago ORDER BY SUM(monto) DESC"))

    def report_stock(self):self.report_window("Stock bajo",("Insumo","Código","Stock","Mínimo","Precio"),self.query("SELECT nombre,codigo,stock,stock_minimo,precio_venta FROM insumos WHERE stock<=stock_minimo ORDER BY stock"))

    def report_movements(self):self.report_window("Movimientos de insumos",("Insumo","Tipo","Cantidad","Fecha","Orden","Motivo"),self.query("SELECT i.nombre,m.tipo,m.cantidad,m.fecha,COALESCE(m.id_orden,'-'),COALESCE(m.motivo,'') FROM movimientos_insumos m JOIN insumos i ON i.id_insumo=m.id_insumo ORDER BY m.id_movimiento DESC"))

    def report_window(self,title,columns,rows):
        win=tk.Toplevel(self);win.title(title);win.geometry("850x500");tree=ttk.Treeview(win,columns=columns,show="headings")
        for c in columns:tree.heading(c,text=c);tree.column(c,width=145)
        for r in rows:tree.insert("","end",values=tuple(r))
        tree.pack(fill="both",expand=True,padx=15,pady=15)

    def export_orders(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="ordenes_saint_repairs.csv")
        if not path:return
        rows=self.query("""SELECT o.id_orden,c.nombre||' '||c.apellido,e.tipo||' '||COALESCE(e.marca,'')||' '||COALESCE(e.modelo,''),o.problema_informado,o.estado,o.prioridad,o.fecha_ingreso
                          FROM ordenes_trabajo o JOIN clientes c ON c.id_cliente=o.id_cliente JOIN equipos e ON e.id_equipo=o.id_equipo ORDER BY o.id_orden DESC""")
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f,delimiter=";");w.writerow(["ID","Cliente","Equipo","Problema","Estado","Prioridad","Fecha ingreso"]);w.writerows([tuple(r) for r in rows])
        messagebox.showinfo("Exportación","Archivo CSV generado correctamente.")
