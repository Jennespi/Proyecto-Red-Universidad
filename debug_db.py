import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
import os

print("=== DEBUG DE CONEXIÓN A BASE DE DATOS ===")

# Mostrar configuración actual
print(f"Host: {MYSQL_HOST}")
print(f"Usuario: {MYSQL_USER}")
print(f"Base de datos: {MYSQL_DB}")
print(f"Contraseña: {'*' * len(MYSQL_PASSWORD) if MYSQL_PASSWORD else '(vacía)'}")

# Probar conexión básica
try:
    print("\n1. Probando conexión sin base de datos...")
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        auth_plugin='mysql_native_password'
    )
    print("   ✅ Conexión básica exitosa")
    
    # Listar bases de datos
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print("\n2. Bases de datos disponibles:")
    for db in databases:
        print(f"   - {db[0]}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"   ❌ Error en conexión básica: {e}")

# Probar conexión con base de datos específica
try:
    print("\n3. Probando conexión a base de datos específica...")
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        auth_plugin='mysql_native_password'
    )
    print(f"   ✅ Conexión a '{MYSQL_DB}' exitosa")
    
    # Listar tablas
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\n4. Tablas en '{MYSQL_DB}':")
    for table in tables:
        print(f"   - {table[0]}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"   ❌ Error conectando a '{MYSQL_DB}': {e}")

print("\n=== FIN DEBUG ===")