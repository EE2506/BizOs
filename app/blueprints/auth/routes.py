from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.extensions import db
from app.models.user import User
from app.models.company import Company
from . import auth_bp

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 1. Validate data
    required = ['company_name', 'email', 'password', 'first_name', 'last_name']
    if not all(k in data for k in required):
        return jsonify({"message": "Missing required fields"}), 400
        
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already exists"}), 400

    # 2. Create Company
    slug = data['company_name'].lower().replace(' ', '-')
    company = Company(name=data['company_name'], slug=slug)
    db.session.add(company)
    db.session.flush() # Get company ID
    
    # 3. Create Owner User
    user = User(
        company_id=company.id,
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role='owner',
        status='active' # Owner is auto-activated for now
    )
    user.set_password(data['password'])
    db.session.add(user)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
        
    return jsonify({
        "message": "Company and owner registered successfully",
        "company": company.name,
        "user": user.email
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        if user.status != 'active':
            return jsonify({"message": "Account is not active"}), 403
            
        tokens = user.get_tokens()
        return jsonify({
            "message": "Login successful",
            "tokens": tokens,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "company_id": user.company_id
            }
        }), 200
        
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "company": user.company.name
    }), 200
