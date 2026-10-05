"""Funciones del módulo deliveries."""

from .common import *


class DeliveriesMixin:

    def show_deliveries(self):
        rows=self.query("""SELECT e.id_entrega,e.id_orden,c.nombre||' '||c.apellido,e.fecha,e.recibido_por,e.observaciones
                          FROM entregas e JOIN ordenes_trabajo o ON o.id_orden=e.id_orden JOIN clientes c ON c.id_cliente=o.id_cliente ORDER BY e.id_entrega DESC""")
        self.table_page("Entregas",("ID","Orden","Cliente","Fecha","Recibido por","Observaciones"),rows,self.new_delivery)

    def new_delivery(self):
        orders=self.query("SELECT o.id_orden,c.nombre||' '||c.apellido cliente FROM ordenes_trabajo o JOIN clientes c ON c.id_cliente=o.id_cliente WHERE o.estado='Listo para entregar' ORDER BY o.id_orden DESC")
        if not orders:messagebox.showinfo("Entregas","No hay órdenes listas para entregar.");return
        win=tk.Toplevel(self);win.title("Registrar entrega");win.geometry("470x320");tk.Label(win,text="Orden").pack(pady=(25,5));cb=ttk.Combobox(win,state="readonly",width=40,values=[f"{r['id_orden']} - {r['cliente']}" for r in orders]);cb.pack();tk.Label(win,text="Recibido por").pack(pady=(15,5));r=ttk.Entry(win,width=40);r.pack();tk.Label(win,text="Observaciones").pack(pady=(15,5));o=ttk.Entry(win,width=40);o.pack()
        def save():
            if not cb.get() or not r.get().strip():messagebox.showwarning("Validación","Orden y persona que recibe son obligatorios.",parent=win);return
            oid=int(cb.get().split(" - ")[0]);now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:self.execute("INSERT INTO entregas(id_orden,fecha,recibido_por,observaciones) VALUES (?,?,?,?)",(oid,now,r.get().strip(),o.get().strip()))
            except sqlite3.IntegrityError:messagebox.showwarning("Entrega","La orden ya tiene una entrega registrada.",parent=win);return
            self.execute("UPDATE ordenes_trabajo SET estado='Entregado',fecha_finalizacion=? WHERE id_orden=?",(now,oid));self.add_history(oid,"Listo para entregar","Entregado","Entrega registrada");win.destroy();self.show_deliveries()
        ttk.Button(win,text="Registrar entrega",command=save).pack(pady=22)
