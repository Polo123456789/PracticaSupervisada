import hash
from flask import Flask, render_template, session, redirect, request, url_for\
    , flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
app.secret_key = "NoDeveriasVerEsto,PeroNoEstamosEnProduccionAsiQueNoImporta"
db = SQLAlchemy(app)

"""---- Base de datos -----"""
class Grado(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    Grado             = db.Column(db.String(30), nullable=False)
    alumnos           = db.relationship("Alumno", backref="grado")
    clases            = db.relationship("Clases", backref="clasesPorGrado")

class Alumno(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    NombreUsuario     = db.Column(db.String(30), unique=True, nullable=False)
    Contrasena        = db.Column(db.String(32), nullable=False)
    Nombre            = db.Column(db.String(30), nullable=False)
    CorreoElectronico = db.Column(db.String(30), nullable=False)
    TelefonoPadres    = db.Column(db.String(10), nullable=False)
    IdGrado           = db.Column(db.Integer, db.ForeignKey('grado.Id'), nullable=False)
    tareas            = db.relationship("Tareas", backref="tareasPorAlumno")

class Maestro(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    NombreUsuario     = db.Column(db.String(30), unique=True, nullable=False)
    Contrasena        = db.Column(db.String(32), nullable=False)
    Nombre            = db.Column(db.String(30), nullable=False)
    CorreoElectronico = db.Column(db.String(30), nullable=False)
    Admin             = db.Column(db.Boolean, nullable=False)
    clases            = db.relationship("Clases", backref="clasesPorMaestro")

class Clases(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    Nombre            = db.Column(db.String(30), nullable=False)
    IdGrado           = db.Column(db.Integer, db.ForeignKey('grado.Id'), nullable=False)
    IdMaestro         = db.Column(db.Integer, db.ForeignKey('maestro.Id'), nullable=False)
    tareas            = db.relationship("Tareas", backref="tareasPorClase")

class Tareas(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    IdAlumno          = db.Column(db.Integer, db.ForeignKey('alumno.Id'), nullable=False)
    IdClase           = db.Column(db.Integer, db.ForeignKey('clases.Id'), nullable=False)
    Titulo            = db.Column(db.String(30), nullable=False)
    Descripcion       = db.Column(db.String(120), nullable=False)
    PathAdjuntos      = db.Column(db.String(50), nullable=False)
    Calificado        = db.Column(db.Boolean, nullable=False)
    Nota              = db.Column(db.Float, nullable=True)
    HoraLimite        = db.Column(db.DateTime, nullable=False)
    Entregado         = db.Column(db.Boolean, nullable=False)
    PathRespuesta     = db.Column(db.String(50), nullable=True)
    HoraEntrega       = db.Column(db.DateTime, nullable=False)

"""---- Rutas de la pagina web -----"""
# Login y home page
@app.route("/")
def index():
    return render_template("homePage.html")

@app.route("/login")
def loginVacio():
    return redirect("/")

@app.route("/login/alumno", methods=["GET", "POST"])
def loginAlumno():
    if request.method == "POST":
        user = request.form.get("nombre")
        passwd = request.form.get("pwd")
        original = Alumno.query.filter_by(NombreUsuario=user).first()
        if not original:
            flash("Ese nombre de usuario no existe")
            return redirect("/login/alumno")
        if hash.check_passwd(passwd, original.Contrasena):
            session["type"] = "Alumno"
            return redirect("/tareas")
        else:
            flash("Error al iniciar sesion")
            return redirect("/login/alumno")

    else:
        return render_template("login.html", quien="alumno")

@app.route("/login/maestro", methods=["GET", "POST"])
def loginMaestro():
    if request.method == "POST":
        user = request.form.get("nombre")
        passwd = request.form.get("pwd")
        original = Maestro.query.filter_by(NombreUsuario=user).first()
        if not original:
            flash("Ese nombre de usuario no existe")
            return redirect("/login/maestro")
        if hash.check_passwd(passwd, original.Contrasena):
            if original.Admin:
                session["type"] = "Admin"
                return redirect("/gestionDeUsuarios")
            else:
                session["type"] = "Profe"
                return redirect("calificar")
        else:
            flash("Error al iniciar sesion")
            return redirect("/login/maestro")

    else:
        return render_template("login.html", quien="maestro")

# Alumnos
@app.route("/tareas", methods=["GET", "POST"])
def tareas():
    if "type" in session:
        if session["type"] == "Alumno":
            return "Ver mis tareas"

    return redirect("/404")

@app.route("/notas")
def notas():
    if "type" in session:
        if session["type"] == "Alumno":
            return "Ver mis notas"

    return redirect("/404")

# Maestros
@app.route("/crear_tareas", methods=["GET", "POST"])
def crearTareas():
    if "type" in session:
        if session["type"] == "Profe":
            return "Crear tareas"

    return redirect("/404")

@app.route("/calificar", methods=["GET", "POST"])
def calificar():
    if "type" in session:
        if session["type"] == "Profe":
            return "Calificar Tareas"

    return redirect("/404")


# Administradores
@app.route("/gestionDeUsuarios", methods=["GET", "POST"])
def gestionUsuarios():
    if "type" in session:
        if session["type"] == "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/gestionDeUsuarios/actualizarA/<int:id>", methods=["GET", "POST"])
def gestionUsuariosActualizarA(id):
    if "type" in session:
        if session["type"] == "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/gestionDeUsuarios/actualizarM/<int:id>", methods=["GET", "POST"])
def gestionUsuariosActualizarM(id):
    if "type" in session:
        if session["type"] == "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/gestionDeUsuarios/actualizarG/<int:id>", methods=["GET", "POST"])
def gestionUsuariosActualizarG(id):
    if "type" in session:
        if session["type"] == "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/gestionDeUsuarios/anadirA", methods=["GET", "POST"])
def gestionUsuariosAnadirA():
    if "type" in session:
        if session["type"] == "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/gestionDeUsuarios/anadirM", methods=["GET", "POST"])
def gestionUsuariosAnadirM():
    if "type" in session:
        if session["type"] == "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/gestionDeUsuarios/anadirG", methods=["GET", "POST"])
def gestionUsuariosAnadirG():
    if "type" in session:
        if session["type"] == "Admin":
            return "Gestion de usuarios"

    return redirect("/404")

@app.route("/gestionDeUsuarios/Eliminar/<tipo>/<int:id>", methods=["GET", "POST"])
def eliminar(tipo, id):
    if "type" in session:
        if session["type"] == "Admin":
            return "Eliminar"

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
