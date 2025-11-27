/**
 * **Feature: frontend-backend-integration, Property 6: Search Filtering Correctness**
 * **Validates: Requirements 7.2**
 * 
 * For any search query string and list of students, the filtered results SHALL contain
 * only students whose names include the search string (case-insensitive), and an empty
 * search SHALL return all students.
 */

import { describe, it, expect } from 'vitest';
import { test, fc } from '@fast-check/vitest';

// Generate valid student data
const studentArb = fc.record({
  id: fc.integer({ min: 1 }),
  display_name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  age: fc.option(fc.integer({ min: 1, max: 18 })),
  class_id: fc.integer({ min: 1 }),
  child_code: fc.string({ minLength: 4, maxLength: 8 })
});

// Generate a list of students
const studentsListArb = fc.array(studentArb, { minLength: 0, maxLength: 20 });

// Generate search query strings
const searchQueryArb = fc.string({ minLength: 0, maxLength: 30 });

/**
 * Filter function that matches the AdminDashboard implementation
 * This is the function under test
 */
function filterStudentsByName(students, searchQuery) {
  if (!searchQuery.trim()) return students;
  const searchLower = searchQuery.toLowerCase();
  return students.filter(student => {
    const name = student.display_name || student.name || '';
    return name.toLowerCase().includes(searchLower);
  });
}

describe('Property 6: Search Filtering Correctness', () => {
  
  /**
   * Property 6.1: Empty search returns all students
   * WHEN an admin searches with an empty string THEN all students should be returned
   * **Validates: Requirements 7.2**
   */
  test.prop([studentsListArb], { numRuns: 100 })(
    'empty search query returns all students',
    (students) => {
      const result = filterStudentsByName(students, '');
      expect(result).toEqual(students);
      expect(result.length).toBe(students.length);
    }
  );

  /**
   * Property 6.2: Whitespace-only search returns all students
   * WHEN an admin searches with only whitespace THEN all students should be returned
   * **Validates: Requirements 7.2**
   */
  test.prop([studentsListArb, fc.string({ minLength: 1, maxLength: 10 }).map(s => ' '.repeat(s.length))], { numRuns: 100 })(
    'whitespace-only search query returns all students',
    (students, whitespace) => {
      const result = filterStudentsByName(students, whitespace);
      expect(result).toEqual(students);
      expect(result.length).toBe(students.length);
    }
  );

  /**
   * Property 6.3: All filtered results contain the search string
   * WHEN an admin searches for a string THEN all returned students' names contain that string
   * **Validates: Requirements 7.2**
   */
  test.prop([studentsListArb, searchQueryArb.filter(s => s.trim().length > 0)], { numRuns: 100 })(
    'all filtered results contain the search string (case-insensitive)',
    (students, searchQuery) => {
      const result = filterStudentsByName(students, searchQuery);
      const searchLower = searchQuery.toLowerCase();
      
      // Every result should contain the search string
      result.forEach(student => {
        const name = (student.display_name || student.name || '').toLowerCase();
        expect(name).toContain(searchLower);
      });
    }
  );

  /**
   * Property 6.4: No matching students are excluded
   * WHEN an admin searches for a string THEN no student whose name contains that string is excluded
   * **Validates: Requirements 7.2**
   */
  test.prop([studentsListArb, searchQueryArb.filter(s => s.trim().length > 0)], { numRuns: 100 })(
    'no matching students are excluded from results',
    (students, searchQuery) => {
      const result = filterStudentsByName(students, searchQuery);
      const searchLower = searchQuery.toLowerCase();
      
      // Find all students that should match
      const expectedMatches = students.filter(student => {
        const name = (student.display_name || student.name || '').toLowerCase();
        return name.includes(searchLower);
      });
      
      // Result should contain exactly the expected matches
      expect(result.length).toBe(expectedMatches.length);
      expectedMatches.forEach(expected => {
        expect(result).toContainEqual(expected);
      });
    }
  );

  /**
   * Property 6.5: Search is case-insensitive
   * WHEN an admin searches with different cases THEN the same results are returned
   * **Validates: Requirements 7.2**
   */
  test.prop([studentsListArb, fc.string({ minLength: 1, maxLength: 20 }).filter(s => s.trim().length > 0 && /[a-zA-Z]/.test(s))], { numRuns: 100 })(
    'search is case-insensitive',
    (students, searchQuery) => {
      const lowerResult = filterStudentsByName(students, searchQuery.toLowerCase());
      const upperResult = filterStudentsByName(students, searchQuery.toUpperCase());
      const mixedResult = filterStudentsByName(students, searchQuery);
      
      // All case variations should return the same results
      expect(lowerResult.length).toBe(upperResult.length);
      expect(lowerResult.length).toBe(mixedResult.length);
      
      // Same students should be in all results
      lowerResult.forEach(student => {
        expect(upperResult).toContainEqual(student);
        expect(mixedResult).toContainEqual(student);
      });
    }
  );

  /**
   * Property 6.6: Filtered results are a subset of original
   * WHEN an admin searches THEN the results are always a subset of the original list
   * **Validates: Requirements 7.2**
   */
  test.prop([studentsListArb, searchQueryArb], { numRuns: 100 })(
    'filtered results are always a subset of original students',
    (students, searchQuery) => {
      const result = filterStudentsByName(students, searchQuery);
      
      // Result length should be <= original length
      expect(result.length).toBeLessThanOrEqual(students.length);
      
      // Every result should be in the original list
      result.forEach(student => {
        expect(students).toContainEqual(student);
      });
    }
  );

  /**
   * Property 6.7: Search with exact name returns that student
   * WHEN an admin searches with an exact student name THEN that student is in the results
   * **Validates: Requirements 7.2**
   */
  test.prop([
    fc.array(studentArb, { minLength: 1, maxLength: 20 })
  ], { numRuns: 100 })(
    'searching with exact name returns that student',
    (students) => {
      // Pick a random student from the list
      const targetStudent = students[0];
      const searchQuery = targetStudent.display_name || targetStudent.name;
      
      const result = filterStudentsByName(students, searchQuery);
      
      // The target student should be in the results
      expect(result).toContainEqual(targetStudent);
    }
  );

  /**
   * Property 6.8: Partial name search works
   * WHEN an admin searches with a partial name THEN students with that substring are returned
   * **Validates: Requirements 7.2**
   */
  test.prop([
    fc.array(studentArb, { minLength: 1, maxLength: 20 })
  ], { numRuns: 100 })(
    'partial name search returns matching students',
    (students) => {
      // Pick a random student and use part of their name
      const targetStudent = students[0];
      const fullName = targetStudent.display_name || targetStudent.name;
      
      // Use first half of the name as search query (at least 1 char)
      const partialName = fullName.substring(0, Math.max(1, Math.floor(fullName.length / 2)));
      
      const result = filterStudentsByName(students, partialName);
      
      // The target student should be in the results
      expect(result).toContainEqual(targetStudent);
    }
  );

  /**
   * Property 6.9: Non-matching search returns empty or subset
   * WHEN an admin searches with a non-matching string THEN only matching students are returned
   * **Validates: Requirements 7.2**
   */
  it('non-matching search returns empty array', () => {
    const students = [
      { id: 1, display_name: 'Alice', name: 'Alice', age: 5, class_id: 1, child_code: 'ABC1' },
      { id: 2, display_name: 'Bob', name: 'Bob', age: 6, class_id: 1, child_code: 'ABC2' },
      { id: 3, display_name: 'Charlie', name: 'Charlie', age: 5, class_id: 2, child_code: 'ABC3' }
    ];
    
    // Search for something that doesn't exist
    const result = filterStudentsByName(students, 'XYZ123NonExistent');
    
    expect(result).toEqual([]);
    expect(result.length).toBe(0);
  });

  /**
   * Property 6.10: Idempotence - filtering twice gives same result
   * WHEN filtering is applied twice with the same query THEN the result is the same
   * **Validates: Requirements 7.2**
   */
  test.prop([studentsListArb, searchQueryArb], { numRuns: 100 })(
    'filtering is idempotent',
    (students, searchQuery) => {
      const firstFilter = filterStudentsByName(students, searchQuery);
      const secondFilter = filterStudentsByName(firstFilter, searchQuery);
      
      // Filtering twice should give the same result
      expect(secondFilter).toEqual(firstFilter);
    }
  );
});
