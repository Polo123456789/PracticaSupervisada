# Classroom
# Copyright © 2020  Pablo Sanchez
#
# Este programa es software libre: usted puede redistribuirlo y/o modificarlo
# conforme a los términos de la Licencia Pública General de GNU publicada por
# la Fundación para el Software Libre, ya sea la versión 3 de esta Licencia
# o (a su elección) cualquier versión posterior.
#
# Este programa se distribuye con el deseo de que le resulte útil, pero SIN
# GARANTÍAS DE NINGÚN TIPO; ni siquiera con las garantías implícitas de
# COMERCIABILIDAD o APTITUD PARA UN PROPÓSITO DETERMINADO.  Para más información,
# consulte la Licencia Pública General de GNU.
#
# Para leer la licencia, ingrese en <http://www.gnu.org/licenses/>.

import hash
import os
import logging
from flask import Flask, render_template, session, redirect, request, url_for\
    , flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = "userFiles/"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'zip', 'gz', 'ppt'}

app.secret_key = "NoDeveriasVerEsto,PeroNoEstamosEnProduccionAsiQueNoImporta"

db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
# Ejemplo de un log
# app.logger.info(type(admin))
# app.logger.info(admin)

app.logger.info("Classroom")
app.logger.info("Copyright © 2020  Pablo Sanchez")

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
    entregas          = db.relationship("Entregas", backref="tareasEntregadasPorAlumno")

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
    IdClase           = db.Column(db.Integer, db.ForeignKey('clases.Id'), nullable=False)
    Titulo            = db.Column(db.String(30), nullable=False)
    Descripcion       = db.Column(db.String(120), nullable=False)
    PathAdjuntos      = db.Column(db.String(50), nullable=False)
    entregas          = db.relationship("Entregas", backref="tareasEntregadas")

class Entregas(db.Model):
    Id                = db.Column(db.Integer, primary_key=True)
    IdTarea           = db.Column(db.Integer, db.ForeignKey('tareas.Id'), nullable=False)
    IdAlumno          = db.Column(db.Integer, db.ForeignKey('alumno.Id'), nullable=False)
    PathAdjuntos      = db.Column(db.String(50), nullable=False)
    Respuesta         = db.Column(db.String(300), nullable=False)
    Calificado        = db.Column(db.Boolean, nullable=False)
    Nota              = db.Column(db.Integer, nullable=False)

# Utilidades
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/file/<filename>")
def sendFile(filename):
    filename.replace('_', ' ')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


""" ---------------------- Rutas de la pagina web ---------------------- """
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
            session["id"] = original.Id
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
            session["id"] = original.Id
            if original.Admin:
                session["type"] = "Admin"
                return redirect("/gestionDeUsuarios")
            else:
                session["type"] = "Profe"
                return redirect("/crear_tareas")
        else:
            flash("Error al iniciar sesion")
            return redirect("/login/maestro")

    else:
        return render_template("login.html", quien="maestro")

# ------------ Alumnos ------------
@app.route("/tareas")
def tareas():
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Alumno":
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")

    idAlumno = session["id"]
    entregasPendientes = Entregas.query.filter_by(IdAlumno=idAlumno, Respuesta="SinRespuesta").all()
    tareas = []
    for entrega in entregasPendientes:
        t = Tareas.query.get(entrega.IdTarea)
        tareas.append(t)
    return render_template("listaTareas.html", type=session["type"], tareas=tareas)

@app.route("/tareas/<int:idTarea>", methods=["POST", "GET"])
def ResolverTareas(idTarea):
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Alumno":
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")

    if request.method == "POST":
        entrega = Entregas.query.get(idTarea)
        if entrega is None:
            flash("No hemos podido identificar la tarea")
            return redirect("/tareas")
        if entrega.IdAlumno != session["id"]:
            flash("No puede entregar tareas que no le corresponden")
            return redirect("/tareas")
        archivo = request.files["file"]
        if archivo.filename:
            if allowed_file(archivo.filename):
               filename = secure_filename(archivo.filename)
               archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
               flash("Error con el archivo adjunto.\
               Le recordamos que solo pueden tener las siguientes extencionses:\
               'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'zip', 'gz', 'ppt'.")
               return redirect("/tareas")
        else:
            flash("Tarea sin adjuntos")
            filename = "SinArchivo"

        entrega.Respuesta = request.form.get("respuesta")
        entrega.PathAdjuntos = filename
        db.session.commit()
        return redirect("/tareas")
    else:
        tarea = Tareas.query.get(idTarea)
        return render_template("realizarTarea.html", tarea=tarea, type=session["type"])


class VerNotas:
    def __init__(self, clase, tarea, nota):
        self.Clase = clase
        self.Tarea = tarea
        self.Nota = nota

@app.route("/notas")
def notas():
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Alumno":
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")

    notas = []
    entregas = Entregas.query.filter_by(Calificado=True)
    for entrega in entregas:
        app.logger.info(entrega)
        tarea = Tareas.query.get(entrega.IdTarea)
        clase = Clases.query.get(tarea.IdClase)
        notas.append(
            VerNotas(clase.Nombre, tarea.Titulo, entrega.Nota)
        )
    return render_template("verNotas.html", type=session["type"], notas=notas)

# ------------ Maestros ------------
@app.route("/crear_tareas")
def crearTareas():
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin" and session["type"] != "Profe":
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if not "id" in session:
        flash("Ha ocurrido un error, y no hemos podido idedentificar su id\
        , porfavor inicie sesion otra vez")
        return redirect("/login/maestro")

    clases = Clases.query.filter_by(IdMaestro=session["id"])
    return render_template("listaClases.html", clases=clases, type=session['type'])

@app.route("/crear_tareas/<int:idClase>", methods=["GET", "POST"])
def subirTareas(idClase):
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin" and session["type"] != "Profe":
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if not "id" in session:
        flash("Ha ocurrido un error, y no hemos podido idedentificar su id\
        , porfavor inicie sesion otra vez")
        return redirect("/login/maestro")

    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        archivo = request.files['file']
        if archivo.filename:
            if allowed_file(archivo.filename):
               filename = secure_filename(archivo.filename)
               archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
               flash("Error con el archivo adjunto.\
               Le recordamos que solo pueden tener las siguientes extencionses:\
               'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'zip', 'gz', 'ppt'.")
               return redirect("/crear_tareas")
        else:
            flash("Tarea sin adjuntos")
            filename = "SinArchivo"

        # Creamos la tarea
        tarea = Tareas()
        tarea.IdClase           = idClase
        tarea.Titulo            = titulo
        tarea.Descripcion       = descripcion
        tarea.PathAdjuntos      = filename
        db.session.add(tarea)
        db.session.commit()

        # Y la asignamos a los alumnos del grado
        idGrado = Clases.query.get(idClase).IdGrado
        alumnos = Alumno.query.filter_by(IdGrado=idGrado).all()
        for alumno in alumnos:
            entrega = Entregas()
            entrega.IdTarea           = tarea.Id
            entrega.IdAlumno          = alumno.Id
            entrega.PathAdjuntos      = "SinAdjuntos"
            entrega.Respuesta         = "SinRespuesta"
            entrega.Calificado        = False
            entrega.Nota              = 0
            db.session.add(entrega)
        db.session.commit()

        return redirect("/crear_tareas")
    else:
        return render_template("anadirT.html", id=idClase, type=session["type"])

class EntregaPendiente:
    def __init__(self, alumno, tarea, clase, IdEntrega):
        self.alumno = alumno
        self.tarea = tarea
        self.clase = clase
        self.IdEntrega = IdEntrega

@app.route("/calificar")
def tareasCalificar():
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin" and session["type"] != "Profe":
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if not "id" in session:
        flash("Ha ocurrido un error, y no hemos podido idedentificar su id\
        , porfavor inicie sesion otra vez")
        return redirect("/login/maestro")

    entregasPorCalificar = []
    clasesDelMaestro = Clases.query.filter_by(IdMaestro=session["id"]).all()
    for clase in clasesDelMaestro:
        tareas = Tareas.query.filter_by(IdClase=clase.Id).all()
        for tarea in tareas:
            entregasPendientes = Entregas.query.filter(
                Entregas.Respuesta!="SinRespuesta",
                Entregas.Calificado==False,
                Entregas.IdTarea==tarea.Id
            ).all()
            for entrega in entregasPendientes:
                entregasPorCalificar.append(
                    EntregaPendiente(
                        Alumno.query.get(entrega.IdAlumno).Nombre,
                        Tareas.query.get(entrega.IdTarea).Titulo,
                        clase.Nombre,
                        entrega.Id
                    )
                )

    return render_template("tareasCalificar.html", entregas=entregasPorCalificar, type=session["type"])

@app.route("/calificar/<int:idEntrega>", methods=["GET", "POST"])
def calificarTareas(idEntrega):
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin" and session["type"] != "Profe":
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if request.method == "POST":
        nota = request.form.get("nota")
        entrega = Entregas.query.get(idEntrega)
        if entrega:
            entrega.Nota = nota
            entrega.Calificado = True
            db.session.commit()
        else:
            flash("Id de tarea incorrecto")
        return redirect("/calificar")
    else:
        entrega = Entregas.query.get(idEntrega)
        tarea = Tareas.query.get(entrega.IdTarea)
        return render_template("calificarTarea.html", entrega=entrega, tarea=tarea, type=session["type"])
    return f"Calificar {idTarea}"

# ------------ Administradores ------------
@app.route("/gestionDeUsuarios", methods=["GET", "POST"])
def gestionUsuarios():
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")

    return render_template("gestionU.html", type=session["type"])

@app.route("/gestionDeUsuarios/actualizarA/<int:id>", methods=["GET", "POST"])
def gestionUsuariosActualizarA(id):
    if not "type" in session:
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")

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
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")

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
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")
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
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")

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
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")

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
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")

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
        flash("Cuidado mano, que tengo tu ip")
        return redirect("/")
    if session["type"] != "Admin":
        flash("Cuidado, que tengo tu IP")
        return redirect("/")

    if request.method == "POST":
        nombre = request.form.get("Nombre")
        idGrado = request.form.get("IdGrado")
        idMaestro = request.form.get("IdMaestro")
        if Clases.query.filter_by(Nombre=nombre).first() == None:
            clase = Clases()
            clase.Nombre    = nombre 
            clase.IdGrado   = idGrado
            clase.IdMaestro = idMaestro
            db.session.add(clase)
            db.session.commit()

        else:
            flash(f"La clase con el nombre {nombre} ya existe")
        return redirect("/gestionDeUsuarios")
    else:
        grados = Grado.query.all()
        maestros = Maestro.query.all()
        return render_template("anadirC.html", type=session["type"], grados=grados, maestros=maestros)

@app.errorhandler(404)
def sinPagina(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def laRegaste(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run()
