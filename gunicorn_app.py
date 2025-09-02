#!/usr/bin/env python3
"""
WSGI entry point for Gunicorn deployment on Render
"""
import os
import sys
import importlib.util

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app and SocketIO from app.py file (not app directory)
spec = importlib.util.spec_from_file_location("main_app", "app.py")
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)

app = main_app.app
socketio = main_app.socketio
db = main_app.db

# Initialize database
with app.app_context():
    db.create_all()

# Export the application for Gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
