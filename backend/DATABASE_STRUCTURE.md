# Database Structure Overview

This document provides an overview of all database tables and their relationships in the educational mindfulness platform.

## Tables Summary

The database consists of **11 tables** organized into the following categories:

### 1. Core Entity Tables (4 tables)

#### Schools
Multi-tenant educational institutions
- **Fields**: id, name, logo, primary_color, enrolled_families, app_installs
- **Relationships**: Has many classes, teachers, weekly_metrics

#### Teachers
Authenticated users (teachers and admins)
- **Fields**: id, school_id, email, password_hash, name, role
- **Relationships**: Belongs to school, has many primary_classes

#### Classes
Groups of children within a school
- **Fields**: id, school_id, name, grade_level, primary_teacher_id
- **Relationships**: Belongs to school and teacher, has many children

#### Children
Students enrolled in classes (pseudonymous identification)
- **Fields**: id, class_id, display_name, child_code (unique), age
- **Relationships**: Belongs to class, has many daily_metrics, parent_links

### 2. Event & Consent Tables (2 tables)

#### EventRaw
Raw app interaction events from mobile app
- **Fields**: id, child_code, puzzle_id, skill_tags (JSON), started_at, ended_at, completed
- **Purpose**: Stores all child interactions with puzzles/activities
- **Privacy**: Uses only pseudonymous child_code, no PII

#### ParentLink
Parent-child relationships with consent tracking
- **Fields**: id, child_id, parent_id, consent_status, consent_timestamp, consent_scope
- **Consent Statuses**: pending, granted, denied
- **Purpose**: Tracks parental authorization for data collection

### 3. Metrics Tables (3 tables)

#### ChildDailyMetrics
Aggregated daily metrics per child
- **Fields**: id, child_id, date, sessions_count, avg_duration, skill_scores (JSON)
- **Unique Constraint**: child_id + date
- **Purpose**: Pre-computed daily analytics for individual children

#### ClassWeeklyMetrics
Aggregated weekly metrics per class
- **Fields**: id, class_id, week_start_date, engagement_level, avg_skill_scores (JSON)
- **Unique Constraint**: class_id + week_start_date
- **Engagement Levels**: low, medium, high

#### SchoolWeeklyMetrics
Aggregated weekly metrics per school
- **Fields**: id, school_id, week_start_date, metrics (JSON)
- **Unique Constraint**: school_id + week_start_date
- **Purpose**: School-wide analytics and reporting

### 4. Template Tables (2 tables)

#### ActivitySuggestion
Activity recommendations for skill development
- **Fields**: id, skill_tag, activity_text
- **Skill Tags**: attention, patience, sensory, emotionAwareness, bodyAwareness
- **Purpose**: Provides teachers with activity ideas for each skill

#### MessageTemplate
Communication templates for parents
- **Fields**: id, template_type, language, content
- **Unique Constraint**: template_type + language
- **Template Types**: parent_welcome, parent_progress, parent_consent, handout_app_guide, handout_skills, handout_ptm, etc.
- **Languages**: en (English), es (Spanish), etc.

## Skill Tags

The platform tracks 5 core skills across all activities:
1. **attention** - Focus and concentration
2. **patience** - Self-regulation and waiting
3. **sensory** - Sensory awareness and discrimination
4. **emotionAwareness** - Emotional intelligence
5. **bodyAwareness** - Physical coordination and proprioception

## Data Flow

```
Mobile App → EventRaw (raw events with child_code)
                ↓
         Aggregation Process
                ↓
    ChildDailyMetrics (daily rollup)
                ↓
    ClassWeeklyMetrics (weekly class rollup)
                ↓
    SchoolWeeklyMetrics (weekly school rollup)
```

## Privacy & Security

- **Pseudonymous Identifiers**: Children are identified by `child_code` (e.g., "child_0bcd68b8c9034d05") in events
- **No GPS/Microphone Data**: Platform never collects location or audio data
- **Consent Tracking**: ParentLink table tracks parental authorization
- **Password Security**: Teacher passwords are hashed using werkzeug.security
- **Multi-tenant Isolation**: Each school's data is isolated via school_id foreign keys

## Current Seed Data

All tables have been populated with **10 dummy records each** (110 total records):
- 10 Schools with varying enrollment sizes
- 10 Teachers across different schools (mix of admins and teachers)
- 10 Classes with different grade levels
- 10 Children with unique child_codes
- 10 EventRaw records with various puzzles and skills
- 10 ParentLink records with different consent statuses
- 10 ChildDailyMetrics records with skill scores
- 10 ClassWeeklyMetrics records with engagement levels
- 10 SchoolWeeklyMetrics records with comprehensive metrics
- 10 ActivitySuggestion records covering all 5 skills
- 10 MessageTemplate records in multiple languages

## Running the Seed Script

To populate the database with dummy data:

```bash
cd backend
python3 seed_all_tables.py
```

This will:
1. Clear all existing data
2. Insert 10 records into each table
3. Display a summary of created records
