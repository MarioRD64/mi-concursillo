import sys
import logging
import os
logging.basicConfig(stream=sys.stderr)

from app import create_app, socketio

app = create_app(os.getenv('FLASK_CONFIG') or 'production')
application = app

if __name__ == "__main__":
    socketio.run(app)