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
