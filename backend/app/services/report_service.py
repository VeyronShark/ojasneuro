"""Report service for generating PDF reports.

Requirements: 6.1 - Generate child report PDF with metrics and skill profile
Requirements: 6.2 - Generate school monthly report PDF with engagement and skill summaries
Requirements: 6.3 - Use template-based rendering with consistent formatting
"""
from dataclasses import dataclass
from datetime import date, timedelta
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import Image as RLImage

from app import db
from app.models.child import Child
from app.models.school import School
from app.models.class_ import Class
from app.services.analytics_service import AnalyticsService, DateRange
from app.schemas.event import VALID_SKILL_TAGS


class ChildNotFoundError(Exception):
    """Raised when a child is not found."""
    pass


class SchoolNotFoundError(Exception):
    """Raised when a school is not found."""
    pass


# Skill tag display names for human-readable reports
SKILL_DISPLAY_NAMES = {
    'attention': 'Attention',
    'patience': 'Patience',
    'sensory': 'Sensory Awareness',
    'emotionAwareness': 'Emotion Awareness',
    'bodyAwareness': 'Body Awareness'
}


@dataclass
class ChildReportData:
    """Data structure for child report content."""
    child_name: str
    child_age: Optional[int]
    class_name: str
    school_name: str
    report_date: date
    total_sessions: int
    avg_duration_seconds: float
    skill_scores: dict
    date_range_start: date
    date_range_end: date
    
    def to_dict(self) -> dict:
        return {
            'child_name': self.child_name,
            'child_age': self.child_age,
            'class_name': self.class_name,
            'school_name': self.school_name,
            'report_date': self.report_date.isoformat(),
            'total_sessions': self.total_sessions,
            'avg_duration_seconds': self.avg_duration_seconds,
            'skill_scores': self.skill_scores,
            'date_range_start': self.date_range_start.isoformat(),
            'date_range_end': self.date_range_end.isoformat(),
        }


@dataclass
class SchoolReportData:
    """Data structure for school report content."""
    school_name: str
    report_month: date
    total_classes: int
    total_children: int
    total_sessions: int
    avg_sessions_per_child: float
    engagement_summary: dict
    skill_summaries: dict
    class_summaries: list
    
    def to_dict(self) -> dict:
        return {
            'school_name': self.school_name,
            'report_month': self.report_month.isoformat(),
            'total_classes': self.total_classes,
            'total_children': self.total_children,
            'total_sessions': self.total_sessions,
            'avg_sessions_per_child': self.avg_sessions_per_child,
            'engagement_summary': self.engagement_summary,
            'skill_summaries': self.skill_summaries,
            'class_summaries': self.class_summaries,
        }


class ReportService:
    """Service for generating PDF reports."""
    
    @staticmethod
    def _get_styles():
        """Get report styles."""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        ))
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='ReportBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6
        ))
        return styles

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        minutes = int(seconds / 60)
        remaining_seconds = int(seconds % 60)
        if remaining_seconds > 0:
            return f"{minutes} min {remaining_seconds} sec"
        return f"{minutes} minutes"
    
    @staticmethod
    def _format_score(score: Optional[float]) -> str:
        """Format skill score as percentage."""
        if score is None:
            return "N/A"
        return f"{score * 100:.0f}%"
    
    @staticmethod
    def _create_skill_table(skill_scores: dict, styles) -> Table:
        """Create a table displaying skill scores."""
        data = [['Skill', 'Score']]
        for skill_tag in VALID_SKILL_TAGS:
            skill_name = SKILL_DISPLAY_NAMES.get(skill_tag, skill_tag)
            score = skill_scores.get(skill_tag)
            score_str = ReportService._format_score(score)
            data.append([skill_name, score_str])
        
        table = Table(data, colWidths=[3*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E7E6E6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        return table
    
    @staticmethod
    def _gather_child_report_data(child_id: int, date_range: DateRange) -> ChildReportData:
        """Gather all data needed for a child report.
        
        Args:
            child_id: ID of the child
            date_range: Date range for metrics
            
        Returns:
            ChildReportData with all report content
            
        Raises:
            ChildNotFoundError: If child doesn't exist
        """
        child = db.session.get(Child, child_id)
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        # Get class and school info
        class_ = child.class_
        school = class_.school
        
        # Get metrics
        metrics = AnalyticsService.get_child_metrics(child_id, date_range)
        
        # Get skill profile
        skill_profile = AnalyticsService.get_skill_profile(child_id)
        skill_scores = {
            'attention': skill_profile.attention,
            'patience': skill_profile.patience,
            'sensory': skill_profile.sensory,
            'emotionAwareness': skill_profile.emotionAwareness,
            'bodyAwareness': skill_profile.bodyAwareness,
        }
        
        return ChildReportData(
            child_name=child.display_name,
            child_age=child.age,
            class_name=class_.name,
            school_name=school.name,
            report_date=date.today(),
            total_sessions=metrics.total_sessions,
            avg_duration_seconds=metrics.avg_duration_seconds,
            skill_scores=skill_scores,
            date_range_start=date_range.start_date,
            date_range_end=date_range.end_date,
        )
    
    @staticmethod
    def generate_child_report(child_id: int, date_range: Optional[DateRange] = None) -> bytes:
        """Generate a PDF report for a child.
        
        Args:
            child_id: ID of the child
            date_range: Optional date range for metrics (defaults to last 30 days)
            
        Returns:
            PDF bytes
            
        Raises:
            ChildNotFoundError: If child doesn't exist
        """
        # Default date range: last 30 days
        if date_range is None:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            date_range = DateRange(start_date=start_date, end_date=end_date)
        
        # Gather report data
        report_data = ReportService._gather_child_report_data(child_id, date_range)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = ReportService._get_styles()
        story = []
        
        # Title
        story.append(Paragraph("Child Progress Report", styles['ReportTitle']))
        story.append(Spacer(1, 12))
        
        # Child info section
        story.append(Paragraph("Student Information", styles['SectionTitle']))
        age_str = f", Age: {report_data.child_age}" if report_data.child_age else ""
        story.append(Paragraph(f"<b>Name:</b> {report_data.child_name}{age_str}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Class:</b> {report_data.class_name}", styles['ReportBody']))
        story.append(Paragraph(f"<b>School:</b> {report_data.school_name}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Report Date:</b> {report_data.report_date.strftime('%B %d, %Y')}", styles['ReportBody']))
        story.append(Paragraph(
            f"<b>Period:</b> {report_data.date_range_start.strftime('%B %d, %Y')} - {report_data.date_range_end.strftime('%B %d, %Y')}",
            styles['ReportBody']
        ))
        story.append(Spacer(1, 12))
        
        # Activity summary section
        story.append(Paragraph("Activity Summary", styles['SectionTitle']))
        story.append(Paragraph(f"<b>Total Sessions:</b> {report_data.total_sessions}", styles['ReportBody']))
        duration_str = ReportService._format_duration(report_data.avg_duration_seconds)
        story.append(Paragraph(f"<b>Average Session Duration:</b> {duration_str}", styles['ReportBody']))
        story.append(Spacer(1, 12))
        
        # Skill profile section
        story.append(Paragraph("Skill Profile", styles['SectionTitle']))
        skill_table = ReportService._create_skill_table(report_data.skill_scores, styles)
        story.append(skill_table)
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

    @staticmethod
    def _gather_school_report_data(school_id: int, month: date) -> SchoolReportData:
        """Gather all data needed for a school monthly report.
        
        Args:
            school_id: ID of the school
            month: Month for the report (uses first day of month)
            
        Returns:
            SchoolReportData with all report content
            
        Raises:
            SchoolNotFoundError: If school doesn't exist
        """
        school = db.session.get(School, school_id)
        if school is None:
            raise SchoolNotFoundError(f"School with id {school_id} not found")
        
        # Calculate date range for the month
        start_date = month.replace(day=1)
        # Get last day of month
        if month.month == 12:
            end_date = date(month.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(month.year, month.month + 1, 1) - timedelta(days=1)
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        # Get all classes in the school
        classes = Class.query.filter_by(school_id=school_id).all()
        total_classes = len(classes)
        
        # Aggregate metrics across all classes
        total_children = 0
        total_sessions = 0
        engagement_counts = {'low': 0, 'medium': 0, 'high': 0}
        skill_totals = {tag: [] for tag in VALID_SKILL_TAGS}
        class_summaries = []
        
        for class_ in classes:
            class_metrics = AnalyticsService.get_class_metrics(class_.id, date_range)
            total_children += class_metrics.total_children
            total_sessions += class_metrics.total_sessions
            
            # Track engagement levels
            engagement_counts[class_metrics.engagement_level] += 1
            
            # Aggregate skill scores
            for tag in VALID_SKILL_TAGS:
                score = class_metrics.avg_skill_scores.get(tag)
                if score is not None:
                    skill_totals[tag].append(score)
            
            # Add class summary
            class_summaries.append({
                'class_name': class_.name,
                'total_children': class_metrics.total_children,
                'active_children': class_metrics.active_children,
                'total_sessions': class_metrics.total_sessions,
                'engagement_level': class_metrics.engagement_level,
            })
        
        # Calculate school-wide skill averages
        skill_summaries = {}
        for tag in VALID_SKILL_TAGS:
            scores = skill_totals[tag]
            if scores:
                skill_summaries[tag] = sum(scores) / len(scores)
            else:
                skill_summaries[tag] = None
        
        # Calculate average sessions per child
        avg_sessions_per_child = total_sessions / total_children if total_children > 0 else 0.0
        
        return SchoolReportData(
            school_name=school.name,
            report_month=month,
            total_classes=total_classes,
            total_children=total_children,
            total_sessions=total_sessions,
            avg_sessions_per_child=avg_sessions_per_child,
            engagement_summary=engagement_counts,
            skill_summaries=skill_summaries,
            class_summaries=class_summaries,
        )
    
    @staticmethod
    def _create_class_summary_table(class_summaries: list, styles) -> Table:
        """Create a table displaying class summaries."""
        data = [['Class', 'Children', 'Active', 'Sessions', 'Engagement']]
        for summary in class_summaries:
            data.append([
                summary['class_name'],
                str(summary['total_children']),
                str(summary['active_children']),
                str(summary['total_sessions']),
                summary['engagement_level'].capitalize(),
            ])
        
        table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E7E6E6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        return table
    
    @staticmethod
    def generate_school_report(school_id: int, month: date) -> bytes:
        """Generate a monthly PDF report for a school.
        
        Args:
            school_id: ID of the school
            month: Month for the report
            
        Returns:
            PDF bytes
            
        Raises:
            SchoolNotFoundError: If school doesn't exist
        """
        # Gather report data
        report_data = ReportService._gather_school_report_data(school_id, month)
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = ReportService._get_styles()
        story = []
        
        # Title
        story.append(Paragraph("School Monthly Report", styles['ReportTitle']))
        story.append(Spacer(1, 12))
        
        # School info section
        story.append(Paragraph("School Information", styles['SectionTitle']))
        story.append(Paragraph(f"<b>School:</b> {report_data.school_name}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Report Month:</b> {report_data.report_month.strftime('%B %Y')}", styles['ReportBody']))
        story.append(Spacer(1, 12))
        
        # Overview section
        story.append(Paragraph("Overview", styles['SectionTitle']))
        story.append(Paragraph(f"<b>Total Classes:</b> {report_data.total_classes}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Total Children:</b> {report_data.total_children}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Total Sessions:</b> {report_data.total_sessions}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Avg Sessions per Child:</b> {report_data.avg_sessions_per_child:.1f}", styles['ReportBody']))
        story.append(Spacer(1, 12))
        
        # Engagement summary
        story.append(Paragraph("Engagement Summary", styles['SectionTitle']))
        eng = report_data.engagement_summary
        story.append(Paragraph(f"<b>High Engagement Classes:</b> {eng.get('high', 0)}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Medium Engagement Classes:</b> {eng.get('medium', 0)}", styles['ReportBody']))
        story.append(Paragraph(f"<b>Low Engagement Classes:</b> {eng.get('low', 0)}", styles['ReportBody']))
        story.append(Spacer(1, 12))
        
        # School-wide skill scores
        story.append(Paragraph("School-Wide Skill Scores", styles['SectionTitle']))
        skill_table = ReportService._create_skill_table(report_data.skill_summaries, styles)
        story.append(skill_table)
        story.append(Spacer(1, 12))
        
        # Class summaries
        if report_data.class_summaries:
            story.append(Paragraph("Class Summaries", styles['SectionTitle']))
            class_table = ReportService._create_class_summary_table(report_data.class_summaries, styles)
            story.append(class_table)
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
