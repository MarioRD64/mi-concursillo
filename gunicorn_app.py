#!/usr/bin/env python3
"""
WSGI entry point for Gunicorn deployment on Render
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the create_app function from app package
from app import create_app

# Create the application instance
app = create_app('production')

# Initialize database
with app.app_context():
    from app import db
    db.create_all()

# Export the application for Gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
