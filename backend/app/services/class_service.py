"""Class service for class management operations.

Requirements: 2.3 - Children filtered by class
Requirements: 2.4 - Teacher access restricted to assigned classes
Requirements: 9.2 - Teacher assignment validation
"""
from app import db
from app.models.class_ import Class
from app.models.child import Child
from app.models.teacher import Teacher


class ClassNotFoundError(Exception):
    """Raised when a class is not found."""
    pass


class AccessDeniedError(Exception):
    """Raised when user doesn't have access to the requested resource."""
    pass


class ClassService:
    """Service for handling class-related operations."""
    
    @staticmethod
    def _check_teacher_access(class_obj: Class, user: Teacher) -> bool:
        """Check if a teacher has access to a class.
        
        Teachers can access a class if:
        - They are an admin of the same school
        - They are the primary teacher of the class
        
        Args:
            class_obj: The class to check access for
            user: The teacher requesting access
            
        Returns:
            True if access is allowed
        """
        # Must be in the same school (multi-tenancy)
        if user.school_id != class_obj.school_id:
            return False
        
        # Admins can access all classes in their school
        if user.is_admin():
            return True
        
        # Teachers can only access classes they are assigned to
        return class_obj.primary_teacher_id == user.id
    
    @staticmethod
    def get_class(class_id: int, user: Teacher) -> Class:
        """Get a class by ID with access control.
        
        Args:
            class_id: ID of the class
            user: The authenticated user making the request
            
        Returns:
            Class instance
            
        Raises:
            ClassNotFoundError: If class doesn't exist
            AccessDeniedError: If user doesn't have access to the class
        """
        class_obj = db.session.get(Class, class_id)
        
        if class_obj is None:
            raise ClassNotFoundError(f"Class with id {class_id} not found")
        
        if not ClassService._check_teacher_access(class_obj, user):
            raise AccessDeniedError("Access denied to this class")
        
        return class_obj
    
    @staticmethod
    def get_children(class_id: int, user: Teacher) -> list[Child]:
        """Get all children enrolled in a class.
        
        Args:
            class_id: ID of the class
            user: The authenticated user making the request
            
        Returns:
            List of Child instances enrolled in the class
            
        Raises:
            ClassNotFoundError: If class doesn't exist
            AccessDeniedError: If user doesn't have access to the class
        """
        class_obj = db.session.get(Class, class_id)
        
        if class_obj is None:
            raise ClassNotFoundError(f"Class with id {class_id} not found")
        
        # Check teacher access
        if not ClassService._check_teacher_access(class_obj, user):
            raise AccessDeniedError("Access denied to this class")
        
        # Return children enrolled in this class
        return Child.query.filter_by(class_id=class_id).all()
    
    @staticmethod
    def validate_teacher_assignment(class_id: int, teacher_id: int) -> bool:
        """Validate that a teacher can be assigned to a class.
        
        A teacher can be assigned to a class if they belong to the same school.
        
        Args:
            class_id: ID of the class
            teacher_id: ID of the teacher to assign
            
        Returns:
            True if assignment is valid
            
        Raises:
            ClassNotFoundError: If class doesn't exist
        """
        class_obj = db.session.get(Class, class_id)
        
        if class_obj is None:
            raise ClassNotFoundError(f"Class with id {class_id} not found")
        
        teacher = db.session.get(Teacher, teacher_id)
        
        if teacher is None:
            return False
        
        # Teacher must belong to the same school as the class
        return teacher.school_id == class_obj.school_id
