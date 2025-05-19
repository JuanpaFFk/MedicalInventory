from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from functools import wraps
from config import COnfig
from models import db, User, MedicalSupply, UsageHistory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(COnfig)

# Inicializar extensiones (vincula a sql)
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Decorador genérico de roles
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                flash('Acceso denegado', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) #ayuda a flask a buscar el usuario desde el id directamenbte

@app.route('/')
def index():
    return redirect(url_for('login'))
 
#estas son la tablas para cada clase, (si ya fueron creadas solo lo revisa)


@app.before_request
def create_tables_once():
    if not hasattr(app, 'tables_created'):  # Más seguro y evita variables globales
        db.create_all()
        app.tables_created = True


@app.route('/login', methods=['GET','POST']) #ruta de login
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for(f'dashboard_{user.role}'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout') #ruta pa desloguearse
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard_admin', methods=['GET','POST']) #funciones del adnimistrador, con add agrega registros, con update los modifica y con delete los elimina
@roles_required('admin')
def dashboard_admin():
    supplies = MedicalSupply.query.all()
    if request.method == 'POST':
        op = request.form['action']
        if op == 'add':
            s = MedicalSupply(
                name=request.form['name'],
                min_stock=int(request.form['min_stock']),
                current_stock=int(request.form['current_stock'])
            )
            db.session.add(s)
        elif op == 'update':
            s = MedicalSupply.query.get(int(request.form['id']))
            s.name = request.form['name']
            s.min_stock = int(request.form['min_stock'])
            s.current_stock = int(request.form['current_stock'])
        elif op == 'delete':
            s = MedicalSupply.query.get(int(request.form['id']))
            db.session.delete(s)
        db.session.commit()
        flash('Operación completada', 'success')
        return redirect(url_for('dashboard_admin'))
    return render_template('dashboard_admin.html', supplies=supplies)

@app.route('/dashboard_nurse', methods=['GET','POST']) #acciones del enfermero retirar del inventario medicamentos, la razon y se guarda un historial de 20 ultimos
@roles_required('admin','nurse')
def dashboard_nurse():
    supplies = MedicalSupply.query.all()
    history = UsageHistory.query.order_by(UsageHistory.timestamp.desc()).limit(20)
    if request.method == 'POST':
        sid = int(request.form['supply_id'])
        amt = int(request.form['amount'])
        note = request.form.get('note')
        s = MedicalSupply.query.get(sid)
        if s and s.current_stock >= amt:
            s.current_stock -= amt
            record = UsageHistory(
                user_id=current_user.id,
                supply_id=sid,
                amount=amt,
                note=note
            )
            db.session.add(record)
            db.session.commit()
            flash('Salida registrada', 'success')
        else:
            flash('Stock insuficiente', 'warning')
        return redirect(url_for('dashboard_nurse'))
    return render_template('dashboard_nurse.html', supplies=supplies, history=history)

@app.route('/dashboard_patient') #acciones del paciente revisar su historial o agregar notas a ese historial
@roles_required('patient')
def dashboard_patient():
    history = UsageHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard_patient.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)

