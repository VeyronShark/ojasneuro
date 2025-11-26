"""Template service for parent communication templates and handouts.

Requirements: 8.1 - Return template text for specified language
Requirements: 8.2 - Return formatted handout content (text or PDF)
Requirements: 8.3 - Support multiple languages where available
"""
from typing import Optional
from io import BytesIO

from app import db
from app.models.template import MessageTemplate


class TemplateNotFoundError(Exception):
    """Raised when a template is not found."""
    pass


class InvalidTemplateTypeError(Exception):
    """Raised when an invalid template type is provided."""
    pass


# Valid template types
VALID_TEMPLATE_TYPES = ['parent_message', 'handout', 'welcome', 'report_intro']

# Default language fallback
DEFAULT_LANGUAGE = 'en'


class TemplateService:
    """Service for retrieving communication templates."""
    
    @staticmethod
    def get_parent_message(language: str = DEFAULT_LANGUAGE) -> str:
        """Get parent message template for the specified language.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Template content string
            
        Raises:
            TemplateNotFoundError: If no template exists for the language
        """
        template = MessageTemplate.query.filter_by(
            template_type='parent_message',
            language=language
        ).first()
        
        # Fallback to default language if not found
        if template is None and language != DEFAULT_LANGUAGE:
            template = MessageTemplate.query.filter_by(
                template_type='parent_message',
                language=DEFAULT_LANGUAGE
            ).first()
        
        if template is None:
            raise TemplateNotFoundError(
                f"Parent message template not found for language '{language}'"
            )
        
        return template.content
    
    @staticmethod
    def get_handout(
        format: str = 'text',
        language: str = DEFAULT_LANGUAGE
    ) -> str | bytes:
        """Get handout template in the specified format.
        
        Args:
            format: Output format ('text' or 'pdf')
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Template content as string (text) or bytes (pdf)
            
        Raises:
            TemplateNotFoundError: If no template exists for the language
        """
        template = MessageTemplate.query.filter_by(
            template_type='handout',
            language=language
        ).first()
        
        # Fallback to default language if not found
        if template is None and language != DEFAULT_LANGUAGE:
            template = MessageTemplate.query.filter_by(
                template_type='handout',
                language=DEFAULT_LANGUAGE
            ).first()
        
        if template is None:
            raise TemplateNotFoundError(
                f"Handout template not found for language '{language}'"
            )
        
        if format == 'pdf':
            return TemplateService._generate_handout_pdf(template.content)
        
        return template.content
    
    @staticmethod
    def _generate_handout_pdf(content: str) -> bytes:
        """Generate a PDF from handout content.
        
        Args:
            content: Text content to convert to PDF
            
        Returns:
            PDF bytes
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch
        except ImportError:
            # If reportlab is not available, return content as bytes
            return content.encode('utf-8')
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30
        )
        story.append(Paragraph("Parent Handout", title_style))
        story.append(Spacer(1, 0.25 * inch))
        
        # Add content paragraphs
        body_style = styles['Normal']
        for paragraph in content.split('\n\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))
                story.append(Spacer(1, 0.15 * inch))
        
        doc.build(story)
        return buffer.getvalue()
    
    @staticmethod
    def get_template(
        template_type: str,
        language: str = DEFAULT_LANGUAGE
    ) -> str:
        """Get any template by type and language.
        
        Args:
            template_type: Type of template to retrieve
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Template content string
            
        Raises:
            InvalidTemplateTypeError: If template_type is not valid
            TemplateNotFoundError: If no template exists
        """
        if template_type not in VALID_TEMPLATE_TYPES:
            raise InvalidTemplateTypeError(
                f"Invalid template type: {template_type}. "
                f"Valid types are: {VALID_TEMPLATE_TYPES}"
            )
        
        template = MessageTemplate.query.filter_by(
            template_type=template_type,
            language=language
        ).first()
        
        # Fallback to default language if not found
        if template is None and language != DEFAULT_LANGUAGE:
            template = MessageTemplate.query.filter_by(
                template_type=template_type,
                language=DEFAULT_LANGUAGE
            ).first()
        
        if template is None:
            raise TemplateNotFoundError(
                f"Template '{template_type}' not found for language '{language}'"
            )
        
        return template.content
    
    @staticmethod
    def get_available_languages(template_type: str) -> list[str]:
        """Get list of available languages for a template type.
        
        Args:
            template_type: Type of template
            
        Returns:
            List of language codes
        """
        templates = MessageTemplate.query.filter_by(
            template_type=template_type
        ).all()
        
        return [t.language for t in templates]
