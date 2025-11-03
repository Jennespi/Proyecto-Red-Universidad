from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("error.html", mensaje="La página que buscas no existe."), 404

@app.errorhandler(500)
def error_servidor(e):
    return render_template("error.html", mensaje="Error interno del servidor."), 500

# --- USUARIOS DE PRUEBA (sin base de datos) ---
usuarios = {
    "jennifer": "1234",
    "leo": "abcd"
}

# --- RUTA DE LOGIN ---
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

# --- RUTA DE DASHBOARD ---
@app.route("/dashboard")
def dashboard():
    nombre = request.args.get("nombre", "Usuario")
    return render_template("dashboard.html", nombre=nombre)


# --- MAIN ---
if __name__ == "__main__":
    app.run(debug=True)

