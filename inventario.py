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
        """Método para obtener la información formateada"""
        return f"{self.modelo} - {self.material} ({self.peso})"

class Catalogo:
    """Clase Inventario: Gestiona la colección y la base de datos SQLite"""
    def __init__(self):
        self.db_name = 'joyeria.db'
        self.crear_tabla()
        # Diccionario para optimizar búsquedas rápidas en memoria
        self.productos_dict = {} 
        self.sincronizar_diccionario()

    def crear_tabla(self):
        """Crea la tabla si no existe al iniciar el sistema"""
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            modelo TEXT,
                            coleccion TEXT,
                            material TEXT,
                            peso TEXT,
                            cantidad INTEGER,
                            precio REAL)''')
        conexion.commit()
        conexion.close()

    def añadir_pieza(self, modelo, coleccion, material, peso, cantidad, precio):
        """Añade nuevos productos a la base de datos"""
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO productos (modelo, coleccion, material, peso, cantidad, precio) VALUES (?, ?, ?, ?, ?, ?)",
                       (modelo, coleccion, material, peso, cantidad, precio))
        conexion.commit()
        conexion.close()
        self.sincronizar_diccionario() # Actualiza el diccionario tras añadir

    def obtener_todo(self):
        """Recupera todos los productos como una lista de objetos Pieza"""
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        filas = cursor.fetchall()
        conexion.close()
        return [Pieza(f[0], f[1], f[2], f[3], f[4], f[5], f[6]) for f in filas]

    def sincronizar_diccionario(self):
        """Carga los datos en un diccionario para búsqueda rápida"""
        lista_productos = self.obtener_todo()
        self.productos_dict = {p.id: p for p in lista_productos}

    def buscar_por_nombre(self, nombre):
        """Busca y muestra productos por nombre"""
        todos = self.obtener_todo()
        return [p for p in todos if nombre.lower() in p.modelo.lower()]

    def eliminar_producto(self, id_producto):
        """Elimina productos de la base de datos por ID"""
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conexion.commit()
        conexion.close()
        self.sincronizar_diccionario()

    def actualizar_stock(self, id_prod, nueva_cantidad):
     if id_prod in self.productos_dict:
        self.productos_dict[id_prod].cantidad = nueva_cantidad
        
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, id_prod))
        conexion.commit()
        conexion.close()
        
        print("Stock actualizado correctamente.")
     else:
        print("Producto no encontrado.")

    def actualizar_precio(self, id_prod, nuevo_precio):
     if id_prod in self.productos_dict:
        self.productos_dict[id_prod].precio = nuevo_precio
        
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("UPDATE productos SET precio = ? WHERE id = ?", 
                       (nuevo_precio, id_prod))
        conexion.commit()
        conexion.close()
        
        print("Precio actualizado correctamente.")
     else:
        print("Producto no encontrado.")