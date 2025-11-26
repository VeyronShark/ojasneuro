"""Database seed script for initial data.

This script populates the database with sample data for development and testing:
- Sample schools, teachers, classes, and children
- Activity suggestions for all skill tags
- Message templates in English

Requirements: 5.3 - Activity suggestions for skills
Requirements: 8.1 - Communication templates for parents
"""
from app import create_app, db
from app.models import (
    School, Teacher, Class, Child,
    ActivitySuggestion, MessageTemplate
)


def seed_schools():
    """Create sample schools."""
    schools = [
        School(
            name="Sunshine Montessori Academy",
            logo="sunshine_logo",
            primary_color="#FF9800",
            enrolled_families=45,
            app_installs=38
        ),
        School(
            name="Green Valley Montessori",
            logo="greenvalley_logo",
            primary_color="#4CAF50",
            enrolled_families=32,
            app_installs=28
        ),
        School(
            name="Little Stars Learning Center",
            logo="littlestars_logo",
            primary_color="#2196F3",
            enrolled_families=58,
            app_installs=52
        ),
    ]
    
    for school in schools:
        db.session.add(school)
    db.session.commit()
    
    print(f"Created {len(schools)} schools")
    return schools


def seed_teachers(schools):
    """Create sample teachers for each school."""
    teachers_data = [
        # Sunshine Montessori Academy teachers
        {"school": schools[0], "email": "admin@sunshine.edu", "name": "Sarah Johnson", "role": "admin", "password": "admin123"},
        {"school": schools[0], "email": "maria@sunshine.edu", "name": "Maria Garcia", "role": "teacher", "password": "teacher123"},
        {"school": schools[0], "email": "john@sunshine.edu", "name": "John Smith", "role": "teacher", "password": "teacher123"},
        
        # Green Valley Montessori teachers
        {"school": schools[1], "email": "admin@greenvalley.edu", "name": "Emily Chen", "role": "admin", "password": "admin123"},
        {"school": schools[1], "email": "david@greenvalley.edu", "name": "David Wilson", "role": "teacher", "password": "teacher123"},
        
        # Little Stars Learning Center teachers
        {"school": schools[2], "email": "admin@littlestars.edu", "name": "Michael Brown", "role": "admin", "password": "admin123"},
        {"school": schools[2], "email": "lisa@littlestars.edu", "name": "Lisa Anderson", "role": "teacher", "password": "teacher123"},
        {"school": schools[2], "email": "james@littlestars.edu", "name": "James Taylor", "role": "teacher", "password": "teacher123"},
    ]
    
    teachers = []
    for data in teachers_data:
        teacher = Teacher(
            school_id=data["school"].id,
            email=data["email"],
            name=data["name"],
            role=data["role"]
        )
        teacher.set_password(data["password"])
        teachers.append(teacher)
        db.session.add(teacher)
    
    db.session.commit()
    print(f"Created {len(teachers)} teachers")
    return teachers


def seed_classes(schools, teachers):
    """Create sample classes for each school."""
    # Group teachers by school
    teachers_by_school = {}
    for teacher in teachers:
        if teacher.school_id not in teachers_by_school:
            teachers_by_school[teacher.school_id] = []
        if teacher.role == 'teacher':
            teachers_by_school[teacher.school_id].append(teacher)
    
    classes_data = [
        # Sunshine Montessori Academy classes
        {"school": schools[0], "name": "Toddler Room A", "grade_level": "Toddler", "teacher_idx": 0},
        {"school": schools[0], "name": "Primary Room 1", "grade_level": "Primary", "teacher_idx": 1},
        {"school": schools[0], "name": "Primary Room 2", "grade_level": "Primary", "teacher_idx": 0},
        
        # Green Valley Montessori classes
        {"school": schools[1], "name": "Infant Community", "grade_level": "Infant", "teacher_idx": 0},
        {"school": schools[1], "name": "Children's House", "grade_level": "Primary", "teacher_idx": 0},
        
        # Little Stars Learning Center classes
        {"school": schools[2], "name": "Butterfly Room", "grade_level": "Toddler", "teacher_idx": 0},
        {"school": schools[2], "name": "Rainbow Room", "grade_level": "Primary", "teacher_idx": 1},
        {"school": schools[2], "name": "Sunshine Room", "grade_level": "Primary", "teacher_idx": 0},
    ]
    
    classes = []
    for data in classes_data:
        school_teachers = teachers_by_school.get(data["school"].id, [])
        teacher_id = None
        if school_teachers and data["teacher_idx"] < len(school_teachers):
            teacher_id = school_teachers[data["teacher_idx"]].id
        
        class_ = Class(
            school_id=data["school"].id,
            name=data["name"],
            grade_level=data["grade_level"],
            primary_teacher_id=teacher_id
        )
        classes.append(class_)
        db.session.add(class_)
    
    db.session.commit()
    print(f"Created {len(classes)} classes")
    return classes


def seed_children(classes):
    """Create sample children for each class."""
    children_names = [
        # Names for variety
        "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
        "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
        "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Luna", "Sebastian",
        "Ella", "Jack", "Chloe", "Aiden", "Penelope", "Owen", "Layla", "Samuel"
    ]
    
    ages_by_grade = {
        "Infant": [1, 2],
        "Toddler": [2, 3],
        "Primary": [3, 4, 5, 6]
    }
    
    children = []
    name_idx = 0
    
    for class_ in classes:
        # 4-6 children per class
        num_children = 4 + (class_.id % 3)
        ages = ages_by_grade.get(class_.grade_level, [4, 5])
        
        for i in range(num_children):
            name = children_names[name_idx % len(children_names)]
            age = ages[i % len(ages)]
            
            child = Child(
                class_id=class_.id,
                display_name=name,
                age=age
            )
            children.append(child)
            db.session.add(child)
            name_idx += 1
    
    db.session.commit()
    print(f"Created {len(children)} children")
    return children


def seed_activity_suggestions():
    """Create activity suggestions for all skill tags.
    
    Skill tags: attention, patience, sensory, emotionAwareness, bodyAwareness
    Requirements: 5.3 - Activity suggestions for skills
    """
    suggestions = [
        # Attention skill activities
        ActivitySuggestion(
            skill_tag="attention",
            activity_text="Practice the 'Silence Game' where children try to be completely quiet and still for increasing periods of time."
        ),
        ActivitySuggestion(
            skill_tag="attention",
            activity_text="Use sorting activities with small objects like beads or buttons, requiring careful focus on details."
        ),
        ActivitySuggestion(
            skill_tag="attention",
            activity_text="Introduce 'I Spy' games that encourage sustained visual attention and concentration."
        ),
        ActivitySuggestion(
            skill_tag="attention",
            activity_text="Practice pouring water between containers, which requires careful attention to avoid spilling."
        ),
        ActivitySuggestion(
            skill_tag="attention",
            activity_text="Use puzzle activities with increasing complexity to build sustained attention skills."
        ),
        
        # Patience skill activities
        ActivitySuggestion(
            skill_tag="patience",
            activity_text="Practice waiting turns during group activities, using a visual timer to help children understand the passage of time."
        ),
        ActivitySuggestion(
            skill_tag="patience",
            activity_text="Engage in gardening activities where children plant seeds and observe growth over time."
        ),
        ActivitySuggestion(
            skill_tag="patience",
            activity_text="Use baking or cooking activities that require waiting for results (dough rising, cookies baking)."
        ),
        ActivitySuggestion(
            skill_tag="patience",
            activity_text="Practice threading beads or lacing cards, which require slow, deliberate movements."
        ),
        ActivitySuggestion(
            skill_tag="patience",
            activity_text="Introduce 'freeze dance' games where children must hold still when the music stops."
        ),
        
        # Sensory skill activities
        ActivitySuggestion(
            skill_tag="sensory",
            activity_text="Create a sensory bin with different textures (rice, sand, water beads) for tactile exploration."
        ),
        ActivitySuggestion(
            skill_tag="sensory",
            activity_text="Practice sound discrimination activities using musical instruments or sound cylinders."
        ),
        ActivitySuggestion(
            skill_tag="sensory",
            activity_text="Use the 'Mystery Bag' activity where children identify objects by touch alone."
        ),
        ActivitySuggestion(
            skill_tag="sensory",
            activity_text="Introduce smell jars with different scents for olfactory discrimination practice."
        ),
        ActivitySuggestion(
            skill_tag="sensory",
            activity_text="Practice color matching and grading activities using color tablets or paint chips."
        ),
        
        # Emotion Awareness skill activities
        ActivitySuggestion(
            skill_tag="emotionAwareness",
            activity_text="Use emotion cards or pictures to help children identify and name different feelings."
        ),
        ActivitySuggestion(
            skill_tag="emotionAwareness",
            activity_text="Read stories about characters experiencing different emotions and discuss how they might feel."
        ),
        ActivitySuggestion(
            skill_tag="emotionAwareness",
            activity_text="Create an 'emotion check-in' routine where children share how they're feeling each day."
        ),
        ActivitySuggestion(
            skill_tag="emotionAwareness",
            activity_text="Practice deep breathing exercises as a calming strategy when experiencing strong emotions."
        ),
        ActivitySuggestion(
            skill_tag="emotionAwareness",
            activity_text="Use role-playing scenarios to practice responding to different emotional situations."
        ),
        
        # Body Awareness skill activities
        ActivitySuggestion(
            skill_tag="bodyAwareness",
            activity_text="Practice yoga poses designed for children, focusing on body position and balance."
        ),
        ActivitySuggestion(
            skill_tag="bodyAwareness",
            activity_text="Use 'Simon Says' games that focus on different body parts and movements."
        ),
        ActivitySuggestion(
            skill_tag="bodyAwareness",
            activity_text="Practice walking on a line or balance beam to develop proprioceptive awareness."
        ),
        ActivitySuggestion(
            skill_tag="bodyAwareness",
            activity_text="Engage in obstacle courses that require crawling, climbing, and navigating spaces."
        ),
        ActivitySuggestion(
            skill_tag="bodyAwareness",
            activity_text="Use body tracing activities where children lie down and trace their outline, then label body parts."
        ),
    ]
    
    for suggestion in suggestions:
        db.session.add(suggestion)
    
    db.session.commit()
    print(f"Created {len(suggestions)} activity suggestions")
    return suggestions


def seed_message_templates():
    """Create message templates in English.
    
    Requirements: 8.1 - Communication templates for parents
    """
    templates = [
        # Parent message templates
        MessageTemplate(
            template_type="parent_welcome",
            language="en",
            content="""Dear Parent/Guardian,

Welcome to our mindfulness learning program! We're excited to have your child participate in this journey of self-discovery and skill development.

Our app-based activities are designed to help children develop:
- Attention and focus skills
- Patience and self-regulation
- Sensory awareness
- Emotional intelligence
- Body awareness and coordination

You can track your child's progress through our parent portal. If you have any questions, please don't hesitate to reach out to your child's teacher.

Warm regards,
The Teaching Team"""
        ),
        MessageTemplate(
            template_type="parent_progress",
            language="en",
            content="""Dear Parent/Guardian,

We wanted to share an update on your child's progress in our mindfulness program.

This week, your child has been working on developing their skills through various engaging activities. We've noticed growth in their ability to focus and regulate their emotions.

Key highlights:
- Completed multiple mindfulness activities
- Showed improvement in attention span
- Demonstrated positive engagement with peers

We encourage you to continue supporting these skills at home by:
- Practicing deep breathing together
- Creating quiet time for focused activities
- Discussing emotions and feelings openly

Thank you for your partnership in your child's development.

Best regards,
The Teaching Team"""
        ),
        MessageTemplate(
            template_type="parent_consent",
            language="en",
            content="""Dear Parent/Guardian,

We are requesting your consent to collect and display your child's individual learning data in our educational platform.

What data we collect:
- Activity completion records
- Skill development metrics
- Engagement patterns

How we use this data:
- To provide personalized learning insights
- To generate progress reports
- To help teachers support your child's development

Your child's privacy is our priority:
- All data is stored securely
- No GPS or microphone data is collected
- Data is identified by pseudonymous codes, not names

Please review and submit your consent through the parent portal.

Thank you,
The Administration Team"""
        ),
        # Handout templates
        MessageTemplate(
            template_type="handout_app_guide",
            language="en",
            content="""# Mindfulness App Parent Guide

## Getting Started

1. Download the app from your device's app store
2. Enter the school code provided by your teacher
3. Create your child's profile using their unique child code

## Daily Activities

The app offers various mindfulness activities:
- **Breathing exercises**: Calming activities for emotional regulation
- **Focus puzzles**: Games that build attention skills
- **Sensory exploration**: Activities engaging different senses
- **Movement activities**: Body awareness exercises

## Tips for Success

- Set a consistent time for app activities
- Create a quiet, distraction-free space
- Celebrate your child's efforts, not just completion
- Discuss the activities together afterward

## Support

For technical issues: support@mindfulnessapp.edu
For educational questions: Contact your child's teacher

Thank you for supporting your child's mindfulness journey!"""
        ),
        MessageTemplate(
            template_type="handout_skills",
            language="en",
            content="""# Understanding the Five Core Skills

Our mindfulness program focuses on developing five essential skills:

## 1. Attention
The ability to focus on a task and filter out distractions. Children practice this through concentration activities and the 'Silence Game'.

## 2. Patience
Learning to wait calmly and persist through challenges. Activities include turn-taking games and projects that unfold over time.

## 3. Sensory Awareness
Developing keen observation through all five senses. Children explore textures, sounds, smells, and visual details.

## 4. Emotion Awareness
Recognizing and naming feelings in oneself and others. We use emotion cards, stories, and daily check-ins.

## 5. Body Awareness
Understanding how our body moves and occupies space. Yoga, balance activities, and movement games support this skill.

## How You Can Help at Home

- Model mindful behavior
- Create opportunities for focused activities
- Discuss emotions openly
- Practice patience together
- Engage in sensory-rich experiences"""
        ),
        MessageTemplate(
            template_type="handout_ptm",
            language="en",
            content="""# Parent-Teacher Meeting Preparation Guide

## Before the Meeting

Please review:
- Your child's progress report in the parent portal
- Any questions or concerns you'd like to discuss
- Your child's experiences with the mindfulness activities at home

## During the Meeting

We will discuss:
- Your child's skill development across all five areas
- Specific strengths and areas for growth
- Strategies for supporting learning at home
- Goals for the upcoming period

## Questions to Consider

- How does my child engage with mindfulness activities at home?
- What changes have I noticed in my child's behavior?
- How can I better support my child's development?

## After the Meeting

- Review the action items discussed
- Implement suggested strategies at home
- Reach out if you have follow-up questions

We look forward to partnering with you in your child's growth!"""
        ),
    ]
    
    for template in templates:
        db.session.add(template)
    
    db.session.commit()
    print(f"Created {len(templates)} message templates")
    return templates


def clear_database():
    """Clear all existing data from the database."""
    # Delete in reverse order of dependencies
    MessageTemplate.query.delete()
    ActivitySuggestion.query.delete()
    Child.query.delete()
    Class.query.delete()
    Teacher.query.delete()
    School.query.delete()
    db.session.commit()
    print("Cleared existing data")


def seed_all(clear_existing=True):
    """Run all seed functions to populate the database.
    
    Args:
        clear_existing: If True, clear existing data before seeding
    """
    if clear_existing:
        clear_database()
    
    print("\n=== Seeding Database ===\n")
    
    # Seed in order of dependencies
    schools = seed_schools()
    teachers = seed_teachers(schools)
    classes = seed_classes(schools, teachers)
    children = seed_children(classes)
    
    # Seed templates and suggestions (no dependencies)
    seed_activity_suggestions()
    seed_message_templates()
    
    print("\n=== Seeding Complete ===")
    print(f"Total: {len(schools)} schools, {len(teachers)} teachers, "
          f"{len(classes)} classes, {len(children)} children")


def main():
    """Main entry point for the seed script."""
    app = create_app('development')
    
    with app.app_context():
        seed_all(clear_existing=True)


if __name__ == '__main__':
    main()
