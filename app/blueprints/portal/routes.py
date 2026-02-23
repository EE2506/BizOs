from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.client import Client, ProjectUpdate, File
from . import portal_bp

@portal_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    client = Client.query.filter_by(email=data.get('email')).first()
    
    if client and client.check_password(data.get('password')):
        if client.status != 'active':
            return jsonify({"message": "Client account is deactivated"}), 403
            
        return jsonify({
            "tokens": client.get_tokens(),
            "client": {"id": client.id, "email": client.email, "name": client.name}
        }), 200
        
    return jsonify({"message": "Invalid credentials"}), 401

@portal_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    client_id = get_jwt_identity()
    client = Client.query.get(client_id)
    return jsonify({
        "id": client.id,
        "email": client.email,
        "name": client.name,
        "company": client.company.name
    }), 200

@portal_bp.route('/updates', methods=['GET'])
@jwt_required()
def get_updates():
    client_id = get_jwt_identity()
    updates = ProjectUpdate.query.filter_by(client_id=client_id).order_by(ProjectUpdate.created_at.desc()).all()
    return jsonify([{
        "id": u.id,
        "title": u.title,
        "content": u.content,
        "status": u.status,
        "created_at": u.created_at
    } for u in updates]), 200

# Staff Routes (Requires staff role)
from app.utils.security import require_permission

@portal_bp.route('/staff/clients', methods=['GET'])
@jwt_required()
@require_permission('portal.view')
def staff_get_clients():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    clients = Client.query.filter_by(company_id=user.company_id).all()
    return jsonify([{
        "id": c.id,
        "email": c.email,
        "name": c.name,
        "status": c.status
    } for c in clients]), 200

@portal_bp.route('/staff/clients', methods=['POST'])
@jwt_required()
@require_permission('portal.create')
def staff_create_client():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    if Client.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Client email already exists"}), 400
        
    client = Client(
        company_id=user.company_id,
        email=data['email'],
        name=data.get('name')
    )
    client.set_password(data.get('password', 'ChangeMe123!')) # Default password
    db.session.add(client)
    db.session.commit()
    
    return jsonify({"message": "Client created successfully", "id": client.id}), 201

@portal_bp.route('/staff/updates', methods=['POST'])
@jwt_required()
@require_permission('portal.create')
def staff_create_update():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    update = ProjectUpdate(
        company_id=user.company_id,
        client_id=data['client_id'],
        title=data['title'],
        content=data['content'],
        status=data.get('status', 'In Progress')
    )
    db.session.add(update)
    db.session.commit()
    
    return jsonify({"message": "Project update posted"}), 201
