"""Funciones del módulo payments."""

from .common import *


class PaymentsMixin:

    def show_pagos(self):
        rows=self.query("""SELECT p.id_pago,p.id_orden,c.nombre||' '||c.apellido,p.fecha,p.monto,p.metodo_pago,COALESCE(p.tipo,''),COALESCE(p.observaciones,'')
                          FROM pagos p JOIN ordenes_trabajo o ON o.id_orden=p.id_orden JOIN clientes c ON c.id_cliente=o.id_cliente ORDER BY p.id_pago DESC""")
        self.table_page("Pagos",("ID","Orden","Cliente","Fecha","Monto","Método","Tipo","Observaciones"),rows,self.new_pago)

    def new_pago(self):
        orders=self.query("SELECT o.id_orden,c.nombre||' '||c.apellido cliente FROM ordenes_trabajo o JOIN clientes c ON c.id_cliente=o.id_cliente ORDER BY o.id_orden DESC")
        if not orders:messagebox.showinfo("Pagos","Primero debe existir una orden.");return
        win=tk.Toplevel(self);win.title("Registrar pago");win.geometry("470x420")
        labels=["Orden","Monto","Método","Tipo","Observaciones"];tk.Label(win,text="Orden").pack(pady=(20,5));cb=ttk.Combobox(win,state="readonly",width=40,values=[f"{r['id_orden']} - {r['cliente']}" for r in orders]);cb.pack()
        tk.Label(win,text="Monto").pack(pady=(15,5));e=ttk.Entry(win);e.pack();tk.Label(win,text="Método").pack(pady=(15,5));m=ttk.Combobox(win,state="readonly",values=METODOS_PAGO);m.pack();tk.Label(win,text="Tipo").pack(pady=(15,5));t=ttk.Combobox(win,state="readonly",values=["Seña","Pago","Saldo"]);t.set("Pago");t.pack();tk.Label(win,text="Observaciones").pack(pady=(15,5));o=ttk.Entry(win,width=40);o.pack()
        def save():
            try:amt=float(e.get())
            except:messagebox.showwarning("Validación","Monto inválido.",parent=win);return
            if not cb.get() or amt<=0:return
            oid=int(cb.get().split(" - ")[0]);self.execute("INSERT INTO pagos(id_orden,fecha,monto,metodo_pago,tipo,observaciones) VALUES (?,?,?,?,?,?)",(oid,self._date(),amt,m.get() or "Efectivo",t.get(),o.get().strip()));win.destroy();self.show_pagos()
        ttk.Button(win,text="Registrar",command=save).pack(pady=20)
