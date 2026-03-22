import mysql.connector
import os

def get_db_connection():

    # 👉 SI estás en Railway
    if os.getenv("MYSQLHOST") and os.getenv("MYSQLHOST") != "localhost":
        print("☁️ USANDO RAILWAY")
        return mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT"))
        )

    # 👉 SI estás en LOCAL (Workbench)
    else:
        print("💻 USANDO LOCAL WORKBENCH")
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="joyeria_resplandor_mysql",
            port=3306
        )