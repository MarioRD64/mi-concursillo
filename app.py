import gevent.monkey
import os
gevent.monkey.patch_all()

from flask import Flask
from flask_socketio import SocketIO

print("✅ Flask está iniciando...")  # 🔥 Agregamos esto para ver si el código se ejecuta
app = Flask(__name__)

socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def home():
    return "whomp whomp"


if __name__ == '__main__':
    print("🚀 Ejecutando Flask en el puerto 5000...")  # 🔥 Mensaje de prueba
    port = int(os.environ.get("PORT", 5000))  # Asegura que use un puerto dinámico
    socketio.run(app, host='0.0.0.0', port=port)


import gevent.monkey
import os
import json
import time
import threading
from flask import Flask, jsonify, request
from flask_socketio import SocketIO

# 🟢 Parcheamos para usar gevent
gevent.monkey.patch_all()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Permitir conexiones

# 📌 Cargamos preguntas desde un archivo JSON
def cargar_preguntas():
    with open("preguntas.json", "r", encoding="utf-8") as file:
        return json.load(file)


preguntas = cargar_preguntas()

# 📌 Diccionario para almacenar jugadores y puntuaciones
jugadores = {}
presentador = "Mario"  # Solo el presentador puede controlar el juego

# ✅ Ruta para obtener todas las preguntas
@app.route("/preguntas", methods=["GET"])
def obtener_preguntas():
    return jsonify(preguntas)


# ✅ Ruta para registrar un nuevo jugador
@app.route("/registrar", methods=["POST"])
def registrar_jugador():
    datos = request.json
    nombre = datos.get("nombre")

    if nombre and nombre not in jugadores:
        jugadores[nombre] = 0
        return jsonify({"mensaje": f"👤 {nombre} se ha unido", "jugadores": jugadores})
    
    return jsonify({"error": "Nombre inválido o ya registrado"}), 400


# ✅ Función para actualizar la puntuación de un jugador
@app.route("/puntuacion", methods=["POST"])
def actualizar_puntuacion():
    datos = request.json
    nombre = datos.get("nombre")
    puntos = datos.get("puntos", 0)

    if nombre in jugadores:
        jugadores[nombre] += puntos
        return jsonify({"mensaje": f"🏆 {nombre} ahora tiene {jugadores[nombre]} puntos"})
    
    return jsonify({"error": "Jugador no encontrado"}), 404


# ✅ WebSocket para mensajes en el chat
@socketio.on("mensaje")
def manejar_mensaje(datos):
    print(f"💬 Mensaje recibido: {datos}")
    socketio.emit("mensaje", datos)  # Reenviar mensaje a todos


# ✅ Temporizador para responder
def iniciar_temporizador(segundos):
    print(f"⏳ Tiempo límite: {segundos} segundos")
    time.sleep(segundos)
    print("⏰ ¡Tiempo terminado!")


# 🔥 Ruta para iniciar un temporizador
@app.route("/temporizador", methods=["POST"])
def iniciar_temporizador_api():
    datos = request.json
    segundos = datos.get("segundos", 30)

    t = threading.Thread(target=iniciar_temporizador, args=(segundos,))
    t.start()

    return jsonify({"mensaje": f"Temporizador de {segundos} segundos iniciado"})


# ✅ Inicio del servidor
if __name__ == "__main__":
    print("🚀 Iniciando servidor...")
    port = int(os.environ.get("PORT", 5000))  # Soporte para Render
    socketio.run(app, host="0.0.0.0", port=port)
