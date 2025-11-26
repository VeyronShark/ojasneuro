"""School service for school management operations.

Requirements: 2.1 - School summary with enrolled families and app install counts
Requirements: 2.2 - Classes filtered by school
Requirements: 9.1 - Multi-tenancy data isolation by school_id
"""
from app import db
from app.models.school import School
from app.models.class_ import Class
from app.models.teacher import Teacher


class SchoolNotFoundError(Exception):
    """Raised when a school is not found."""
    pass


class AccessDeniedError(Exception):
    """Raised when user doesn't have access to the requested resource."""
    pass


class SchoolService:
    """Service for handling school-related operations."""
    
    @staticmethod
    def get_school_summary(school_id: int, user: Teacher) -> dict:
        """Get school summary including enrolled families and app installs.
        
        Args:
            school_id: ID of the school to retrieve
            user: The authenticated user making the request
            
        Returns:
            Dictionary with school details
            
        Raises:
            SchoolNotFoundError: If school doesn't exist
            AccessDeniedError: If user doesn't belong to the school
        """
        # Multi-tenancy check: user must belong to the requested school
        if user.school_id != school_id:
            raise AccessDeniedError("Access denied to this school")
        
        school = db.session.get(School, school_id)
        
        if school is None:
            raise SchoolNotFoundError(f"School with id {school_id} not found")
        
        # Get additional counts
        class_count = Class.query.filter_by(school_id=school_id).count()
        teacher_count = Teacher.query.filter_by(school_id=school_id).count()
        
        return {
            'id': school.id,
            'name': school.name,
            'logo': school.logo,
            'primary_color': school.primary_color,
            'enrolled_families': school.enrolled_families,
            'app_installs': school.app_installs,
            'class_count': class_count,
            'teacher_count': teacher_count,
        }
    
    @staticmethod
    def get_classes(school_id: int, user: Teacher) -> list[Class]:
        """Get all classes belonging to a school.
        
        Args:
            school_id: ID of the school
            user: The authenticated user making the request
            
        Returns:
            List of Class instances belonging to the school
            
        Raises:
            SchoolNotFoundError: If school doesn't exist
            AccessDeniedError: If user doesn't belong to the school
        """
        # Multi-tenancy check: user must belong to the requested school
        if user.school_id != school_id:
            raise AccessDeniedError("Access denied to this school")
        
        school = db.session.get(School, school_id)
        
        if school is None:
            raise SchoolNotFoundError(f"School with id {school_id} not found")
        
        # Return only classes belonging to this school (multi-tenancy filter)
        return Class.query.filter_by(school_id=school_id).all()
    
    @staticmethod
    def get_school(school_id: int, user: Teacher) -> School:
        """Get a school by ID with access control.
        
        Args:
            school_id: ID of the school
            user: The authenticated user making the request
            
        Returns:
            School instance
            
        Raises:
            SchoolNotFoundError: If school doesn't exist
            AccessDeniedError: If user doesn't belong to the school
        """
        # Multi-tenancy check
        if user.school_id != school_id:
            raise AccessDeniedError("Access denied to this school")
        
        school = db.session.get(School, school_id)
        
        if school is None:
            raise SchoolNotFoundError(f"School with id {school_id} not found")
        
        return school
