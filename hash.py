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

from hashlib import md5

def hash_passwd(pwd):
    return md5(pwd.encode('utf-8')).hexdigest()

def check_passwd(entered, h):
    return hash_passwd(entered) == h
