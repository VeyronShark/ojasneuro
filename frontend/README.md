# School Dashboard - Frontend

A clean, minimal React application for teacher and school admin dashboards.

## Features

- **Role-based access**: Admin and Teacher views
- **Admin Dashboard**: School-wide insights, engagement metrics, top skills
- **Teacher Dashboard**: Class overview, student engagement, alerts
- **Class View**: Student list with filters, engagement heatmap
- **Child Profile**: Individual student insights, skill radar, weekly activity
- **Skill Suggestions**: Montessori/mindfulness classroom activities
- **Parent Communication**: Templates for WhatsApp, email, and handouts

## Tech Stack

- React 18
- React Router 6
- Vite
- Pure CSS (no external UI libraries)

## Getting Started

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open browser to `http://localhost:5173`

## Demo Credentials

- **Admin**: admin@school.com / admin123
- **Teacher**: teacher@school.com / teacher123

## Dummy Data

All data is stored in `src/data/dummyData.js` as a const dictionary (JSON format).
You can easily modify this file to change:
- User credentials
- School information
- Student data
- Engagement metrics
- Skill suggestions
- Communication templates

## Design Principles

- Light theme with minimal transitions
- Clean, simple interface
- No leaderboards or comparisons
- Focus on support and reinforcement
- Mobile-friendly (responsive design)
- Traffic light colors for engagement levels
- Non-technical language for insights
