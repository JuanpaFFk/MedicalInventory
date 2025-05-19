# init_db.py
from app import app, db
from models import User

with app.app_context():
   # db.drop_all()#usar unicamente esto para reinciar la base de datos
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        u = User(fullname='Juan Pablo Montaña Gonzalez',
                 cedula='1006123301',
                 username='admin',
                 role='admin')
        u.set_password('admin123')
        db.session.add(u)
        db.session.commit()
        print("Usuario admin creado: admin / admin123")
    else:
        print("Usuario administrador ya existe")


    if not User.query.filter_by(username='nurse').first():
        u = User(fullname='Juan pero enfermero',
                 cedula='10061233001',
                 username='nurse',
                 role='nurse')
        u.set_password('nurse123')
        db.session.add(u)
        db.session.commit()
        print("Usuario nurse creado: nurse / nurse123")
    else:
        print("Usuario enfermerx ya existe")


    if not User.query.filter_by(username='patient').first():
        u = User(fullname='Juan pero paciente',
                 cedula='10061223301',
                 username='patient',
                 role='patient')
        u.set_password('patient123')
        db.session.add(u)
        db.session.commit()
        print("Usuario admin creado: patient / patient123")
    else:
        print("Usuario paciente ya existe")