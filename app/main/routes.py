from flask import render_template, request, jsonify, session
from flask_babel import _, get_locale
from app.main import bp

@bp.route('/')
def index():
    return render_template('index.html')

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
