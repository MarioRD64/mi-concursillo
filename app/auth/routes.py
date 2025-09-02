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

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': _('El email ya está registrado')}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': _('El nombre de usuario ya está en uso')}), 400
    
    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Send confirmation email
    send_confirmation_email(email)
    
    return jsonify({'message': _('Registro exitoso. Revisa tu correo para confirmar.')}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        if not user.confirmed:
            return jsonify({'error': _('Debes confirmar tu correo antes de jugar.')}), 403
        
        login_user(user)
        return jsonify({
            'message': _('Inicio de sesión exitoso'),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    
    return jsonify({'error': _('Credenciales incorrectas')}), 401

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': _('Has cerrado sesión')}), 200

@bp.route('/confirm/<token>')
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
