"""Funciones del módulo clients."""

from .common import *


class ClientsMixin:

    def show_clients(self):
        rows=self.query("SELECT id_cliente,nombre,apellido,telefono,email,documento,fecha_alta FROM clientes ORDER BY id_cliente DESC")
        self.client_tree=self.table_page("Clientes",("ID","Nombre","Apellido","Teléfono","Email","Documento","Alta"),rows,self.new_client,
                                         [("Editar",self.edit_client),("Eliminar",self.delete_client)])

    def client_form(self,row=None):
        win=tk.Toplevel(self); win.title("Cliente"); win.geometry("540x520"); win.transient(self)
        fields=["Nombre","Apellido","Teléfono","Email","Dirección","Documento","Observaciones"]; entries={}
        for i,label in enumerate(fields):
            tk.Label(win,text=label).grid(row=i,column=0,sticky="w",padx=20,pady=8)
            e=ttk.Entry(win,width=44); e.grid(row=i,column=1,padx=20,pady=8); entries[label]=e
        if row:
            vals=[row["nombre"],row["apellido"],row["telefono"] or "",row["email"] or "",row["direccion"] or "",row["documento"] or "",row["observaciones"] or ""]
            for e,v in zip(entries.values(),vals): e.insert(0,v)
        def save():
            if not entries["Nombre"].get().strip() or not entries["Apellido"].get().strip():
                messagebox.showwarning("Validación","Nombre y apellido son obligatorios.",parent=win); return
            vals=tuple(entries[x].get().strip() for x in fields)
            if row:
                self.execute("UPDATE clientes SET nombre=?,apellido=?,telefono=?,email=?,direccion=?,documento=?,observaciones=? WHERE id_cliente=?",vals+(row["id_cliente"],))
            else:
                self.execute("INSERT INTO clientes(nombre,apellido,telefono,email,direccion,documento,fecha_alta,observaciones) VALUES (?,?,?,?,?,?,?,?)",vals[:6]+(self._date(),vals[6]))
            win.destroy(); self.show_clients()
        ttk.Button(win,text="Guardar",command=save).grid(row=8,column=1,pady=20,sticky="e")

    def new_client(self): self.client_form()

    def edit_client(self):
        sel=self._require_selection(self.client_tree, "Editar cliente")
        if sel:self.client_form(self.query("SELECT * FROM clientes WHERE id_cliente=?",(self.client_tree.item(sel)["values"][0],))[0])

    def delete_client(self):
        sel=self._require_selection(self.client_tree, "Eliminar cliente")
        if not sel:return
        cid=self.client_tree.item(sel)["values"][0]
        if messagebox.askyesno("Confirmar","¿Eliminar cliente seleccionado?"):
            try:self.execute("DELETE FROM clientes WHERE id_cliente=?",(cid,)); self.show_clients()
            except sqlite3.IntegrityError:messagebox.showerror("No se puede eliminar","El cliente tiene equipos u órdenes asociadas.")
