from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import mysql.connector
import secrets
from utils.db_connection import get_db_connection

app = Flask(__name__)
app.secret_key = 'clave_secreta_ucundinamarca_2024_jennifer_leo'

def registrar_log_db(usuario_id, accion, detalles=""):
    """Registra actividad en la base de datos - adaptado a la estructura real"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # La tabla logs_transacciones solo tiene: id, usuario_id, accion, fecha_hora
            cursor.execute("""
                INSERT INTO logs_transacciones 
                (usuario_id, accion) 
                VALUES (%s, %s)
            """, (usuario_id, f"{accion}: {detalles}" if detalles else accion))
            
            conn.commit()
            cursor.close()
            print(f"Log registrado: {accion} - Usuario: {usuario_id}")
        except Exception as e:
            print(f"Error registrando log: {e}")
        finally:
            conn.close()

def obtener_tipos_documento():
    """Obtiene los tipos de documento de la base de datos"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, codigo, descripcion FROM tipos_documento ORDER BY id")
            tipos = cursor.fetchall()
            cursor.close()
            return tipos
        except Exception as e:
            print(f"Error obteniendo tipos de documento: {e}")
            return []
        finally:
            conn.close()
    return []

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        correo = request.form["usuario"]
        contrasena = request.form["contrasena"]

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            try:
                # Consulta SIN la columna 'activo' (no existe en tu BD)
                cursor.execute("""
                    SELECT u.*, td.descripcion as tipo_documento 
                    FROM usuarios u 
                    JOIN tipos_documento td ON u.tipo_documento_id = td.id 
                    WHERE u.correo = %s
                """, (correo,))
                
                usuario = cursor.fetchone()
                
                if usuario and check_password_hash(usuario['contrasena'], contrasena):
                    session["usuario_id"] = usuario["id"]
                    session["usuario"] = usuario["nombre"]
                    session["correo"] = usuario["correo"]
                    session["rol"] = usuario["rol"]
                    session["tipo_documento"] = usuario["tipo_documento"]
                    
                    registrar_log_db(usuario["id"], "LOGIN", "Inicio de sesión exitoso")
                    
                    if usuario["rol"] == "administrador":
                        return redirect(url_for("admin_dashboard"))
                    else:
                        return redirect(url_for("dashboard"))
                else:
                    error = "Correo o contraseña incorrectos."
                    
            except Exception as e:
                error = f"Error en el sistema: {e}"
                print(f"Error detallado: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            error = "Error de conexión a la base de datos."

    return render_template("login.html", error=error)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None
    tipos_documento = obtener_tipos_documento()

    if request.method == "POST":
        tipo_documento_id = request.form.get("tipo_documento")
        documento = request.form.get("documento")
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")
        contrasena = request.form.get("contrasena")
        confirmar = request.form.get("confirmar")

        if contrasena != confirmar:
            error = "Las contraseñas no coinciden."
        elif len(contrasena) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        else:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
                    if cursor.fetchone():
                        error = "El correo electrónico ya está registrado."
                    else:
                        contrasena_hash = generate_password_hash(contrasena)
                        
                        cursor.execute("""
                            INSERT INTO usuarios 
                            (tipo_documento_id, documento, nombre, correo, telefono, contrasena, rol) 
                            VALUES (%s, %s, %s, %s, %s, %s, 'estudiante')
                        """, (tipo_documento_id, documento, nombre, correo, telefono, contrasena_hash))
                        
                        conn.commit()
                        usuario_id = cursor.lastrowid
                        
                        registrar_log_db(usuario_id, "REGISTRO", f"Usuario {nombre} registrado")
                        
                        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
                        return redirect(url_for("login"))
                    
                except mysql.connector.Error as err:
                    error = f"Error en la base de datos: {err}"
                finally:
                    cursor.close()
                    conn.close()
            else:
                error = "Error de conexión a la base de datos."

    return render_template("registro.html", error=error, tipos_documento=tipos_documento)

@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    registrar_log_db(session["usuario_id"], "ACCESO_DASHBOARD", "Accedió al panel de usuario")
    return render_template("dashboard.html", nombre=session["usuario"])

@app.route("/admin")
def admin_dashboard():
    if "usuario_id" not in session or session.get("rol") != "administrador":
        flash("Acceso restringido al administrador.")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    stats = {}
    registros = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            stats['total_usuarios'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM mensajes")
            stats['total_mensajes'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as hoy FROM logs_transacciones WHERE DATE(fecha_hora) = CURDATE()")
            stats['actividad_hoy'] = cursor.fetchone()['hoy']
            
            cursor.execute("""
                SELECT l.*, u.nombre as usuario_nombre 
                FROM logs_transacciones l 
                JOIN usuarios u ON l.usuario_id = u.id 
                ORDER BY l.fecha_hora DESC 
                LIMIT 20
            """)
            registros = cursor.fetchall()
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
        finally:
            cursor.close()
            conn.close()
    
    registrar_log_db(session["usuario_id"], "ACCESO_ADMIN", "Accedió al panel administrativo")
    return render_template("admin_dashboard.html", stats=stats, registros=registros)

@app.route("/chat")
def chat():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    registrar_log_db(session["usuario_id"], "ACCESO_CHAT", "Accedió al sistema de chat")
    return render_template("chat.html", nombre=session["usuario"])

@app.route("/logout")
def logout():
    if "usuario_id" in session:
        registrar_log_db(session["usuario_id"], "LOGOUT", "Cerró sesión")
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))

# =========================================================
# RUTAS PARA LOS MÓDULOS ADMIN
# =========================================================

@app.route("/admin/usuarios")
def gestion_usuarios():
    if "usuario_id" not in session or session.get("rol") != "administrador":
        flash("Acceso restringido al administrador.")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    usuarios = []
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.*, td.descripcion as tipo_documento 
                FROM usuarios u 
                JOIN tipos_documento td ON u.tipo_documento_id = td.id 
                ORDER BY u.fecha_creacion DESC
            """)
            usuarios = cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
        finally:
            cursor.close()
            conn.close()
    
    registrar_log_db(session["usuario_id"], "ACCESO_USUARIOS", "Accedió a gestión de usuarios")
    return render_template("admin_usuarios.html", usuarios=usuarios)

@app.route("/admin/estadisticas")
def estadisticas_detalladas():
    if "usuario_id" not in session or session.get("rol") != "administrador":
        flash("Acceso restringido al administrador.")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    stats = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Estadísticas generales
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            stats['total_usuarios'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM mensajes")
            stats['total_mensajes'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM logs_transacciones WHERE DATE(fecha_hora) = CURDATE()")
            stats['actividad_hoy'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM trafico_red WHERE fecha = CURDATE()")
            stats['conexiones_hoy'] = cursor.fetchone()['total']
            
            # Usuarios por rol
            cursor.execute("SELECT rol, COUNT(*) as cantidad FROM usuarios GROUP BY rol")
            stats['usuarios_rol'] = cursor.fetchall()
            
            # Actividad por hora
            cursor.execute("""
                SELECT HOUR(fecha_hora) as hora, COUNT(*) as cantidad 
                FROM logs_transacciones 
                WHERE DATE(fecha_hora) = CURDATE() 
                GROUP BY HOUR(fecha_hora) 
                ORDER BY hora
            """)
            stats['actividad_hora'] = cursor.fetchall()
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
        finally:
            cursor.close()
            conn.close()
    
    registrar_log_db(session["usuario_id"], "ACCESO_ESTADISTICAS", "Accedió a estadísticas detalladas")
    return render_template("admin_estadisticas.html", stats=stats)

@app.route("/admin/xmpp")
def estado_xmpp():
    if "usuario_id" not in session or session.get("rol") != "administrador":
        flash("Acceso restringido al administrador.")
        return redirect(url_for("login"))
    
    # Simular estado XMPP (en un caso real conectarías con tu servidor XMPP)
    estado_xmpp = {
        'conectado': True,
        'usuarios_conectados': 15,
        'mensajes_hoy': 47,
        'servidor': 'xmpp.ucundinamarca.edu.co',
        'version': '1.0.0'
    }
    
    registrar_log_db(session["usuario_id"], "ACCESO_XMPP", "Accedió al estado XMPP")
    return render_template("admin_xmpp.html", estado=estado_xmpp)

@app.route("/admin/config")
def configuracion():
    if "usuario_id" not in session or session.get("rol") != "administrador":
        flash("Acceso restringido al administrador.")
        return redirect(url_for("login"))
    
    registrar_log_db(session["usuario_id"], "ACCESO_CONFIG", "Accedió a configuración")
    return render_template("admin_config.html")

if __name__ == "__main__":
    print("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=5000)