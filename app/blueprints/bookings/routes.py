from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.booking import Service, Booking, Availability
from app.utils.security import require_permission
from . import bookings_bp

@bookings_bp.route('/services', methods=['GET'])
def get_services():
    company_id = request.args.get('company_id')
    services = Service.query.filter_by(company_id=company_id, is_active=True).all()
    return jsonify([{
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "duration": s.duration,
        "price": str(s.price)
    } for s in services]), 200

@bookings_bp.route('/book', methods=['POST'])
def create_booking():
    data = request.get_json()
    # Simple guest booking for now
    booking = Booking(
        company_id=data['company_id'],
        service_id=data['service_id'],
        staff_id=data['staff_id'],
        booking_time=data['booking_time'],
        client_name=data['client_name'],
        client_email=data['client_email'],
        status='pending'
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify({"message": "Booking request received", "id": booking.id}), 201

@bookings_bp.route('/staff/services', methods=['POST'])
@jwt_required()
@require_permission('bookings.manage')
def create_service():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    service = Service(
        company_id=user.company_id,
        name=data['name'],
        description=data.get('description'),
        duration=data['duration'],
        price=data['price']
    )
    db.session.add(service)
    db.session.commit()
    return jsonify({"message": "Service created", "id": service.id}), 201
