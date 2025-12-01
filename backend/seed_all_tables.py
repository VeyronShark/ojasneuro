"""Enhanced database seed script with 10 records for ALL tables.

This script populates ALL database tables with 10 dummy records each:
- Schools, Teachers, Classes, Children
- EventRaw (raw app interaction events)
- ParentLink (consent records)
- ChildDailyMetrics, ClassWeeklyMetrics, SchoolWeeklyMetrics
- ActivitySuggestion, MessageTemplate
"""
from datetime import datetime, date, timedelta
import random
from app import create_app, db
from app.models import (
    School, Teacher, Class, Child, EventRaw, ParentLink,
    ChildDailyMetrics, ClassWeeklyMetrics, SchoolWeeklyMetrics,
    ActivitySuggestion, MessageTemplate
)


def clear_all_tables():
    """Clear all existing data from all tables."""
    print("Clearing all tables...")
    
    # Delete in reverse order of dependencies
    SchoolWeeklyMetrics.query.delete()
    ClassWeeklyMetrics.query.delete()
    ChildDailyMetrics.query.delete()
    ParentLink.query.delete()
    EventRaw.query.delete()
    MessageTemplate.query.delete()
    ActivitySuggestion.query.delete()
    Child.query.delete()
    Class.query.delete()
    Teacher.query.delete()
    School.query.delete()
    
    db.session.commit()
    print("✓ All tables cleared")


def seed_schools():
    """Create 10 schools."""
    print("\nSeeding Schools...")
    
    schools_data = [
        {"name": "Sunshine Montessori Academy", "logo": "sunshine_logo", "color": "#FF9800", "families": 45, "installs": 38},
        {"name": "Green Valley Montessori", "logo": "greenvalley_logo", "color": "#4CAF50", "families": 32, "installs": 28},
        {"name": "Little Stars Learning Center", "logo": "littlestars_logo", "color": "#2196F3", "families": 58, "installs": 52},
        {"name": "Rainbow Bridge Academy", "logo": "rainbow_logo", "color": "#9C27B0", "families": 41, "installs": 35},
        {"name": "Bright Minds Montessori", "logo": "brightminds_logo", "color": "#F44336", "families": 37, "installs": 31},
        {"name": "Peaceful Pathways School", "logo": "peaceful_logo", "color": "#00BCD4", "families": 29, "installs": 24},
        {"name": "Discovery Kids Academy", "logo": "discovery_logo", "color": "#FF5722", "families": 52, "installs": 47},
        {"name": "Harmony House Learning", "logo": "harmony_logo", "color": "#8BC34A", "families": 44, "installs": 39},
        {"name": "Wisdom Tree Montessori", "logo": "wisdom_logo", "color": "#3F51B5", "families": 36, "installs": 30},
        {"name": "Creative Minds Center", "logo": "creative_logo", "color": "#E91E63", "families": 48, "installs": 42},
    ]
    
    schools = []
    for data in schools_data:
        school = School(
            name=data["name"],
            logo=data["logo"],
            primary_color=data["color"],
            enrolled_families=data["families"],
            app_installs=data["installs"]
        )
        schools.append(school)
        db.session.add(school)
    
    db.session.commit()
    print(f"✓ Created {len(schools)} schools")
    return schools


def seed_teachers(schools):
    """Create 10 teachers across schools."""
    print("Seeding Teachers...")
    
    teachers_data = [
        {"school_idx": 0, "email": "sarah.johnson@sunshine.edu", "name": "Sarah Johnson", "role": "admin"},
        {"school_idx": 0, "email": "maria.garcia@sunshine.edu", "name": "Maria Garcia", "role": "teacher"},
        {"school_idx": 1, "email": "emily.chen@greenvalley.edu", "name": "Emily Chen", "role": "admin"},
        {"school_idx": 2, "email": "david.wilson@littlestars.edu", "name": "David Wilson", "role": "teacher"},
        {"school_idx": 3, "email": "lisa.anderson@rainbow.edu", "name": "Lisa Anderson", "role": "teacher"},
        {"school_idx": 4, "email": "michael.brown@brightminds.edu", "name": "Michael Brown", "role": "admin"},
        {"school_idx": 5, "email": "jennifer.lee@peaceful.edu", "name": "Jennifer Lee", "role": "teacher"},
        {"school_idx": 6, "email": "robert.taylor@discovery.edu", "name": "Robert Taylor", "role": "teacher"},
        {"school_idx": 7, "email": "amanda.white@harmony.edu", "name": "Amanda White", "role": "admin"},
        {"school_idx": 8, "email": "james.martin@wisdom.edu", "name": "James Martin", "role": "teacher"},
    ]
    
    teachers = []
    for data in teachers_data:
        teacher = Teacher(
            school_id=schools[data["school_idx"]].id,
            email=data["email"],
            name=data["name"],
            role=data["role"]
        )
        teacher.set_password("password123")
        teachers.append(teacher)
        db.session.add(teacher)
    
    db.session.commit()
    print(f"✓ Created {len(teachers)} teachers")
    return teachers


def seed_classes(schools, teachers):
    """Create 10 classes across schools."""
    print("Seeding Classes...")
    
    classes_data = [
        {"school_idx": 0, "name": "Toddler Room A", "grade": "Toddler", "teacher_idx": 1},
        {"school_idx": 0, "name": "Primary Room 1", "grade": "Primary", "teacher_idx": 1},
        {"school_idx": 1, "name": "Infant Community", "grade": "Infant", "teacher_idx": 2},
        {"school_idx": 2, "name": "Butterfly Room", "grade": "Toddler", "teacher_idx": 3},
        {"school_idx": 3, "name": "Rainbow Room", "grade": "Primary", "teacher_idx": 4},
        {"school_idx": 4, "name": "Sunshine Class", "grade": "Primary", "teacher_idx": 5},
        {"school_idx": 5, "name": "Peace Circle", "grade": "Toddler", "teacher_idx": 6},
        {"school_idx": 6, "name": "Explorer's Den", "grade": "Primary", "teacher_idx": 7},
        {"school_idx": 7, "name": "Harmony Hall", "grade": "Primary", "teacher_idx": 8},
        {"school_idx": 8, "name": "Wisdom Wing", "grade": "Toddler", "teacher_idx": 9},
    ]
    
    classes = []
    for data in classes_data:
        class_ = Class(
            school_id=schools[data["school_idx"]].id,
            name=data["name"],
            grade_level=data["grade"],
            primary_teacher_id=teachers[data["teacher_idx"]].id
        )
        classes.append(class_)
        db.session.add(class_)
    
    db.session.commit()
    print(f"✓ Created {len(classes)} classes")
    return classes


def seed_children(classes):
    """Create 10 children across classes."""
    print("Seeding Children...")
    
    children_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava",
        "Ethan", "Sophia", "Mason", "Isabella", "William"
    ]
    
    children = []
    for i, name in enumerate(children_names):
        child = Child(
            class_id=classes[i % len(classes)].id,
            display_name=name,
            age=3 + (i % 4)  # Ages 3-6
        )
        children.append(child)
        db.session.add(child)
    
    db.session.commit()
    print(f"✓ Created {len(children)} children")
    return children


def seed_events(children):
    """Create 10 raw events."""
    print("Seeding EventRaw...")
    
    puzzles = ["puzzle_001", "puzzle_002", "puzzle_003", "puzzle_004", "puzzle_005"]
    skills = ["attention", "patience", "sensory", "emotionAwareness", "bodyAwareness"]
    
    events = []
    base_time = datetime.utcnow() - timedelta(days=7)
    
    for i in range(10):
        child = children[i % len(children)]
        started = base_time + timedelta(hours=i * 2)
        duration = random.randint(60, 300)  # 1-5 minutes
        ended = started + timedelta(seconds=duration)
        
        event = EventRaw(
            child_code=child.child_code,
            puzzle_id=random.choice(puzzles),
            skill_tags=random.sample(skills, k=random.randint(1, 3)),
            started_at=started,
            ended_at=ended,
            completed=random.choice([True, True, True, False])  # 75% completion rate
        )
        events.append(event)
        db.session.add(event)
    
    db.session.commit()
    print(f"✓ Created {len(events)} raw events")
    return events


def seed_parent_links(children):
    """Create 10 parent-child consent links."""
    print("Seeding ParentLink...")
    
    consent_statuses = ["granted", "granted", "granted", "pending", "denied"]
    consent_scopes = ["full", "limited", "full", None, None]
    
    parent_links = []
    for i in range(10):
        child = children[i % len(children)]
        status = consent_statuses[i % len(consent_statuses)]
        scope = consent_scopes[i % len(consent_scopes)]
        
        parent_link = ParentLink(
            child_id=child.id,
            parent_id=1000 + i,  # Dummy parent IDs
            consent_status=status,
            consent_timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if status != "pending" else None,
            consent_scope=scope
        )
        parent_links.append(parent_link)
        db.session.add(parent_link)
    
    db.session.commit()
    print(f"✓ Created {len(parent_links)} parent links")
    return parent_links


def seed_child_daily_metrics(children):
    """Create 10 child daily metrics."""
    print("Seeding ChildDailyMetrics...")
    
    metrics = []
    base_date = date.today() - timedelta(days=10)
    
    for i in range(10):
        child = children[i % len(children)]
        metric_date = base_date + timedelta(days=i)
        
        metric = ChildDailyMetrics(
            child_id=child.id,
            date=metric_date,
            sessions_count=random.randint(1, 5),
            avg_duration=random.randint(120, 300),  # 2-5 minutes
            skill_scores={
                "attention": round(random.uniform(0.5, 1.0), 2),
                "patience": round(random.uniform(0.5, 1.0), 2),
                "sensory": round(random.uniform(0.5, 1.0), 2),
                "emotionAwareness": round(random.uniform(0.5, 1.0), 2),
                "bodyAwareness": round(random.uniform(0.5, 1.0), 2),
            }
        )
        metrics.append(metric)
        db.session.add(metric)
    
    db.session.commit()
    print(f"✓ Created {len(metrics)} child daily metrics")
    return metrics


def seed_class_weekly_metrics(classes):
    """Create 10 class weekly metrics."""
    print("Seeding ClassWeeklyMetrics...")
    
    engagement_levels = ["low", "medium", "high"]
    metrics = []
    base_date = date.today() - timedelta(weeks=10)
    
    for i in range(10):
        class_ = classes[i % len(classes)]
        week_start = base_date + timedelta(weeks=i)
        
        metric = ClassWeeklyMetrics(
            class_id=class_.id,
            week_start_date=week_start,
            engagement_level=random.choice(engagement_levels),
            avg_skill_scores={
                "attention": round(random.uniform(0.6, 0.9), 2),
                "patience": round(random.uniform(0.6, 0.9), 2),
                "sensory": round(random.uniform(0.6, 0.9), 2),
                "emotionAwareness": round(random.uniform(0.6, 0.9), 2),
                "bodyAwareness": round(random.uniform(0.6, 0.9), 2),
            }
        )
        metrics.append(metric)
        db.session.add(metric)
    
    db.session.commit()
    print(f"✓ Created {len(metrics)} class weekly metrics")
    return metrics


def seed_school_weekly_metrics(schools):
    """Create 10 school weekly metrics."""
    print("Seeding SchoolWeeklyMetrics...")
    
    metrics = []
    base_date = date.today() - timedelta(weeks=10)
    
    for i in range(10):
        school = schools[i % len(schools)]
        week_start = base_date + timedelta(weeks=i)
        
        metric = SchoolWeeklyMetrics(
            school_id=school.id,
            week_start_date=week_start,
            metrics={
                "total_sessions": random.randint(50, 200),
                "active_children": random.randint(20, 50),
                "avg_engagement": round(random.uniform(0.6, 0.9), 2),
                "completion_rate": round(random.uniform(0.7, 0.95), 2),
                "avg_skill_scores": {
                    "attention": round(random.uniform(0.6, 0.9), 2),
                    "patience": round(random.uniform(0.6, 0.9), 2),
                    "sensory": round(random.uniform(0.6, 0.9), 2),
                    "emotionAwareness": round(random.uniform(0.6, 0.9), 2),
                    "bodyAwareness": round(random.uniform(0.6, 0.9), 2),
                }
            }
        )
        metrics.append(metric)
        db.session.add(metric)
    
    db.session.commit()
    print(f"✓ Created {len(metrics)} school weekly metrics")
    return metrics


def seed_activity_suggestions():
    """Create 10 activity suggestions."""
    print("Seeding ActivitySuggestion...")
    
    suggestions_data = [
        {"skill": "attention", "text": "Practice the 'Silence Game' where children try to be completely quiet and still for increasing periods."},
        {"skill": "attention", "text": "Use sorting activities with small objects like beads or buttons, requiring careful focus on details."},
        {"skill": "patience", "text": "Practice waiting turns during group activities, using a visual timer to help children understand time."},
        {"skill": "patience", "text": "Engage in gardening activities where children plant seeds and observe growth over time."},
        {"skill": "sensory", "text": "Create a sensory bin with different textures (rice, sand, water beads) for tactile exploration."},
        {"skill": "sensory", "text": "Practice sound discrimination activities using musical instruments or sound cylinders."},
        {"skill": "emotionAwareness", "text": "Use emotion cards or pictures to help children identify and name different feelings."},
        {"skill": "emotionAwareness", "text": "Read stories about characters experiencing different emotions and discuss how they might feel."},
        {"skill": "bodyAwareness", "text": "Practice yoga poses designed for children, focusing on body position and balance."},
        {"skill": "bodyAwareness", "text": "Use 'Simon Says' games that focus on different body parts and movements."},
    ]
    
    suggestions = []
    for data in suggestions_data:
        suggestion = ActivitySuggestion(
            skill_tag=data["skill"],
            activity_text=data["text"]
        )
        suggestions.append(suggestion)
        db.session.add(suggestion)
    
    db.session.commit()
    print(f"✓ Created {len(suggestions)} activity suggestions")
    return suggestions


def seed_message_templates():
    """Create 10 message templates."""
    print("Seeding MessageTemplate...")
    
    templates_data = [
        {"type": "parent_welcome", "lang": "en", "content": "Welcome to our mindfulness learning program! We're excited to have your child participate."},
        {"type": "parent_welcome", "lang": "es", "content": "¡Bienvenido a nuestro programa de aprendizaje de mindfulness! Estamos emocionados de tener a su hijo participando."},
        {"type": "parent_progress", "lang": "en", "content": "We wanted to share an update on your child's progress in our mindfulness program."},
        {"type": "parent_progress", "lang": "es", "content": "Queríamos compartir una actualización sobre el progreso de su hijo en nuestro programa de mindfulness."},
        {"type": "parent_consent", "lang": "en", "content": "We are requesting your consent to collect and display your child's individual learning data."},
        {"type": "handout_app_guide", "lang": "en", "content": "# Mindfulness App Parent Guide\n\nGetting started with the app is easy..."},
        {"type": "handout_skills", "lang": "en", "content": "# Understanding the Five Core Skills\n\nOur program focuses on five essential skills..."},
        {"type": "handout_ptm", "lang": "en", "content": "# Parent-Teacher Meeting Preparation Guide\n\nBefore the meeting, please review..."},
        {"type": "reminder_activity", "lang": "en", "content": "Reminder: Your child has new mindfulness activities available in the app today!"},
        {"type": "celebration", "lang": "en", "content": "Congratulations! Your child has completed 10 mindfulness activities this week!"},
    ]
    
    templates = []
    for data in templates_data:
        template = MessageTemplate(
            template_type=data["type"],
            language=data["lang"],
            content=data["content"]
        )
        templates.append(template)
        db.session.add(template)
    
    db.session.commit()
    print(f"✓ Created {len(templates)} message templates")
    return templates


def seed_all():
    """Run all seed functions to populate ALL tables with 10 records each."""
    print("\n" + "="*60)
    print("SEEDING ALL TABLES WITH 10 DUMMY RECORDS")
    print("="*60)
    
    clear_all_tables()
    
    # Seed in order of dependencies
    schools = seed_schools()
    teachers = seed_teachers(schools)
    classes = seed_classes(schools, teachers)
    children = seed_children(classes)
    
    # Seed event and consent data
    events = seed_events(children)
    parent_links = seed_parent_links(children)
    
    # Seed metrics
    child_metrics = seed_child_daily_metrics(children)
    class_metrics = seed_class_weekly_metrics(classes)
    school_metrics = seed_school_weekly_metrics(schools)
    
    # Seed templates
    suggestions = seed_activity_suggestions()
    templates = seed_message_templates()
    
    print("\n" + "="*60)
    print("SEEDING COMPLETE!")
    print("="*60)
    print(f"""
Summary:
  ✓ {len(schools)} Schools
  ✓ {len(teachers)} Teachers
  ✓ {len(classes)} Classes
  ✓ {len(children)} Children
  ✓ {len(events)} EventRaw records
  ✓ {len(parent_links)} ParentLink records
  ✓ {len(child_metrics)} ChildDailyMetrics records
  ✓ {len(class_metrics)} ClassWeeklyMetrics records
  ✓ {len(school_metrics)} SchoolWeeklyMetrics records
  ✓ {len(suggestions)} ActivitySuggestion records
  ✓ {len(templates)} MessageTemplate records

Total: 110 records across 11 tables
    """)


def main():
    """Main entry point for the seed script."""
    # Use production config to read DATABASE_URL from .env
    app = create_app('production')
    
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        seed_all()


if __name__ == '__main__':
    main()
