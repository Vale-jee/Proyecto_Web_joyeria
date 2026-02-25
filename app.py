from flask import Flask, render_template, request # 'request' para detectar clics
from inventario import Catalogo 

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)