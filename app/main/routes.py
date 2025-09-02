import os
from flask import render_template, request, jsonify, session, send_from_directory, current_app
from flask_babel import _, get_locale
from app.main import bp
from app import app

# Create a route to serve static files directly
@bp.route('/<path:path>')
def static_proxy(path):
    # First try to serve static files
    try:
        return current_app.send_static_file(path)
    except:
        pass
    
    # Then try to serve from static folder
    try:
        return send_from_directory(os.path.join(current_app.root_path, '..', 'static'), path)
    except:
        pass
        
    # If file not found, return 404
    return "File not found", 404

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/favicon.ico')
def favicon():
    from flask import send_from_directory
    return send_from_directory('../static', 'favicon.ico')

@bp.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

# Serve static files explicitly
@bp.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(app.root_path, '..', 'static'), path)

# Serve root static files
@bp.route('/<path:filename>')
def serve_root_static(filename):
    if filename in ['favicon.ico', 'robots.txt', 'script.js', 'style.css']:
        return send_from_directory(os.path.join(app.root_path, '..', 'static'), filename)
    return send_from_directory(os.path.join(app.root_path, '..', 'static'), filename, as_attachment=False)

@bp.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return jsonify({'status': 'success', 'language': language})

@bp.route('/get_translations')
def get_translations():
    """Get all translations for current language"""
    translations = {
        'welcome_title': _('¡Bienvenido a El Concursillo!'),
        'login_with_google': _('Iniciar sesión con Google'),
        'register_with_email': _('Registrarse con correo'),
        'email_placeholder': _('Correo electrónico'),
        'password_placeholder': _('Contraseña'),
        'username_placeholder': _('Nombre de usuario'),
        'register_button': _('Registrarse'),
        'login_button': _('Iniciar sesión'),
        'create_room': _('Crear sala'),
        'join_room': _('Unirse a sala'),
        'room_code_placeholder': _('Código de sala'),
        'waiting_players': _('Esperando jugadores...'),
        'start_game': _('Iniciar juego'),
        'current_level': _('Nivel actual'),
        'current_prize': _('Premio actual'),
        'lifelines': _('Comodines'),
        'fifty_fifty': _('50/50'),
        'phone_friend': _('Llamar a un amigo'),
        'ask_audience': _('Pregunta al público'),
        'final_answer': _('Respuesta final'),
        'correct': _('¡Correcto!'),
        'incorrect': _('Incorrecto'),
        'game_over': _('Fin del juego'),
        'congratulations': _('¡Felicidades!'),
        'you_won': _('¡Has ganado!'),
        'language': _('Idioma')
    }
    return jsonify(translations)
