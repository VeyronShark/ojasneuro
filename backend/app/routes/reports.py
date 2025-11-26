"""Report routes for generating PDF reports.

Requirements: 6.1 - GET /children/{id}/report.pdf generates child report
Requirements: 6.2 - GET /schools/{id}/monthly-report.pdf generates school report
"""
from datetime import date, timedelta
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.class_service import ClassService, ClassNotFoundError, AccessDeniedError
from app.services.report_service import (
    ReportService,
    ChildNotFoundError,
    SchoolNotFoundError,
)
from app.services.analytics_service import DateRange
from app.models.child import Child
from app.models.teacher import Teacher
from app import db

reports_bp = Blueprint('reports', __name__)


def _get_child_with_access_check(child_id: int, user):
    """Get a child and verify user has access.
    
    Args:
        child_id: ID of the child
        user: Authenticated user
        
    Returns:
        Child instance
        
    Raises:
        ChildNotFoundError: If child doesn't exist
        AccessDeniedError: If user doesn't have access
    """
    child = db.session.get(Child, child_id)
    if child is None:
        raise ChildNotFoundError(f"Child with id {child_id} not found")
    
    # Verify user has access to the child's class
    ClassService.get_class(child.class_id, user)
    
    return child


def _parse_date_range(request) -> DateRange:
    """Parse date range from request query parameters.
    
    Defaults to last 30 days if not specified.
    """
    end_date_str = request.args.get('end_date')
    start_date_str = request.args.get('start_date')
    
    if end_date_str:
        try:
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            end_date = date.today()
    else:
        end_date = date.today()
    
    if start_date_str:
        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError:
            start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=30)
    
    return DateRange(start_date=start_date, end_date=end_date)


def _parse_month(request) -> date:
    """Parse month from request query parameters.
    
    Defaults to current month if not specified.
    """
    month_str = request.args.get('month')
    
    if month_str:
        try:
            # Expect format YYYY-MM
            parts = month_str.split('-')
            if len(parts) >= 2:
                return date(int(parts[0]), int(parts[1]), 1)
        except (ValueError, IndexError):
            pass
    
    # Default to current month
    today = date.today()
    return date(today.year, today.month, 1)


@reports_bp.route('/children/<int:child_id>/report.pdf', methods=['GET'])
@jwt_required()
def get_child_report(child_id: int):
    """Generate and return a PDF report for a child.
    
    Query Parameters:
        start_date: Start date for metrics (ISO format, defaults to 30 days ago)
        end_date: End date for metrics (ISO format, defaults to today)
    
    Returns:
        200: PDF file
        401: If not authenticated
        403: If user doesn't have access to the child's class
        404: If child not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user has access to the child
        _get_child_with_access_check(child_id, user)
        
        # Parse date range
        date_range = _parse_date_range(request)
        
        # Generate PDF
        pdf_bytes = ReportService.generate_child_report(child_id, date_range)
        
        # Return PDF response
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=child_report_{child_id}.pdf'
            }
        )
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401
    except AccessDeniedError as e:
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': str(e)
            }
        }), 403
    except ChildNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@reports_bp.route('/schools/<int:school_id>/monthly-report.pdf', methods=['GET'])
@jwt_required()
def get_school_monthly_report(school_id: int):
    """Generate and return a monthly PDF report for a school.
    
    Query Parameters:
        month: Month for the report (YYYY-MM format, defaults to current month)
    
    Returns:
        200: PDF file
        401: If not authenticated
        403: If user doesn't have access to the school
        404: If school not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user has access to the school (must be admin of that school)
        if user.school_id != school_id:
            raise AccessDeniedError("You don't have access to this school")
        
        if user.role != 'admin':
            raise AccessDeniedError("Only admins can generate school reports")
        
        # Parse month
        month = _parse_month(request)
        
        # Generate PDF
        pdf_bytes = ReportService.generate_school_report(school_id, month)
        
        # Return PDF response
        month_str = month.strftime('%Y-%m')
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=school_report_{school_id}_{month_str}.pdf'
            }
        )
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401
    except AccessDeniedError as e:
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': str(e)
            }
        }), 403
    except SchoolNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
