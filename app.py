import gevent.monkey
import os
gevent.monkey.patch_all()

from flask import Flask
from flask_socketio import SocketIO

print("✅ Flask está iniciando...")  # 🔥 Agregamos esto para ver si el código se ejecuta

app = Flask(__name__)

socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
@application
def home():
    return "¡Hola, Bienvenido a Mi Concursillo!"

if __name__ == '__main__':
    print("🚀 Ejecutando Flask en el puerto 5000...")  # 🔥 Mensaje de prueba
    port = int(os.environ.get("PORT", 5000))  # Asegura que use un puerto dinámico
    socketio.run(app, host='0.0.0.0', port=port)
