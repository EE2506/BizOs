from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.reports import FieldReport, Survey, SurveyResponse
from app.utils.security import require_permission
from . import reports_bp

@reports_bp.route('/field-reports', methods=['POST'])
@jwt_required()
def create_field_report():
    from app.models.user import User
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    report = FieldReport(
        company_id=user.company_id,
        user_id=user.id,
        title=data['title'],
        content=data['content'],
        location=data.get('location')
    )
    db.session.add(report)
    db.session.commit()
    
    return jsonify({"message": "Field report submitted"}), 201

@reports_bp.route('/surveys', methods=['GET'])
def get_surveys():
    company_id = request.args.get('company_id')
    surveys = Survey.query.filter_by(company_id=company_id, is_active=True).all()
    return jsonify([{
        "id": s.id,
        "title": s.title,
        "description": s.description
    } for s in surveys]), 200

@reports_bp.route('/surveys/<int:survey_id>/respond', methods=['POST'])
def submit_survey(survey_id):
    data = request.get_json()
    
    response = SurveyResponse(
        survey_id=survey_id,
        client_id=data.get('client_id'),
        answers=data['answers']
    )
    db.session.add(response)
    db.session.commit()
    
    return jsonify({"message": "Survey submitted successfully"}), 201
