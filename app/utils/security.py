from functools import wraps
from flask import g, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.user import User

def require_permission(*permissions):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.status != 'active':
                abort(403, description="Account inactive or not found.")
                
            # Basic RBAC logic (as per PRD 4.1)
            # This is a placeholder for more complex logic if permissions are stored in DB
            if user.role == 'owner' or user.role == 'admin':
                return f(*args, **kwargs)
                
            # TODO: Add granular permission check logic
            
            abort(403)
        return decorated
    return decorator
