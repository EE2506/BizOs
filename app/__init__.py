import os
from flask import Flask
from config import config
from app.extensions import db, migrate, bcrypt, jwt, cors, csrf, limiter

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
        
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.portal import portal_bp
    from app.blueprints.bookings import bookings_bp
    from app.blueprints.invoicing import invoicing_bp
    from app.blueprints.inventory import inventory_bp
    from app.blueprints.reports import reports_bp
    from app.blueprints.social import social_bp
    from app.blueprints.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(portal_bp, url_prefix='/api/v1/portal')
    app.register_blueprint(bookings_bp, url_prefix='/api/v1/bookings')
    app.register_blueprint(invoicing_bp, url_prefix='/api/v1/invoicing')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/reports')
    app.register_blueprint(social_bp, url_prefix='/api/v1/social')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
        
    return app
