from app.extensions import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Enum('pending', 'active', 'suspended', 'deactivated', name='company_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Module activation (from PRD 5.2)
    client_portal = db.Column(db.Boolean, default=True)
    bookings = db.Column(db.Boolean, default=True)
    invoicing = db.Column(db.Boolean, default=True)
    inventory = db.Column(db.Boolean, default=False)
    team_onboarding = db.Column(db.Boolean, default=False)
    field_reports = db.Column(db.Boolean, default=False)
    surveys = db.Column(db.Boolean, default=False)
    social_scheduler = db.Column(db.Boolean, default=False)
    
    users = db.relationship('User', backref='company', lazy=True)

    def __repr__(self):
        return f'<Company {self.name}>'
