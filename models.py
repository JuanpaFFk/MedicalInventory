from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy() #esto me va a ayudar a pasar de python a las tablas de la bd

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'nurse', 'patient'
    password_hash = db.Column(db.Text, nullable=False)

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

class MedicalSupply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    min_stock = db.Column(db.Integer, nullable=False, default=1)
    current_stock = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UsageHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    supply_id = db.Column(db.Integer, db.ForeignKey('medical_supply.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(200))
    dosage_type = db.Column(db.String(50))  # Ej: "Cada 8 horas", "Cada 3 días"
    next_dose_date = db.Column(db.DateTime) # Próxima dosis
    user = db.relationship('User')
    supply = db.relationship('MedicalSupply')
