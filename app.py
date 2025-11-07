from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------------------------------------------------
# MANEJO DE ERRORES
# ---------------------------------------------------------
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("error.html", mensaje="La página que buscas no existe."), 404

@app.errorhandler(500)
def error_servidor(e):
    return render_template("error.html", mensaje="Error interno del servidor."), 500


# ---------------------------------------------------------
# USUARIOS DE PRUEBA — NO SE TOCAN ✅
# ---------------------------------------------------------
usuarios = {
    "jennifer": "1234",
    "leo": "abcd"
}


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]

        if usuario in usuarios and usuarios[usuario] == contrasena:
            return redirect(url_for("dashboard", nombre=usuario))
        else:
            error = "Usuario o contraseña incorrectos."

    return render_template("login.html", error=error)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    nombre = request.args.get("nombre", "Usuario")
    return render_template("dashboard.html", nombre=nombre)


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@app.route("/logout")
def logout():
    return redirect(url_for("login"))


# ---------------------------------------------------------
# REGISTRO
# (Esto agrega usuarios al diccionario, pero NO toca jennifer ni leo)
# ---------------------------------------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None

    if request.method == "POST":
        usuario = request.form.get("documento")   # por ahora se guardará como string
        contrasena = request.form.get("contrasena")
        confirmar = request.form.get("confirmar")

        if contrasena != confirmar:
            error = "Las contraseñas no coinciden."
        elif usuario in usuarios:
            error = "El usuario ya existe."
        else:
            usuarios[usuario] = contrasena
            return redirect(url_for("login"))

    return render_template("registro.html", error=error)


# ---------------------------------------------------------
# RECUPERAR CONTRASEÑA (SIMULADO)
# ---------------------------------------------------------
@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    mensaje = None

    if request.method == "POST":
        correo = request.form.get("correo")
        mensaje = "Si el correo está registrado, se enviarán instrucciones."

    return render_template("recuperar_contrasena.html", mensaje=mensaje)


# ---------------------------------------------------------
# CHAT COMPLETO
# ---------------------------------------------------------
@app.route("/chat")
def chat():
    return render_template("chat.html")


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
