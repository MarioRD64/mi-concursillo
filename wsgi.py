import sys
import logging
import os
logging.basicConfig(stream=sys.stderr)

"""
WSGI config for Mi Concursillo.

It exposes the WSGI callable as a module-level variable named ``application``.
"""
from app import create_app, db
from app.models import User

# Create application instance
application = create_app(os.getenv('FLASK_CONFIG') or 'production')

@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)