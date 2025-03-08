import gevent.monkey
import os
import json
import time
import threading
import random
import string
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_socketio import join_room, leave_room
# 🟢 Parcheamos para usar gevent antes de importar otras librerías
gevent.monkey.patch_all()

print("✅ Flask está iniciando...")  # 🔥 Mensaje de prueba

# Inicializamos Flask y WebSockets
app = Flask(__name__)
app.secret_key = "super_secreta"  # Cambia esto por una clave segura
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar extensiones
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.login_view = "login"

# 📌 Configurar Google OAuth
google_bp = make_google_blueprint(client_id="TU_CLIENT_ID", client_secret="TU_CLIENT_SECRET", redirect_to="google_login_callback")
app.register_blueprint(google_bp, url_prefix="/login")

# 📌 Modelo de usuario
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    google_id = db.Column(db.String(150), unique=True, nullable=True)

    def set_password(self, password):
        """Encripta la contraseña antes de guardarla en la base de datos."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña ingresada es correcta."""
        return check_password_hash(self.password_hash, password)

# 📌 Cargar preguntas desde JSON
def cargar_preguntas():
    try:
        with open("preguntas.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("⚠️ Error: No se encontró el archivo preguntas.json")
        return []

preguntas = cargar_preguntas()
jugadores = {}
salas = {}

# 📌 Cargar usuario en sesión
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Ruta principal (Carga la interfaz web)
@app.route('/')
def home():
    return send_from_directory("static", "index.html")

# ✅ Ruta de registro con email y contraseña
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

# ✅ Ruta de inicio de sesión con email y contraseña
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

# ✅ Ruta de inicio de sesión con Google
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

# ✅ Ruta de cierre de sesión
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"mensaje": "✅ Has cerrado sesión"}), 200

# ✅ Ruta protegida para probar autenticación
@app.route("/perfil")
@login_required
def perfil():
    return jsonify({"usuario": current_user.email})

# ✅ Ruta para obtener todas las preguntas
@app.route("/preguntas", methods=["GET"])
def obtener_preguntas():
    return jsonify(preguntas)

# ✅ Ruta para registrar un nuevo jugador en una partida
@app.route("/registrar", methods=["POST"])
def registrar_jugador():
    datos = request.json
    nombre = datos.get("nombre")

    if not nombre or nombre in jugadores:
        return jsonify({"error": "Nombre inválido o en uso"}), 400

    jugadores[nombre] = 0
    return jsonify({"mensaje": f"👤 {nombre} se ha unido", "jugadores": jugadores}), 200

# ✅ Ruta para crear una sala
@app.route("/crear_sala", methods=["POST"])
def crear_sala():
    datos = request.json
    nombre = datos.get("nombre")

    # Generar un código aleatorio de 6 caracteres
    codigo_sala = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    # Asegurar que la sala no exista (poco probable, pero prevenimos)
    while codigo_sala in salas:
        codigo_sala = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    salas[codigo_sala] = [nombre]  # Guardar al creador como el primer jugador
    socketio.emit("jugador_unido", {"jugadores": salas[codigo_sala], "sala": codigo_sala})

    return jsonify({
        "mensaje": f"Sala {codigo_sala} creada",
        "codigo_sala": codigo_sala,  # 📢 Enviar el código de la sala al frontend
        "jugadores": salas[codigo_sala]
    }), 200

# ✅ Ruta para unirse a una sala
@app.route("/unirse_sala", methods=["POST"])
def unirse_sala():
    datos = request.json
    nombre = datos.get("nombre")
    sala = datos.get("sala")

    if sala not in salas or nombre in salas[sala]:
        return jsonify({"error": "Sala no encontrada o nombre en uso"}), 400

    salas[sala].append(nombre)
    socketio.emit("jugador_unido", {"jugadores": salas[sala], "sala": sala})
    return jsonify({"mensaje": f"{nombre} se unió a la sala {sala}", "jugadores": salas[sala]}), 200

# ✅ WebSocket para mensajes en el chat
@socketio.on("mensaje")
def manejar_mensaje(datos):
    print(f"💬 Mensaje recibido: {datos}")
    socketio.emit("mensaje", datos)

# ✅ Evento para iniciar la partida
@socketio.on("iniciar_partida")
def iniciar_partida(data):
    sala = data["sala"]
    if sala not in salas or len(salas[sala]) < 2:
        socketio.emit("error", {"mensaje": "No hay suficientes jugadores"})
        return
    socketio.emit("inicio_partida", {"sala": sala})

# ✅ Iniciar el servidor
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crear la base de datos si no existe
    print("🚀 Ejecutando Flask en el puerto 5000...")
    socketio.run(app, host="0.0.0.0", port=5000)
 
# ✅ Ruta para crear una sala
@app.route("/crear_sala", methods=["POST"])
def crear_sala():
    datos = request.json
    nombre = datos.get("nombre")

    # Generar un código aleatorio de 6 caracteres
    codigo_sala = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    # Asegurar que la sala no exista (poco probable, pero prevenimos)
    while codigo_sala in salas:
        codigo_sala = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    salas[codigo_sala] = [nombre]  # Guardar al creador como el primer jugador
    print(f"📢 Sala creada: {codigo_sala} por {nombre}")

    return jsonify({
        "mensaje": f"Sala {codigo_sala} creada",
        "codigo_sala": codigo_sala,  # 📢 Enviar el código de la sala al frontend
        "jugadores": salas[codigo_sala]
    }), 200

# ✅ Ruta para unirse a una sala
@app.route("/unirse_sala", methods=["POST"])
def unirse_sala():
    datos = request.json
    nombre = datos.get("nombre")
    sala = datos.get("sala")

    if sala not in salas:
        return jsonify({"error": "❌ Sala no encontrada"}), 400

    if nombre in salas[sala]:
        return jsonify({"error": "❌ Nombre en uso"}), 400

    salas[sala].append(nombre)

    print(f"✅ {nombre} se unió a la sala {sala}")

    # 📢 Emitimos a TODOS en la sala
    socketio.emit("jugador_unido", {"jugadores": salas[sala], "sala": sala}, room=sala)

    return jsonify({
        "mensaje": f"{nombre} se unió a la sala {sala}",
        "jugadores": salas[sala]
    }), 200

# ✅ Evento WebSocket para unirse a una sala
@socketio.on("unirse_sala")
def manejar_unirse_sala(data):
    nombre = data["nombre"]
    sala = data["sala"]

    if sala not in salas or nombre in salas[sala]:
        return  # Si la sala no existe o el nombre ya está, no hacemos nada

    join_room(sala)  # 📌 Unimos al jugador a la sala WebSocket
    salas[sala].append(nombre)
    
    print(f"🟢 {nombre} se unió a {sala} vía WebSocket")
    
    socketio.emit("jugador_unido", {"jugadores": salas[sala], "sala": sala}, room=sala)

# ✅ Evento WebSocket para iniciar la partida
@socketio.on("iniciar_partida")
def iniciar_partida(data):
    sala = data["sala"]
    
    if sala not in salas or len(salas[sala]) < 2:
        socketio.emit("error", {"mensaje": "❌ No hay suficientes jugadores"}, room=sala)
        return

    print(f"🚀 Partida iniciada en la sala {sala}")

    socketio.emit("inicio_partida", {"sala": sala}, room=sala)
