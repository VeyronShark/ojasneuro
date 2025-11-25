import { useState } from 'react'
import Layout from '../components/Layout'
import Card from '../components/Card'
import { DUMMY_DATA } from '../data/dummyData'

export default function SkillSuggestions({ user }) {
  const [selectedSkill, setSelectedSkill] = useState('patience')
  const suggestions = DUMMY_DATA.skillSuggestions

  const topSkills = ['patience', 'attention', 'sensory']

  return (
    <Layout user={user} title="Skill Themes & Classroom Suggestions">
      <Card title="This Week's Top 3 Skills Reinforced at Home">
        <div style={styles.topSkills}>
          {topSkills.map(skill => (
            <div key={skill} style={styles.skillBadge}>
              {skill.replace(/([A-Z])/g, ' $1').trim()}
            </div>
          ))}
        </div>
      </Card>

      <div style={styles.selector}>
        <label style={styles.label}>Select a skill to see classroom activities:</label>
        <select
          value={selectedSkill}
          onChange={(e) => setSelectedSkill(e.target.value)}
          style={styles.select}
        >
          {Object.keys(suggestions).map(skill => (
            <option key={skill} value={skill}>
              {skill.replace(/([A-Z])/g, ' $1').trim()}
            </option>
          ))}
        </select>
      </div>

      <Card title={`Suggested Activities for ${selectedSkill.replace(/([A-Z])/g, ' $1').trim()}`}>
        <div style={styles.activities}>
          {suggestions[selectedSkill].map((activity, i) => (
            <div key={i} style={styles.activity}>
              <span style={styles.activityNumber}>{i + 1}</span>
              <span style={styles.activityText}>{activity}</span>
            </div>
          ))}
        </div>

        <div style={styles.actions}>
          <button style={styles.actionBtn}>
            📧 Email these suggestions to yourself
          </button>
          <button style={styles.actionBtn}>
            📋 Copy to clipboard
          </button>
        </div>
      </Card>

      <Card title="Montessori & Mindfulness Connection">
        <p style={styles.info}>
          These activities are designed to reinforce the same skills children practice in the app,
          using hands-on Montessori materials and mindfulness techniques. They help bridge home
          learning with classroom experiences.
        </p>
      </Card>
    </Layout>
  )
}

const styles = {
  topSkills: {
    display: 'flex',
    gap: '1rem',
    flexWrap: 'wrap'
  },
  skillBadge: {
    padding: '0.75rem 1.5rem',
    background: '#e7f3ff',
    color: '#4a90e2',
    borderRadius: '20px',
    fontSize: '1rem',
    fontWeight: '500',
    textTransform: 'capitalize'
  },
  selector: {
    margin: '1.5rem 0',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem'
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#495057'
  },
  select: {
    padding: '0.75rem',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '1rem',
    background: 'white',
    maxWidth: '400px'
  },
  activities: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    marginBottom: '1.5rem'
  },
  activity: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '1rem',
    padding: '1rem',
    background: '#f8f9fa',
    borderRadius: '4px'
  },
  activityNumber: {
    width: '28px',
    height: '28px',
    borderRadius: '50%',
    background: '#4a90e2',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.875rem',
    fontWeight: '600',
    flexShrink: 0
  },
  activityText: {
    fontSize: '0.9375rem',
    lineHeight: '1.6',
    color: '#495057'
  },
  actions: {
    display: 'flex',
    gap: '1rem',
    paddingTop: '1rem',
    borderTop: '1px solid #e1e4e8'
  },
  actionBtn: {
    padding: '0.75rem 1.5rem',
    background: '#f8f9fa',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    fontSize: '0.875rem',
    color: '#495057',
    fontWeight: '500'
  },
  info: {
    fontSize: '0.9375rem',
    lineHeight: '1.6',
    color: '#6c757d'
  }
}
