import { useState } from 'react'
import Layout from '../components/Layout'
import Card from '../components/Card'

// Static communication templates - could be fetched from API in future
const COMMUNICATION_TEMPLATES = {
  whatsappTemplate: "Hello! 👋 We're excited to share our new learning app that helps reinforce mindfulness and Montessori principles at home. It's safe, ad-free, and takes just a few minutes a day. Download link: [APP_LINK]",
  emailTemplate: "Dear Parents,\n\nWe're introducing a new educational tool to support your child's development at home. The app provides short, engaging activities that reinforce the Montessori and mindfulness practices we use in class.\n\nKey benefits:\n- Safe and ad-free environment\n- Just 2-3 minutes per day\n- Builds attention, patience, and emotional awareness\n\nPlease install the app and let us know if you have any questions.\n\nBest regards,\n[Teacher Name]",
  handout: "How to Install & Use the Lockscreen App\n\n1. Download from [link]\n2. Enable lockscreen permissions\n3. Your child will see fun, educational puzzles\n4. No ads, completely safe\n5. Progress shared with teacher (with your consent)"
}

export default function ParentCommunication() {
  const [copied, setCopied] = useState('')
  const templates = COMMUNICATION_TEMPLATES

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text)
    setCopied(type)
    setTimeout(() => setCopied(''), 2000)
  }

  return (
    <Layout title="Parent Communication Tools">
      <Card title="WhatsApp Message Template">
        <div style={styles.template}>
          <pre style={styles.templateText}>{templates.whatsappTemplate}</pre>
        </div>
        <button
          onClick={() => copyToClipboard(templates.whatsappTemplate, 'whatsapp')}
          style={styles.copyBtn}
        >
          {copied === 'whatsapp' ? '✓ Copied!' : '📋 Copy WhatsApp Message'}
        </button>
      </Card>

      <Card title="Email Template">
        <div style={styles.template}>
          <pre style={styles.templateText}>{templates.emailTemplate}</pre>
        </div>
        <button
          onClick={() => copyToClipboard(templates.emailTemplate, 'email')}
          style={styles.copyBtn}
        >
          {copied === 'email' ? '✓ Copied!' : '📋 Copy Email Template'}
        </button>
      </Card>

      <Card title="Parent Handout">
        <div style={styles.template}>
          <pre style={styles.templateText}>{templates.handout}</pre>
        </div>
        <div style={styles.actions}>
          <button
            onClick={() => copyToClipboard(templates.handout, 'handout')}
            style={styles.copyBtn}
          >
            {copied === 'handout' ? '✓ Copied!' : '📋 Copy Handout'}
          </button>
          <button style={styles.downloadBtn}>
            📄 Download as PDF
          </button>
        </div>
      </Card>

      <Card title="Sharing Log">
        <p style={styles.info}>
          Keep track of which classes you've shared these materials with for your reference.
        </p>
        <div style={styles.log}>
          <div style={styles.logEntry}>
            <span style={styles.logDate}>Nov 20, 2024</span>
            <span style={styles.logClass}>Nursery A</span>
            <span style={styles.logType}>WhatsApp + Email</span>
          </div>
          <div style={styles.logEntry}>
            <span style={styles.logDate}>Nov 18, 2024</span>
            <span style={styles.logClass}>KG-B</span>
            <span style={styles.logType}>Email + Handout</span>
          </div>
        </div>
      </Card>
    </Layout>
  )
}

const styles = {
  template: {
    background: '#f8f9fa',
    padding: '1rem',
    borderRadius: '4px',
    marginBottom: '1rem',
    border: '1px solid #e1e4e8'
  },
  templateText: {
    fontSize: '0.875rem',
    lineHeight: '1.6',
    color: '#495057',
    whiteSpace: 'pre-wrap',
    fontFamily: 'inherit',
    margin: 0
  },
  copyBtn: {
    padding: '0.75rem 1.5rem',
    background: '#4a90e2',
    color: 'white',
    borderRadius: '4px',
    fontSize: '0.875rem',
    fontWeight: '500'
  },
  actions: {
    display: 'flex',
    gap: '1rem'
  },
  downloadBtn: {
    padding: '0.75rem 1.5rem',
    background: '#f8f9fa',
    border: '1px solid #e1e4e8',
    borderRadius: '4px',
    fontSize: '0.875rem',
    color: '#495057',
    fontWeight: '500'
  },
  info: {
    fontSize: '0.875rem',
    color: '#6c757d',
    marginBottom: '1rem'
  },
  log: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  },
  logEntry: {
    display: 'grid',
    gridTemplateColumns: '120px 150px 1fr',
    padding: '0.75rem',
    background: '#f8f9fa',
    borderRadius: '4px',
    fontSize: '0.875rem'
  },
  logDate: {
    color: '#6c757d'
  },
  logClass: {
    fontWeight: '500',
    color: '#495057'
  },
  logType: {
    color: '#6c757d'
  }
}
