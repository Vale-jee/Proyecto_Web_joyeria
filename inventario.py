import sqlite3

class Pieza:
    """Clase Producto: Define los atributos y métodos de obtención"""

    def __init__(self, id, modelo, coleccion, material, peso, cantidad, precio):
        self.id = id
        self.modelo = modelo
        self.coleccion = coleccion
        self.material = material
        self.peso = peso
        self.cantidad = cantidad
        self.precio = precio

    def obtener_datos(self):
        return f"{self.modelo} - {self.material} ({self.peso})"


class Catalogo:
    """Clase Inventario: Gestiona la colección y la base de datos SQLite"""

    def __init__(self):
        self.db_name = 'joyeria.db'
        self.crear_tabla()
        self.productos_dict = {}
        self.sincronizar_diccionario()

    def crear_tabla(self):
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modelo TEXT,
                coleccion TEXT,
                material TEXT,
                peso TEXT,
                cantidad INTEGER,
                precio REAL
            )
        ''')
        conexion.commit()
        conexion.close()

    def añadir_pieza(self, modelo, coleccion, material, peso, cantidad, precio):
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO productos (modelo, coleccion, material, peso, cantidad, precio) VALUES (?, ?, ?, ?, ?, ?)",
            (modelo, coleccion, material, peso, cantidad, precio)
        )
        conexion.commit()
        conexion.close()
        self.sincronizar_diccionario()

    def obtener_todo(self):
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        filas = cursor.fetchall()
        conexion.close()

        return [Pieza(f[0], f[1], f[2], f[3], f[4], f[5], f[6]) for f in filas]

    def sincronizar_diccionario(self):
        lista_productos = self.obtener_todo()
        self.productos_dict = {p.id: p for p in lista_productos}

    def buscar_por_nombre(self, nombre):
        return [
            p for p in self.productos_dict.values()
            if nombre.lower() in p.modelo.lower()
        ]

    def eliminar_producto(self, id_producto):
        if id_producto in self.productos_dict:

            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            conexion.commit()
            conexion.close()

            del self.productos_dict[id_producto]
            print("Producto eliminado correctamente.")
        else:
            print("Producto no encontrado.")

    def actualizar_producto(self, id_prod, modelo, coleccion, material, peso, cantidad, precio):

        if id_prod in self.productos_dict:

            # Actualiza en memoria (diccionario)
            self.productos_dict[id_prod].modelo = modelo
            self.productos_dict[id_prod].coleccion = coleccion
            self.productos_dict[id_prod].material = material
            self.productos_dict[id_prod].peso = peso
            self.productos_dict[id_prod].cantidad = cantidad
            self.productos_dict[id_prod].precio = precio

            # Actualiza en la base de datos
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE productos
                SET modelo = ?, coleccion = ?, material = ?, peso = ?, cantidad = ?, precio = ?
                WHERE id = ?
            """, (modelo, coleccion, material, peso, cantidad, precio, id_prod))

            conexion.commit()
            conexion.close()

            print("Producto actualizado correctamente.")
        else:
            print("Producto no encontrado.")