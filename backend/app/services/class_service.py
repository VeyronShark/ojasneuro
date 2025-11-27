"""Class service for class management operations.

Requirements: 2.3 - Children filtered by class
Requirements: 2.4 - Teacher access restricted to assigned classes
Requirements: 9.2 - Teacher assignment validation
Requirements: 2.2, 4.4, 6.3, 6.4 - Class CRUD operations
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


class ValidationError(Exception):
    """Raised when validation fails."""
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
    
    @staticmethod
    def create_class(data: dict, user: Teacher) -> Class:
        """Create a new class.
        
        Args:
            data: Dictionary with class data (name, grade_level, school_id, primary_teacher_id)
            user: The authenticated user making the request
            
        Returns:
            Created Class instance
            
        Raises:
            AccessDeniedError: If user doesn't have permission to create classes
            ValidationError: If required fields are missing
        """
        # Only admins can create classes
        if not user.is_admin():
            raise AccessDeniedError("Only administrators can create classes")
        
        # Validate required fields
        if not data.get('name'):
            raise ValidationError("Class name is required")
        
        # Use user's school_id if not provided
        school_id = data.get('school_id', user.school_id)
        
        # Multi-tenancy check: can only create classes in own school
        if school_id != user.school_id:
            raise AccessDeniedError("Cannot create classes in another school")
        
        # Validate teacher assignment if provided
        primary_teacher_id = data.get('primary_teacher_id')
        if primary_teacher_id:
            teacher = db.session.get(Teacher, primary_teacher_id)
            if teacher is None or teacher.school_id != school_id:
                raise ValidationError("Invalid teacher assignment")
        
        new_class = Class(
            name=data['name'],
            grade_level=data.get('grade_level'),
            school_id=school_id,
            primary_teacher_id=primary_teacher_id
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        return new_class
    
    @staticmethod
    def update_class(class_id: int, data: dict, user: Teacher) -> Class:
        """Update an existing class.
        
        Args:
            class_id: ID of the class to update
            data: Dictionary with updated class data
            user: The authenticated user making the request
            
        Returns:
            Updated Class instance
            
        Raises:
            ClassNotFoundError: If class doesn't exist
            AccessDeniedError: If user doesn't have permission to update the class
            ValidationError: If validation fails
        """
        class_obj = db.session.get(Class, class_id)
        
        if class_obj is None:
            raise ClassNotFoundError(f"Class with id {class_id} not found")
        
        # Multi-tenancy check
        if class_obj.school_id != user.school_id:
            raise AccessDeniedError("Access denied to this class")
        
        # Only admins can update classes
        if not user.is_admin():
            raise AccessDeniedError("Only administrators can update classes")
        
        # Update fields if provided
        if 'name' in data:
            if not data['name']:
                raise ValidationError("Class name cannot be empty")
            class_obj.name = data['name']
        
        if 'grade_level' in data:
            class_obj.grade_level = data['grade_level']
        
        if 'primary_teacher_id' in data:
            teacher_id = data['primary_teacher_id']
            if teacher_id:
                teacher = db.session.get(Teacher, teacher_id)
                if teacher is None or teacher.school_id != class_obj.school_id:
                    raise ValidationError("Invalid teacher assignment")
            class_obj.primary_teacher_id = teacher_id
        
        db.session.commit()
        
        return class_obj
    
    @staticmethod
    def delete_class(class_id: int, user: Teacher) -> None:
        """Delete a class.
        
        Args:
            class_id: ID of the class to delete
            user: The authenticated user making the request
            
        Raises:
            ClassNotFoundError: If class doesn't exist
            AccessDeniedError: If user doesn't have permission to delete the class
        """
        class_obj = db.session.get(Class, class_id)
        
        if class_obj is None:
            raise ClassNotFoundError(f"Class with id {class_id} not found")
        
        # Multi-tenancy check
        if class_obj.school_id != user.school_id:
            raise AccessDeniedError("Access denied to this class")
        
        # Only admins can delete classes
        if not user.is_admin():
            raise AccessDeniedError("Only administrators can delete classes")
        
        db.session.delete(class_obj)
        db.session.commit()
