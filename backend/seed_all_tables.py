"""Minimal database seed script.

Creates:
- 1 School
- 1 Admin
- 1 Teacher
- 2 Classes
- 20 Students (10 per class)
- Metrics data for school analytics
"""
from datetime import datetime, date, timedelta
import random
from app import create_app, db
from app.models import School, Teacher, Class, Child, SchoolWeeklyMetrics, ChildDailyMetrics, EventRaw


def clear_all_tables():
    """Clear all existing data from core tables."""
    print("Clearing tables...")
    
    EventRaw.query.delete()
    ChildDailyMetrics.query.delete()
    SchoolWeeklyMetrics.query.delete()
    Child.query.delete()
    Class.query.delete()
    Teacher.query.delete()
    School.query.delete()
    
    db.session.commit()
    print("✓ Tables cleared")


def seed_school():
    """Create 1 school."""
    print("\nSeeding School...")
    
    school = School(
        name="Sunshine Montessori Academy",
        logo="sunshine_logo",
        primary_color="#FF9800",
        enrolled_families=20,
        app_installs=20
    )
    db.session.add(school)
    db.session.commit()
    
    print(f"✓ Created school: {school.name}")
    return school


def seed_teachers(school):
    """Create 1 admin and 1 teacher."""
    print("Seeding Teachers...")
    
    admin = Teacher(
        school_id=school.id,
        email="admin@sunshine.edu",
        name="Sarah Johnson",
        role="admin"
    )
    admin.set_password("password123")
    db.session.add(admin)
    
    teacher = Teacher(
        school_id=school.id,
        email="teacher@sunshine.edu",
        name="Maria Garcia",
        role="teacher"
    )
    teacher.set_password("password123")
    db.session.add(teacher)
    
    db.session.commit()
    print(f"✓ Created admin: {admin.name}")
    print(f"✓ Created teacher: {teacher.name}")
    return admin, teacher


def seed_classes(school, teacher):
    """Create 2 classes."""
    print("Seeding Classes...")
    
    class1 = Class(
        school_id=school.id,
        name="Primary Room A",
        grade_level="Primary",
        primary_teacher_id=teacher.id
    )
    db.session.add(class1)
    
    class2 = Class(
        school_id=school.id,
        name="Primary Room B",
        grade_level="Primary",
        primary_teacher_id=teacher.id
    )
    db.session.add(class2)
    
    db.session.commit()
    print(f"✓ Created class: {class1.name}")
    print(f"✓ Created class: {class2.name}")
    return class1, class2


def seed_children(class1, class2):
    """Create 20 children, 10 per class."""
    print("Seeding Children...")
    
    children_names = [
        "Emma", "Liam", "Olivia", "Noah", "Ava",
        "Ethan", "Sophia", "Mason", "Isabella", "William",
        "James", "Charlotte", "Benjamin", "Amelia", "Lucas",
        "Mia", "Henry", "Harper", "Alexander", "Evelyn"
    ]
    
    children = []
    for i, name in enumerate(children_names):
        # First 10 in class1, next 10 in class2
        class_id = class1.id if i < 10 else class2.id
        
        child = Child(
            class_id=class_id,
            display_name=name,
            age=4 + (i % 3)  # Ages 4-6
        )
        children.append(child)
        db.session.add(child)
    
    db.session.commit()
    print(f"✓ Created {len(children)} children (10 in {class1.name}, 10 in {class2.name})")
    return children


def seed_events_and_metrics(school, children):
    """Create event data and metrics for analytics."""
    print("Seeding Events and Metrics...")
    
    skills = ['attention', 'patience', 'sensory', 'emotionAwareness', 'bodyAwareness']
    
    # Refresh children to ensure child_code is loaded
    db.session.refresh(school)
    for child in children:
        db.session.refresh(child)
    
    # Create events for the last 30 days
    events_created = 0
    for child in children:
        for day_offset in range(30):
            event_date = date.today() - timedelta(days=day_offset)
            # Random 1-5 sessions per day
            num_sessions = random.randint(1, 5)
            
            for _ in range(num_sessions):
                event = EventRaw(
                    child_code=child.child_code,
                    puzzle_id=f"puzzle_{random.randint(1, 20)}",
                    skill_tags=random.sample(skills, k=random.randint(1, 3)),
                    started_at=datetime.combine(event_date, datetime.min.time()),
                    ended_at=datetime.combine(event_date, datetime.min.time()) + timedelta(minutes=random.randint(2, 10)),
                    completed=random.choice([True, False])
                )
                db.session.add(event)
                events_created += 1
    
    db.session.commit()
    print(f"✓ Created {events_created} event records")
    
    # Create daily metrics for children
    metrics_created = 0
    for child in children:
        for day_offset in range(30):
            metric_date = date.today() - timedelta(days=day_offset)
            
            # Random skill scores
            skill_scores = {skill: round(random.uniform(0.5, 1.0), 2) for skill in skills}
            
            metric = ChildDailyMetrics(
                child_id=child.id,
                date=metric_date,
                sessions_count=random.randint(1, 5),
                avg_duration=random.randint(120, 600),  # 2-10 minutes
                skill_scores=skill_scores
            )
            db.session.add(metric)
            metrics_created += 1
    
    db.session.commit()
    print(f"✓ Created {metrics_created} daily metrics records")
    
    # Create school weekly metrics for the last 4 weeks
    for week_offset in range(4):
        week_start = date.today() - timedelta(weeks=week_offset, days=date.today().weekday())
        
        # Calculate metrics based on children data
        avg_sessions = sum(random.randint(2, 4) for _ in children) / len(children)
        top_skills = random.sample(skills, k=5)
        
        metrics_data = {
            'app_install_rate': round(random.uniform(75, 95), 1),
            'avg_daily_sessions': round(avg_sessions, 1),
            'top_skills': top_skills,
            'weekly_engagement': [round(random.uniform(0.6, 1.0), 2) for _ in range(4)],
            'total_teachers': 2,
            'total_classes': 2,
            'total_students': len(children)
        }
        
        school_metric = SchoolWeeklyMetrics(
            school_id=school.id,
            week_start_date=week_start,
            metrics=metrics_data
        )
        db.session.add(school_metric)
    
    db.session.commit()
    print(f"✓ Created 4 school weekly metrics records")





def seed_all():
    """Run all seed functions."""
    print("\n" + "="*60)
    print("SEEDING DATABASE")
    print("="*60)
    
    clear_all_tables()
    
    school = seed_school()
    admin, teacher = seed_teachers(school)
    class1, class2 = seed_classes(school, teacher)
    children = seed_children(class1, class2)
    seed_events_and_metrics(school, children)
    
    print("\n" + "="*60)
    print("SEEDING COMPLETE!")
    print("="*60)
    print(f"""
Summary:
  ✓ 1 School
  ✓ 1 Admin (email: admin@sunshine.edu, password: password123)
  ✓ 1 Teacher (email: teacher@sunshine.edu, password: password123)
  ✓ 2 Classes
  ✓ 20 Children (10 per class)
  ✓ Events and Metrics data for analytics

Total: 24+ records with analytics data
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
