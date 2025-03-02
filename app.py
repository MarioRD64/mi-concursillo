import gevent.monkey
import os
import json
import time
import threading
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO

# 🟢 Parcheamos para usar gevent antes de importar otras librerías
gevent.monkey.patch_all()

print("✅ Flask está iniciando...")  # 🔥 Mensaje de prueba

# Inicializamos Flask y WebSockets
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 📌 Cargamos preguntas desde un archivo JSON
def cargar_preguntas():
    try:
        with open("preguntas.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("⚠️ Error: No se encontró el archivo preguntas.json")
        return []

preguntas = cargar_preguntas()

# 📌 Diccionario para almacenar jugadores y puntuaciones
jugadores = {}
presentador = "Mario"  # Solo el presentador puede controlar el juego

# ✅ Ruta principal (Carga la interfaz web)
@app.route('/')
def home():
    return send_from_directory("static", "index.html")

# ✅ Ruta para obtener todas las preguntas
@app.route("/preguntas", methods=["GET"])
def obtener_preguntas():
    return jsonify(preguntas)

# ✅ Ruta para registrar un nuevo jugador
@app.route("/registrar", methods=["POST"])
def registrar_jugador():
    datos = request.json
    nombre = datos.get("nombre")

    # Verificamos si el nombre es válido
    if not nombre:
        return jsonify({"error": "Nombre inválido"}), 400

    # Verificamos si el nombre ya está en uso
    if nombre in jugadores:
        return jsonify({"error": "El nombre ya está en uso"}), 400

    # Registramos al jugador y asignamos puntuación inicial
    jugadores[nombre] = 0
    return jsonify({"mensaje": f"👤 {nombre} se ha unido", "jugadores": jugadores}), 200

# ✅ Ruta para actualizar puntuaciones
@app.route("/puntuacion", methods=["POST"])
def actualizar_puntuacion():
    datos = request.json
    nombre = datos.get("nombre")
    puntos = datos.get("puntos", 0)

    if nombre not in jugadores:
        return jsonify({"error": "Jugador no encontrado"}), 404

    jugadores[nombre] += puntos
    return jsonify({"mensaje": f"🏆 {nombre} ahora tiene {jugadores[nombre]} puntos"})

# ✅ WebSocket para mensajes en el chat
@socketio.on("mensaje")
def manejar_mensaje(datos):
    print(f"💬 Mensaje recibido: {datos}")
    socketio.emit("mensaje", datos)  # Reenviar mensaje a todos los jugadores

# ✅ Temporizador para responder preguntas
def iniciar_temporizador(segundos):
    print(f"⏳ Tiempo límite: {segundos} segundos")
    time.sleep(segundos)
    print("⏰ ¡Tiempo terminado!")

# ✅ Ruta para iniciar un temporizador
@app.route("/temporizador", methods=["POST"])
def iniciar_temporizador_api():
    datos = request.json
    segundos = datos.get("segundos", 30)

    t = threading.Thread(target=iniciar_temporizador, args=(segundos,))
    t.start()

    return jsonify({"mensaje": f"⏳ Temporizador de {segundos} segundos iniciado"})

# ✅ Inicio del servidor Flask y WebSockets
if __name__ == "__main__":
    print("🚀 Ejecutando Flask en el puerto 5000...")
    port = int(os.environ.get("PORT", 5000))  # Soporte para Render
    socketio.run(app, host="0.0.0.0", port=port)

