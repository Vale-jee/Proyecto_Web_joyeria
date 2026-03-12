import mysql.connector as mysql
from flask import current_app

def get_db_connection():
    conexion = mysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DATABASE']
    )
    return conexion