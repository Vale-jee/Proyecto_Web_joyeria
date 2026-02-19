from flask import Flask, render_template

app = Flask(__name__)

# 1. RUTA PRINCIPAL
@app.route('/')
def inicio():
    return render_template('index.html')

# 2. RUTA NOSOTROS
@app.route('/about')
def about():
    return render_template('about.html')

# 3. RUTA CATÁLOGO (General)
@app.route('/producto')
def catalogo():
    return render_template('producto.html')

# 4. RUTA DETALLE DE PRODUCTO 
@app.route('/producto/<nombre>')
def detalle_producto(nombre):
    return render_template('detalle.html', nombre=nombre)

if __name__ == '__main__':
    app.run(debug=True)