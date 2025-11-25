export const DUMMY_DATA = {
  users: {
    admin: {
      id: 1,
      email: "admin@school.com",
      password: "admin123",
      role: "admin",
      name: "Principal Smith",
      schoolId: 1
    },
    teacher: {
      id: 2,
      email: "teacher@school.com",
      password: "teacher123",
      role: "teacher",
      name: "Ms. Johnson",
      schoolId: 1,
      classIds: [1, 2]
    }
  },

  school: {
    id: 1,
    name: "Sunshine Montessori School",
    logo: "🏫",
    primaryColor: "#4a90e2",
    enrolledFamilies: 120,
    appInstalls: 95
  },

  classes: [
    { id: 1, name: "Nursery A", teacherId: 2, studentCount: 15 },
    { id: 2, name: "KG-B", teacherId: 2, studentCount: 18 }
  ],

  students: [
    {
      id: 1,
      name: "Emma Wilson",
      classId: 1,
      age: 4,
      engagement: "high",
      avgSessionsPerDay: 2.3,
      trend: "up",
      lastActive: "2024-11-24",
      skills: {
        attention: "high",
        patience: "medium",
        sensory: "high",
        emotionAwareness: "medium",
        bodyAwareness: "high"
      },
      weeklyActivity: [2, 3, 2, 3, 2, 2, 3]
    },
    {
      id: 2,
      name: "Liam Chen",
      classId: 1,
      age: 4,
      engagement: "medium",
      avgSessionsPerDay: 1.4,
      trend: "stable",
      lastActive: "2024-11-23",
      skills: {
        attention: "medium",
        patience: "low",
        sensory: "high",
        emotionAwareness: "medium",
        bodyAwareness: "medium"
      },
      weeklyActivity: [1, 2, 1, 1, 2, 1, 2]
    },
    {
      id: 3,
      name: "Sophia Patel",
      classId: 1,
      age: 3,
      engagement: "low",
      avgSessionsPerDay: 0.6,
      trend: "down",
      lastActive: "2024-11-20",
      skills: {
        attention: "low",
        patience: "low",
        sensory: "medium",
        emotionAwareness: "low",
        bodyAwareness: "medium"
      },
      weeklyActivity: [0, 1, 0, 1, 0, 0, 1]
    },
    {
      id: 4,
      name: "Noah Martinez",
      classId: 2,
      age: 5,
      engagement: "high",
      avgSessionsPerDay: 2.8,
      trend: "up",
      lastActive: "2024-11-24",
      skills: {
        attention: "high",
        patience: "high",
        sensory: "medium",
        emotionAwareness: "high",
        bodyAwareness: "high"
      },
      weeklyActivity: [3, 3, 2, 3, 3, 3, 2]
    },
    {
      id: 5,
      name: "Olivia Brown",
      classId: 2,
      age: 5,
      engagement: "medium",
      avgSessionsPerDay: 1.7,
      trend: "stable",
      lastActive: "2024-11-24",
      skills: {
        attention: "medium",
        patience: "medium",
        sensory: "high",
        emotionAwareness: "medium",
        bodyAwareness: "medium"
      },
      weeklyActivity: [2, 1, 2, 2, 1, 2, 2]
    }
  ],

  adminStats: {
    appInstallRate: 79,
    avgDailySessionsPerChild: 1.8,
    topSkills: ["Sensory Awareness", "Attention", "Body Awareness"],
    weeklyEngagement: [1.5, 1.6, 1.7, 1.8]
  },

  teacherAlerts: [
    "3 children have significantly lower usage than class average",
    "2 children show consistent struggle in patience tasks"
  ],

  skillSuggestions: {
    patience: [
      "Transferring beans with a spoon",
      "Watching a sand timer before the next turn",
      "Slow pouring activities with water"
    ],
    attention: [
      "Sound matching games",
      "Following multi-step instructions",
      "Sorting activities by color or size"
    ],
    sensory: [
      "Texture exploration with natural materials",
      "Smelling jars activity",
      "Temperature comparison exercises"
    ],
    emotionAwareness: [
      "Emotion cards matching",
      "Mirror activities for facial expressions",
      "Story time with emotion discussions"
    ],
    bodyAwareness: [
      "Yoga poses for children",
      "Walking on a line exercise",
      "Body part identification games"
    ]
  },

  parentCommunication: {
    whatsappTemplate: "Hello! 👋 We're excited to share our new learning app that helps reinforce mindfulness and Montessori principles at home. It's safe, ad-free, and takes just a few minutes a day. Download link: [APP_LINK]",
    emailTemplate: "Dear Parents,\n\nWe're introducing a new educational tool to support your child's development at home. The app provides short, engaging activities that reinforce the Montessori and mindfulness practices we use in class.\n\nKey benefits:\n- Safe and ad-free environment\n- Just 2-3 minutes per day\n- Builds attention, patience, and emotional awareness\n\nPlease install the app and let us know if you have any questions.\n\nBest regards,\n[Teacher Name]",
    handout: "How to Install & Use the Lockscreen App\n\n1. Download from [link]\n2. Enable lockscreen permissions\n3. Your child will see fun, educational puzzles\n4. No ads, completely safe\n5. Progress shared with teacher (with your consent)"
  }
}
