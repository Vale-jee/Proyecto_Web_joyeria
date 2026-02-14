from flask import Flask

app = Flask(__name__)

# 1. RUTA PRINCIPAL
@app.route('/')
def inicio():
    return "<h1>Sistema Joyería Resplandor</h1><p>Bienvenido al catálogo de piezas exclusivas y joyería fina.</p>"

# 2. RUTA DE CATÁLOGO 
@app.route('/producto')
def catalogo():
    return """
    <h2>Catálogo General de Productos</h2>
    <p>Categorías activas:</p>
    <ul>
        <li>Anillos</li>
        <li>Pulseras</li>
        <li>Cadenas</li>
        <li>Relojes</li>
    """
# 3. RUTA DINÁMICA
@app.route('/producto/<nombre>')
def detalle_producto(nombre):
    return f"<h2>Producto: {nombre.capitalize()}</h2><p>Estado: <strong>Disponible para entrega inmediata.</strong></p>"

if __name__ == '__main__':
    app.run(debug=True)