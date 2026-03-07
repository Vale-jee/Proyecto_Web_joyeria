from flask import Flask, render_template, request, redirect # 'request' para detectar clics
from flask_sqlalchemy import SQLAlchemy
from inventario import Catalogo 
from inventario import guardar_txt, guardar_json, guardar_csv, leer_txt, leer_json, leer_csv
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'joyeria_orm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)

class ProductoORM(db.Model):
    __tablename__ = 'productos_orm'

    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100))
    precio = db.Column(db.Float)
    cantidad = db.Column(db.Integer)

    def __repr__(self):
        return f"<Producto {self.modelo}>"
    

class MensajeORM(db.Model):
    __tablename__ = 'mensajes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    mensaje = db.Column(db.Text)

    def __repr__(self):
        return f"<Mensaje {self.nombre}>"

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
        producto_dict = {
            "modelo": modelo,
            "precio": precio,
            "cantidad": cantidad
        }

        guardar_txt(producto_dict)
        guardar_json(producto_dict)
        guardar_csv(producto_dict)
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

@app.route('/ver_datos')
def ver_datos():
    from inventario import leer_txt, leer_json, leer_csv
    
    datos_txt = leer_txt()
    datos_json = leer_json()
    datos_csv = leer_csv()

    return render_template(
        'datos.html',
        datos_txt=datos_txt,
        datos_json=datos_json,
        datos_csv=datos_csv
    )


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    mensaje_enviado = False

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        mensaje = request.form['mensaje']

        nuevo = MensajeORM(
            nombre=nombre,
            email=email,
            telefono=telefono,
            mensaje=mensaje
        )

        db.session.add(nuevo)
        db.session.commit()

        mensaje_enviado = True

    mensajes = MensajeORM.query.all()

    return render_template(
        'contacto.html',
        mensaje_enviado=mensaje_enviado,
        mensajes=mensajes
    )

@app.route('/eliminar_mensaje/<int:id>')
def eliminar_mensaje(id):
    mensaje = MensajeORM.query.get(id)

    if mensaje:
        db.session.delete(mensaje)
        db.session.commit()

    return redirect('/contacto')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)