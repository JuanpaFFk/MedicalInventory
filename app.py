from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from functools import wraps
from config import COnfig
from models import db, User, MedicalSupply, UsageHistory
from datetime import datetime, timedelta
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
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

# Crear tablas una sola vez (antes usabas before_request)
@app.before_request
def create_tables_once():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for(f'dashboard_{user.role}'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard_admin', methods=['GET','POST'])
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

# Nueva ruta para editar un insumo (Formulario dedicado)
@app.route('/edit/<int:id>', methods=['GET'])
@roles_required('admin')
def edit_item(id):
    item = MedicalSupply.query.get_or_404(id)
    return render_template('edit_item.html', item=item)

@app.route('/dashboard_nurse', methods=['GET','POST'])
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

@app.route('/dashboard_patient', methods=['GET','POST'])
@roles_required('patient')
def dashboard_patient():
    if request.method == 'POST':
        supply_id = int(request.form['supply_id'])
        dosage_type = request.form['dosage_type']
        note = request.form.get('note', '')
        record = UsageHistory(
            user_id=current_user.id,
            supply_id=supply_id,
            amount=1,
            dosage_type=dosage_type,
            note=note,
            next_dose_date=datetime.utcnow() + timedelta(days=1)
        )
        db.session.add(record)
        db.session.commit()
        flash('Dosis registrada', 'success')
        return redirect(url_for('dashboard_patient'))

    history = UsageHistory.query.filter_by(user_id=current_user.id).order_by(UsageHistory.timestamp.desc()).limit(20)
    supplies = MedicalSupply.query.all()
    return render_template('dashboard_patient.html', history=history, supplies=supplies)
if __name__ == '__main__':
    app.run(debug=True)

