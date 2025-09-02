from flask import request, jsonify, session, render_template
from flask_login import login_required, current_user
from flask_babel import _
from app.game import bp
from app import db
from app.models import GameRoom, Question, PlayerScore, PlayerAnswer, User, POINTS_PER_CORRECT, BONUS_POINTS
import random
import string

# In-memory storage for active rooms
active_rooms = {}

@bp.route('/host')
@login_required
def host_dashboard():
    """Host dashboard to control the game"""
    return render_template('host_dashboard.html')

@bp.route('/player/<room_code>')
def player_interface(room_code):
    """Player interface to join and play"""
    return render_template('player_interface.html', room_code=room_code)

@bp.route('/create_room', methods=['POST'])
@login_required
def create_room():
    data = request.json
    language = data.get('language', session.get('language', 'es'))
    
    # Generate unique room code
    room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    while GameRoom.query.filter_by(room_code=room_code).first():
        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Create game room
    room = GameRoom(
        room_code=room_code,
        host_id=current_user.id,
        language=language
    )
    db.session.add(room)
    db.session.commit()
    
    # Initialize room state
    active_rooms[room_code] = {
        'players': [],
        'host': current_user.username,
        'current_question': None,
        'room_id': room.id,
        'answers_submitted': {},
        'lifeline_requests': []
    }
    
    return jsonify({
        'message': _('Sala %(room_code)s creada', room_code=room_code),
        'room_code': room_code,
        'host_url': f'/game/host?room={room_code}',
        'player_url': f'/game/player/{room_code}'
    }), 200

@bp.route('/host/get_question', methods=['POST'])
@login_required
def host_get_question():
    """Host gets next question with correct answer visible"""
    data = request.json
    room_code = data.get('room_code')
    question_number = data.get('question_number', 1)
    
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room or room.host_id != current_user.id:
        return jsonify({'error': _('No tienes permisos para esta sala')}), 403
    
    # Get random question for current number
    questions = Question.query.filter_by(
        difficulty_level=min(question_number, 15),
        language=room.language
    ).all()
    
    if not questions:
        return jsonify({'error': _('No hay más preguntas')}), 404
    
    question = random.choice(questions)
    room.current_question_id = question.id
    room.current_question_number = question_number
    db.session.commit()
    
    # Clear previous answers
    if room_code in active_rooms:
        active_rooms[room_code]['answers_submitted'] = {}
        active_rooms[room_code]['current_question'] = question.id
    
    return jsonify({
        'id': question.id,
        'text': question.text,
        'options': question.get_options(),
        'correct_answer': question.correct_answer,  # Host sees correct answer
        'question_number': question_number,
        'category': question.category
    })

@bp.route('/player/submit_answer', methods=['POST'])
def player_submit_answer():
    """Player submits answer (doesn't know if correct until host reveals)"""
    data = request.json
    room_code = data.get('room_code')
    username = data.get('username')
    selected_answer = data.get('answer')
    question_id = data.get('question_id')
    
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room:
        return jsonify({'error': _('Sala no encontrada')}), 404
    
    # Store answer
    answer = PlayerAnswer(
        room_id=room.id,
        username=username,
        question_id=question_id,
        selected_answer=selected_answer
    )
    db.session.add(answer)
    db.session.commit()
    
    # Track in memory for real-time updates
    if room_code in active_rooms:
        active_rooms[room_code]['answers_submitted'][username] = {
            'answer': selected_answer,
            'timestamp': answer.answered_at.isoformat()
        }
    
    return jsonify({'message': _('Respuesta enviada'), 'status': 'submitted'})

@bp.route('/player/join', methods=['POST'])
def player_join():
    """Player joins a game room"""
    data = request.json
    room_code = data.get('room_code')
    username = data.get('username')
    
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room:
        return jsonify({'error': _('Sala no encontrada')}), 404
    
    # Check if player already exists
    existing_score = PlayerScore.query.filter_by(
        room_id=room.id,
        username=username
    ).first()
    
    if not existing_score:
        # Create new player score record
        player_score = PlayerScore(
            room_id=room.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            username=username
        )
        db.session.add(player_score)
        db.session.commit()
        
        # Add to active rooms
        if room_code in active_rooms:
            active_rooms[room_code]['players'].append(username)
    
    return jsonify({'message': _('Te has unido al juego'), 'status': 'joined'})

@bp.route('/host/reveal_answers', methods=['POST'])
@login_required
def host_reveal_answers():
    """Host reveals correct answer and updates player scores"""
    data = request.json
    room_code = data.get('room_code')
    question_id = data.get('question_id')
    
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room or room.host_id != current_user.id:
        return jsonify({'error': _('No tienes permisos')}), 403
    
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': _('Pregunta no encontrada')}), 404
    
    # Get all answers for this question
    answers = PlayerAnswer.query.filter_by(
        room_id=room.id,
        question_id=question_id
    ).all()
    
    results = []
    first_correct = True
    
    for answer in answers:
        is_correct = answer.selected_answer == question.correct_answer
        answer.is_correct = is_correct
        
        # Update player score if correct
        if is_correct:
            player_score = PlayerScore.query.filter_by(
                room_id=room.id,
                username=answer.username
            ).first()
            
            if player_score:
                player_score.correct_answers += 1
                points = POINTS_PER_CORRECT
                
                # Bonus for first correct answer
                if first_correct:
                    points += BONUS_POINTS['first_correct']
                    first_correct = False
                
                player_score.current_score += points
        
        results.append({
            'username': answer.username,
            'answer': answer.selected_answer,
            'is_correct': is_correct,
            'timestamp': answer.answered_at.isoformat()
        })
    
    db.session.commit()
    
    # Get updated leaderboard
    leaderboard = PlayerScore.query.filter_by(room_id=room.id)\
        .order_by(PlayerScore.current_score.desc()).all()
    
    return jsonify({
        'correct_answer': question.correct_answer,
        'results': results,
        'leaderboard': [{
            'username': score.username,
            'score': score.current_score,
            'correct_answers': score.correct_answers,
            'questions_answered': score.questions_answered
        } for score in leaderboard]
    })

@bp.route('/player/request_lifeline', methods=['POST'])
def player_request_lifeline():
    """Player requests lifeline - host must approve"""
    data = request.json
    room_code = data.get('room_code')
    username = data.get('username')
    lifeline_type = data.get('lifeline')
    
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room:
        return jsonify({'error': _('Sala no encontrada')}), 404
    
    # Check if player has lifelines left
    player_score = PlayerScore.query.filter_by(
        room_id=room.id,
        username=username
    ).first()
    
    if player_score:
        lifelines = player_score.get_lifelines_used()
        if lifelines.get(lifeline_type, 0) >= 1:
            return jsonify({'error': _('Ya has usado este comodín')}), 400
    
    # Add to lifeline requests for host to see
    if room_code in active_rooms:
        active_rooms[room_code]['lifeline_requests'].append({
            'username': username,
            'lifeline': lifeline_type,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return jsonify({'message': _('Solicitud de comodín enviada al presentador'), 'status': 'pending'})

@bp.route('/host/approve_lifeline', methods=['POST'])
@login_required
def host_approve_lifeline():
    """Host approves lifeline and provides result"""
    data = request.json
    room_code = data.get('room_code')
    username = data.get('username')
    lifeline_type = data.get('lifeline')
    approved = data.get('approved', True)
    
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room or room.host_id != current_user.id:
        return jsonify({'error': _('No tienes permisos')}), 403
    
    if not approved:
        return jsonify({'message': _('Comodín denegado')})
    
    # Mark lifeline as used
    player_score = PlayerScore.query.filter_by(
        room_id=room.id,
        username=username
    ).first()
    
    if player_score:
        player_score.use_lifeline(lifeline_type)
        db.session.commit()
    
    return jsonify({
        'message': _('Comodín aprobado'),
        'lifeline': lifeline_type,
        'username': username
    })

@bp.route('/host/get_room_status/<room_code>')
@login_required
def get_room_status(room_code):
    """Get current room status for host dashboard"""
    room = GameRoom.query.filter_by(room_code=room_code).first()
    if not room or room.host_id != current_user.id:
        return jsonify({'error': _('No tienes permisos')}), 403
    
    # Get player scores
    scores = PlayerScore.query.filter_by(room_id=room.id)\
        .order_by(PlayerScore.current_score.desc()).all()
    
    # Get pending answers
    pending_answers = []
    if room_code in active_rooms:
        pending_answers = list(active_rooms[room_code]['answers_submitted'].items())
        lifeline_requests = active_rooms[room_code]['lifeline_requests']
    else:
        lifeline_requests = []
    
    return jsonify({
        'room_code': room_code,
        'status': room.status,
        'current_question_number': room.current_question_number,
        'players': [{
            'username': score.username,
            'score': score.current_score,
            'correct_answers': score.correct_answers,
            'lifelines_used': score.get_lifelines_used()
        } for score in scores],
        'pending_answers': pending_answers,
        'lifeline_requests': lifeline_requests
    })
