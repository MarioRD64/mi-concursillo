from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    google_id = db.Column(db.String(150), unique=True, nullable=True)  # Para login con Google

    def set_password(self, password):
        """Encripta la contraseña antes de guardarla en la base de datos."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña ingresada es correcta."""
        return check_password_hash(self.password_hash, password)
