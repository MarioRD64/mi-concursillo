from flask import render_template, request, jsonify, url_for, redirect, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import _
from app.auth import bp
from app import db, mail
from app.models import User
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import os

serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev_key'))

@bp.route('/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://mi-concursillo.onrender.com')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
        
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    if not all([email, username, password]):
        return jsonify({'error': _('Todos los campos son obligatorios')}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': _('El email ya está registrado')}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': _('El nombre de usuario ya está en uso')}), 400
    
    try:
        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Send confirmation email
        send_confirmation_email(email)
        
        response = jsonify({
            'message': _('Registro exitoso. Revisa tu correo para confirmar.'),
            'status': 'success'
        })
        response.status_code = 201
        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://mi-concursillo.onrender.com')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': _('Email y contraseña son obligatorios')}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        if not user.confirmed:
            return jsonify({'error': _('Debes confirmar tu correo antes de jugar.')}), 403
        
        login_user(user)
        response = jsonify({
            'message': _('Inicio de sesión exitoso'),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'status': 'success'
        })
        response.status_code = 200
        return response
    
    return jsonify({'error': _('Credenciales incorrectas')}), 401

@bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': _('Has cerrado sesión')}), 200

@bp.route('/auth/confirm/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
    except:
        return jsonify({'error': _('Enlace inválido o expirado.')}), 400
    
    user = User.query.filter_by(email=email).first_or_404()
    user.confirmed = True
    db.session.commit()
    
    return jsonify({'message': _('Correo confirmado, ya puedes iniciar sesión.')})

def send_confirmation_email(email):
    token = serializer.dumps(email, salt='email-confirm')
    link = url_for('auth.confirm_email', token=token, _external=True)
    msg = Message(_('Confirma tu correo'), recipients=[email])
    msg.body = _('Por favor confirma tu correo haciendo clic en este enlace: %(link)s', link=link)
    mail.send(msg)
