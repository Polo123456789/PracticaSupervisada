import hash
import logging
from flask import Flask, render_template, session, redirect, request, url_for\
    , flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
app.secret_key = "NoDeveriasVerEsto,PeroNoEstamosEnProduccionAsiQueNoImporta"
db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
# Ejemplo de un log
# app.logger.info(type(admin))
# app.logger.info(admin)


"""---- Base de datos -----"""
class Grado(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    Grado             = db.Column(db.String(30), unique=True, nullable=False)
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
    return render_template("index.html")

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
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin" and session["type"] != "Profe":
        return redirect("/404")

    return "Crear tareas"

@app.route("/calificar", methods=["GET", "POST"])
def calificar():
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin" and session["type"] != "Profe":
        return redirect("/404")

    return "Calificar"

# Administradores
@app.route("/gestionDeUsuarios", methods=["GET", "POST"])
def gestionUsuarios():
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    return render_template("gestionU.html", type=session["type"])

@app.route("/gestionDeUsuarios/actualizarA/<int:id>", methods=["GET", "POST"])
def gestionUsuariosActualizarA(id):
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    if request.method == "POST":
        if id != 0:
            alumno = Alumno.query.get(id)
            nombreUsuario            = request.form.get("nombreUsuario")
            contrasena               = request.form.get("contrasena")
            nombre                   = request.form.get("nombre")
            correoElectronico        = request.form.get("correoElectronico")
            telefonoPadres           = request.form.get("telefonoPadres")
            idGrado                  = request.form.get("idGrado")
            alumno.NombreUsuario     = nombreUsuario
            if contrasena != "":
                alumno.Contrasena        = hash.hash_passwd(contrasena)
            alumno.Nombre            = nombre
            alumno.CorreoElectronico = correoElectronico
            alumno.TelefonoPadres    = telefonoPadres
            alumno.IdGrado           = idGrado
            db.session.commit()
        return redirect("/gestionDeUsuarios/actualizarA/0")

    else:
        if id == 0:
            alumnos = Alumno.query.all()
            return render_template("enlistarA.html", type=session["type"], alumnos=alumnos)
        else:
            alumno = Alumno.query.get(id)
            return render_template("modificarA.html", type=session["type"], alumno=alumno)


@app.route("/gestionDeUsuarios/actualizarM/<int:id>", methods=["GET", "POST"])
def gestionUsuariosActualizarM(id):
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    if request.method == "POST":
        if id != 0:
            nMaestro = Maestro.query.get(id)
            contra = request.form.get("contrasena")
            if contra != "":
                nMaestro.Contrasena = hash.hash_passwd(contra)
            nMaestro.NombreUsuario     = request.form.get("nombreUsuario")
            nMaestro.Nombre            = request.form.get("nombre")
            nMaestro.CorreoElectronico = request.form.get("correoElectronico")
            nMaestro.Admin             = request.form.get("admin") == "on"
            db.session.commit()

        return redirect("/gestionDeUsuarios/actualizarM/0")

    else:
        if id == 0:
            maestros = Maestro.query.all()
            return render_template("enlistarM.html", type=session["type"], maestros=maestros)
        else:
            maestro = Maestro.query.get(id)
            return render_template("modificarM.html", type=session["type"], maestro=maestro)

@app.route("/gestionDeUsuarios/actualizarG/<int:id>", methods=["GET", "POST"])
def gestionUsuariosActualizarG(id):
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")
    if request.method == "POST":
        if id != 0:
            nGrado = Grado.query.get(id)
            nGrado.Grado = request.form.get("grado")
            db.session.commit()
        return redirect("/gestionDeUsuarios/actualizarG/0")
    else:
        if id == 0:
            grados = Grado.query.all()
            return render_template("enlistarG.html", type=session["type"], grados=grados)
        else:
            grado = Grado.query.get(id)
            return render_template("modificarG.html", type=session["type"], grado=grado)

@app.route("/gestionDeUsuarios/anadirA", methods=["GET", "POST"])
def gestionUsuariosAnadirA():
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    if request.method == "POST":
        nombreUsuario = request.form.get("nombreUsuario")
        if Alumno.query.filter_by(NombreUsuario=nombreUsuario).first() == None:
            contrasena        = request.form.get("contrasena")
            nombre            = request.form.get("nombre")
            correoElectronico = request.form.get("correoElectronico")
            telefonoPadres    = request.form.get("telefonoPadres")
            idGrado           = request.form.get("idGrado")
            alumno = Alumno()
            alumno.NombreUsuario     = nombreUsuario
            alumno.Contrasena        = hash.hash_passwd(contrasena)
            alumno.Nombre            = nombre
            alumno.CorreoElectronico = correoElectronico
            alumno.TelefonoPadres    = telefonoPadres
            alumno.IdGrado           = idGrado
            db.session.add(alumno)
            db.session.commit()
            return redirect("/gestionDeUsuarios")
        else:
            flash(f"El usuario {nombreUsuario} ya existe")
            return redirect("/gestionDeUsuarios/anadirA")

    else:
        grados = Grado.query.all()
        return render_template("anadirA.html", type=session["type"], grados=grados)

@app.route("/gestionDeUsuarios/anadirM", methods=["GET", "POST"])
def gestionUsuariosAnadirM():
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    if request.method == "POST":
        nombreUsuario = request.form.get("nombreUsuario")
        if Maestro.query.filter_by(NombreUsuario=nombreUsuario).first() == None:
            contra  =  request.form.get("contrasena")
            nombre  =  request.form.get("nombre")
            correoE =  request.form.get("correoElectronico")
            admin   =  request.form.get("admin")
            maestro = Maestro()
            maestro.NombreUsuario     = nombreUsuario
            maestro.Contrasena        = hash.hash_passwd(contra)
            maestro.Nombre            = nombre
            maestro.CorreoElectronico = correoE
            maestro.Admin             = (admin=="on")
            db.session.add(maestro)
            db.session.commit()
        else:
            flash(f"El nombre de ususario '{nombreUsuario}' ya esta ocupado")

        return redirect("/gestionDeUsuarios")
    else:
        return render_template("anadirM.html", type=session["type"])

@app.route("/gestionDeUsuarios/anadirG", methods=["GET", "POST"])
def gestionUsuariosAnadirG():
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    if request.method == "POST":
        nombre = request.form.get('grado')
        grado = Grado(Grado=nombre)
        check = Grado.query.filter_by(Grado=nombre).first()
        if check is None:
            db.session.add(grado)
            db.session.commit()
        else:
            flash(f'Intento ingresar un dato que ya existe. "{check.Grado}" tiene el Id:"{check.Id}"')
        return redirect("/gestionDeUsuarios")
    else:
        return render_template("anadirG.html", type=session["type"])

@app.route("/gestionDeUsuarios/anadirC", methods=["GET", "POST"])
def gestionUsuariosAnadirC():
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    if request.method == "POST":
        return redirect("/gestionDeUsuarios")
    else:
        grados = Grado.query.all()
        return render_template("anadirC.html", type=session["type"], grados=grados)

@app.route("/gestionDeUsuarios/Eliminar/<tipo>/<int:id>", methods=["GET", "POST"])
def eliminar(tipo, id):
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    return "Eliminar"

@app.route("/mantenimiento", methods=["GET", "POST"])
def mantenimiento():
    if not "type" in session:
        return redirect("/404")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/404")

    return "Mantenimiento"


@app.route("/404")
def noPage():
    return "Que haces para llegar aca? Esta pagina no existe"

if __name__ == "__main__":
    app.run()
