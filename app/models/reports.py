from app.extensions import db
from datetime import datetime

class FieldReport(db.Model):
    __tablename__ = 'field_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Field worker
    
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255))
    photos = db.Column(db.JSON) # List of file paths/URLs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Survey(db.Model):
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('SurveyQuestion', backref='survey', lazy=True)

class SurveyQuestion(db.Model):
    __tablename__ = 'survey_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('text', 'rating', 'multiple_choice', name='question_type'), default='text')
    options = db.Column(db.JSON) # For multiple choice

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True) # Anonymous if null
    
    answers = db.Column(db.JSON) # List of answers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
