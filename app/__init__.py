from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_babel import Babel
from flask_cors import CORS
from datetime import timedelta
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO()
babel = Babel()

def create_app(config_name='default'):
    # Get the root path of the project
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    app = Flask(__name__, 
               static_folder=os.path.join(root_path, 'static'),
               static_url_path='')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize app configuration
    config[config_name].init_app(app)
    
    # Configure session and static files
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SEND_FILE_MAX_AGE_DEFAULT=0,  # Disable caching for development
        PREFERRED_URL_SCHEME='https'  # Force HTTPS for URL generation
    )
    
    # Initialize CORS
    CORS(app, 
         resources={"*": {"origins": ["https://mi-concursillo.onrender.com", "http://localhost:5000"]}},
         supports_credentials=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, 
                     cors_allowed_origins=["https://mi-concursillo.onrender.com", "http://localhost:5000"],
                     manage_session=False,
                     cors_credentials=True)
    
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
    
    # Language selector - move after babel.init_app
    def get_locale():
        from flask import request, session
        if 'language' in session:
            return session['language']
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'es'
    
    babel.init_app(app, locale_selector=get_locale)
    
    return app
