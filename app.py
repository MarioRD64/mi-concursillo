import gevent.monkey
import os
import json
import time
import threading
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO
import random
import string

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

# Diccionario para almacenar jugadores, puntuaciones y salas
jugadores = {}
salas = {}

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

# ✅ Ruta para crear una sala
@app.route("/crear_sala", methods=["POST"])
def crear_sala():
    datos = request.json
    nombre = datos.get("nombre")

    # Generar un código de sala aleatorio de 6 caracteres
    codigo_sala = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    if codigo_sala in salas:
        return jsonify({"error": "La sala ya existe, intenta crear otra"}), 400

    salas[codigo_sala] = [nombre]  # El creador es el primer jugador
    socketio.emit("jugador_unido", {"jugadores": salas[codigo_sala], "sala": codigo_sala})

    return jsonify({"mensaje": f"Sala {codigo_sala} creada", "jugadores": salas[codigo_sala]}), 200

# ✅ Ruta para unirse a una sala existente
@app.route("/unirse_sala", methods=["POST"])
def unirse_sala():
    datos = request.json
    nombre = datos.get("nombre")
    sala = datos.get("sala")

    if sala not in salas:
        return jsonify({"error": "Sala no encontrada"}), 404

    if nombre in salas[sala]:
        return jsonify({"error": "Jugador ya en la sala"}), 400

    salas[sala].append(nombre)
    socketio.emit("jugador_unido", {"jugadores": salas[sala], "sala": sala})
    return jsonify({"mensaje": f"{nombre} se unió a la sala {sala}", "jugadores": salas[sala]}), 200

# ✅ WebSocket para mensajes en el chat
@socketio.on("mensaje")
def manejar_mensaje(datos):
    print(f"💬 Mensaje recibido: {datos}")
    socketio.emit("mensaje", datos)  # Reenviar mensaje a todos los jugadores

# ✅ Evento para iniciar la partida cuando haya suficientes jugadores
@socketio.on("iniciar_partida")
def iniciar_partida(data):
    sala = data["sala"]
    
    if sala not in salas or len(salas[sala]) < 2:
        socketio.emit("error", {"mensaje": "No hay suficientes jugadores para iniciar."})
        return
    
    socketio.emit("inicio_partida", {"sala": sala})  # Emitir evento a todos los jugadores
    # Lógica para iniciar el juego (enviar preguntas, etc.)

# ✅ Evento para actualizar la puntuación de los jugadores
@socketio.on("actualizar_puntuacion")
def actualizar_puntuacion_socket(data):
    nombre = data["nombre"]
    puntos = data["puntos"]
    
    # Actualizar las puntuaciones
    if nombre in jugadores:
        jugadores[nombre] += puntos
        socketio.emit("puntuacion_actualizada", {"jugador": nombre, "puntos": jugadores[nombre]})

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

# ✅ Evento para mostrar la pregunta
@socketio.on("mostrar_pregunta")
def mostrar_pregunta(data):
    pregunta = data.get("pregunta")
    opciones = data.get("opciones")
    respuesta_correcta = data.get("respuesta_correcta")

    # Enviar la pregunta y las opciones a todos los jugadores
    socketio.emit("nueva_pregunta", {"pregunta": pregunta, "opciones": opciones, "respuesta_correcta": respuesta_correcta})

# ✅ Inicio del servidor Flask y WebSockets
if __name__ == "__main__":
    print("🚀 Ejecutando Flask en el puerto 5000...")
    port = int(os.environ.get("PORT", 5000))  # Soporte para Render
    socketio.run(app, host="0.0.0.0", port=port)
