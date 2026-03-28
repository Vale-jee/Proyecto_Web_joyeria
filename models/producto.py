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