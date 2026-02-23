from app.extensions import db, bcrypt
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    status = db.Column(db.Enum('active', 'deactivated', name='client_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_tokens(self):
        # Using a custom claim to distinguish clients from staff
        additional_claims = {"is_client": True}
        access_token = create_access_token(identity=self.id, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=self.id, additional_claims=additional_claims)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def __repr__(self):
        return f'<Client {self.email}>'

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True) # If null, it's a company-wide file
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectUpdate(db.Model):
    __tablename__ = 'project_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='In Progress') # In Progress / Review / Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
