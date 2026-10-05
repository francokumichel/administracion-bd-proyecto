"""Funciones del módulo services."""

from .common import *


class ServicesMixin:

    def show_services(self):
        rows=self.query("SELECT id_servicio,nombre,descripcion,precio_base,tiempo_estimado FROM servicios ORDER BY nombre")
        self.service_tree=self.table_page("Servicios",("ID","Nombre","Descripción","Precio","Tiempo (min)"),rows,self.new_service,[("Editar",self.edit_service),("Eliminar",self.delete_service)])
        self.service_tree.bind("<Double-1>", lambda e: self._safe_action(self.edit_service, "Servicios — Editar"))

    def service_form(self,row=None):
        win=self._new_window("Editar servicio" if row else "Nuevo servicio", "520x330")
        win.grab_set()
        fields=["Nombre","Descripción","Precio","Tiempo estimado (min)"];es=[]
        for i,l in enumerate(fields):
            tk.Label(win,text=l).grid(row=i,column=0,sticky="w",padx=20,pady=10)
            e=ttk.Entry(win,width=38);e.grid(row=i,column=1,padx=20,pady=10);es.append(e)
        if row:
            for e,v in zip(es,[row["nombre"],row["descripcion"] or "",row["precio_base"],row["tiempo_estimado"] or 0]):e.insert(0,str(v))
        def save():
            nombre=es[0].get().strip()
            if not nombre:
                messagebox.showwarning("Validación","El nombre del servicio es obligatorio.",parent=win);es[0].focus_set();return
            try:
                p=float(es[2].get() or 0)
                t=int(es[3].get() or 0)
                if p < 0 or t < 0: raise ValueError
            except ValueError:
                messagebox.showwarning("Validación","Precio y tiempo deben ser números válidos y no negativos.",parent=win);return
            try:
                if row:
                    self.execute("UPDATE servicios SET nombre=?,descripcion=?,precio_base=?,tiempo_estimado=? WHERE id_servicio=?",(nombre,es[1].get().strip(),p,t,row["id_servicio"]))
                else:
                    self.execute("INSERT INTO servicios(nombre,descripcion,precio_base,tiempo_estimado) VALUES (?,?,?,?)",(nombre,es[1].get().strip(),p,t))
                win.grab_release();win.destroy();self.show_services()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error","Ya existe un servicio con ese nombre.",parent=win)
        ttk.Button(win,text="Guardar",command=save,style="Primary.TButton").grid(row=5,column=1,pady=15,sticky="e")
        ttk.Button(win,text="Cancelar",command=lambda:(win.grab_release(),win.destroy())).grid(row=5,column=0,pady=15,padx=20,sticky="w")
        win.bind("<Return>",lambda e:save())
        es[0].focus_set()

    def new_service(self):self.service_form()

    def edit_service(self):
        sel=self._require_selection(self.service_tree, "Editar servicio")
        if sel:self.service_form(self.query("SELECT * FROM servicios WHERE id_servicio=?",(self.service_tree.item(sel)["values"][0],))[0])

    def delete_service(self):
        sel=self._require_selection(self.service_tree, "Eliminar servicio")
        if not sel:return
        sid=self.service_tree.item(sel)["values"][0]
        if messagebox.askyesno("Confirmar","¿Eliminar servicio?"):
            try:self.execute("DELETE FROM servicios WHERE id_servicio=?",(sid,));self.show_services()
            except sqlite3.IntegrityError:messagebox.showerror("No se puede eliminar","El servicio está utilizado en órdenes.")
