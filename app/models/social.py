from app.extensions import db
from datetime import datetime

class SocialPlatform(db.Model):
    __tablename__ = 'social_platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    platform_name = db.Column(db.Enum('facebook', 'instagram', 'twitter', 'linkedin', name='platform_types'), nullable=False)
    account_name = db.Column(db.String(255))
    access_token = db.Column(db.String(512)) # Encrypted in production
    is_connected = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SocialPost(db.Model):
    __tablename__ = 'social_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    media_urls = db.Column(db.JSON) # List of image/video URLs
    
    scheduled_for = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('draft', 'scheduled', 'posted', 'failed', name='post_status'), default='scheduled')
    platform_ids = db.Column(db.JSON) # List of platform IDs to post to
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
