from flask import Flask, render_template, request, redirect # 'request' para detectar clics
from flask_sqlalchemy import SQLAlchemy
from inventario import Catalogo 
from inventario import guardar_txt, guardar_json, guardar_csv, leer_txt, leer_json, leer_csv
from conexion.conexion import get_db_connection
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder='templates')
app.config['MYSQL_HOST'] = os.getenv("MYSQLHOST", "localhost")
app.config['MYSQL_USER'] = os.getenv("MYSQLUSER", "root")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQLPASSWORD", "")
app.config['MYSQL_DATABASE'] = os.getenv("MYSQLDATABASE", "joyeria_resplandor_mysql")
app.config['MYSQL_PORT'] = int(os.getenv("MYSQLPORT", 3306))
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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos_mysql")
    piezas = cursor.fetchall()

    col_elegida = request.args.get('coleccion')

    if col_elegida:
        filtradas = [p for p in piezas if p['coleccion'] == col_elegida]
        cursor.close()
        conn.close()
        return render_template('producto.html', joyas=filtradas, titulo=col_elegida, modo="piezas")
    else:
        nombres_col = sorted(list(set(p['coleccion'] for p in piezas)))
        cursor.close()
        conn.close()
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

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT modelo, precio, cantidad FROM productos_mysql")
    datos = cursor.fetchall()

    cursor.close()
    conn.close()

    datos_txt = datos
    datos_json = [{"modelo": d[0], "precio": d[1], "cantidad": d[2]} for d in datos]
    datos_csv = [{"modelo": d[0], "precio": d[1], "cantidad": d[2]} for d in datos]

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



@app.route('/mysql')
def mysql():

    conn = get_db_connection()
    cursor = conn.cursor()

    editar_id = request.args.get('editar')
    usuario_editar = None

    if editar_id:
        cursor.execute(
            "SELECT * FROM usuarios WHERE id_usuario=%s",
            (editar_id,)
        )
        usuario_editar = cursor.fetchone()

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM productos_mysql")
    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "mysql.html",
        usuarios=usuarios,
        productos=productos,
        usuario_editar=usuario_editar
    )
@app.route('/agregar_producto_mysql', methods=['POST'])
def agregar_producto_mysql():

    modelo = request.form['modelo']
    coleccion = request.form['coleccion']
    material = request.form['material']
    peso = request.form['peso']
    cantidad = request.form['cantidad']
    precio = request.form['precio']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO productos_mysql
        (modelo,coleccion,material,peso,cantidad,precio)
        VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (modelo,coleccion,material,peso,cantidad,precio)
    )

    conn.commit()
    cursor.close()
    conn.close()

    # -------- SINCRONIZAR CON PERSISTENCIA --------

    producto_dict = {
        "modelo": modelo,
        "precio": float(precio),
        "cantidad": int(cantidad)
    }

    guardar_txt(producto_dict)
    guardar_json(producto_dict)
    guardar_csv(producto_dict)

    return redirect('/mysql')

@app.route('/eliminar_producto_mysql/<int:id>')
def eliminar_producto_mysql(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    # primero obtenemos el producto para saber su modelo
    cursor.execute(
        "SELECT modelo FROM productos_mysql WHERE id_producto=%s",
        (id,)
    )
    producto = cursor.fetchone()

    # eliminamos en MySQL
    cursor.execute(
        "DELETE FROM productos_mysql WHERE id_producto=%s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    # -------- eliminar también de persistencia --------

    if producto:
        modelo = producto[0]

        datos_txt = leer_txt()
        datos_txt = [d for d in datos_txt if d[0] != modelo]

        datos_json = leer_json()
        datos_json = [d for d in datos_json if d["modelo"] != modelo]

        datos_csv = leer_csv()
        datos_csv = [d for d in datos_csv if d["modelo"] != modelo]

    # --------------------------------------------------

    return redirect('/mysql')

@app.route('/editar_producto_mysql/<int:id>', methods=['POST'])
def editar_producto_mysql(id):

    modelo = request.form['modelo']
    coleccion = request.form['coleccion']
    material = request.form['material']
    peso = request.form['peso']
    cantidad = request.form['cantidad']
    precio = request.form['precio']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE productos_mysql
        SET modelo=%s, coleccion=%s, material=%s, peso=%s, cantidad=%s, precio=%s
        WHERE id_producto=%s
        """,
        (modelo,coleccion,material,peso,cantidad,precio,id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/mysql')

@app.route('/agregar_usuario_mysql', methods=['POST'])
def agregar_usuario_mysql():

    id_usuario = request.form.get('id_usuario')
    nombre = request.form['nombre']
    email = request.form['email']
    telefono = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    if id_usuario:
        cursor.execute(
            """
            UPDATE usuarios
            SET nombre=%s, email=%s, telefono=%s
            WHERE id_usuario=%s
            """,
            (nombre, email, telefono, id_usuario)
        )
    else:
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, telefono)
            VALUES (%s, %s, %s)
            """,
            (nombre, email, telefono)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/mysql')

@app.route('/editar_usuario_mysql/<int:id>', methods=['GET','POST'])
def editar_usuario_mysql(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':

        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['password']

        cursor.execute(
            """
            UPDATE usuarios
            SET nombre=%s, email=%s, telefono=%s
            WHERE id_usuario=%s
            """,
            (nombre, email, telefono, id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/mysql')

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (id,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("editar_usuario_mysql.html", usuario=usuario)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)