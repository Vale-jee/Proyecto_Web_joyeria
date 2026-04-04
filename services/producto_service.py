import sqlite3
import os
import json
import csv
from models.producto import Pieza

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_PATH, exist_ok=True)


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

        # Tabla colecciones (NUEVA)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colecciones (
            id_coleccion INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE
        )
    ''')

        # Tabla productos (MODIFICADA)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT,
            id_coleccion INTEGER,
            material TEXT,
            peso TEXT,
            cantidad INTEGER,
            precio REAL,
            FOREIGN KEY (id_coleccion) REFERENCES colecciones(id_coleccion)
        )
    ''')

        conexion.commit()
        conexion.close()

    def añadir_pieza(self, modelo, coleccion, material, peso, cantidad, precio):
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()

        # 1. Buscar colección
        cursor.execute("SELECT id_coleccion FROM colecciones WHERE nombre = ?", (coleccion,))
        resultado = cursor.fetchone()

        if resultado:
            id_coleccion = resultado[0]
        else:
            # 2. Insertar colección si no existe
            cursor.execute("INSERT INTO colecciones (nombre) VALUES (?)", (coleccion,))
            id_coleccion = cursor.lastrowid

        # 3. Insertar producto con ID de colección
        cursor.execute(
            "INSERT INTO productos (modelo, id_coleccion, material, peso, cantidad, precio) VALUES (?, ?, ?, ?, ?, ?)",
            (modelo, id_coleccion, material, peso, cantidad, precio)
    )

        conexion.commit()
        conexion.close()
        self.sincronizar_diccionario()

    def obtener_todo(self):
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT p.id, p.modelo, c.nombre, p.material, p.peso, p.cantidad, p.precio
            FROM productos p
            JOIN colecciones c ON p.id_coleccion = c.id_coleccion
        """)
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

# ---------- PERSISTENCIA TXT ----------
def guardar_txt(producto):
    ruta = os.path.join(DATA_PATH, "datos.txt")
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(f"{producto['modelo']},{producto['precio']},{producto['cantidad']}\n")

def leer_txt():
    ruta = os.path.join(DATA_PATH, "datos.txt")
    productos = []
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                productos.append(linea.strip().split(","))
    return productos


# ---------- PERSISTENCIA JSON ----------
def guardar_json(producto):
    ruta = os.path.join(DATA_PATH, "datos.json")
    datos = []

    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except:
                datos = []

    datos.append(producto)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def leer_json():
    ruta = os.path.join(DATA_PATH, "datos.json")
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ---------- PERSISTENCIA CSV ----------
def guardar_csv(producto):
    ruta = os.path.join(DATA_PATH, "datos.csv")
    archivo_existe = os.path.exists(ruta)

    with open(ruta, mode='a', newline='', encoding='utf-8') as archivo:
        campos = ["modelo", "precio", "cantidad"]
        escritor = csv.DictWriter(archivo, fieldnames=campos)

        if not archivo_existe:
            escritor.writeheader()

        escritor.writerow(producto)

def leer_csv():
    ruta = os.path.join(DATA_PATH, "datos.csv")
    datos = []

    if not os.path.exists(ruta):
        return datos

    with open(ruta, mode='r', newline='', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)

        for fila in lector:
            # Ignorar filas vacías
            if len(fila) == 3:
                datos.append({
                    "modelo": fila[0],
                    "precio": fila[1],
                    "cantidad": fila[2]
                })

    return datos