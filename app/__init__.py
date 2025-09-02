from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_babel import Babel
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()
babel = Babel()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize app configuration
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    babel.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.game import bp as game_bp
    app.register_blueprint(game_bp, url_prefix='/game')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Language selector
    @app.babel.localeselector
    def get_locale():
        from flask import request, session
        if 'language' in session:
            return session['language']
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'es'
    
    return app
