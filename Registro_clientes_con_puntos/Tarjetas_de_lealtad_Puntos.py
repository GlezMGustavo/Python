import tkinter as tk
from tkinter import ttk
import sqlite3
import random
from ttkthemes import ThemedStyle

class ClienteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Clientes")

        # Aplicar el estilo vintage
        style = ThemedStyle(root)
        style.set_theme("radiance")

        # Conectar a la base de datos (o crearla si no existe)
        self.conn = sqlite3.connect("clientes.db")
        self.c = self.conn.cursor()

        # Crear la tabla si no existe
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                telefono TEXT,
                puntos INTEGER
            )
        ''')
        self.conn.commit()

        # Crear widgets
        ttk.Label(root, text="Nombre:").grid(row=0, column=0, pady=5, sticky="E")
        ttk.Label(root, text="Teléfono:").grid(row=1, column=0, padx=1, pady=5, sticky="E")
        ttk.Label(root, text="Puntos:").grid(row=2, column=0, padx=1, pady=5, sticky="E")

        self.entry_nombre = ttk.Entry(root)
        self.entry_telefono = ttk.Entry(root)
        self.entry_puntos = ttk.Entry(root)

        self.entry_nombre.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="EW")
        self.entry_telefono.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="EW")
        self.entry_puntos.grid(row=2, column=1, padx=(0, 10), pady=5, sticky="EW")

        ttk.Button(root, text="Agregar Cliente", command=self.agregar_cliente).grid(row=3, column=0, columnspan=1, padx=(10, 0), pady=(10, 5), sticky="EW")
        ttk.Button(root, text="Eliminar Cliente", command=self.eliminar_cliente).grid(row=3, column=1, columnspan=1, padx=(0, 10), pady=10, sticky="EW")
        ttk.Button(root, text="Actualizar Cliente", command=self.actualizar_cliente).grid(row=4, column=0, padx=(10, 0), pady=(0, 10), sticky="EW")


        # Crear widgets para añadir y eliminar puntos
        ttk.Label(root, text="Operaciones:").grid(row=0, column=2, columnspan=2, pady=10)
        ttk.Label(root, text="Cantidad de Puntos:").grid(row=1, column=2, pady=5)
        self.entry_cantidad_puntos = ttk.Entry(root)
        self.entry_cantidad_puntos.grid(row=1, column=3, padx=(0, 10), pady=5, sticky="EW")

        ttk.Button(root, text="Añadir Puntos", command=self.anadir_puntos).grid(row=2, column=2, pady=5, sticky="EW")
        ttk.Button(root, text="Eliminar Puntos", command=self.eliminar_puntos).grid(row=2, column=3, padx=(0, 10), pady=5, sticky="EW")

        # Crear cuadros de búsqueda
        ttk.Label(root, text="Buscar:").grid(row=5, column=0, padx=(10, 0), pady=5, sticky="EW")
        # ttk.Label(root, text="ID:").grid(row=5, column=0, pady=5)
        # ttk.Label(root, text="Nombre:").grid(row=5, column=1, pady=5)
        # ttk.Label(root, text="Teléfono:").grid(row=5, column=2, pady=5)

        self.entry_buscar_id = ttk.Entry(root)
        self.entry_buscar_nombre = ttk.Entry(root)
        self.entry_buscar_telefono = ttk.Entry(root)

        self.entry_buscar_id.grid(row=6, column=0, padx=(10, 0), pady=2, sticky="EW")
        self.entry_buscar_nombre.grid(row=6, column=1, padx=2, pady=2, sticky="EW")
        self.entry_buscar_telefono.grid(row=6, column=2, pady=2, sticky="EW")

        # Listar clientes
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Teléfono", "Puntos"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Puntos", text="Puntos")
        self.tree.bind("<ButtonRelease-1>", self.on_cliente_seleccionado)
        self.listar_clientes()
        self.tree.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky="NSEW")

        # Asignar eventos de teclado para activar los filtros
        self.entry_buscar_id.bind("<KeyRelease>", lambda event: self.filtrar_registros(event, column="ID"))
        self.entry_buscar_nombre.bind("<KeyRelease>", lambda event: self.filtrar_registros(event, column="Nombre"))
        self.entry_buscar_telefono.bind("<KeyRelease>", lambda event: self.filtrar_registros(event, column="Teléfono"))

        # Configurar el diseño de la ventana
        self.configurar_diseno()

    def configurar_diseno(self):
        for i in range(11):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)
    def agregar_cliente(self):
        nombre = self.entry_nombre.get()
        telefono = self.entry_telefono.get()
        puntos = self.entry_puntos.get()

        if nombre and telefono and puntos:
            id_cliente = self.generar_id_unico()
            self.c.execute('''
                INSERT INTO clientes (id, nombre, telefono, puntos) VALUES (?, ?, ?, ?)
            ''', (id_cliente, nombre, telefono, puntos))
            self.conn.commit()
            self.listar_clientes()
            self.limpiar_campos()
        else:
            print("Por favor, complete todos los campos.")

    def generar_id_unico(self):
        while True:
            id_cliente = random.randint(1000, 9999)

            # Verificar si el ID ya existe en la base de datos
            self.c.execute("SELECT * FROM clientes WHERE id=?", (id_cliente,))
            existe = self.c.fetchone()

            if not existe:
                return id_cliente

    def listar_clientes(self):
        # Limpiar la lista actual
        for record in self.tree.get_children():
            self.tree.delete(record)

        # Obtener datos de la base de datos
        self.c.execute("SELECT * FROM clientes")
        clientes = self.c.fetchall()

        # Mostrar datos en la lista
        for cliente in clientes:
            self.tree.insert("", "end", values=cliente)

    def eliminar_cliente(self):
        # Obtener el ID seleccionado
        seleccion = self.tree.selection()
        if seleccion:
            id_cliente = self.tree.item(seleccion, "values")[0]

            # Eliminar el cliente de la base de datos
            self.c.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
            self.conn.commit()

            # Actualizar la lista
            self.listar_clientes()
        else:
            print("Por favor, seleccione un cliente para eliminar.")
    #  comentario
    def anadir_puntos(self):
        seleccion = self.tree.selection()
        cantidad_puntos = self.entry_cantidad_puntos.get()

        if seleccion and cantidad_puntos.isdigit():
            id_cliente = self.tree.item(seleccion, "values")[0]
            self.c.execute("UPDATE clientes SET puntos = puntos + ? WHERE id=?", (int(cantidad_puntos), id_cliente))
            self.conn.commit()
            self.listar_clientes()
            self.entry_cantidad_puntos.delete(0, "end")
        else:
            print("Por favor, seleccione un cliente y proporcione una cantidad válida de puntos.")

    def eliminar_puntos(self):
        seleccion = self.tree.selection()
        cantidad_puntos = self.entry_cantidad_puntos.get()

        if seleccion and cantidad_puntos.isdigit():
            id_cliente = self.tree.item(seleccion, "values")[0]
            self.c.execute("UPDATE clientes SET puntos = CASE WHEN puntos > ? THEN puntos - ? ELSE 0 END WHERE id=?",
                           (int(cantidad_puntos), int(cantidad_puntos), id_cliente))
            self.conn.commit()
            self.listar_clientes()
            self.entry_cantidad_puntos.delete(0, "end")
        else:
            print("Por favor, seleccione un cliente y proporcione una cantidad válida de puntos para eliminar.")

    def filtrar_registros(self, event, column):
        valor = event.widget.get()

        if column == "ID":
            columna_bd = "id"
        elif column == "Nombre":
            columna_bd = "nombre"
        elif column == "Teléfono":
            columna_bd = "telefono"
        else:
            return

        self.tree.delete(*self.tree.get_children())

        if valor:
            self.c.execute(f"SELECT * FROM clientes WHERE {columna_bd} LIKE ?", ('%' + valor + '%',))
        else:
            self.c.execute("SELECT * FROM clientes")

        clientes = self.c.fetchall()

        for cliente in clientes:
            self.tree.insert("", "end", values=cliente)

    def actualizar_cliente(self):
        seleccion = self.tree.selection()
        if seleccion:
            id_cliente = self.tree.item(seleccion, "values")[0]
            nombre = self.entry_nombre.get()
            telefono = self.entry_telefono.get()
            puntos = self.entry_puntos.get()

            if nombre and telefono and puntos:
                self.c.execute('''
                    UPDATE clientes SET nombre=?, telefono=?, puntos=? WHERE id=?
                ''', (nombre, telefono, puntos, id_cliente))
                self.conn.commit()
                self.listar_clientes()
                self.limpiar_campos()
            else:
                print("Por favor, complete todos los campos.")
        else:
            print("Por favor, seleccione un cliente para actualizar.")

    def on_cliente_seleccionado(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            cliente = self.tree.item(seleccion, "values")
            self.entry_nombre.delete(0, "end")
            self.entry_telefono.delete(0, "end")
            self.entry_puntos.delete(0, "end")
            self.entry_nombre.insert(0, cliente[1])
            self.entry_telefono.insert(0, cliente[2])
            self.entry_puntos.insert(0, cliente[3])

    def limpiar_campos(self):
        self.entry_nombre.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_puntos.delete(0, "end")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteApp(root)
    root.mainloop()
