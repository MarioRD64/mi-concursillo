from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    confirmed = db.Column(db.Boolean, default=False)
    google_id = db.Column(db.String(150), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Game statistics
    games_played = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON string
    correct_answer = db.Column(db.String(1), nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=False)  # 1-15
    category = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(2), nullable=False)  # es, en, fr, de
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_options(self):
        return json.loads(self.options)
    
    def set_options(self, options_dict):
        self.options = json.dumps(options_dict)

class GameRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(6), unique=True, nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)
    current_question_number = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='waiting')  # waiting, playing, finished
    language = db.Column(db.String(2), default='es')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    host = db.relationship('User', foreign_keys=[host_id], backref='hosted_rooms')
    current_question = db.relationship('Question', foreign_keys=[current_question_id])

class PlayerScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('game_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)  # For non-registered players
    current_score = db.Column(db.Integer, default=0)
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    lifelines_used = db.Column(db.Text, default='{"fifty_fifty": 0, "phone_friend": 0, "ask_audience": 0}')
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    room = db.relationship('GameRoom', backref='player_scores')
    user = db.relationship('User', backref='game_scores')
    
    def get_lifelines_used(self):
        return json.loads(self.lifelines_used)
    
    def use_lifeline(self, lifeline_type):
        lifelines = self.get_lifelines_used()
        lifelines[lifeline_type] += 1
        self.lifelines_used = json.dumps(lifelines)

class PlayerAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('game_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=True)  # Host marks this
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    room = db.relationship('GameRoom', backref='player_answers')
    user = db.relationship('User', backref='answers')
    question = db.relationship('Question', backref='player_answers')

# Scoring system for competitive play
POINTS_PER_CORRECT = 10
BONUS_POINTS = {
    'first_correct': 5,    # First player to answer correctly
    'streak_3': 15,        # 3 correct answers in a row
    'streak_5': 25,        # 5 correct answers in a row
    'no_lifelines': 20     # Answer without using lifelines
}
