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
    return render_template("admin/admin_dashboard.html", stats=stats, registros=registros)

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
    return render_template("admin/admin_usuarios.html", usuarios=usuarios)

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
    return render_template("admin/admin_estadisticas.html", stats=stats)

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
    return render_template("admin/admin_config.html")
# =========================================================
# APIs PARA EL PANEL ADMIN - CONEXIÓN CON JAVASCRIPT
# =========================================================

@app.route("/admin/api/estadisticas")
def api_estadisticas():
    """API para obtener estadísticas en tiempo real"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    conn = get_db_connection()
    stats = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Total usuarios
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            stats['total_usuarios'] = cursor.fetchone()['total']
            
            # Total mensajes
            cursor.execute("SELECT COUNT(*) as total FROM mensajes")
            stats['total_mensajes'] = cursor.fetchone()['total']
            
            # Actividad hoy
            cursor.execute("SELECT COUNT(*) as hoy FROM logs_transacciones WHERE DATE(fecha_hora) = CURDATE()")
            stats['actividad_hoy'] = cursor.fetchone()['hoy']
            
            # Usuarios activos hoy (usuarios que han tenido actividad hoy)
            cursor.execute("""
                SELECT COUNT(DISTINCT usuario_id) as activos 
                FROM logs_transacciones 
                WHERE DATE(fecha_hora) = CURDATE()
            """)
            stats['usuarios_activos_hoy'] = cursor.fetchone()['activos']
            
        except Exception as e:
            print(f"Error obteniendo estadísticas API: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify(stats)

@app.route("/admin/api/actividad")
def api_actividad():
    """API para datos de actividad para gráficas"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    dias = request.args.get('dias', 7, type=int)
    
    conn = get_db_connection()
    datos = {"labels": [], "data": []}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Obtener actividad de los últimos N días
            cursor.execute("""
                SELECT DATE(fecha_hora) as fecha, COUNT(*) as cantidad
                FROM logs_transacciones 
                WHERE fecha_hora >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(fecha_hora)
                ORDER BY fecha
            """, (dias,))
            
            resultados = cursor.fetchall()
            
            # Crear array con todos los días (incluso los que no tienen actividad)
            for i in range(dias):
                fecha = (datetime.now() - timedelta(days=dias-1-i)).strftime('%Y-%m-%d')
                datos['labels'].append(fecha)
                
                # Buscar si hay datos para esta fecha
                cantidad = 0
                for resultado in resultados:
                    if resultado['fecha'].strftime('%Y-%m-%d') == fecha:
                        cantidad = resultado['cantidad']
                        break
                datos['data'].append(cantidad)
            
        except Exception as e:
            print(f"Error obteniendo datos de actividad: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify(datos)

@app.route("/admin/api/usuarios")
def api_usuarios():
    """API para datos de usuarios (paginados)"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    pagina = request.args.get('pagina', 1, type=int)
    busqueda = request.args.get('busqueda', '')
    por_pagina = 10
    
    conn = get_db_connection()
    usuarios = []
    paginacion = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Construir query base
            query = """
                SELECT u.*, td.descripcion as tipo_documento 
                FROM usuarios u 
                JOIN tipos_documento td ON u.tipo_documento_id = td.id 
            """
            params = []
            
            # Agregar búsqueda si existe
            if busqueda:
                query += " WHERE u.nombre LIKE %s OR u.correo LIKE %s OR u.documento LIKE %s"
                params.extend([f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"])
            
            # Ordenar
            query += " ORDER BY u.fecha_creacion DESC"
            
            # Contar total
            count_query = "SELECT COUNT(*) as total FROM usuarios u"
            if busqueda:
                count_query += " WHERE u.nombre LIKE %s OR u.correo LIKE %s OR u.documento LIKE %s"
            
            cursor.execute(count_query, params)
            total_usuarios = cursor.fetchone()['total']
            total_paginas = (total_usuarios + por_pagina - 1) // por_pagina
            
            # Obtener usuarios paginados
            query += " LIMIT %s OFFSET %s"
            offset = (pagina - 1) * por_pagina
            params.extend([por_pagina, offset])
            
            cursor.execute(query, params)
            usuarios = cursor.fetchall()
            
            paginacion = {
                'pagina_actual': pagina,
                'total_paginas': total_paginas,
                'total_usuarios': total_usuarios,
                'por_pagina': por_pagina
            }
            
        except Exception as e:
            print(f"Error obteniendo usuarios API: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({
        'usuarios': usuarios,
        'paginacion': paginacion
    })

@app.route("/admin/api/logs")
def api_logs():
    """API para logs de actividad (paginados)"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    pagina = request.args.get('pagina', 1, type=int)
    usuario = request.args.get('usuario', '')
    accion = request.args.get('accion', '')
    por_pagina = 20
    
    conn = get_db_connection()
    logs = []
    paginacion = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Construir query base
            query = """
                SELECT l.*, u.nombre as usuario_nombre 
                FROM logs_transacciones l 
                LEFT JOIN usuarios u ON l.usuario_id = u.id 
            """
            params = []
            
            # Agregar filtros
            where_conditions = []
            if usuario:
                where_conditions.append("u.nombre LIKE %s")
                params.append(f"%{usuario}%")
            if accion:
                where_conditions.append("l.accion LIKE %s")
                params.append(f"%{accion}%")
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            
            # Ordenar
            query += " ORDER BY l.fecha_hora DESC"
            
            # Contar total
            count_query = "SELECT COUNT(*) as total FROM logs_transacciones l LEFT JOIN usuarios u ON l.usuario_id = u.id"
            if where_conditions:
                count_query += " WHERE " + " AND ".join(where_conditions)
            
            cursor.execute(count_query, params)
            total_logs = cursor.fetchone()['total']
            total_paginas = (total_logs + por_pagina - 1) // por_pagina
            
            # Obtener logs paginados
            query += " LIMIT %s OFFSET %s"
            offset = (pagina - 1) * por_pagina
            params.extend([por_pagina, offset])
            
            cursor.execute(query, params)
            logs = cursor.fetchall()
            
            # Convertir datetime a string para JSON
            for log in logs:
                if log['fecha_hora']:
                    log['fecha_hora'] = log['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')
            
            paginacion = {
                'pagina_actual': pagina,
                'total_paginas': total_paginas,
                'total_logs': total_logs,
                'por_pagina': por_pagina
            }
            
        except Exception as e:
            print(f"Error obteniendo logs API: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({
        'logs': logs,
        'paginacion': paginacion
    })

@app.route("/admin/api/usuarios/<int:user_id>/estado", methods=["PUT"])
def api_cambiar_estado_usuario(user_id):
    """API para activar/desactivar usuarios"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.get_json()
    if not data or 'activo' not in data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    nuevo_estado = data['activo']
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # En tu BD actual no tienes columna 'activo', así que simulamos
            # Si quieres agregar esta funcionalidad, necesitarías agregar la columna
            # Por ahora solo registramos la acción en logs
            cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (user_id,))
            usuario = cursor.fetchone()
            
            if usuario:
                accion = "ACTIVADO" if nuevo_estado else "DESACTIVADO"
                registrar_log_db(
                    session["usuario_id"], 
                    f"USUARIO_{accion}", 
                    f"Usuario ID {user_id} ({usuario[0]}) {accion.lower()}"
                )
                
                return jsonify({
                    "success": True, 
                    "message": f"Usuario {accion.lower()} correctamente"
                })
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
                
        except Exception as e:
            print(f"Error cambiando estado de usuario: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Error de conexión"}), 500

# =========================================================
# FUNCIONES AUXILIARES PARA LAS APIS
# =========================================================

def obtener_estadisticas_detalladas():
    """Función auxiliar para estadísticas detalladas"""
    conn = get_db_connection()
    stats = {}
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Tus consultas existentes...
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            stats['total_usuarios'] = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM mensajes")
            stats['total_mensajes'] = cursor.fetchone()['total']
            
            # ... resto de tus consultas
            
        except Exception as e:
            print(f"Error obteniendo estadísticas detalladas: {e}")
        finally:
            cursor.close()
            conn.close()
    
    return stats
# =========================================================
# GESTIÓN COMPLETA DE USUARIOS - APIS
# =========================================================

@app.route("/admin/api/usuarios/<int:user_id>", methods=['GET'])
def api_obtener_usuario(user_id):
    """API para obtener datos de un usuario específico"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.*, td.descripcion as tipo_documento 
                FROM usuarios u 
                JOIN tipos_documento td ON u.tipo_documento_id = td.id 
                WHERE u.id = %s
            """, (user_id,))
            
            usuario = cursor.fetchone()
            if usuario:
                return jsonify({"usuario": usuario})
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
                
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Error de conexión"}), 500

@app.route("/admin/api/usuarios/<int:user_id>", methods=['PUT'])
def api_actualizar_usuario(user_id):
    """API para actualizar datos de usuario"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Construir query dinámicamente basado en los campos proporcionados
            campos = []
            valores = []
            
            campos_permitidos = ['nombre', 'correo', 'telefono', 'rol', 'tipo_documento_id', 'documento']
            
            for campo in campos_permitidos:
                if campo in data:
                    campos.append(f"{campo} = %s")
                    valores.append(data[campo])
            
            if not campos:
                return jsonify({"error": "No hay campos para actualizar"}), 400
            
            valores.append(user_id)
            query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = %s"
            
            cursor.execute(query, valores)
            conn.commit()
            
            # Registrar la acción
            registrar_log_db(
                session["usuario_id"], 
                "USUARIO_ACTUALIZADO", 
                f"Actualizó datos del usuario ID {user_id}"
            )
            
            return jsonify({"success": True, "message": "Usuario actualizado correctamente"})
            
        except mysql.connector.Error as err:
            print(f"Error actualizando usuario: {err}")
            return jsonify({"error": f"Error en base de datos: {err}"}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Error de conexión"}), 500

@app.route("/admin/api/usuarios/<int:user_id>", methods=['DELETE'])
def api_eliminar_usuario(user_id):
    """API para eliminar usuario"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    # No permitir eliminar el propio usuario
    if user_id == session["usuario_id"]:
        return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Primero obtener info del usuario para el log
            cursor.execute("SELECT nombre, rol FROM usuarios WHERE id = %s", (user_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # No permitir eliminar administradores
            if usuario[1] == 'administrador':
                return jsonify({"error": "No se pueden eliminar usuarios administradores"}), 400
            
            # Eliminar usuario
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            conn.commit()
            
            # Registrar la acción
            registrar_log_db(
                session["usuario_id"], 
                "USUARIO_ELIMINADO", 
                f"Eliminó al usuario: {usuario[0]} (ID: {user_id})"
            )
            
            return jsonify({"success": True, "message": "Usuario eliminado correctamente"})
            
        except mysql.connector.Error as err:
            print(f"Error eliminando usuario: {err}")
            return jsonify({"error": f"Error en base de datos: {err}"}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Error de conexión"}), 500

@app.route("/admin/api/usuarios/<int:user_id>/contrasena", methods=['PUT'])
def api_resetear_contrasena(user_id):
    """API para resetear contraseña de usuario"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.get_json()
    if not data or 'nueva_contrasena' not in data:
        return jsonify({"error": "Contraseña requerida"}), 400
    
    nueva_contrasena = data['nueva_contrasena']
    
    if len(nueva_contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Verificar que el usuario existe
            cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (user_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({"error": "Usuario no encontrado"}), 404
            
            # Actualizar contraseña
            contrasena_hash = generate_password_hash(nueva_contrasena)
            cursor.execute(
                "UPDATE usuarios SET contrasena = %s WHERE id = %s",
                (contrasena_hash, user_id)
            )
            conn.commit()
            
            # Registrar la acción
            registrar_log_db(
                session["usuario_id"], 
                "CONTRASENA_RESETEADA", 
                f"Reseteó contraseña del usuario: {usuario[0]}"
            )
            
            return jsonify({"success": True, "message": "Contraseña actualizada correctamente"})
            
        except mysql.connector.Error as err:
            print(f"Error reseteando contraseña: {err}")
            return jsonify({"error": f"Error en base de datos: {err}"}), 500
        finally:
            cursor.close()
            conn.close()
    
    return jsonify({"error": "Error de conexión"}), 500

if __name__ == "__main__":
    print("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0', port=5000)
