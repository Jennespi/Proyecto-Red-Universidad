import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos MySQL
    """
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            auth_plugin='mysql_native_password'
        )
        print("Conexión a MySQL establecida correctamente")
        return conn
    except mysql.connector.Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def test_connection():
    """
    Función para probar la conexión a la base de datos
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"Conectado a la base de datos: {db_name[0]}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Tablas en la base de datos:")
            for table in tables:
                print(f"   - {table[0]}")
            
            cursor.close()
            conn.close()
            return True
        except mysql.connector.Error as e:
            print(f"Error en la consulta: {e}")
            return False
    return False