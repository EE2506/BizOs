from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.inventory import Product, Category, StockMovement
from app.utils.security import require_permission
from . import inventory_bp

@inventory_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    products = Product.query.filter_by(company_id=user.company_id).all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "stock": str(p.current_stock),
        "price": str(p.unit_price)
    } for p in products]), 200

@inventory_bp.route('/stock/update', methods=['POST'])
@jwt_required()
@require_permission('inventory.manage')
def update_stock():
    data = request.get_json()
    product = Product.query.get(data['product_id'])
    
    if not product:
        return jsonify({"message": "Product not found"}), 404
        
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Update current stock
    product.current_stock += data['change_amount']
    
    # Record movement
    movement = StockMovement(
        product_id=product.id,
        user_id=user.id,
        change_amount=data['change_amount'],
        reason=data.get('reason', 'Manual Update')
    )
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        "message": "Stock updated successfully",
        "new_stock": str(product.current_stock)
    }), 200
