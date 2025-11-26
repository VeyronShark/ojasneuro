"""Consent service for managing parent authorization.

Requirements: 7.1 - Store consent records with timestamp and scope
Requirements: 7.2 - Return current consent state
Requirements: 7.3 - Exclude non-consented children from individual dashboards
Requirements: 7.4 - Anonymize or delete child's event data on request
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from app import db
from app.models.consent import ParentLink
from app.models.child import Child
from app.models.event import EventRaw


class ConsentError(Exception):
    """Raised when consent operations fail."""
    pass


@dataclass
class ConsentStatus:
    """Represents the consent status for a child."""
    child_id: int
    consent_status: str
    consent_timestamp: Optional[datetime]
    consent_scope: Optional[str]
    is_consent_granted: bool
    
    def to_dict(self) -> dict:
        return {
            'child_id': self.child_id,
            'consent_status': self.consent_status,
            'consent_timestamp': self.consent_timestamp.isoformat() if self.consent_timestamp else None,
            'consent_scope': self.consent_scope,
            'is_consent_granted': self.is_consent_granted
        }


class ConsentService:
    """Service for handling consent operations."""
    
    @staticmethod
    def submit_consent(child_id: int, parent_id: int, consent_status: str, scope: str = 'full') -> ParentLink:
        """Submit or update consent for a child.
        
        Args:
            child_id: ID of the child
            parent_id: ID of the parent
            consent_status: 'granted' or 'denied'
            scope: Scope of consent ('full', 'limited', 'analytics_only')
            
        Returns:
            ParentLink instance with updated consent
            
        Raises:
            ConsentError: If child not found or invalid status
        """
        # Validate child exists
        child = db.session.get(Child, child_id)
        if child is None:
            raise ConsentError(f"Child with id {child_id} not found")
        
        # Validate consent status
        if consent_status not in ('granted', 'denied'):
            raise ConsentError("consent_status must be 'granted' or 'denied'")
        
        # Validate scope
        valid_scopes = ('full', 'limited', 'analytics_only')
        if scope not in valid_scopes:
            raise ConsentError(f"scope must be one of: {valid_scopes}")
        
        # Find existing parent link or create new one
        parent_link = ParentLink.query.filter_by(
            child_id=child_id,
            parent_id=parent_id
        ).first()
        
        if parent_link is None:
            parent_link = ParentLink(
                child_id=child_id,
                parent_id=parent_id
            )
            db.session.add(parent_link)
        
        # Update consent
        if consent_status == 'granted':
            parent_link.grant_consent(scope)
        else:
            parent_link.deny_consent()
        
        db.session.commit()
        return parent_link
    
    @staticmethod
    def get_consent_status(child_id: int) -> ConsentStatus:
        """Get the consent status for a child.
        
        Args:
            child_id: ID of the child
            
        Returns:
            ConsentStatus with current consent state
            
        Raises:
            ConsentError: If child not found
        """
        # Validate child exists
        child = db.session.get(Child, child_id)
        if child is None:
            raise ConsentError(f"Child with id {child_id} not found")
        
        # Get the most recent parent link with consent
        parent_link = ParentLink.query.filter_by(child_id=child_id).first()
        
        if parent_link is None:
            # No consent record exists - default to pending
            return ConsentStatus(
                child_id=child_id,
                consent_status='pending',
                consent_timestamp=None,
                consent_scope=None,
                is_consent_granted=False
            )
        
        return ConsentStatus(
            child_id=child_id,
            consent_status=parent_link.consent_status,
            consent_timestamp=parent_link.consent_timestamp,
            consent_scope=parent_link.consent_scope,
            is_consent_granted=parent_link.is_consent_granted()
        )
    
    @staticmethod
    def delete_child_data(child_id: int) -> bool:
        """Delete or anonymize a child's event data.
        
        Args:
            child_id: ID of the child
            
        Returns:
            True if deletion was successful
            
        Raises:
            ConsentError: If child not found
        """
        # Validate child exists
        child = db.session.get(Child, child_id)
        if child is None:
            raise ConsentError(f"Child with id {child_id} not found")
        
        # Get the child's code to find events
        child_code = child.child_code
        
        # Delete all events for this child
        EventRaw.query.filter_by(child_code=child_code).delete()
        
        db.session.commit()
        return True
    
    @staticmethod
    def is_consent_granted(child_id: int) -> bool:
        """Check if consent has been granted for a child.
        
        Args:
            child_id: ID of the child
            
        Returns:
            True if consent is granted, False otherwise
        """
        parent_link = ParentLink.query.filter_by(child_id=child_id).first()
        if parent_link is None:
            return False
        return parent_link.is_consent_granted()
    
    @staticmethod
    def get_consented_children_ids(class_id: int = None) -> list[int]:
        """Get IDs of children with granted consent.
        
        Args:
            class_id: Optional class ID to filter by
            
        Returns:
            List of child IDs with granted consent
        """
        query = db.session.query(Child.id).join(
            ParentLink, Child.id == ParentLink.child_id
        ).filter(ParentLink.consent_status == 'granted')
        
        if class_id is not None:
            query = query.filter(Child.class_id == class_id)
        
        return [row[0] for row in query.all()]
    
    @staticmethod
    def filter_children_by_consent(children: list[Child], require_consent: bool = True) -> list[Child]:
        """Filter a list of children based on consent status.
        
        Args:
            children: List of Child instances
            require_consent: If True, only return children with granted consent
            
        Returns:
            Filtered list of children
        """
        if not require_consent:
            return children
        
        consented_ids = set(ConsentService.get_consented_children_ids())
        return [child for child in children if child.id in consented_ids]
