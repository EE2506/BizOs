from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.social import SocialPost, SocialPlatform
from app.utils.security import require_permission
from . import social_bp

@social_bp.route('/posts', methods=['POST'])
@jwt_required()
@require_permission('social.manage')
def schedule_post():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    post = SocialPost(
        company_id=user.company_id,
        user_id=user.id,
        content=data['content'],
        media_urls=data.get('media_urls', []),
        scheduled_for=data['scheduled_for'],
        platform_ids=data['platform_ids']
    )
    db.session.add(post)
    db.session.commit()
    
    return jsonify({"message": "Post scheduled successfully", "id": post.id}), 201

@social_bp.route('/platforms', methods=['GET'])
@jwt_required()
def get_platforms():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    platforms = SocialPlatform.query.filter_by(company_id=user.company_id).all()
    return jsonify([{
        "id": p.id,
        "platform_name": p.platform_name,
        "account_name": p.account_name,
        "is_connected": p.is_connected
    } for p in platforms]), 200
