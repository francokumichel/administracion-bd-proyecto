"""Funciones del módulo inventory."""

from .common import *


class InventoryMixin:

    def show_insumos(self):
        rows=self.query("SELECT id_insumo,nombre,codigo,categoria,marca,modelo_compatible,costo,precio_venta,stock,stock_minimo,ubicacion FROM insumos ORDER BY nombre")
        self.insumo_tree=self.table_page("Insumos",("ID","Nombre","Código","Categoría","Marca","Modelo","Costo","Precio","Stock","Mínimo","Ubicación"),rows,self.new_insumo,
                                         [("Editar",self.edit_insumo),("Eliminar",self.delete_insumo),("Entrada stock",self.stock_entry),("Movimientos",self.show_movements)])

    def insumo_form(self,row=None):
        win=tk.Toplevel(self);win.title("Insumo");win.geometry("620x620")
        fields=["Nombre","Código","Categoría","Marca","Modelo compatible","Costo","Precio venta","Stock","Stock mínimo","Ubicación","Observaciones"];es={}
        for i,l in enumerate(fields):
            tk.Label(win,text=l).grid(row=i,column=0,sticky="w",padx=18,pady=6);e=ttk.Entry(win,width=44);e.grid(row=i,column=1,padx=18,pady=6);es[l]=e
        if row:
            vals=[row["nombre"],row["codigo"] or "",row["categoria"] or "",row["marca"] or "",row["modelo_compatible"] or "",row["costo"],row["precio_venta"],row["stock"],row["stock_minimo"],row["ubicacion"] or "",row["observaciones"] or ""]
            for l,v in zip(fields,vals):es[l].insert(0,str(v))
        def num(k,integer=False):
            try:return int(float(es[k].get() or 0)) if integer else float(es[k].get() or 0)
            except:return 0
        def save():
            if not es["Nombre"].get().strip():messagebox.showwarning("Validación","El nombre es obligatorio.",parent=win);return
            vals=(es["Nombre"].get().strip(),es["Código"].get().strip() or None,es["Categoría"].get().strip(),es["Marca"].get().strip(),es["Modelo compatible"].get().strip(),num("Costo"),num("Precio venta"),num("Stock",True),num("Stock mínimo",True),es["Ubicación"].get().strip(),es["Observaciones"].get().strip())
            try:
                if row:self.execute("UPDATE insumos SET nombre=?,codigo=?,categoria=?,marca=?,modelo_compatible=?,costo=?,precio_venta=?,stock=?,stock_minimo=?,ubicacion=?,observaciones=? WHERE id_insumo=?",vals+(row["id_insumo"],))
                else:self.execute("INSERT INTO insumos(nombre,codigo,categoria,marca,modelo_compatible,costo,precio_venta,stock,stock_minimo,ubicacion,observaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?)",vals)
                win.destroy();self.show_insumos()
            except sqlite3.IntegrityError:messagebox.showerror("Error","El código ya existe.",parent=win)
        ttk.Button(win,text="Guardar insumo",command=save).grid(row=12,column=1,pady=18,sticky="e")

    def new_insumo(self):self.insumo_form()

    def edit_insumo(self):
        sel=self._require_selection(self.insumo_tree, "Editar insumo")
        if sel:self.insumo_form(self.query("SELECT * FROM insumos WHERE id_insumo=?",(self.insumo_tree.item(sel)["values"][0],))[0])

    def delete_insumo(self):
        sel=self._require_selection(self.insumo_tree, "Eliminar insumo")
        if not sel:return
        iid=self.insumo_tree.item(sel)["values"][0]
        if messagebox.askyesno("Confirmar","¿Eliminar insumo?"):
            try:self.execute("DELETE FROM insumos WHERE id_insumo=?",(iid,));self.show_insumos()
            except sqlite3.IntegrityError:messagebox.showerror("No se puede eliminar","El insumo tiene órdenes o movimientos asociados.")

    def stock_entry(self):
        sel=self._require_selection(self.insumo_tree, "Entrada de stock")
        if not sel:return
        iid=int(self.insumo_tree.item(sel)["values"][0]);win=tk.Toplevel(self);win.title("Entrada de stock");win.geometry("400x250")
        tk.Label(win,text="Cantidad").pack(pady=(25,5));q=ttk.Entry(win);q.pack()
        tk.Label(win,text="Motivo").pack(pady=(12,5));m=ttk.Entry(win);m.pack()
        def save():
            try:n=int(q.get())
            except:messagebox.showwarning("Validación","Ingrese una cantidad entera.",parent=win);return
            if n<=0:return
            self.execute("UPDATE insumos SET stock=stock+? WHERE id_insumo=?",(n,iid));self.execute("INSERT INTO movimientos_insumos(id_insumo,id_usuario,tipo,cantidad,motivo) VALUES (?,?,?,?,?)",(iid,self.current_user_id,"ENTRADA",n,m.get().strip() or "Ajuste de stock"));win.destroy();self.show_insumos()
        ttk.Button(win,text="Registrar entrada",command=save).pack(pady=20)

    def show_movements(self):
        rows=self.query("""SELECT m.id_movimiento,i.nombre,m.tipo,m.cantidad,m.fecha,COALESCE(m.id_orden,'-'),COALESCE(u.nombre,'-'),COALESCE(m.motivo,'')
                          FROM movimientos_insumos m JOIN insumos i ON i.id_insumo=m.id_insumo LEFT JOIN usuarios u ON u.id_usuario=m.id_usuario ORDER BY m.id_movimiento DESC""")
        self.table_page("Movimientos de insumos",("ID","Insumo","Movimiento","Cantidad","Fecha","Orden","Usuario","Motivo"),rows)
