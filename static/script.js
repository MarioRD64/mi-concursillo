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

# Diccionario para almacenar jugadores y puntuaciones
jugadores = {}
salas = {}  # Diccionario para almacenar salas y jugadores

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

    if not nombre:
        return jsonify({"error": "Nombre inválido"}), 400
    if nombre in jugadores:
        return jsonify({"error": "El nombre ya está en uso"}), 400

    jugadores[nombre] = 0
    return jsonify({"mensaje": f"👤 {nombre} se ha unido", "jugadores": jugadores}), 200

# ✅ Ruta para unirse a una sala
@app.route("/unirse_sala", methods=["POST"])
def unirse_a_sala():
    datos = request.json
    nombre = datos.get("nombre")
    sala = datos.get("sala")
    
    if not nombre or not sala:
        return jsonify({"error": "Nombre o sala inválidos"}), 400

    if sala not in salas:
        salas[sala] = []

    if nombre in salas[sala]:
        return jsonify({"error": "Jugador ya está en la sala"}), 400

    salas[sala].append(nombre)

    # Enviar una nueva pregunta a los jugadores de la sala
    if preguntas:
        pregunta_aleatoria = preguntas[0]  # Se podría hacer aleatorio si se desea
        socketio.emit("nueva_pregunta", pregunta_aleatoria, room=sala)

    return jsonify({"mensaje": f"👤 {nombre} se unió a la sala {sala}", "jugadores": salas[sala]}), 200

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

# ✅ WebSocket para actualizar las puntuaciones en tiempo real
@socketio.on("actualizar_puntuacion")
def actualizar_puntuacion_socket(data):
    nombre = data["nombre"]
    puntos = data["puntos"]
    
    if nombre in jugadores:
        jugadores[nombre] += puntos
        socketio.emit("puntuacion_actualizada", {"jugador": nombre, "puntos": jugadores[nombre]})

# ✅ Evento para mostrar la pregunta
@socketio.on("mostrar_pregunta")
def mostrar_pregunta(data):
    pregunta = data.get("pregunta")
    opciones = data.get("opciones")
    socketio.emit("nueva_pregunta", {"pregunta": pregunta, "opciones": opciones})

# ✅ Inicio del servidor Flask y WebSockets
if __name__ == "__main__":
    print("🚀 Ejecutando Flask en el puerto 5000...")
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
