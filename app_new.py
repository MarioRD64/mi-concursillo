"""
Enhanced El Concursillo - Host-Controlled Multilingual Quiz Platform
Based on IlloJuan's format with host control and player rankings
"""

from app import create_app, db, socketio
from app.models import User, Question, GameRoom, PlayerScore, PlayerAnswer
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'development')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Question': Question, 
            'GameRoom': GameRoom, 'PlayerScore': PlayerScore, 'PlayerAnswer': PlayerAnswer}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("🚀 El Concursillo server starting...")
        print("📱 Host Dashboard: /game/host")
        print("👥 Player Interface: /game/player/ROOMCODE")
    
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
