"""Funciones del módulo equipment."""

from .common import *


class EquipmentMixin:

    def show_equipos(self):
        rows=self.query("""SELECT e.id_equipo,c.nombre||' '||c.apellido cliente,e.tipo,e.marca,e.modelo,e.numero_serie,e.estado_fisico
                          FROM equipos e JOIN clientes c ON c.id_cliente=e.id_cliente ORDER BY e.id_equipo DESC""")
        self.equipo_tree=self.table_page("Equipos",("ID","Cliente","Tipo","Marca","Modelo","N° Serie","Estado físico"),rows,self.new_equipo,
                                         [("Editar",self.edit_equipo),("Eliminar",self.delete_equipo)])

    def equipo_form(self,row=None):
        win=tk.Toplevel(self); win.title("Equipo"); win.geometry("580x620")
        clients=self.query("SELECT id_cliente,nombre||' '||apellido nombre FROM clientes ORDER BY nombre,apellido")
        tk.Label(win,text="Cliente").grid(row=0,column=0,sticky="w",padx=20,pady=8)
        cb_client=ttk.Combobox(win,width=42,state="readonly",values=[f"{r['id_cliente']} - {r['nombre']}" for r in clients]);cb_client.grid(row=0,column=1,padx=20,pady=8)
        tk.Label(win,text="Tipo").grid(row=1,column=0,sticky="w",padx=20,pady=8)
        cb_tipo=ttk.Combobox(win,width=42,state="readonly",values=TIPOS_EQUIPO);cb_tipo.grid(row=1,column=1,padx=20,pady=8)
        fields=["Marca","Modelo","Número de serie","IMEI","Color","Clave dispositivo","Accesorios entregados","Estado físico","Observaciones"]; es=[]
        for i,label in enumerate(fields,2):
            tk.Label(win,text=label).grid(row=i,column=0,sticky="w",padx=20,pady=6)
            e=ttk.Entry(win,width=44);e.grid(row=i,column=1,padx=20,pady=6);es.append(e)
        if row:
            cb_client.set(f"{row['id_cliente']} - "+self.query("SELECT nombre||' '||apellido nombre FROM clientes WHERE id_cliente=?",(row['id_cliente'],))[0]["nombre"])
            cb_tipo.set(row["tipo"])
            vals=[row["marca"] or "",row["modelo"] or "",row["numero_serie"] or "",row["imei"] or "",row["color"] or "",row["clave_dispositivo"] or "",row["accesorios_entregados"] or "",row["estado_fisico"] or "",row["observaciones"] or ""]
            for e,v in zip(es,vals):e.insert(0,v)
        def save():
            if not cb_client.get() or not cb_tipo.get():messagebox.showwarning("Validación","Cliente y tipo son obligatorios.",parent=win);return
            cid=int(cb_client.get().split(" - ")[0]); vals=[e.get().strip() for e in es]
            if row:self.execute("UPDATE equipos SET id_cliente=?,tipo=?,marca=?,modelo=?,numero_serie=?,imei=?,color=?,clave_dispositivo=?,accesorios_entregados=?,estado_fisico=?,observaciones=? WHERE id_equipo=?",(cid,cb_tipo.get(),*vals,row["id_equipo"]))
            else:self.execute("INSERT INTO equipos(id_cliente,tipo,marca,modelo,numero_serie,imei,color,clave_dispositivo,accesorios_entregados,estado_fisico,observaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(cid,cb_tipo.get(),*vals))
            win.destroy();self.show_equipos()
        ttk.Button(win,text="Guardar",command=save).grid(row=12,column=1,pady=20,sticky="e")

    def new_equipo(self): self.equipo_form()

    def edit_equipo(self):
        sel=self._require_selection(self.equipo_tree, "Editar equipo")
        if sel:self.equipo_form(self.query("SELECT * FROM equipos WHERE id_equipo=?",(self.equipo_tree.item(sel)["values"][0],))[0])

    def delete_equipo(self):
        sel=self._require_selection(self.equipo_tree, "Eliminar equipo")
        if not sel:return
        eid=self.equipo_tree.item(sel)["values"][0]
        if messagebox.askyesno("Confirmar","¿Eliminar equipo?"):
            try:self.execute("DELETE FROM equipos WHERE id_equipo=?",(eid,));self.show_equipos()
            except sqlite3.IntegrityError:messagebox.showerror("No se puede eliminar","El equipo tiene órdenes asociadas.")
