import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secreta_key_for_development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///concursillo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Google OAuth
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    
    # Internationalization
    LANGUAGES = {
        'es': 'Español',
        'en': 'English', 
        'fr': 'Français',
        'de': 'Deutsch'
    }
    BABEL_DEFAULT_LOCALE = 'es'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_USERNAME = 'mario2011rd@gmail.com'
    MAIL_PASSWORD = 'jlnt iadv avgl hdzw'

class ProductionConfig(Config):
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        import os
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
