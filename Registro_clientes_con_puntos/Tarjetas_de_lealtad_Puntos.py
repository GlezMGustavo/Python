import tkinter as tk
from tkinter import ttk
import sqlite3
import random

class ClienteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Clientes")

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
        self.label_nombre = ttk.Label(root, text="Nombre:")
        self.label_telefono = ttk.Label(root, text="Teléfono:")
        self.label_puntos = ttk.Label(root, text="Puntos:")

        self.entry_nombre = ttk.Entry(root)
        self.entry_telefono = ttk.Entry(root)
        self.entry_puntos = ttk.Entry(root)

        self.btn_agregar = ttk.Button(root, text="Agregar Cliente", command=self.agregar_cliente)
        self.btn_eliminar = ttk.Button(root, text="Eliminar Cliente", command=self.eliminar_cliente)

        # Listar clientes
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Teléfono", "Puntos"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Puntos", text="Puntos")
        self.listar_clientes()

        # Crear widgets para añadir y eliminar puntos
        self.label_operaciones = ttk.Label(root, text="Operaciones:")
        self.btn_anadir_puntos = ttk.Button(root, text="Añadir Puntos", command=self.anadir_puntos)
        self.btn_eliminar_puntos = ttk.Button(root, text="Eliminar Puntos", command=self.eliminar_puntos)

        # Entrada para la cantidad de puntos
        self.label_cantidad_puntos = ttk.Label(root, text="Cantidad de Puntos:")
        self.entry_cantidad_puntos = ttk.Entry(root)

        # Posicionar widgets en la interfaz
        self.label_nombre.grid(row=0, column=0, padx=5, pady=5, sticky="E")
        self.label_telefono.grid(row=1, column=0, padx=5, pady=5, sticky="E")
        self.label_puntos.grid(row=2, column=0, padx=5, pady=5, sticky="E")

        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
        self.entry_telefono.grid(row=1, column=1, padx=5, pady=5)
        self.entry_puntos.grid(row=2, column=1, padx=5, pady=5)

        self.btn_agregar.grid(row=3, column=0, columnspan=2, pady=10)
        self.btn_eliminar.grid(row=4, column=0, columnspan=2, pady=10)

        self.tree.grid(row=5, column=0, columnspan=2, pady=10)

        self.label_operaciones.grid(row=6, column=0, columnspan=2, pady=10)
        self.btn_anadir_puntos.grid(row=7, column=0, pady=5)
        self.btn_eliminar_puntos.grid(row=7, column=1, pady=5)

        self.label_cantidad_puntos.grid(row=8, column=0, pady=5)
        self.entry_cantidad_puntos.grid(row=8, column=1, pady=5)

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

    def limpiar_campos(self):
        self.entry_nombre.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.entry_puntos.delete(0, "end")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteApp(root)
    root.mainloop()
