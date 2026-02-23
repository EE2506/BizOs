from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.invoice import Invoice, Receipt
from app.services.ai_ocr import ocr_service
from app.utils.security import require_permission
from . import invoicing_bp

@invoicing_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    invoices = Invoice.query.filter_by(company_id=user.company_id).all()
    return jsonify([{
        "id": i.id,
        "invoice_number": i.invoice_number,
        "status": i.status,
        "total_amount": str(i.total_amount)
    } for i in invoices]), 200

@invoicing_bp.route('/receipts/scan', methods=['POST'])
@jwt_required()
@require_permission('invoicing.scan')
def scan_receipt():
    # Placeholder for file upload handling
    # file = request.files['receipt']
    # path = save_file(file)
    
    path = "placeholder/path/to/receipt.jpg"
    data = ocr_service.scan_receipt(path)
    
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    receipt = Receipt(
        company_id=user.company_id,
        user_id=user.id,
        file_path=path,
        vendor_name=data['vendor_name'],
        total_amount=data['total_amount'],
        currency=data['currency'],
        ocr_status='completed',
        raw_ocr_data=data
    )
    db.session.add(receipt)
    db.session.commit()
    
    return jsonify({
        "message": "Receipt scanned successfully",
        "data": data
    }), 201
