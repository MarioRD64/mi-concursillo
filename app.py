import gevent.monkey
import os
import json
import time
import threading
import random
import string
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session
from flask_socketio import SocketIO, join_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google

# 🟢 Parcheamos gevent
gevent.monkey.patch_all()

print("✅ Flask está iniciando...")

# Inicialización
app = Flask(__name__)
app.secret_key = "super_secreta"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Google OAuth
google_bp = make_google_blueprint(client_id="TU_CLIENT_ID", client_secret="TU_CLIENT_SECRET", redirect_to="google_login_callback")
app.register_blueprint(google_bp, url_prefix="/login")

# Modelo Usuario
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    google_id = db.Column(db.String(150), unique=True, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Preguntas
def cargar_preguntas():
    try:
        with open("preguntas.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("⚠️ Error: No se encontró el archivo preguntas.json")
        return []

preguntas = cargar_preguntas()
salas = {}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas web
@app.route('/')
def home():
    return send_from_directory("static", "index.html")

@app.route("/registro", methods=["POST"])
def registro():
    datos = request.json
    email = datos.get("email")
    password = datos.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    nuevo_usuario = User(email=email)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"mensaje": "✅ Registro exitoso"}), 201

@app.route("/login", methods=["POST"])
def login():
    datos = request.json
    email = datos.get("email")
    password = datos.get("password")

    usuario = User.query.filter_by(email=email).first()
    if usuario and usuario.check_password(password):
        login_user(usuario)
        return jsonify({"mensaje": "✅ Inicio de sesión exitoso"}), 200
    return jsonify({"error": "Credenciales incorrectas"}), 401

@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()

    usuario = User.query.filter_by(email=user_info["email"]).first()
    if not usuario:
        usuario = User(email=user_info["email"], google_id=user_info["id"])
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

@app.route("/preguntas", methods=["GET"])
def obtener_preguntas():
    return jsonify(preguntas)

# ✅ Crear sala (HTTP)
@app.route("/crear_sala", methods=["POST"])
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

# ✅ Eventos WebSocket
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

    join_room(sala)  # Unir a sala WebSocket
    salas[sala].append(nombre)
    print(f"🟢 {nombre} se unió a {sala}")

    # Notificar a todos en la sala
    socketio.emit("jugador_unido", {"jugadores": salas[sala], "sala": sala}, room=sala)

@socketio.on("mensaje")
def manejar_mensaje(datos):
    print(f"💬 Mensaje recibido: {datos}")
    sala = datos["sala"]
    socketio.emit("mensaje", datos, room=sala)

@socketio.on("iniciar_partida")
def iniciar_partida(data):
    sala = data["sala"]
    if sala not in salas or len(salas[sala]) < 2:
        socketio.emit("error", {"mensaje": "❌ No hay suficientes jugadores para iniciar"}, room=sala)
        return

    print(f"🚀 Partida iniciada en sala {sala}")
    socketio.emit("inicio_partida", {"sala": sala}, room=sala)

# ✅ Inicializar base de datos y correr app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("🚀 Ejecutando Flask en el puerto 5000...")
    socketio.run(app, host="0.0.0.0", port=5000)
