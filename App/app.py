from flask import Flask, render_template, session, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
app.secret_key = "NoDeveriasVerEsto,PeroNoEstamosEnProduccionAsiQueNoImporta"
db = SQLAlchemy(app)

"""---- Base de datos -----"""
class Grado(db.Model):
    Id      = db.Column(db.Integer, primary_key=True)
    Grado   = db.Column(db.String(30), nullable=False)
    alumnos = db.relationship("Alumno", backref="grado")

class Alumno(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    NombreUsuario     = db.Column(db.String(30), unique=True, nullable=False)
    Contrasena        = db.Column(db.String(64), nullable=False)
    Nombre            = db.Column(db.String(30), nullable=False)
    CorreoElectronico = db.Column(db.String(30), nullable=False)
    TelefonoPadres    = db.Column(db.String(10), nullable=False)
    IdGrado           = db.Column(db.Integer, db.ForeignKey('grado.Id'), nullable=False)

class Maestro(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    NombreUsuario     = db.Column(db.String(30), unique=True, nullable=False)
    Contrasena        = db.Column(db.String(64), nullable=False)
    Nombre            = db.Column(db.String(30), nullable=False)
    CorreoElectronico = db.Column(db.String(30), nullable=False)
    Admin             = db.Column(db.Boolean, nullable=False)

"""---- Rutas de la pagina web -----"""
@app.route("/", methods=["GET", "POST"])
def index():
    if not "type" in session:
        session["type"] = ""

    return render_template("base.html", type=session["type"])

@app.route("/tareas", methods=["GET", "POST"])
def tareas():
    return "Tareas"

@app.route("/notas")
def notas():
    return "Notas"

@app.route("/crear_tareas", methods=["GET", "POST"])
def crearTareas():
    return "Crear tareas"

@app.route("/calificar", methods=["GET", "POST"])
def calificar():
    return "calificar"

@app.route("/gestionDeUsuarios", methods=["GET", "POST"])
def gestionUsuarios():
    if "type" in session:
        if session["type"] != "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/mantenimiento", methods=["GET", "POST"])
def mantenimiento():
    if "type" in session:
        if session["type"] == "Admin":
            return "Mantenimiento"
    return redirect("/404")

@app.route("/404")
def noPage():
    return "Que haces para llegar aca? Esta pagina no existe"

if __name__ == "__main__":
    app.run()
