"""Funciones del módulo orders."""

from .common import *


class OrdersMixin:

    def show_orders(self):
        rows=self.query("""SELECT o.id_orden,c.nombre||' '||c.apellido cliente,
                   e.tipo||' '||COALESCE(e.marca,'')||' '||COALESCE(e.modelo,'') equipo,
                   o.problema_informado,o.estado,o.prioridad,substr(o.fecha_ingreso,1,10),COALESCE(u.nombre,'-')
            FROM ordenes_trabajo o JOIN clientes c ON c.id_cliente=o.id_cliente JOIN equipos e ON e.id_equipo=o.id_equipo
            LEFT JOIN usuarios u ON u.id_usuario=o.id_tecnico ORDER BY o.id_orden DESC""")
        self.order_tree=self.table_page("Órdenes de Trabajo",("ID","Cliente","Equipo","Problema","Estado","Prioridad","Ingreso","Técnico"),rows,self.new_order,
                                        [("Editar",self.edit_order),("Servicios/Insumos",self.order_components),("Diagnóstico",self.edit_diagnosis),("Historial",self.view_order_history),("Cambiar estado",self.change_order_state),("Eliminar",self.delete_order)])

    def order_form(self,row=None):
        win=tk.Toplevel(self);win.title("Orden de Trabajo");win.geometry("700x760")
        clients=self.query("SELECT id_cliente,nombre||' '||apellido nombre FROM clientes ORDER BY nombre,apellido")
        tk.Label(win,text="Cliente").grid(row=0,column=0,sticky="w",padx=18,pady=7)
        cb_c=ttk.Combobox(win,width=48,state="readonly",values=[f"{r['id_cliente']} - {r['nombre']}" for r in clients]);cb_c.grid(row=0,column=1,padx=18,pady=7)
        tk.Label(win,text="Equipo").grid(row=1,column=0,sticky="w",padx=18,pady=7)
        cb_e=ttk.Combobox(win,width=48,state="readonly");cb_e.grid(row=1,column=1,padx=18,pady=7)
        tk.Label(win,text="Fecha estimada (AAAA-MM-DD HH:MM)").grid(row=2,column=0,sticky="w",padx=18,pady=7)
        e_date=ttk.Entry(win,width=51);e_date.grid(row=2,column=1,padx=18,pady=7)
        tk.Label(win,text="Problema informado").grid(row=3,column=0,sticky="w",padx=18,pady=7)
        e_prob=ttk.Entry(win,width=51);e_prob.grid(row=3,column=1,padx=18,pady=7)
        tk.Label(win,text="Diagnóstico").grid(row=4,column=0,sticky="w",padx=18,pady=7)
        e_diag=ttk.Entry(win,width=51);e_diag.grid(row=4,column=1,padx=18,pady=7)
        tk.Label(win,text="Solución").grid(row=5,column=0,sticky="w",padx=18,pady=7)
        e_sol=ttk.Entry(win,width=51);e_sol.grid(row=5,column=1,padx=18,pady=7)
        tk.Label(win,text="Estado").grid(row=6,column=0,sticky="w",padx=18,pady=7)
        cb_s=ttk.Combobox(win,width=48,state="readonly",values=ESTADOS);cb_s.grid(row=6,column=1,padx=18,pady=7)
        tk.Label(win,text="Prioridad").grid(row=7,column=0,sticky="w",padx=18,pady=7)
        cb_p=ttk.Combobox(win,width=48,state="readonly",values=PRIORIDADES);cb_p.grid(row=7,column=1,padx=18,pady=7)
        tk.Label(win,text="Técnico").grid(row=8,column=0,sticky="w",padx=18,pady=7)
        users=self.query("SELECT id_usuario,nombre FROM usuarios WHERE activo=1 ORDER BY nombre")
        cb_u=ttk.Combobox(win,width=48,state="readonly",values=["0 - Sin asignar"]+[f"{r['id_usuario']} - {r['nombre']}" for r in users]);cb_u.grid(row=8,column=1,padx=18,pady=7)
        tk.Label(win,text="Observaciones").grid(row=9,column=0,sticky="w",padx=18,pady=7)
        e_obs=ttk.Entry(win,width=51);e_obs.grid(row=9,column=1,padx=18,pady=7)

        def refresh_equipos(*_):
            if not cb_c.get():return
            cid=int(cb_c.get().split(" - ")[0])
            es=self.query("SELECT id_equipo,tipo||' '||COALESCE(marca,'')||' '||COALESCE(modelo,'') descp FROM equipos WHERE id_cliente=? ORDER BY id_equipo DESC",(cid,))
            cb_e["values"]=[f"{r['id_equipo']} - {r['descp']}" for r in es]
            if es:cb_e.current(0)
            else:cb_e.set("")
        cb_c.bind("<<ComboboxSelected>>",refresh_equipos)
        if row:
            client=self.query("SELECT nombre||' '||apellido nombre FROM clientes WHERE id_cliente=?",(row["id_cliente"],))[0]["nombre"]
            cb_c.set(f"{row['id_cliente']} - {client}");refresh_equipos()
            eq=self.query("SELECT tipo||' '||COALESCE(marca,'')||' '||COALESCE(modelo,'') descp FROM equipos WHERE id_equipo=?",(row["id_equipo"],))[0]["descp"]
            cb_e.set(f"{row['id_equipo']} - {eq}")
            for e,v in [(e_date,row["fecha_estimada"] or ""),(e_prob,row["problema_informado"]),(e_diag,row["diagnostico"] or ""),(e_sol,row["solucion"] or ""),(e_obs,row["observaciones"] or "")]:e.insert(0,v)
            cb_s.set(row["estado"]);cb_p.set(row["prioridad"])
            cb_u.set("0 - Sin asignar" if not row["id_tecnico"] else f"{row['id_tecnico']} - "+self.query("SELECT nombre FROM usuarios WHERE id_usuario=?",(row["id_tecnico"],))[0]["nombre"])
        else:
            cb_s.set("En diagnostico");cb_p.set("Normal");cb_u.set("0 - Sin asignar");e_date.insert(0,(datetime.now()+timedelta(days=3)).strftime("%Y-%m-%d %H:%M"))
        def save():
            if not cb_c.get() or not cb_e.get() or not e_prob.get().strip():messagebox.showwarning("Validación","Cliente, equipo y problema son obligatorios.",parent=win);return
            cid=int(cb_c.get().split(" - ")[0]);eid=int(cb_e.get().split(" - ")[0]);tech=int(cb_u.get().split(" - ")[0]) if cb_u.get() and not cb_u.get().startswith("0 -") else None
            vals=(cid,eid,tech,e_date.get().strip() or None,e_prob.get().strip(),e_diag.get().strip(),e_sol.get().strip(),cb_s.get() or "En diagnostico",cb_p.get() or "Normal",e_obs.get().strip())
            if row:
                old=row["estado"]
                self.execute("UPDATE ordenes_trabajo SET id_cliente=?,id_equipo=?,id_tecnico=?,fecha_estimada=?,problema_informado=?,diagnostico=?,solucion=?,estado=?,prioridad=?,observaciones=? WHERE id_orden=?",vals+(row["id_orden"],))
                if old!=vals[7]:self.add_history(row["id_orden"],old,vals[7],"Cambio desde edición")
            else:
                oid=self.execute("INSERT INTO ordenes_trabajo(id_cliente,id_equipo,id_tecnico,fecha_ingreso,fecha_estimada,problema_informado,diagnostico,solucion,estado,prioridad,observaciones) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(cid,eid,tech,self._date(),vals[3],vals[4],vals[5],vals[6],vals[7],vals[8],vals[9]));self.add_history(oid,None,vals[7],"Alta de orden")
            win.destroy();self.show_orders()
        ttk.Button(win,text="Guardar orden",command=save).grid(row=11,column=1,pady=22,sticky="e")

    def new_order(self):self.order_form()

    def edit_order(self):
        sel=self.order_tree.selection()
        if sel:self.order_form(self.query("SELECT * FROM ordenes_trabajo WHERE id_orden=?",(self.order_tree.item(sel)["values"][0],))[0])

    def add_history(self,oid,old,new,comment=""):
        self.execute("INSERT INTO historial_estados(id_orden,id_usuario,estado_anterior,estado_nuevo,comentario) VALUES (?,?,?,?,?)",(oid,self.current_user_id,old,new,comment))

    def view_order_history(self):
        sel=self._require_selection(self.order_tree, "Historial de la orden")
        if not sel:return
        oid=int(self.order_tree.item(sel)["values"][0])
        rows=self.query("""SELECT h.fecha,COALESCE(u.nombre,'-'),COALESCE(h.estado_anterior,'-'),h.estado_nuevo,COALESCE(h.comentario,'')
                          FROM historial_estados h LEFT JOIN usuarios u ON u.id_usuario=h.id_usuario
                          WHERE h.id_orden=? ORDER BY h.id_historial DESC""",(oid,))
        win=tk.Toplevel(self);win.title(f"Historial de orden #{oid:05d}");win.geometry("820x450");win.transient(self)
        tk.Label(win,text=f"HISTORIAL — ORDEN #{oid:05d}",font=("Segoe UI",15,"bold"),fg=TEXT).pack(anchor="w",padx=18,pady=15)
        tree=ttk.Treeview(win,columns=("Fecha","Usuario","Anterior","Nuevo","Comentario"),show="headings")
        for c,w in [("Fecha",150),("Usuario",180),("Anterior",150),("Nuevo",170),("Comentario",300)]:tree.heading(c,text=c);tree.column(c,width=w,stretch=False)
        for r in rows:tree.insert("","end",values=tuple(r))
        tree.pack(fill="both",expand=True,padx=18,pady=8)

    def change_order_state(self):
        sel=self._require_selection(self.order_tree, "Cambiar estado")
        if not sel:return
        oid=self.order_tree.item(sel)["values"][0];row=self.query("SELECT estado FROM ordenes_trabajo WHERE id_orden=?",(oid,))[0]
        win=tk.Toplevel(self);win.title("Cambiar estado");win.geometry("390x210")
        tk.Label(win,text="Nuevo estado").pack(pady=(25,7));cb=ttk.Combobox(win,state="readonly",values=ESTADOS,width=32);cb.set(row["estado"]);cb.pack()
        tk.Label(win,text="Comentario").pack(pady=(12,5));e=ttk.Entry(win,width=35);e.pack()
        def save():
            new=cb.get()
            if new==row["estado"]:win.destroy();return
            self.execute("UPDATE ordenes_trabajo SET estado=? WHERE id_orden=?",(new,oid));self.add_history(oid,row["estado"],new,e.get().strip())
            if new=="Entregado":self.execute("UPDATE ordenes_trabajo SET fecha_finalizacion=? WHERE id_orden=?",(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),oid))
            win.destroy();self.show_orders()
        ttk.Button(win,text="Guardar",command=save).pack(pady=18)

    def edit_diagnosis(self):
        sel=self._require_selection(self.order_tree, "Diagnóstico")
        if not sel:return
        oid=self.order_tree.item(sel)["values"][0];row=self.query("SELECT diagnostico,solucion FROM ordenes_trabajo WHERE id_orden=?",(oid,))[0]
        win=tk.Toplevel(self);win.title(f"Diagnóstico de orden #{oid:05d}");win.geometry("620x300")
        tk.Label(win,text="Diagnóstico").pack(anchor="w",padx=20,pady=(20,5));d=ttk.Entry(win,width=75);d.pack(padx=20);d.insert(0,row["diagnostico"] or "")
        tk.Label(win,text="Solución").pack(anchor="w",padx=20,pady=(15,5));s=ttk.Entry(win,width=75);s.pack(padx=20);s.insert(0,row["solucion"] or "")
        def save():self.execute("UPDATE ordenes_trabajo SET diagnostico=?,solucion=? WHERE id_orden=?",(d.get().strip(),s.get().strip(),oid));win.destroy()
        ttk.Button(win,text="Guardar",command=save).pack(pady=22)

    def delete_order(self):
        sel=self._require_selection(self.order_tree, "Eliminar orden")
        if not sel:return
        oid=int(self.order_tree.item(sel)["values"][0])
        if not messagebox.askyesno("Confirmar","¿Eliminar la orden y todos sus registros asociados?\n\nLos insumos utilizados serán devueltos al stock.", parent=self):
            return
        try:
            with get_connection() as c:
                # Restaurar primero los insumos consumidos por la orden.
                used = c.execute("SELECT id_insumo,cantidad FROM insumos_orden WHERE id_orden=?", (oid,)).fetchall()
                for r in used:
                    c.execute("UPDATE insumos SET stock=stock+? WHERE id_insumo=?", (r["cantidad"], r["id_insumo"]))
                # Eliminar dependencias respetando las FK del DER definitivo.
                for table in (
                    "movimientos_insumos", "insumos_orden", "servicios_orden",
                    "historial_estados", "detalle_presupuesto", "presupuestos",
                    "pagos", "entregas", "garantias"
                ):
                    c.execute(f"DELETE FROM {table} WHERE id_orden=?", (oid,))
                c.execute("DELETE FROM ordenes_trabajo WHERE id_orden=?", (oid,))
                c.commit()
            self.show_orders()
        except sqlite3.Error as exc:
            messagebox.showerror("Eliminar orden", f"No fue posible eliminar la orden.\n\nDetalle: {exc}", parent=self)

    def order_components(self):
        sel=self._require_selection(self.order_tree, "Servicios e insumos")
        if not sel:return
        oid=int(self.order_tree.item(sel)["values"][0])
        win=tk.Toplevel(self);win.title(f"Servicios e insumos | Orden #{oid:05d}");win.geometry("900x560")
        tk.Label(win,text=f"ORDEN #{oid:05d}",font=("Segoe UI",15,"bold"),fg=TEXT).pack(anchor="w",padx=20,pady=15)
        nb=ttk.Notebook(win);nb.pack(fill="both",expand=True,padx=15,pady=10)

        tab_s=tk.Frame(nb,bg=BG);nb.add(tab_s,text="Servicios")
        stree=ttk.Treeview(tab_s,columns=("ID","Servicio","Cantidad","Precio","Subtotal"),show="headings")
        for c,w in [("ID",60),("Servicio",300),("Cantidad",100),("Precio",130),("Subtotal",140)]:stree.heading(c,text=c);stree.column(c,width=w)
        stree.pack(fill="both",expand=True,padx=10,pady=10)
        def refresh_s():
            for x in stree.get_children():stree.delete(x)
            rows=self.query("SELECT so.id,s.nombre,so.cantidad,so.precio,so.subtotal FROM servicios_orden so JOIN servicios s ON s.id_servicio=so.id_servicio WHERE so.id_orden=? ORDER BY so.id",(oid,))
            for r in rows:stree.insert("","end",values=(r["id"],r["nombre"],r["cantidad"],self._money(r["precio"]),self._money(r["subtotal"])))
        def add_s():
            services=self.query("SELECT id_servicio,nombre,precio_base FROM servicios ORDER BY nombre")
            if not services:return
            w=tk.Toplevel(win);w.title("Agregar servicio");w.geometry("430x280")
            cb=ttk.Combobox(w,state="readonly",width=38,values=[f"{r['id_servicio']} - {r['nombre']}" for r in services]);cb.pack(pady=(30,10));cb.current(0)
            q=ttk.Entry(w,width=12);q.insert(0,"1");q.pack(pady=8)
            def save():
                try:n=max(1,int(q.get()))
                except:messagebox.showwarning("Validación","Cantidad inválida",parent=w);return
                sid=int(cb.get().split(" - ")[0])
                r=self.query("SELECT precio_base FROM servicios WHERE id_servicio=?",(sid,))[0]
                price=float(r["precio_base"])
                try:
                    self.execute("INSERT INTO servicios_orden(id_orden,id_servicio,precio,cantidad,subtotal) VALUES (?,?,?,?,?)",(oid,sid,price,n,price*n))
                except sqlite3.IntegrityError as exc:
                    messagebox.showwarning("Servicio", f"No se pudo agregar el servicio.\n\nDetalle: {exc}", parent=w)
                    return
                w.destroy();refresh_s()
            ttk.Button(w,text="Agregar",command=save).pack(pady=20)
        def del_s():
            sel2=stree.selection()
            if not sel2:
                messagebox.showwarning("Servicios", "Seleccione un servicio para eliminar.", parent=win)
                return
            if messagebox.askyesno("Confirmar", "¿Quitar el servicio de la orden?", parent=win):
                self.execute("DELETE FROM servicios_orden WHERE id=?",(stree.item(sel2[0])["values"][0],));refresh_s()
        bar=tk.Frame(tab_s,bg=BG);bar.pack(fill="x",padx=10);ttk.Button(bar,text="+ Agregar servicio",command=add_s).pack(side="left");ttk.Button(bar,text="Eliminar",command=del_s).pack(side="left",padx=8);refresh_s()

        tab_i=tk.Frame(nb,bg=BG);nb.add(tab_i,text="Insumos utilizados")
        itree=ttk.Treeview(tab_i,columns=("ID","Insumo","Cantidad","Precio","Subtotal"),show="headings")
        for c,w in [("ID",60),("Insumo",300),("Cantidad",100),("Precio",130),("Subtotal",140)]:itree.heading(c,text=c);itree.column(c,width=w)
        itree.pack(fill="both",expand=True,padx=10,pady=10)
        def refresh_i():
            for x in itree.get_children():itree.delete(x)
            rows=self.query("SELECT io.id,i.nombre,io.cantidad,io.precio_unitario,io.subtotal FROM insumos_orden io JOIN insumos i ON i.id_insumo=io.id_insumo WHERE io.id_orden=? ORDER BY io.id",(oid,))
            for r in rows:itree.insert("","end",values=(r["id"],r["nombre"],r["cantidad"],self._money(r["precio_unitario"]),self._money(r["subtotal"])))
        def add_i():
            ins=self.query("SELECT id_insumo,nombre,stock,precio_venta FROM insumos WHERE stock>0 ORDER BY nombre")
            if not ins:messagebox.showinfo("Insumos","No hay insumos con stock disponible.",parent=win);return
            w=tk.Toplevel(win);w.title("Agregar insumo a la orden");w.geometry("500x300")
            cb=ttk.Combobox(w,state="readonly",width=44,values=[f"{r['id_insumo']} - {r['nombre']} (stock {r['stock']})" for r in ins]);cb.pack(pady=(30,10));cb.current(0)
            q=ttk.Entry(w,width=12);q.insert(0,"1");q.pack(pady=8)
            def save():
                try:n=max(1,int(q.get()))
                except:messagebox.showwarning("Validación","Cantidad inválida",parent=w);return
                iid=int(cb.get().split(" - ")[0]);r=self.query("SELECT stock,precio_venta FROM insumos WHERE id_insumo=?",(iid,))[0]
                if r["stock"]<n:messagebox.showwarning("Stock","No hay stock suficiente.",parent=w);return
                try:
                    price=float(r["precio_venta"])
                    self.execute("INSERT INTO insumos_orden(id_orden,id_insumo,cantidad,precio_unitario,subtotal) VALUES (?,?,?,?,?)",(oid,iid,n,price,price*n))
                    self.execute("UPDATE insumos SET stock=stock-? WHERE id_insumo=?",(n,iid))
                    self.execute("INSERT INTO movimientos_insumos(id_insumo,id_orden,id_usuario,tipo,cantidad,motivo) VALUES (?,?,?,?,?,?)",(iid,oid,self.current_user_id,"SALIDA",n,"Uso en reparación"))
                except sqlite3.IntegrityError:messagebox.showwarning("Insumos","Ese insumo ya está cargado en la orden. Edite la cantidad desde el registro existente.",parent=w);return
                w.destroy();refresh_i()
            ttk.Button(w,text="Consumir insumo",command=save).pack(pady=20)
        def del_i():
            sel2=itree.selection()
            if not sel2:
                messagebox.showwarning("Insumos", "Seleccione un insumo para quitarlo de la orden.", parent=win)
                return
            mid=itree.item(sel2[0])["values"][0]
            row=self.query("SELECT id_insumo,cantidad FROM insumos_orden WHERE id=?",(mid,))[0]
            if messagebox.askyesno("Confirmar","¿Quitar el insumo y devolverlo al stock?",parent=win):
                self.execute("DELETE FROM insumos_orden WHERE id=?",(mid,));self.execute("UPDATE insumos SET stock=stock+? WHERE id_insumo=?",(row["cantidad"],row["id_insumo"]));self.execute("INSERT INTO movimientos_insumos(id_insumo,id_orden,id_usuario,tipo,cantidad,motivo) VALUES (?,?,?,?,?,?)",(row["id_insumo"],oid,self.current_user_id,"ENTRADA",row["cantidad"],"Reversión de uso en orden"));refresh_i()
        bar2=tk.Frame(tab_i,bg=BG);bar2.pack(fill="x",padx=10);ttk.Button(bar2,text="+ Consumir insumo",command=add_i).pack(side="left");ttk.Button(bar2,text="Quitar / devolver stock",command=del_i).pack(side="left",padx=8);refresh_i()
