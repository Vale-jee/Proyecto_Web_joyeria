# ======================================================
# IMPORTACIÓN DE LIBRERÍAS
# ======================================================

from flask import Flask, render_template, request, redirect, flash  # Flask y funciones básicas
from flask_sqlalchemy import SQLAlchemy  # ORM para SQLite
from services.producto_service import Catalogo
from forms.producto_form import ProductoForm
from services.producto_service import guardar_txt, guardar_json, guardar_csv, leer_txt, leer_json, leer_csv
from conexion.conexion import get_db_connection  # conexión MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from flask import make_response
from dotenv import load_dotenv
load_dotenv()
import os
import io


# ======================================================
# CONFIGURACIÓN GENERAL DE LA APLICACIÓN
# ======================================================

# Ruta base del proyecto
basedir = os.path.abspath(os.path.dirname(__file__))

# Crear aplicación Flask
app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY", "clave_segura_123")
# ======================================================
# CONFIGURACIÓN DE LOGIN (Flask-Login)
# ======================================================

login_manager = LoginManager()
login_manager.init_app(app)

# si un usuario no está autenticado será enviado a /login
login_manager.login_view = "login"


# ======================================================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL
# ======================================================

app.config['MYSQL_HOST'] = os.getenv("MYSQLHOST", "localhost")
app.config['MYSQL_USER'] = os.getenv("MYSQLUSER", "root")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQLPASSWORD", "")
app.config['MYSQL_DATABASE'] = os.getenv("MYSQLDATABASE", "joyeria_resplandor_mysql")
app.config['MYSQL_PORT'] = int(os.getenv("MYSQLPORT", 3306))


# ======================================================
# CONFIGURACIÓN SQLITE (usado en semanas anteriores)
# ======================================================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'joyeria_orm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)


# ======================================================
# MODELO ORM PARA PRODUCTOS (SQLite)
# ======================================================

class ProductoORM(db.Model):

    __tablename__ = 'productos_orm'

    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100))
    precio = db.Column(db.Float)
    cantidad = db.Column(db.Integer)

    def __repr__(self):
        return f"<Producto {self.modelo}>"


# ======================================================
# MODELO ORM PARA MENSAJES DE CONTACTO
# ======================================================

class MensajeORM(db.Model):

    __tablename__ = 'mensajes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    mensaje = db.Column(db.Text)

    def __repr__(self):
        return f"<Mensaje {self.nombre}>"


# ======================================================
# MODELO DE USUARIO PARA FLASK-LOGIN
# ======================================================

class Usuario(UserMixin):

    # esta clase representa un usuario del sistema
    def __init__(self, id_usuario, nombre, email, password):

        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password


# ======================================================
# RUTAS PÚBLICAS DEL SITIO
# ======================================================

@app.route('/')
def inicio():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


# ======================================================
# CATÁLOGO DE PRODUCTOS (MYSQL)
# ======================================================

@app.route('/agregar_carrito/<int:id>')
def agregar_carrito(id):

    if 'carrito' not in session:
        session['carrito'] = []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos_mysql WHERE id_producto=%s", (id,))
    producto = cursor.fetchone()

    cursor.close()
    conn.close()

    if producto:
        session['carrito'].append(producto)

    return redirect('/carrito')

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

        return render_template('productos/producto.html', joyas=filtradas, titulo=col_elegida, modo="piezas")

    else:

        nombres_col = sorted(list(set(p['coleccion'] for p in piezas)))

        cursor.close()
        conn.close()

        return render_template('productos/producto.html', lista_col=nombres_col, modo="colecciones")

@app.route('/carrito')
def carrito():

    carrito = session.get('carrito', [])
    total = sum(float(p['precio']) for p in carrito)

    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/eliminar_carrito/<int:index>')
def eliminar_carrito(index):

    carrito = session.get('carrito', [])

    if 0 <= index < len(carrito):
        carrito.pop(index)
        session['carrito'] = carrito

    return redirect('/carrito')

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session.pop('carrito', None)
    return redirect('/carrito')

@app.route('/comprar')
def comprar():

    session.pop('carrito', None)

    return "<h2 style='text-align:center;'>✅ Compra realizada con éxito</h2>"

# ======================================================
# INVENTARIO (PROTEGIDO POR LOGIN)
# ======================================================

@app.route('/inventario')
@login_required
def inventario():

    mi_catalogo = Catalogo()
    productos = mi_catalogo.obtener_todo()

    return render_template('inventario.html', productos=productos)


# ======================================================
# AGREGAR PRODUCTO
# ======================================================

@app.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():

    mi_catalogo = Catalogo()

    if request.method == 'POST':

        form = ProductoForm(request.form)

        modelo = form.modelo
        coleccion = form.coleccion
        material = form.material
        peso = form.peso
        cantidad = int(form.cantidad)
        precio = float(form.precio)

        mi_catalogo.añadir_pieza(modelo, coleccion, material, peso, cantidad, precio)

        producto_dict = {
            "modelo": modelo,
            "precio": precio,
            "cantidad": cantidad
        }

        # guardar persistencia
        guardar_txt(producto_dict)
        guardar_json(producto_dict)
        guardar_csv(producto_dict)

        return redirect('/inventario')

    return render_template('agregar.html')


# ======================================================
# EDITAR PRODUCTO
# ======================================================

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
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


# ======================================================
# ELIMINAR PRODUCTO
# ======================================================

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):

    mi_catalogo = Catalogo()
    mi_catalogo.eliminar_producto(id)

    return redirect('/inventario')


# ======================================================
# BUSCAR PRODUCTOS
# ======================================================

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():

    mi_catalogo = Catalogo()
    resultados = []

    if request.method == 'POST':

        nombre = request.form['nombre']
        resultados = mi_catalogo.buscar_por_nombre(nombre)

    return render_template('buscar.html', productos=resultados)


# ======================================================
# PERSISTENCIA DE DATOS
# ======================================================

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


# ======================================================
# CONTACTO
# ======================================================

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


# ======================================================
# LOGIN Y REGISTRO DE USUARIOS
# ======================================================

@login_manager.user_loader
def load_user(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_usuario, nombre, email, password FROM usuarios WHERE id_usuario=%s",
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return Usuario(user[0], user[1], user[2], user[3])

    return None


@app.route('/registro', methods=['GET','POST'])
def registro():

    if request.method == 'POST':

        nombre = request.form['nombre']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password)
                VALUES (%s, %s, %s)
            """, (nombre, email, password))

            conn.commit()

            cursor.close()
            conn.close()

            return redirect('/login')

        except Exception as e:
            return f"Error: {e}"

    return render_template("registro.html")


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_usuario,nombre,email,password FROM usuarios WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user[3], password):
            usuario = Usuario(user[0], user[1], user[2], user[3])
            login_user(usuario)
            return redirect('/')
        else:
            return render_template("login.html", error="Correo o contraseña incorrectos")

    return render_template("login.html")


@app.route('/mysql')
@login_required
def mysql():

    conn = get_db_connection()
    cursor = conn.cursor()

    editar_id = request.args.get('editar')
    producto_editar = None

    # 👉 si se presiona editar
    if editar_id:
        cursor.execute(
            "SELECT * FROM productos_mysql WHERE id_producto=%s",
            (editar_id,)
        )
        producto_editar = cursor.fetchone()

    # productos
    cursor.execute("SELECT * FROM productos_mysql")
    productos = cursor.fetchall()

    # usuarios
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'mysql.html',
        productos=productos,
        usuarios=usuarios,
        producto_editar=producto_editar
    )

@app.route('/producto/<nombre>')
def detalle_producto(nombre):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM productos_mysql WHERE modelo=%s",
        (nombre,)
    )

    joya = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('productos/detalle.html', joya=joya)

@app.route('/agregar_producto_mysql', methods=['POST'])
def agregar_producto_mysql():

    id_producto = request.form.get('id_producto')

    modelo = request.form['modelo']
    coleccion = request.form['coleccion']
    material = request.form['material']
    peso = request.form['peso']
    cantidad = request.form['cantidad']
    precio = request.form['precio']

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✏️ EDITAR
    if id_producto:
        cursor.execute("""
            UPDATE productos_mysql
            SET modelo=%s, coleccion=%s, material=%s,
                peso=%s, cantidad=%s, precio=%s
            WHERE id_producto=%s
        """, (modelo, coleccion, material, peso, cantidad, precio, id_producto))

    # ➕ AGREGAR
    else:
        cursor.execute("""
            INSERT INTO productos_mysql
            (modelo,coleccion,material,peso,cantidad,precio)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (modelo, coleccion, material, peso, cantidad, precio))

    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Producto agregado correctamente")
    return redirect('/mysql')

@app.route('/eliminar_producto_mysql/<int:id>')
def eliminar_producto_mysql(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM productos_mysql WHERE id_producto = %s", (id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/mysql')

@app.route('/eliminar_usuario_mysql/<int:id>')
def eliminar_usuario_mysql(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM usuarios WHERE id_usuario=%s",
        (id,)
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
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

   
    # ➕ AGREGAR
    cursor.execute("""
        INSERT INTO usuarios (nombre, email, password)
        VALUES (%s, %s, %s)
    """, (nombre, email, password))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/mysql')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# PDF

@app.route('/reporte_pdf')
@login_required
def reporte_pdf():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT modelo, coleccion, material, precio, cantidad FROM productos_mysql""")
    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elements = []

    styles = getSampleStyleSheet()

    # 👉 TÍTULO
    titulo = Paragraph("REPORTE DE PRODUCTOS - JOYERÍA RESPLANDOR", styles['Title'])
    elements.append(titulo)

    # 👉 ESPACIO
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # 👉 DATOS DE LA TABLA
    data = [["Producto", "Colección", "Material", "Precio", "Stock"]]

    for p in productos:
        data.append([p[0], f"${p[1]}", p[2], f"${p[3]}", p[4]])

    # 👉 CREAR TABLA
    tabla = Table(data)

    # 👉 ESTILO BONITO
    estilo = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gold),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),

        ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),

        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])

    tabla.setStyle(estilo)

    elements.append(tabla)

    doc.build(elements)

    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_productos.pdf'

    return response

# ======================================================
# EJECUCIÓN DE LA APLICACIÓN
# ======================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port, debug=True)