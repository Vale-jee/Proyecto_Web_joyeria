class ProductoForm:

    def __init__(self, form):
        self.modelo = form.get('modelo')
        self.coleccion = form.get('coleccion')
        self.material = form.get('material')
        self.peso = form.get('peso')
        self.cantidad = form.get('cantidad')
        self.precio = form.get('precio')