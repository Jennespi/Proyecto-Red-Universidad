from werkzeug.security import generate_password_hash
from utils.db_connection import get_db_connection
from datetime import date, time

def poblar_datos_real():
    conn = get_db_connection()
    if not conn:
        print("Error: No se pudo conectar a la base de datos")
        return
    
    cursor = conn.cursor()
    
    try:
        print("Poblando base de datos con estructura real...")
        
        # 1. Limpiar tablas en el orden correcto (primero las que dependen de otras)
        print("Limpiando tablas existentes...")
        cursor.execute("DELETE FROM logs_transacciones")
        cursor.execute("DELETE FROM mensajes")
        cursor.execute("DELETE FROM trafico_red")
        cursor.execute("DELETE FROM usuarios")
        
        # 2. Insertar usuarios con contraseñas REALES encriptadas y obtener sus IDs
        print("Insertando usuarios...")
        
        # Generar hashes reales
        admin_hash = generate_password_hash('admin123')
        estudiante_hash = generate_password_hash('estudiante123')
        
        # Insertar usuario administrador
        cursor.execute("""
            INSERT INTO usuarios 
            (tipo_documento_id, documento, nombre, correo, telefono, contrasena, rol) 
            VALUES 
            (1, '1001234567', 'Jennifer Espitia', 'jennifer@ucundinamarca.edu.co', '3123456789', %s, 'administrador')
        """, (admin_hash,))
        admin_id = cursor.lastrowid
        print(f"  - Admin creado con ID: {admin_id}")
        
        # Insertar usuario estudiante
        cursor.execute("""
            INSERT INTO usuarios 
            (tipo_documento_id, documento, nombre, correo, telefono, contrasena, rol) 
            VALUES 
            (1, '2009876543', 'Leonardo Moscoso', 'leo@ucundinamarca.edu.co', '3187654321', %s, 'estudiante')
        """, (estudiante_hash,))
        estudiante_id = cursor.lastrowid
        print(f"  - Estudiante creado con ID: {estudiante_id}")
        
        # 3. Insertar datos de tráfico
        print("Insertando datos de tráfico...")
        
        datos_trafico = [
            (1, date.today(), time(8, 0), 'portatil', 15, 45.2, 25.1),
            (1, date.today(), time(10, 0), 'movil', 25, 68.7, 32.4),
            (1, date.today(), time(12, 0), 'movil', 42, 95.3, 45.2),
            (2, date.today(), time(9, 0), 'portatil', 18, 156.8, 15.2),
            (3, date.today(), time(13, 0), 'movil', 55, 78.9, 38.6),
        ]
        
        for dato in datos_trafico:
            cursor.execute("""
                INSERT INTO trafico_red 
                (zona_id, fecha, hora, tipo_dispositivo, usuarios_conectados, ancho_banda_consumido, latencia_promedio) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, dato)
        print(f"  - Insertados {len(datos_trafico)} registros de tráfico")
        
        # 4. AHORA insertar logs de ejemplo (después de crear usuarios)
        print("Insertando logs de ejemplo...")
        
        logs = [
            (admin_id, 'REGISTRO - Usuario administrador creado'),
            (estudiante_id, 'REGISTRO - Usuario estudiante creado'),
            (admin_id, 'LOGIN - Inicio de sesión exitoso'),
            (estudiante_id, 'LOGIN - Inicio de sesión exitoso'),
        ]
        
        for usuario_id, accion in logs:
            cursor.execute("""
                INSERT INTO logs_transacciones 
                (usuario_id, accion) 
                VALUES (%s, %s)
            """, (usuario_id, accion))
        print(f"  - Insertados {len(logs)} logs")
        
        # Confirmar cambios
        conn.commit()
        print("✅ Base de datos poblada exitosamente!")
        
        # Mostrar resumen
        print("\n=== RESUMEN ===")
        cursor.execute("SELECT COUNT(*) as count FROM usuarios")
        print(f"Usuarios: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) as count FROM trafico_red")
        print(f"Registros de tráfico: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) as count FROM logs_transacciones")
        print(f"Logs: {cursor.fetchone()[0]}")
        
        print("\n=== CREDENCIALES PARA LOGIN ===")
        print("Administrador: jennifer@ucundinamarca.edu.co / admin123")
        print("Estudiante: leo@ucundinamarca.edu.co / estudiante123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    poblar_datos_real()