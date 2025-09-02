from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from flask_babel import _
from app import socketio, db
from app.models import GameRoom, PlayerScore, User
from app.game.routes import active_rooms

@socketio.on('join_room')
def handle_join_room(data):
    room_code = data['room_code']
    username = data.get('username', current_user.username if current_user.is_authenticated else 'Anonymous')
    
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room:
        emit('error', {'message': _('Sala no encontrada')})
        return
    
    join_room(room_code)
    
    # Add to active rooms tracking
    if room_code not in active_rooms:
        active_rooms[room_code] = {
            'players': [],
            'host': room.host.username,
            'current_question': None,
            'room_id': room.id,
            'answers_submitted': {},
            'lifeline_requests': []
        }
    
    if username not in active_rooms[room_code]['players']:
        active_rooms[room_code]['players'].append(username)
    
    # Notify all users in room
    emit('player_joined', {
        'players': active_rooms[room_code]['players'],
        'room_code': room_code,
        'host': active_rooms[room_code]['host']
    }, room=room_code)

@socketio.on('host_new_question')
def handle_host_new_question(data):
    """Host broadcasts new question to all players"""
    room_code = data['room_code']
    question_data = data['question']
    
    # Send question to all players in room (without correct answer)
    emit('new_question', {
        'room_code': room_code,
        'question': {
            'id': question_data['id'],
            'text': question_data['text'],
            'options': question_data['options'],
            'question_number': question_data['question_number']
        }
    }, room=room_code)

@socketio.on('host_reveal_answers')
def handle_host_reveal_answers(data):
    """Host reveals answers and results to all players"""
    room_code = data['room_code']
    
    emit('answer_revealed', {
        'room_code': room_code,
        'correct_answer': data['correct_answer'],
        'results': data['results'],
        'leaderboard': data['leaderboard']
    }, room=room_code)

@socketio.on('player_answered')
def handle_player_answered(data):
    """Player notifies they submitted an answer"""
    room_code = data['room_code']
    username = data['username']
    
    # Notify host that player answered
    emit('player_answer_notification', {
        'username': username,
        'room_code': room_code
    }, room=room_code)

@socketio.on('lifeline_approved')
def handle_lifeline_approved(data):
    """Host approves lifeline for specific player"""
    room_code = data['room_code']
    username = data['username']
    lifeline = data['lifeline']
    
    emit('lifeline_approved', {
        'room_code': room_code,
        'username': username,
        'lifeline': lifeline
    }, room=room_code)

@socketio.on('lifeline_denied')
def handle_lifeline_denied(data):
    """Host denies lifeline for specific player"""
    room_code = data['room_code']
    username = data['username']
    lifeline = data['lifeline']
    
    emit('lifeline_denied', {
        'room_code': room_code,
        'username': username,
        'lifeline': lifeline
    }, room=room_code)

@socketio.on('disconnect')
def handle_disconnect():
    # Clean up user from active rooms
    for room_code, room_data in active_rooms.items():
        username = current_user.username if current_user.is_authenticated else 'Anonymous'
        
        if username in room_data['players']:
            room_data['players'].remove(username)
        
        # Notify remaining users
        emit('player_left', {
            'players': room_data['players'],
            'username': username
        }, room=room_code)
