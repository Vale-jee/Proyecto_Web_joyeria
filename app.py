from flask import Flask, render_template, request # 'request' para detectar clics
from inventario import Catalogo 
from flask import request, redirect
from inventario import Catalogo
import os

app = Flask(__name__, template_folder='templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/producto')
def catalogo():
    mi_catalogo = Catalogo() 
    piezas = mi_catalogo.obtener_todo()
    
    # Detecta si se hizo clic en una colección
    col_elegida = request.args.get('coleccion')
    
    if col_elegida:
        # Filtra productos por esa colección
        filtradas = [p for p in piezas if p.coleccion == col_elegida]
        return render_template('producto.html', joyas=filtradas, titulo=col_elegida, modo="piezas")
    else:
        # Saca lista de nombres únicos de colecciones
        nombres_col = sorted(list(set(p.coleccion for p in piezas)))
        return render_template('producto.html', lista_col=nombres_col, modo="colecciones")

@app.route('/producto/<nombre>')
def detalle_producto(nombre):
    mi_catalogo = Catalogo()
    piezas = mi_catalogo.obtener_todo()
    joya_encontrada = next((p for p in piezas if p.modelo == nombre), None)
    
    return render_template('detalle.html', joya=joya_encontrada)

@app.route('/inventario')
def inventario():
    mi_catalogo = Catalogo()
    productos = mi_catalogo.obtener_todo()
    return render_template('inventario.html', productos=productos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    mi_catalogo = Catalogo()

    if request.method == 'POST':
        modelo = request.form['modelo']
        coleccion = request.form['coleccion']
        material = request.form['material']
        peso = request.form['peso']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])

        mi_catalogo.añadir_pieza(modelo, coleccion, material, peso, cantidad, precio)

        return redirect('/inventario')

    return render_template('agregar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    mi_catalogo = Catalogo()

    if request.method == 'POST':
        modelo = request.form['modelo']
        coleccion = request.form['coleccion']
        material = request.form['material']
        peso = request.form['peso']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])

        mi_catalogo.actualizar_producto(id, modelo, coleccion, material, peso, cantidad, precio)

        return redirect('/inventario')

    productos = mi_catalogo.obtener_todo()
    producto = next((p for p in productos if p.id == id), None)

    return render_template('editar.html', producto=producto)
    

@app.route('/eliminar/<int:id>')
def eliminar(id):
    mi_catalogo = Catalogo()
    mi_catalogo.eliminar_producto(id)
    return redirect('/inventario')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    mi_catalogo = Catalogo()
    resultados = []

    if request.method == 'POST':
        nombre = request.form['nombre']
        resultados = mi_catalogo.buscar_por_nombre(nombre)

    return render_template('buscar.html', productos=resultados)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)