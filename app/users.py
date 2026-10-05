"""Funciones del módulo users."""

from .common import *


class UsersMixin:

    def show_users(self):
        rows=self.query("SELECT id_usuario,nombre,usuario,rol,activo FROM usuarios ORDER BY id_usuario")
        self.user_tree=self.table_page("Usuarios",("ID","Nombre","Usuario","Rol","Activo"),rows,self.new_user,[("Editar",self.edit_user),("Activar/Desactivar",self.toggle_user)])

    def user_form(self,row=None):
        win=tk.Toplevel(self);win.title("Usuario");win.geometry("500x410");fields=["Nombre","Usuario","Contraseña"];es={}
        for i,l in enumerate(fields):tk.Label(win,text=l).grid(row=i,column=0,sticky="w",padx=20,pady=10);e=ttk.Entry(win,width=34,show="•" if l=="Contraseña" else "");e.grid(row=i,column=1,padx=20,pady=10);es[l]=e
        tk.Label(win,text="Rol").grid(row=3,column=0,sticky="w",padx=20,pady=10);cb=ttk.Combobox(win,state="readonly",width=31,values=ROLES);cb.grid(row=3,column=1,padx=20,pady=10);active=tk.IntVar(value=int(row["activo"]) if row else 1);tk.Checkbutton(win,text="Usuario activo",variable=active,bg=BG).grid(row=4,column=1,sticky="w",padx=20)
        if row:
            es["Nombre"].insert(0,row["nombre"]);es["Usuario"].insert(0,row["usuario"]);cb.set(row["rol"])
        else:cb.set("Tecnico")
        def save():
            if not es["Nombre"].get().strip() or not es["Usuario"].get().strip() or not cb.get():messagebox.showwarning("Validación","Nombre, usuario y rol son obligatorios.",parent=win);return
            try:
                if row:
                    if es["Contraseña"].get():self.execute("UPDATE usuarios SET nombre=?,usuario=?,contrasena_hash=?,rol=?,activo=? WHERE id_usuario=?",(es["Nombre"].get().strip(),es["Usuario"].get().strip(),es["Contraseña"].get(),cb.get(),active.get(),row["id_usuario"]))
                    else:self.execute("UPDATE usuarios SET nombre=?,usuario=?,rol=?,activo=? WHERE id_usuario=?",(es["Nombre"].get().strip(),es["Usuario"].get().strip(),cb.get(),active.get(),row["id_usuario"]))
                else:
                    if not es["Contraseña"].get():messagebox.showwarning("Validación","Ingrese una contraseña.",parent=win);return
                    self.execute("INSERT INTO usuarios(nombre,usuario,contrasena_hash,rol,activo) VALUES (?,?,?,?,?)",(es["Nombre"].get().strip(),es["Usuario"].get().strip(),es["Contraseña"].get(),cb.get(),active.get()))
                win.destroy();self.show_users()
            except sqlite3.IntegrityError:messagebox.showerror("Error","El nombre de usuario ya existe.",parent=win)
        ttk.Button(win,text="Guardar",command=save).grid(row=5,column=1,pady=20,sticky="e")

    def new_user(self):self.user_form()

    def edit_user(self):
        sel=self.user_tree.selection()
        if sel:self.user_form(self.query("SELECT * FROM usuarios WHERE id_usuario=?",(self.user_tree.item(sel[0])["values"][0],))[0])

    def toggle_user(self):
        sel=self.user_tree.selection()
        if not sel:return
        uid=int(self.user_tree.item(sel[0])["values"][0]);row=self.query("SELECT activo FROM usuarios WHERE id_usuario=?",(uid,))[0]
        if uid==self.current_user_id and row["activo"]:messagebox.showwarning("Usuarios","No puede desactivar el usuario con el que inició sesión.");return
        self.execute("UPDATE usuarios SET activo=? WHERE id_usuario=?",(0 if row["activo"] else 1,uid));self.show_users()
