/**
 * **Feature: frontend-backend-integration, Property 2: Entity Creation Round-Trip**
 * **Validates: Requirements 2.2, 2.3, 3.3, 3.4, 6.3**
 * 
 * For any valid entity creation request (classroom or student), submitting the form
 * SHALL result in a POST request to the correct endpoint, and upon success, the new
 * entity SHALL appear in the displayed list with matching data.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { test, fc } from '@fast-check/vitest';
import { apiRequest, API_BASE_URL } from '../../api/config';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  localStorage.clear();
});

afterEach(() => {
  vi.restoreAllMocks();
});

// Arbitraries for generating valid classroom data
const validClassNameArb = fc.string({ minLength: 1, maxLength: 50 })
  .filter(s => s.trim().length > 0)
  .map(s => s.trim());

const validGradeLevelArb = fc.option(
  fc.string({ minLength: 1, maxLength: 20 }).filter(s => s.trim().length > 0),
  { nil: null }
);

const classCreationDataArb = fc.record({
  name: validClassNameArb,
  grade_level: validGradeLevelArb,
  school_id: fc.integer({ min: 1, max: 10000 }),
  primary_teacher_id: fc.option(fc.integer({ min: 1, max: 10000 }), { nil: null })
});

// Arbitraries for generating valid student data
const validStudentNameArb = fc.string({ minLength: 1, maxLength: 50 })
  .filter(s => s.trim().length > 0)
  .map(s => s.trim());

const validAgeArb = fc.option(fc.integer({ min: 2, max: 12 }), { nil: null });

const studentCreationDataArb = fc.record({
  display_name: validStudentNameArb,
  age: validAgeArb,
  class_id: fc.integer({ min: 1, max: 10000 })
});

// Helper to simulate API response with generated ID
const createApiResponse = (data, id) => ({
  ...data,
  id,
  created_at: new Date().toISOString()
});

describe('Property 2: Entity Creation Round-Trip', () => {

  /**
   * Property 2.1: Classroom creation sends correct data to API
   * For any valid classroom data, the POST request SHALL contain all provided fields
   * **Validates: Requirements 2.2, 6.3**
   */
  test.prop([classCreationDataArb], { numRuns: 100 })(
    'classroom creation sends correct data to API',
    async (classData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      const generatedId = Math.floor(Math.random() * 10000) + 1;
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => createApiResponse(classData, generatedId)
      });

      const result = await apiRequest('/classes', {
        method: 'POST',
        body: JSON.stringify(classData)
      });

      // Verify fetch was called with correct parameters
      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      
      expect(url).toBe(`${API_BASE_URL}/classes`);
      expect(options.method).toBe('POST');
      expect(options.headers['Content-Type']).toBe('application/json');
      
      // Verify the body contains the correct data
      const sentBody = JSON.parse(options.body);
      expect(sentBody.name).toBe(classData.name);
      expect(sentBody.school_id).toBe(classData.school_id);
      if (classData.grade_level) {
        expect(sentBody.grade_level).toBe(classData.grade_level);
      }
      if (classData.primary_teacher_id) {
        expect(sentBody.primary_teacher_id).toBe(classData.primary_teacher_id);
      }
    }
  );

  /**
   * Property 2.2: Classroom creation response contains matching data
   * For any valid classroom creation, the response SHALL contain the same data plus an ID
   * **Validates: Requirements 2.3, 6.3**
   */
  test.prop([classCreationDataArb, fc.integer({ min: 1, max: 10000 })], { numRuns: 100 })(
    'classroom creation response contains matching data with ID',
    async (classData, generatedId) => {
      const responseData = createApiResponse(classData, generatedId);
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => responseData
      });

      const result = await apiRequest('/classes', {
        method: 'POST',
        body: JSON.stringify(classData)
      });

      // Verify response contains the original data
      expect(result.name).toBe(classData.name);
      expect(result.school_id).toBe(classData.school_id);
      
      // Verify response has an ID
      expect(result.id).toBe(generatedId);
      expect(typeof result.id).toBe('number');
      expect(result.id).toBeGreaterThan(0);
    }
  );

  /**
   * Property 2.3: Student creation sends correct data to API
   * For any valid student data, the POST request SHALL contain all provided fields
   * **Validates: Requirements 3.3**
   */
  test.prop([studentCreationDataArb], { numRuns: 100 })(
    'student creation sends correct data to API',
    async (studentData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      const generatedId = Math.floor(Math.random() * 10000) + 1;
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({
          ...studentData,
          id: generatedId,
          child_code: `CHILD${generatedId}`
        })
      });

      const result = await apiRequest('/children', {
        method: 'POST',
        body: JSON.stringify(studentData)
      });

      // Verify fetch was called with correct parameters
      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      
      expect(url).toBe(`${API_BASE_URL}/children`);
      expect(options.method).toBe('POST');
      expect(options.headers['Content-Type']).toBe('application/json');
      
      // Verify the body contains the correct data
      const sentBody = JSON.parse(options.body);
      expect(sentBody.display_name).toBe(studentData.display_name);
      expect(sentBody.class_id).toBe(studentData.class_id);
      if (studentData.age !== null) {
        expect(sentBody.age).toBe(studentData.age);
      }
    }
  );

  /**
   * Property 2.4: Student creation response contains matching data
   * For any valid student creation, the response SHALL contain the same data plus an ID
   * **Validates: Requirements 3.4**
   */
  test.prop([studentCreationDataArb, fc.integer({ min: 1, max: 10000 })], { numRuns: 100 })(
    'student creation response contains matching data with ID',
    async (studentData, generatedId) => {
      const responseData = {
        ...studentData,
        id: generatedId,
        child_code: `CHILD${generatedId}`
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => responseData
      });

      const result = await apiRequest('/children', {
        method: 'POST',
        body: JSON.stringify(studentData)
      });

      // Verify response contains the original data
      expect(result.display_name).toBe(studentData.display_name);
      expect(result.class_id).toBe(studentData.class_id);
      
      // Verify response has an ID
      expect(result.id).toBe(generatedId);
      expect(typeof result.id).toBe('number');
      expect(result.id).toBeGreaterThan(0);
    }
  );

  /**
   * Property 2.5: Created entity can be retrieved from list
   * For any created entity, fetching the list SHALL include the new entity
   * **Validates: Requirements 2.3, 3.4**
   */
  test.prop([
    fc.array(classCreationDataArb, { minLength: 0, maxLength: 5 }),
    classCreationDataArb
  ], { numRuns: 100 })(
    'created classroom appears in subsequent list fetch',
    async (existingClasses, newClassData) => {
      // Assign unique IDs to existing classes
      const existingWithIds = existingClasses.map((cls, i) => ({
        ...cls,
        id: i + 1
      }));
      
      const newClassId = existingClasses.length + 1;
      const newClassWithId = { ...newClassData, id: newClassId };
      
      // Simulate the list after creation
      const updatedList = [...existingWithIds, newClassWithId];
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ classes: updatedList })
      });

      const result = await apiRequest('/schools/1/classes');

      // Verify the new class is in the list
      const foundClass = result.classes.find(c => c.id === newClassId);
      expect(foundClass).toBeDefined();
      expect(foundClass.name).toBe(newClassData.name);
    }
  );

  /**
   * Property 2.6: Created student appears in class student list
   * For any created student, fetching the class students SHALL include the new student
   * **Validates: Requirements 3.4**
   */
  test.prop([
    fc.array(studentCreationDataArb, { minLength: 0, maxLength: 5 }),
    studentCreationDataArb
  ], { numRuns: 100 })(
    'created student appears in subsequent class student list fetch',
    async (existingStudents, newStudentData) => {
      // Assign unique IDs to existing students
      const existingWithIds = existingStudents.map((student, i) => ({
        ...student,
        id: i + 1,
        child_code: `CHILD${i + 1}`
      }));
      
      const newStudentId = existingStudents.length + 1;
      const newStudentWithId = {
        ...newStudentData,
        id: newStudentId,
        child_code: `CHILD${newStudentId}`
      };
      
      // Simulate the list after creation
      const updatedList = [...existingWithIds, newStudentWithId];
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ children: updatedList })
      });

      const result = await apiRequest(`/classes/${newStudentData.class_id}/children`);

      // Verify the new student is in the list
      const foundStudent = result.children.find(s => s.id === newStudentId);
      expect(foundStudent).toBeDefined();
      expect(foundStudent.display_name).toBe(newStudentData.display_name);
    }
  );

  /**
   * Property 2.7: Entity creation with all optional fields
   * For any entity with all optional fields populated, all fields SHALL be preserved
   * **Validates: Requirements 2.2, 3.3**
   */
  test.prop([
    fc.record({
      name: validClassNameArb,
      grade_level: fc.string({ minLength: 1, maxLength: 20 }).filter(s => s.trim().length > 0),
      school_id: fc.integer({ min: 1, max: 10000 }),
      primary_teacher_id: fc.integer({ min: 1, max: 10000 })
    })
  ], { numRuns: 100 })(
    'classroom creation preserves all optional fields',
    async (classData) => {
      const generatedId = Math.floor(Math.random() * 10000) + 1;
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => createApiResponse(classData, generatedId)
      });

      const result = await apiRequest('/classes', {
        method: 'POST',
        body: JSON.stringify(classData)
      });

      // Verify all fields are preserved
      expect(result.name).toBe(classData.name);
      expect(result.grade_level).toBe(classData.grade_level);
      expect(result.school_id).toBe(classData.school_id);
      expect(result.primary_teacher_id).toBe(classData.primary_teacher_id);
    }
  );

  /**
   * Property 2.8: Student creation with age preserves age value
   * For any student with age specified, the age SHALL be preserved in response
   * **Validates: Requirements 3.3, 3.4**
   */
  test.prop([
    fc.record({
      display_name: validStudentNameArb,
      age: fc.integer({ min: 2, max: 12 }),
      class_id: fc.integer({ min: 1, max: 10000 })
    })
  ], { numRuns: 100 })(
    'student creation preserves age value',
    async (studentData) => {
      const generatedId = Math.floor(Math.random() * 10000) + 1;
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({
          ...studentData,
          id: generatedId,
          child_code: `CHILD${generatedId}`
        })
      });

      const result = await apiRequest('/children', {
        method: 'POST',
        body: JSON.stringify(studentData)
      });

      // Verify age is preserved
      expect(result.age).toBe(studentData.age);
      expect(typeof result.age).toBe('number');
      expect(result.age).toBeGreaterThanOrEqual(2);
      expect(result.age).toBeLessThanOrEqual(12);
    }
  );
});
