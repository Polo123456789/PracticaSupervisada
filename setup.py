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

from app import db, Maestro
from hash import hash_passwd

def main():
    db.create_all()
    admin = Maestro()
    admin.NombreUsuario     = "root"
    admin.Contrasena        = hash_passwd("toor")
    admin.Nombre            = "Admin"
    admin.CorreoElectronico = "nomail@sorry.bro"
    admin.Admin             = True
    db.session.add(admin)
    db.session.commit()
    return 0


if __name__ == "__main__":
    main()
