"""
Script to populate the database with questions for El Concursillo
Run this once to add all questions to the database
"""

from app import create_app, db
from app.models import Question
from questions_data import QUESTIONS_DATABASE

def populate_questions():
    app = create_app()
    
    with app.app_context():
        # Clear existing questions
        Question.query.delete()
        
        # Add questions from all languages
        for language, questions in QUESTIONS_DATABASE.items():
            for q_data in questions:
                question = Question(
                    text=q_data['text'],
                    correct_answer=q_data['correct_answer'],
                    difficulty_level=q_data['difficulty_level'],
                    category=q_data['category'],
                    language=language
                )
                question.set_options(q_data['options'])
                db.session.add(question)
        
        db.session.commit()
        print(f"✅ Added {Question.query.count()} questions to database")

if __name__ == '__main__':
    populate_questions()
