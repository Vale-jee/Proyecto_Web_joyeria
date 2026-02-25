import sqlite3

def inicializar_db():
    conexion = sqlite3.connect('joyeria.db')
    cursor = conexion.cursor()
    
    # Tabla actualizada con el campo PESO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT NOT NULL,
            coleccion TEXT NOT NULL,
            material TEXT NOT NULL,
            peso TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("Base de Datos actualizada con campo 'Peso'.")

if __name__ == "__main__":
    inicializar_db()