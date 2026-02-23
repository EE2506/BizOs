from app.extensions import db, bcrypt
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.Enum('owner', 'admin', 'manager', 'staff', 'field_worker', 'receptionist', 'accountant', 'viewer', name='user_roles'), default='staff')
    status = db.Column(db.Enum('pending', 'active', 'suspended', 'deactivated', name='user_status'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        # Using cost factor 12 as per PRD 3.1
        self.password_hash = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_tokens(self):
        access_token = create_access_token(identity=self.id)
        refresh_token = create_refresh_token(identity=self.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def __repr__(self):
        return f'<User {self.email}>'
