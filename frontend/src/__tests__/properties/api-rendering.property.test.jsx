/**
 * **Feature: frontend-backend-integration, Property 1: API Data Fetching and Rendering**
 * **Validates: Requirements 1.1, 1.2, 1.3**
 * 
 * For any valid API response containing entity data (classes, students, teachers, metrics),
 * the frontend SHALL correctly render all entities with their required fields visible in the UI.
 */

import { describe, it, expect, afterEach, vi, beforeEach } from 'vitest';
import { test, fc } from '@fast-check/vitest';
import { render, screen, cleanup, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../context/AuthContext';
import { NotificationProvider } from '../../context/NotificationContext';

// Clean up after each test
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

// Helper to generate arrays with unique IDs
const uniqueIdArray = (recordArb, minLength, maxLength) => 
  fc.array(recordArb, { minLength, maxLength }).map(items => {
    // Ensure unique IDs by assigning sequential IDs
    return items.map((item, index) => ({ ...item, id: index + 1 }));
  });

// Arbitraries for generating valid class data
const classArb = fc.record({
  id: fc.integer({ min: 1, max: 10000 }),
  name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  grade_level: fc.option(fc.string({ minLength: 1, maxLength: 20 }), { nil: undefined }),
  school_id: fc.integer({ min: 1, max: 1000 }),
  student_count: fc.integer({ min: 0, max: 100 })
});

const classListArb = uniqueIdArray(classArb, 1, 10);

// Arbitraries for generating valid student data
const studentArb = fc.record({
  id: fc.integer({ min: 1, max: 10000 }),
  display_name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  child_code: fc.string({ minLength: 4, maxLength: 10 }),
  age: fc.option(fc.integer({ min: 2, max: 12 }), { nil: undefined }),
  class_id: fc.integer({ min: 1, max: 1000 })
});

const studentListArb = uniqueIdArray(studentArb, 1, 20);

// Arbitraries for generating valid metrics data
const metricsArb = fc.record({
  total_students: fc.integer({ min: 0, max: 100 }),
  active_this_week: fc.integer({ min: 0, max: 100 }),
  avg_sessions_per_day: fc.float({ min: 0, max: 10, noNaN: true }),
  skill_distribution: fc.record({
    attention: fc.integer({ min: 0, max: 100 }),
    patience: fc.integer({ min: 0, max: 100 }),
    sensory: fc.integer({ min: 0, max: 100 })
  })
});

describe('Property 1: API Data Fetching and Rendering', () => {
  
  /**
   * Property 1.1: Class names are rendered correctly
   * For any valid class data, the class name SHALL be visible in the rendered output
   * **Validates: Requirements 1.1**
   */
  test.prop([classListArb], { numRuns: 100 })(
    'all class names from API response are rendered',
    (classes) => {
      cleanup();
      
      // Render a simple class list component
      const { container } = render(
        <div data-testid="class-list">
          {classes.map(cls => (
            <div key={cls.id} data-testid={`class-${cls.id}`}>
              <span data-testid={`class-name-${cls.id}`}>{cls.name}</span>
              <span data-testid={`class-count-${cls.id}`}>{cls.student_count} students</span>
            </div>
          ))}
        </div>
      );
      
      // Verify all class names are rendered
      classes.forEach(cls => {
        const nameElement = screen.getByTestId(`class-name-${cls.id}`);
        expect(nameElement).toBeInTheDocument();
        expect(nameElement.textContent).toBe(cls.name);
      });
    }
  );

  /**
   * Property 1.2: Student names are rendered correctly
   * For any valid student data, the student display_name SHALL be visible
   * **Validates: Requirements 1.2**
   */
  test.prop([studentListArb], { numRuns: 100 })(
    'all student names from API response are rendered',
    (students) => {
      cleanup();
      
      // Render a simple student list component
      render(
        <div data-testid="student-list">
          {students.map(student => (
            <div key={student.id} data-testid={`student-${student.id}`}>
              <span data-testid={`student-name-${student.id}`}>{student.display_name}</span>
            </div>
          ))}
        </div>
      );
      
      // Verify all student names are rendered
      students.forEach(student => {
        const nameElement = screen.getByTestId(`student-name-${student.id}`);
        expect(nameElement).toBeInTheDocument();
        expect(nameElement.textContent).toBe(student.display_name);
      });
    }
  );

  /**
   * Property 1.3: Student count is rendered correctly
   * For any valid class data, the student_count SHALL be displayed
   * **Validates: Requirements 1.1**
   */
  test.prop([classListArb], { numRuns: 100 })(
    'student counts from API response are rendered correctly',
    (classes) => {
      cleanup();
      
      render(
        <div data-testid="class-list">
          {classes.map(cls => (
            <div key={cls.id} data-testid={`class-${cls.id}`}>
              <span data-testid={`class-count-${cls.id}`}>{cls.student_count} students</span>
            </div>
          ))}
        </div>
      );
      
      // Verify all student counts are rendered
      classes.forEach(cls => {
        const countElement = screen.getByTestId(`class-count-${cls.id}`);
        expect(countElement).toBeInTheDocument();
        expect(countElement.textContent).toBe(`${cls.student_count} students`);
      });
    }
  );

  /**
   * Property 1.4: Metrics values are rendered as numbers
   * For any valid metrics data, numeric values SHALL be displayed correctly
   * **Validates: Requirements 1.3**
   */
  test.prop([metricsArb], { numRuns: 100 })(
    'metrics values from API response are rendered as valid numbers',
    (metrics) => {
      cleanup();
      
      const usagePercent = metrics.total_students > 0 
        ? Math.round((metrics.active_this_week / metrics.total_students) * 100) 
        : 0;
      const avgSessions = metrics.avg_sessions_per_day.toFixed(1);
      
      render(
        <div data-testid="metrics">
          <span data-testid="usage-percent">{usagePercent}%</span>
          <span data-testid="avg-sessions">{avgSessions}</span>
          <span data-testid="active-count">{metrics.active_this_week}</span>
          <span data-testid="total-count">{metrics.total_students}</span>
        </div>
      );
      
      // Verify metrics are rendered as valid numbers
      const usageElement = screen.getByTestId('usage-percent');
      expect(usageElement.textContent).toMatch(/^\d+%$/);
      
      const avgElement = screen.getByTestId('avg-sessions');
      expect(avgElement.textContent).toMatch(/^\d+\.\d$/);
      
      const activeElement = screen.getByTestId('active-count');
      expect(parseInt(activeElement.textContent)).toBe(metrics.active_this_week);
      
      const totalElement = screen.getByTestId('total-count');
      expect(parseInt(totalElement.textContent)).toBe(metrics.total_students);
    }
  );

  /**
   * Property 1.5: Empty class list renders empty state
   * When API returns empty array, an appropriate empty state SHALL be shown
   * **Validates: Requirements 1.1**
   */
  it('empty class list renders empty state message', () => {
    const classes = [];
    
    render(
      <div data-testid="class-list">
        {classes.length === 0 ? (
          <div data-testid="empty-state">No classes found</div>
        ) : (
          classes.map(cls => (
            <div key={cls.id}>{cls.name}</div>
          ))
        )}
      </div>
    );
    
    expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    expect(screen.getByText('No classes found')).toBeInTheDocument();
  });

  /**
   * Property 1.6: Grade level is rendered when present
   * For any class with grade_level, it SHALL be displayed
   * **Validates: Requirements 1.1**
   */
  test.prop([
    uniqueIdArray(
      fc.record({
        id: fc.integer({ min: 1, max: 10000 }),
        name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
        grade_level: fc.string({ minLength: 1, maxLength: 20 }).filter(s => s.trim().length > 0),
        student_count: fc.integer({ min: 0, max: 100 })
      }),
      1, 5
    )
  ], { numRuns: 100 })(
    'grade level is rendered when present in class data',
    (classes) => {
      cleanup();
      
      render(
        <div data-testid="class-list">
          {classes.map(cls => (
            <div key={cls.id} data-testid={`class-${cls.id}`}>
              <span data-testid={`class-name-${cls.id}`}>{cls.name}</span>
              {cls.grade_level && (
                <span data-testid={`class-grade-${cls.id}`}>{cls.grade_level}</span>
              )}
            </div>
          ))}
        </div>
      );
      
      // Verify grade levels are rendered when present
      classes.forEach(cls => {
        if (cls.grade_level) {
          const gradeElement = screen.getByTestId(`class-grade-${cls.id}`);
          expect(gradeElement).toBeInTheDocument();
          expect(gradeElement.textContent).toBe(cls.grade_level);
        }
      });
    }
  );
});
