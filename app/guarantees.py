"""Funciones del módulo guarantees."""

from .common import *


class GuaranteesMixin:

    def show_garantias(self):
        rows=self.query("SELECT id_garantia,id_orden,fecha_inicio,fecha_fin,condiciones,estado FROM garantias ORDER BY fecha_fin")
        self.table_page("Garantías",("ID","Orden","Inicio","Fin","Condiciones","Estado"),rows,self.new_garantia)

    def new_garantia(self):
        orders=self.query("SELECT o.id_orden,c.nombre||' '||c.apellido cliente FROM ordenes_trabajo o JOIN clientes c ON c.id_cliente=o.id_cliente WHERE o.estado='Entregado' ORDER BY o.id_orden DESC")
        if not orders:messagebox.showinfo("Garantías","No hay órdenes entregadas disponibles.");return
        win=tk.Toplevel(self);win.title("Nueva garantía");win.geometry("500x380");tk.Label(win,text="Orden").pack(pady=(25,5));cb=ttk.Combobox(win,state="readonly",width=42,values=[f"{r['id_orden']} - {r['cliente']}" for r in orders]);cb.pack();tk.Label(win,text="Fecha inicio (AAAA-MM-DD)").pack(pady=(15,5));fi=ttk.Entry(win);fi.insert(0,self._date());fi.pack();tk.Label(win,text="Fecha fin (AAAA-MM-DD)").pack(pady=(15,5));ff=ttk.Entry(win);ff.insert(0,(date.today()+timedelta(days=30)).isoformat());ff.pack();tk.Label(win,text="Condiciones").pack(pady=(15,5));co=ttk.Entry(win,width=42);co.pack()
        def save():
            if not cb.get():return
            oid=int(cb.get().split(" - ")[0])
            try:self.execute("INSERT INTO garantias(id_orden,fecha_inicio,fecha_fin,condiciones,estado) VALUES (?,?,?,?,?)",(oid,fi.get().strip(),ff.get().strip(),co.get().strip(),"Activa"))
            except sqlite3.IntegrityError:messagebox.showwarning("Garantía","La orden ya tiene una garantía registrada.",parent=win);return
            win.destroy();self.show_garantias()
        ttk.Button(win,text="Guardar garantía",command=save).pack(pady=22)
