from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.client import Client
from app.models.booking import Booking
from app.models.invoice import Invoice
from . import dashboard_bp

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    company_id = user.company_id
    
    # Aggregated stats
    total_clients = Client.query.filter_by(company_id=company_id).count()
    pending_bookings = Booking.query.filter_by(company_id=company_id, status='pending').count()
    unpaid_invoices = Invoice.query.filter_by(company_id=company_id).filter(Invoice.status != 'paid').count()
    
    return jsonify({
        "clients": total_clients,
        "pending_bookings": pending_bookings,
        "unpaid_invoices": unpaid_invoices,
        "status": "online"
    }), 200
