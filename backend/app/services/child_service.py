"""Child service for child/student management operations.

Requirements: 3.3, 4.4 - Student CRUD operations
"""
from app import db
from app.models.child import Child
from app.models.class_ import Class
from app.models.teacher import Teacher
from app.services.class_service import ClassService, AccessDeniedError


class ChildNotFoundError(Exception):
    """Raised when a child is not found."""
    pass


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ChildService:
    """Service for handling child-related operations."""
    
    @staticmethod
    def _check_access(child: Child, user: Teacher) -> bool:
        """Check if a user has access to a child.
        
        Users can access a child if they have access to the child's class.
        
        Args:
            child: The child to check access for
            user: The teacher requesting access
            
        Returns:
            True if access is allowed
        """
        class_obj = db.session.get(Class, child.class_id)
        if class_obj is None:
            return False
        
        # Must be in the same school (multi-tenancy)
        if user.school_id != class_obj.school_id:
            return False
        
        # Admins can access all children in their school
        if user.is_admin():
            return True
        
        # Teachers can only access children in classes they are assigned to
        return class_obj.primary_teacher_id == user.id
    
    @staticmethod
    def get_child(child_id: int, user: Teacher) -> Child:
        """Get a child by ID with access control.
        
        Args:
            child_id: ID of the child
            user: The authenticated user making the request
            
        Returns:
            Child instance
            
        Raises:
            ChildNotFoundError: If child doesn't exist
            AccessDeniedError: If user doesn't have access to the child
        """
        child = db.session.get(Child, child_id)
        
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        if not ChildService._check_access(child, user):
            raise AccessDeniedError("Access denied to this child")
        
        return child
    
    @staticmethod
    def create_child(data: dict, user: Teacher) -> Child:
        """Create a new child.
        
        Args:
            data: Dictionary with child data (display_name, class_id, age)
            user: The authenticated user making the request
            
        Returns:
            Created Child instance
            
        Raises:
            AccessDeniedError: If user doesn't have permission to create children
            ValidationError: If required fields are missing or invalid
        """
        # Validate required fields
        if not data.get('display_name'):
            raise ValidationError("Display name is required")
        
        if not data.get('class_id'):
            raise ValidationError("Class ID is required")
        
        # Verify the class exists and user has access
        class_id = data['class_id']
        class_obj = db.session.get(Class, class_id)
        
        if class_obj is None:
            raise ValidationError(f"Class with id {class_id} not found")
        
        # Multi-tenancy check: class must be in user's school
        if class_obj.school_id != user.school_id:
            raise AccessDeniedError("Cannot create children in another school's class")
        
        # Check if user has access to the class (admin or assigned teacher)
        if not user.is_admin() and class_obj.primary_teacher_id != user.id:
            raise AccessDeniedError("Access denied to this class")
        
        new_child = Child(
            display_name=data['display_name'],
            class_id=class_id,
            age=data.get('age')
        )
        
        db.session.add(new_child)
        db.session.commit()
        
        return new_child
    
    @staticmethod
    def update_child(child_id: int, data: dict, user: Teacher) -> Child:
        """Update an existing child.
        
        Args:
            child_id: ID of the child to update
            data: Dictionary with updated child data
            user: The authenticated user making the request
            
        Returns:
            Updated Child instance
            
        Raises:
            ChildNotFoundError: If child doesn't exist
            AccessDeniedError: If user doesn't have permission to update the child
            ValidationError: If validation fails
        """
        child = db.session.get(Child, child_id)
        
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        # Check access
        if not ChildService._check_access(child, user):
            raise AccessDeniedError("Access denied to this child")
        
        # Update fields if provided
        if 'display_name' in data:
            if not data['display_name']:
                raise ValidationError("Display name cannot be empty")
            child.display_name = data['display_name']
        
        if 'age' in data:
            child.age = data['age']
        
        if 'class_id' in data:
            new_class_id = data['class_id']
            new_class = db.session.get(Class, new_class_id)
            
            if new_class is None:
                raise ValidationError(f"Class with id {new_class_id} not found")
            
            # Multi-tenancy check
            if new_class.school_id != user.school_id:
                raise AccessDeniedError("Cannot move child to another school's class")
            
            # Check if user has access to the new class
            if not user.is_admin() and new_class.primary_teacher_id != user.id:
                raise AccessDeniedError("Access denied to the target class")
            
            child.class_id = new_class_id
        
        db.session.commit()
        
        return child
    
    @staticmethod
    def delete_child(child_id: int, user: Teacher) -> None:
        """Delete a child.
        
        Args:
            child_id: ID of the child to delete
            user: The authenticated user making the request
            
        Raises:
            ChildNotFoundError: If child doesn't exist
            AccessDeniedError: If user doesn't have permission to delete the child
        """
        child = db.session.get(Child, child_id)
        
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        # Check access
        if not ChildService._check_access(child, user):
            raise AccessDeniedError("Access denied to this child")
        
        db.session.delete(child)
        db.session.commit()
