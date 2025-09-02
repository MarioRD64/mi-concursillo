import gevent.monkey
import os
import json
import random
import string
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
from flask_socketio import SocketIO, join_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google

# Parcheamos gevent
gevent.monkey.patch_all()

# Inicialización
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or "super_secreta"
database_url = os.environ.get('DATABASE_URL') or "sqlite:///usuarios.db"
# Handle Render PostgreSQL URL format
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "mario2011rd@gmail.com"  # Cambiar
app.config["MAIL_PASSWORD"] = "jlnt iadv avgl hdzw"        # Cambiar
app.config["MAIL_DEFAULT_SENDER"] = "mario2011rd@gmail.com"  # Cambiar

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
mail = Mail(app)

# Google OAuth
google_bp = make_google_blueprint(client_id="TU_CLIENT_ID", client_secret="TU_CLIENT_SECRET", redirect_to="google_login_callback")
app.register_blueprint(google_bp, url_prefix="/login")

# Serializador para tokens
serializer = URLSafeTimedSerializer(app.secret_key)

# Modelo Usuario
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    confirmado = db.Column(db.Boolean, default=False)
    google_id = db.Column(db.String(150), unique=True, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Cargar preguntas
def cargar_preguntas():
    try:
        with open("preguntas.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("⚠️ Archivo preguntas.json no encontrado")
        return []

preguntas = cargar_preguntas()
salas = {}

# Enviar correo de confirmación
def enviar_confirmacion(email):
    token = serializer.dumps(email, salt='email-confirm')
    link = url_for('confirmar_email', token=token, _external=True)
    msg = Message("Confirma tu correo", recipients=[email])
    msg.body = f"Por favor confirma tu correo haciendo clic en este enlace: {link}"
    mail.send(msg)

# Rutas
@app.route('/')
def home():
    return send_from_directory("static", "index.html")

@app.route("/registro", methods=["POST"])
def registro():
    datos = request.json
    email = datos.get("email")
    password = datos.get("password")

    # Verificar si el email ya está registrado
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    # Crear nuevo usuario
    nuevo_usuario = User(email=email)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Enviar correo de confirmación
    enviar_confirmacion(email)

    return jsonify({"mensaje": "✅ Registro exitoso. Revisa tu correo para confirmar."}), 201

@app.route("/confirmar/<token>")
def confirmar_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except:
        return jsonify({"error": "❌ Enlace inválido o expirado."}), 400

    usuario = User.query.filter_by(email=email).first_or_404()
    usuario.confirmado = True
    db.session.commit()

    return jsonify({"mensaje": "✅ Correo confirmado, ya puedes iniciar sesión."})

@app.route("/login", methods=["POST"])
def login():
    datos = request.json
    email = datos.get("email")
    password = datos.get("password")

    # Verificar si el usuario existe y las credenciales son correctas
    usuario = User.query.filter_by(email=email).first()
    if usuario and usuario.check_password(password):
        if not usuario.confirmado:
            return jsonify({"error": "❌ Debes confirmar tu correo antes de jugar."}), 403
        login_user(usuario)
        return jsonify({"mensaje": "✅ Inicio de sesión exitoso"}), 200
    return jsonify({"error": "❌ Credenciales incorrectas"}), 401

@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()

    usuario = User.query.filter_by(email=user_info["email"]).first()
    if not usuario:
        usuario = User(email=user_info["email"], google_id=user_info["id"], confirmado=True)
        db.session.add(usuario)
        db.session.commit()

    login_user(usuario)
    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"mensaje": "✅ Has cerrado sesión"}), 200

@app.route("/perfil")
@login_required
def perfil():
    return jsonify({"usuario": current_user.email})

@app.route("/preguntas")
def obtener_preguntas():
    return jsonify(preguntas)

# Crear sala
@app.route("/crear_sala", methods=["POST"])
@login_required
def crear_sala():
    datos = request.json
    nombre = datos.get("nombre")
    codigo_sala = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    while codigo_sala in salas:
        codigo_sala = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    salas[codigo_sala] = [nombre]
    print(f"📢 Sala creada: {codigo_sala} por {nombre}")

    return jsonify({
        "mensaje": f"Sala {codigo_sala} creada",
        "codigo_sala": codigo_sala,
        "jugadores": salas[codigo_sala]
    }), 200

# WebSocket
@socketio.on("unirse_sala")
def manejar_unirse_sala(data):
    nombre = data["nombre"]
    sala = data["sala"]

    if sala not in salas:
        socketio.emit("error", {"mensaje": "❌ Sala no encontrada"}, room=request.sid)
        return

    if nombre in salas[sala]:
        socketio.emit("error", {"mensaje": "❌ Nombre ya en uso"}, room=request.sid)
        return

    join_room(sala)
    salas[sala].append(nombre)
    socketio.emit("jugador_unido", {"jugadores": salas[sala], "sala": sala}, room=sala)

@socketio.on("mensaje")
def manejar_mensaje(datos):
    sala = datos["sala"]
    socketio.emit("mensaje", datos, room=sala)

@socketio.on("iniciar_partida")
def iniciar_partida(data):
    sala = data["sala"]
    if sala not in salas or len(salas[sala]) < 2:
        socketio.emit("error", {"mensaje": "❌ No hay suficientes jugadores para iniciar"}, room=sala)
        return

    socketio.emit("inicio_partida", {"sala": sala}, room=sala)

# Iniciar base de datos
with app.app_context():
    db.create_all()

# Expose the SocketIO app for Gunicorn
application = socketio

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor corriendo en puerto {port}...")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
