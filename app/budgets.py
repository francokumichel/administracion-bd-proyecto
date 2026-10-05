"""Funciones del módulo budgets."""

from .common import *


class BudgetsMixin:

    def show_budgets(self):
        rows=self.query("""SELECT p.id_presupuesto,p.id_orden,c.nombre||' '||c.apellido,p.fecha,p.subtotal,p.descuento,p.total,p.estado,p.fecha_vencimiento
                          FROM presupuestos p JOIN ordenes_trabajo o ON o.id_orden=p.id_orden JOIN clientes c ON c.id_cliente=o.id_cliente ORDER BY p.id_presupuesto DESC""")
        self.budget_tree=self.table_page("Presupuestos",("ID","Orden","Cliente","Fecha","Subtotal","Descuento","Total","Estado","Vencimiento"),rows,self.new_budget,
                                         [("Editar",self.edit_budget),("Ver detalle",self.view_budget_details),("PDF",self.pdf_selected_budget),("Enviar",self.send_selected_budget),("WhatsApp",self.whatsapp_selected_budget),("Email",self.email_selected_budget),("Estado",self.change_budget_status)])

    def _load_budget(self,pid):
        p=self.query("""SELECT p.*,o.id_cliente,o.id_equipo,o.problema_informado,c.nombre||' '||c.apellido cliente,c.telefono,c.email,c.direccion,e.tipo,e.marca,e.modelo,e.numero_serie
                       FROM presupuestos p JOIN ordenes_trabajo o ON o.id_orden=p.id_orden JOIN clientes c ON c.id_cliente=o.id_cliente JOIN equipos e ON e.id_equipo=o.id_equipo WHERE p.id_presupuesto=?""",(pid,))
        if not p:return None
        d=self.query("SELECT * FROM detalle_presupuesto WHERE id_presupuesto=? ORDER BY id_detalle",(pid,));return p[0],d

    def new_budget(self):self.budget_editor()

    def edit_budget(self):
        sel=self._require_selection(self.budget_tree, "Editar presupuesto")
        if sel:self.budget_editor(int(self.budget_tree.item(sel)["values"][0]))

    def budget_editor(self,pid=None):
        """Editor de presupuestos.
        La barra de acciones queda siempre visible: GUARDAR PRESUPUESTO y
        GUARDAR + GENERAR PDF no dependen del alto de la tabla.
        """
        orders=self.query("SELECT o.id_orden,c.nombre||' '||c.apellido cliente,o.estado FROM ordenes_trabajo o JOIN clientes c ON c.id_cliente=o.id_cliente WHERE o.estado!='Cancelado' ORDER BY o.id_orden DESC")
        if not orders:
            messagebox.showinfo("Presupuestos","Primero debe existir una orden.")
            return

        old=self._load_budget(pid) if pid else None
        p=old[0] if old else None
        details=old[1] if old else []

        win=tk.Toplevel(self)
        win.title("Editar presupuesto" if pid else "Nuevo presupuesto")
        win.geometry("1100x650")
        win.minsize(980,580)
        win.transient(self)
        win.grab_set()
        win.configure(bg=BG)

        win.grid_rowconfigure(2,weight=1,minsize=250)
        win.grid_rowconfigure(3,weight=0,minsize=52)
        win.grid_rowconfigure(4,weight=0,minsize=68)
        win.grid_columnconfigure(0,weight=1)

        tk.Label(win,text="PRESUPUESTO DE REPARACIÓN",bg=SIDEBAR,fg=WHITE,
                 font=("Segoe UI",16,"bold"),anchor="w",padx=18).grid(
                     row=0,column=0,sticky="ew")

        top=tk.Frame(win,bg=BG)
        top.grid(row=1,column=0,sticky="ew",padx=18,pady=10)
        top.grid_columnconfigure(1,weight=1)
        top.grid_columnconfigure(3,weight=1)

        tk.Label(top,text="Orden",bg=BG,fg=TEXT).grid(row=0,column=0,padx=8,pady=6,sticky="w")
        cb=ttk.Combobox(top,state="readonly",width=58,
                        values=[f"{r['id_orden']} - {r['cliente']} - {r['estado']}" for r in orders])
        cb.grid(row=0,column=1,padx=8,pady=6,sticky="ew")

        tk.Label(top,text="Descuento",bg=BG,fg=TEXT).grid(row=0,column=2,padx=8,pady=6,sticky="w")
        ed=ttk.Entry(top,width=18)
        ed.insert(0,str(p["descuento"] if p else 0))
        ed.grid(row=0,column=3,padx=8,pady=6,sticky="w")

        tk.Label(top,text="Vencimiento (AAAA-MM-DD)",bg=BG,fg=TEXT).grid(row=1,column=0,padx=8,pady=6,sticky="w")
        ev=ttk.Entry(top,width=18)
        ev.insert(0,(p["fecha_vencimiento"] or "") if p else "")
        ev.grid(row=1,column=1,padx=8,pady=6,sticky="w")

        tk.Label(top,text="Estado",bg=BG,fg=TEXT).grid(row=1,column=2,padx=8,pady=6,sticky="w")
        es=ttk.Combobox(top,state="readonly",width=20,values=ESTADOS_PRESUPUESTO)
        es.set(p["estado"] if p else "Pendiente")
        es.grid(row=1,column=3,padx=8,pady=6,sticky="w")

        if p:
            for i,r in enumerate(orders):
                if r["id_orden"]==p["id_orden"]:
                    cb.current(i)
                    break
        else:
            cb.current(0)

        line=tk.Frame(win,bg=WHITE,bd=1,relief="solid")
        line.grid(row=2,column=0,sticky="nsew",padx=18,pady=(0,8))
        line.grid_columnconfigure(0,weight=1)

        editor=tk.Frame(line,bg=WHITE)
        editor.pack(fill="x",padx=8,pady=6)
        tk.Label(editor,text="Descripción",bg=WHITE,fg=TEXT).grid(row=0,column=0,padx=6,pady=4,sticky="w")
        desc=ttk.Entry(editor,width=42)
        desc.grid(row=1,column=0,padx=6,pady=4,sticky="ew")
        tk.Label(editor,text="Cantidad",bg=WHITE,fg=TEXT).grid(row=0,column=1,padx=6,pady=4,sticky="w")
        qty=ttk.Entry(editor,width=10)
        qty.insert(0,"1")
        qty.grid(row=1,column=1,padx=6,pady=4)
        tk.Label(editor,text="Precio unitario",bg=WHITE,fg=TEXT).grid(row=0,column=2,padx=6,pady=4,sticky="w")
        price=ttk.Entry(editor,width=15)
        price.insert(0,"0")
        price.grid(row=1,column=2,padx=6,pady=4)
        tk.Label(editor,text="Autocompletar servicio / insumo",bg=WHITE,fg=TEXT).grid(row=0,column=3,padx=6,pady=4,sticky="w")
        source=ttk.Combobox(editor,state="readonly",width=36,values=[])
        source.grid(row=1,column=3,padx=6,pady=4)

        def load_source():
            vals=[f"S:{r['id_servicio']} - {r['nombre']}" for r in self.query("SELECT id_servicio,nombre FROM servicios ORDER BY nombre")]
            vals += [f"I:{r['id_insumo']} - {r['nombre']}" for r in self.query("SELECT id_insumo,nombre FROM insumos ORDER BY nombre")]
            source["values"]=vals

        def use_source(*_):
            if not source.get():
                return
            prefix,rest=source.get().split(":",1)
            ident=int(rest.split(" - ",1)[0])
            if prefix=="S":
                r=self.query("SELECT nombre,precio_base FROM servicios WHERE id_servicio=?",(ident,))[0]
                value=r["precio_base"]
            else:
                r=self.query("SELECT nombre,precio_venta FROM insumos WHERE id_insumo=?",(ident,))[0]
                value=r["precio_venta"]
            desc.delete(0,"end")
            desc.insert(0,r["nombre"])
            price.delete(0,"end")
            price.insert(0,str(value))

        source.bind("<<ComboboxSelected>>",use_source)
        load_source()

        actions_line=tk.Frame(editor,bg=WHITE)
        actions_line.grid(row=1,column=4,padx=8,pady=4,sticky="e")

        lines=[]
        tree=ttk.Treeview(line,columns=("Descripción","Cantidad","Precio","Subtotal"),show="headings",height=7)
        for c,w in [("Descripción",480),("Cantidad",100),("Precio",150),("Subtotal",150)]:
            tree.heading(c,text=c)
            tree.column(c,width=w,stretch=(c=="Descripción"))
        tree.pack(fill="both",expand=True,padx=8,pady=(2,8))

        def recalc():
            subtotal=sum(x[2] for x in lines)
            try:
                discount=max(0,float(ed.get() or 0))
            except (TypeError,ValueError):
                discount=0
            return subtotal,max(0,subtotal-discount)

        def add_line():
            try:
                q=max(1,int(qty.get() or 1))
                pr=max(0,float(price.get() or 0))
            except (TypeError,ValueError):
                messagebox.showwarning("Validación","Cantidad y precio inválidos.",parent=win)
                return
            d=desc.get().strip()
            if not d:
                messagebox.showwarning("Validación","Ingrese una descripción.",parent=win)
                return
            sub=q*pr
            lines.append((d,q,sub,pr))
            tree.insert("","end",values=(d,q,self._money(pr),self._money(sub)))
            desc.delete(0,"end")
            qty.delete(0,"end"); qty.insert(0,"1")
            price.delete(0,"end"); price.insert(0,"0")
            source.set("")
            update_total()

        def remove_line():
            sel=tree.selection()
            if not sel:
                messagebox.showwarning("Presupuesto","Seleccione un concepto para quitar.",parent=win)
                return
            for item in reversed(tree.selection()):
                lines.pop(tree.index(item))
                tree.delete(item)
            update_total()

        ttk.Button(actions_line,text="+ Agregar",command=add_line).pack(side="left",padx=3)
        ttk.Button(actions_line,text="Quitar",command=remove_line).pack(side="left",padx=3)

        for d in details:
            item=(d["descripcion"],d["cantidad"],d["subtotal"],d["precio_unitario"])
            lines.append(item)
            tree.insert("","end",values=(d["descripcion"],d["cantidad"],self._money(d["precio_unitario"]),self._money(d["subtotal"])))

        totalvar=tk.StringVar(value="TOTAL: $ 0,00")
        tk.Label(win,textvariable=totalvar,bg=BG,fg=GREEN,font=("Segoe UI",15,"bold"),anchor="e").grid(
            row=3,column=0,sticky="ew",padx=18,pady=6)

        def update_total(*_):
            try:
                sub,tot=recalc()
                totalvar.set(f"Subtotal: {self._money(sub)}    Descuento: {self._money(float(ed.get() or 0))}    TOTAL: {self._money(tot)}")
            except Exception:
                pass
        ed.bind("<KeyRelease>",update_total)
        update_total()

        def save(generate_pdf=False):
            if not cb.get() or not lines:
                messagebox.showwarning("Validación","Seleccione una orden y agregue al menos un concepto.",parent=win)
                return None
            try:
                discount=max(0,float(ed.get() or 0))
            except (TypeError,ValueError):
                messagebox.showwarning("Validación","El descuento debe ser numérico.",parent=win)
                return None
            subtotal=sum(x[2] for x in lines)
            if discount>subtotal:
                messagebox.showwarning("Validación","El descuento no puede superar el subtotal.",parent=win)
                return None
            oid=int(cb.get().split(" - ",1)[0])
            total=max(0,subtotal-discount)
            estado=es.get() or "Pendiente"
            vencimiento=ev.get().strip() or None
            try:
                with get_connection() as c:
                    if pid:
                        bid=pid
                        c.execute("UPDATE presupuestos SET id_orden=?,fecha=?,subtotal=?,descuento=?,total=?,estado=?,fecha_vencimiento=? WHERE id_presupuesto=?",
                                  (oid,self._date(),subtotal,discount,total,estado,vencimiento,pid))
                        c.execute("DELETE FROM detalle_presupuesto WHERE id_presupuesto=?",(bid,))
                    else:
                        cur=c.execute("INSERT INTO presupuestos(id_orden,fecha,subtotal,descuento,total,estado,fecha_vencimiento) VALUES (?,?,?,?,?,?,?)",
                                      (oid,self._date(),subtotal,discount,total,estado,vencimiento))
                        bid=cur.lastrowid
                    for d,q,sub,pr in lines:
                        c.execute("INSERT INTO detalle_presupuesto(id_presupuesto,descripcion,cantidad,precio_unitario,subtotal) VALUES (?,?,?,?,?)",
                                  (bid,d,q,pr,sub))
                    c.execute("UPDATE ordenes_trabajo SET costo_final=? WHERE id_orden=?",(total,oid))
                    c.commit()
            except sqlite3.Error as exc:
                messagebox.showerror("Guardar presupuesto",f"No se pudo guardar el presupuesto.\n\nDetalle: {exc}",parent=win)
                return None

            pdf_path=None
            if generate_pdf:
                pdf_path=self.generate_budget_pdf(bid,open_after=False)
            win.destroy()
            self.show_budgets()
            if generate_pdf and pdf_path:
                messagebox.showinfo("Presupuesto guardado",f"Presupuesto #{bid:05d} guardado correctamente.\n\nPDF generado en:\n{pdf_path}",parent=self)
            else:
                messagebox.showinfo("Presupuesto guardado",f"Presupuesto #{bid:05d} guardado correctamente como '{estado}'.\n\nPuede enviarlo más tarde desde la lista de Presupuestos.",parent=self)
            return bid

        # BARRA FIJA: esta fila nunca comparte espacio con el Treeview.
        actions=tk.Frame(win,bg=SIDEBAR,bd=1,relief="solid")
        actions.grid(row=4,column=0,sticky="ew",padx=18,pady=(2,10),ipady=4)
        tk.Label(actions,text="Acciones:",bg=SIDEBAR,fg=WHITE,font=("Segoe UI",10,"bold")).pack(side="left",padx=14,pady=10)
        ttk.Button(actions,text="Cancelar",command=win.destroy,width=14).pack(side="right",padx=6,pady=8)
        ttk.Button(actions,text="GUARDAR + GENERAR PDF",command=lambda:save(True),width=24).pack(side="right",padx=6,pady=8)
        ttk.Button(actions,text="GUARDAR PRESUPUESTO",command=lambda:save(False),style="Primary.TButton",width=24).pack(side="right",padx=6,pady=8)

        # Acceso rápido con teclado.
        win.bind("<Control-s>",lambda e:save(False))
        win.bind("<Control-p>",lambda e:save(True))
        win.focus_force()

    def change_budget_status(self):
        sel=self._require_selection(self.budget_tree, "Estado del presupuesto")
        if not sel:return
        pid=int(self.budget_tree.item(sel)["values"][0]);row=self.query("SELECT id_orden,estado FROM presupuestos WHERE id_presupuesto=?",(pid,))[0]
        win=tk.Toplevel(self);win.title("Estado del presupuesto");win.geometry("380x190");cb=ttk.Combobox(win,state="readonly",values=ESTADOS_PRESUPUESTO,width=28);cb.set(row["estado"]);cb.pack(pady=25)
        def save():
            new=cb.get();self.execute("UPDATE presupuestos SET estado=? WHERE id_presupuesto=?",(new,pid));target={"Enviado":"Esperando presupuesto","Aprobado":"Aprobado","Rechazado":"Esperando presupuesto"}.get(new)
            if target and target!=row["estado"]:self.execute("UPDATE ordenes_trabajo SET estado=? WHERE id_orden=?",(target,row["id_orden"]));self.add_history(row["id_orden"],None,target,f"Presupuesto {new}")
            win.destroy();self.show_budgets()
        ttk.Button(win,text="Guardar",command=save).pack()

    def view_budget_details(self):
        sel=self._require_selection(self.budget_tree, "Detalle del presupuesto")
        if not sel:return
        pid=int(self.budget_tree.item(sel)["values"][0]);data=self._load_budget(pid)
        if not data:return
        p,details=data;win=tk.Toplevel(self);win.title(f"Detalle presupuesto #{pid:05d}");win.geometry("900x520")
        tk.Label(win,text=f"PRESUPUESTO #{pid:05d} | Orden #{p['id_orden']:05d} | {p['cliente']}",font=("Segoe UI",14,"bold")).pack(anchor="w",padx=18,pady=15)
        tree=ttk.Treeview(win,columns=("Descripción","Cantidad","Precio","Subtotal"),show="headings")
        for c,w in [("Descripción",500),("Cantidad",100),("Precio",140),("Subtotal",140)]:tree.heading(c,text=c);tree.column(c,width=w)
        for d in details:tree.insert("","end",values=(d["descripcion"],d["cantidad"],self._money(d["precio_unitario"]),self._money(d["subtotal"])))
        tree.pack(fill="both",expand=True,padx=18,pady=8);tk.Label(win,text=f"Subtotal: {self._money(p['subtotal'])}   Descuento: {self._money(p['descuento'])}   TOTAL: {self._money(p['total'])}",font=("Segoe UI",12,"bold"),fg=GREEN).pack(anchor="e",padx=18,pady=15)

    def _selected_budget(self):
        sel=self.budget_tree.selection()
        if not sel:
            messagebox.showwarning("Presupuestos", "Seleccione un presupuesto guardado.", parent=self)
            return None
        return int(self.budget_tree.item(sel)["values"][0])

    def generate_budget_pdf(self,pid,open_after=True):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:messagebox.showerror("PDF","Instale reportlab con: pip install reportlab");return None
        data=self._load_budget(pid)
        if not data:return None
        p,details=data;out=Path(__file__).resolve().parent/"presupuestos_generados";out.mkdir(exist_ok=True);pdf=out/f"Presupuesto_{pid:05d}_Orden_{p['id_orden']:05d}.pdf"
        doc=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36);styles=getSampleStyleSheet();normal=styles["BodyText"]
        story=[Paragraph("SAINT REPAIRS",styles["Title"]),Paragraph("Taller de Reparación de Electrónica",normal),Spacer(1,12),Paragraph(f"<b>Presupuesto N° {pid:05d}</b> | Orden #{p['id_orden']:05d} | Fecha: {p['fecha']}",normal),Spacer(1,10),Paragraph(f"<b>Cliente:</b> {p['cliente']}<br/>Teléfono: {p['telefono'] or '-'}<br/>Email: {p['email'] or '-'}",normal),Spacer(1,10)]
        table=[["Descripción","Cantidad","Precio unitario","Subtotal"]]+[[d["descripcion"],str(d["cantidad"]),self._money(d["precio_unitario"]),self._money(d["subtotal"])] for d in details]
        t=Table(table,colWidths=[280,70,100,100],repeatRows=1);t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#061A33")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.4,colors.grey)]));story += [t,Spacer(1,12),Paragraph(f"Subtotal: {self._money(p['subtotal'])}<br/>Descuento: {self._money(p['descuento'])}<br/><b>TOTAL: {self._money(p['total'])}</b>",normal)]
        doc.build(story)
        if open_after:
            try:os.startfile(str(pdf))
            except Exception:webbrowser.open(pdf.as_uri())
        return str(pdf)

    def pdf_selected_budget(self):
        pid=self._selected_budget()
        if pid:self.generate_budget_pdf(pid)

    def send_selected_budget(self):
        pid=self._selected_budget()
        if not pid:
            return
        data=self._load_budget(pid)
        if not data:return
        p,_=data
        win=tk.Toplevel(self);win.title(f"Enviar presupuesto #{pid:05d}");win.geometry("500x330");win.transient(self)
        tk.Label(win,text=f"Presupuesto #{pid:05d}",font=("Segoe UI",16,"bold"),fg=TEXT).pack(pady=(24,6))
        tk.Label(win,text=f"Cliente: {p['cliente']}\nTotal: {self._money(p['total'])}",fg=MUTED,justify="center").pack(pady=6)
        ttk.Button(win,text="Generar / abrir PDF",command=lambda:[self.generate_budget_pdf(pid),win.destroy()]).pack(fill="x",padx=70,pady=7)
        ttk.Button(win,text="Preparar WhatsApp",command=lambda:[self.whatsapp_selected_budget(pid),win.destroy()]).pack(fill="x",padx=70,pady=7)
        ttk.Button(win,text="Preparar Email",command=lambda:[self.email_selected_budget(pid),win.destroy()]).pack(fill="x",padx=70,pady=7)
        ttk.Button(win,text="Cancelar",command=win.destroy).pack(pady=12)

    def whatsapp_selected_budget(self, pid=None):
        pid=pid or self._selected_budget()
        if not pid:
            messagebox.showwarning("WhatsApp", "Seleccione un presupuesto guardado.", parent=self)
            return
        data=self._load_budget(pid)
        if not data:return
        p,_=data;phone="".join(ch for ch in (p["telefono"] or "") if ch.isdigit())
        # WhatsApp necesita código de país. Si se cargó un celular argentino de 10 dígitos,
        # se agrega automáticamente +54 (sin el 0 ni el 15).
        if len(phone)==10:
            phone="54"+phone
        elif phone.startswith("0"):
            phone=phone[1:]
        if not phone:messagebox.showwarning("WhatsApp","El cliente no tiene teléfono cargado.",parent=self);return
        text=f"Hola {p['cliente']}, te enviamos el presupuesto #{pid:05d} de SAINT REPAIRS. Total: {self._money(p['total'])}."
        webbrowser.open("https://wa.me/"+phone+"?text="+urllib.parse.quote(text))

    def email_selected_budget(self, pid=None):
        pid=pid or self._selected_budget()
        if not pid:
            messagebox.showwarning("Email", "Seleccione un presupuesto guardado.", parent=self)
            return
        data=self._load_budget(pid)
        if not data:return
        p,_=data
        if not p["email"]:
            messagebox.showwarning("Email","El cliente no tiene email cargado.",parent=self)
            return
        subject=f"Presupuesto SAINT REPAIRS #{pid:05d}";body=f"Hola {p['cliente']},%0D%0A%0D%0ATotal del presupuesto: {self._money(p['total'])}.%0D%0A%0D%0ASaludos."
        webbrowser.open(f"mailto:{urllib.parse.quote(p['email'])}?subject={urllib.parse.quote(subject)}&body={body}")
