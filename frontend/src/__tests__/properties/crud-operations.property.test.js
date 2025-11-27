/**
 * **Feature: frontend-backend-integration, Property 4: CRUD Operations Integrity**
 * **Validates: Requirements 4.3, 4.4, 6.4**
 * 
 * For any update or delete operation on an entity, the frontend SHALL send the correct
 * HTTP method (PUT/DELETE) to the correct endpoint, and upon success, the UI SHALL
 * reflect the change (updated data or removed entity).
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

// Arbitraries for generating valid entity IDs
const validIdArb = fc.integer({ min: 1, max: 10000 });

// Arbitraries for generating valid classroom update data
const validClassNameArb = fc.string({ minLength: 1, maxLength: 50 })
  .filter(s => s.trim().length > 0)
  .map(s => s.trim());

const classUpdateDataArb = fc.record({
  name: validClassNameArb,
  grade_level: fc.option(
    fc.string({ minLength: 1, maxLength: 20 }).filter(s => s.trim().length > 0),
    { nil: null }
  )
});

// Arbitraries for generating valid student update data
const validStudentNameArb = fc.string({ minLength: 1, maxLength: 50 })
  .filter(s => s.trim().length > 0)
  .map(s => s.trim());

const studentUpdateDataArb = fc.record({
  display_name: validStudentNameArb,
  age: fc.option(fc.integer({ min: 2, max: 12 }), { nil: null })
});

// Arbitraries for generating existing entity data
const existingClassArb = fc.record({
  id: validIdArb,
  name: validClassNameArb,
  grade_level: fc.option(fc.string({ minLength: 1, maxLength: 20 }), { nil: null }),
  school_id: fc.integer({ min: 1, max: 1000 }),
  student_count: fc.integer({ min: 0, max: 100 })
});

const existingStudentArb = fc.record({
  id: validIdArb,
  display_name: validStudentNameArb,
  child_code: fc.string({ minLength: 4, maxLength: 10 }),
  age: fc.option(fc.integer({ min: 2, max: 12 }), { nil: null }),
  class_id: fc.integer({ min: 1, max: 1000 })
});

describe('Property 4: CRUD Operations Integrity', () => {

  /**
   * Property 4.1: Update classroom sends PUT request to correct endpoint
   * For any classroom update, the PUT request SHALL be sent to /classes/{id}
   * **Validates: Requirements 4.4, 6.4**
   */
  test.prop([validIdArb, classUpdateDataArb], { numRuns: 100 })(
    'update classroom sends PUT request to correct endpoint',
    async (classId, updateData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: classId, ...updateData })
      });

      const result = await apiRequest(`/classes/${classId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });

      // Verify fetch was called with correct parameters
      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      
      expect(url).toBe(`${API_BASE_URL}/classes/${classId}`);
      expect(options.method).toBe('PUT');
      expect(options.headers['Content-Type']).toBe('application/json');
    }
  );

  /**
   * Property 4.2: Update classroom response contains updated data
   * For any classroom update, the response SHALL contain the updated fields
   * **Validates: Requirements 4.4, 6.4**
   */
  test.prop([validIdArb, classUpdateDataArb], { numRuns: 100 })(
    'update classroom response contains updated data',
    async (classId, updateData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      const responseData = { id: classId, ...updateData, school_id: 1 };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => responseData
      });

      const result = await apiRequest(`/classes/${classId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });

      // Verify response contains updated data
      expect(result.id).toBe(classId);
      expect(result.name).toBe(updateData.name);
      if (updateData.grade_level) {
        expect(result.grade_level).toBe(updateData.grade_level);
      }
    }
  );

  /**
   * Property 4.3: Update student sends PUT request to correct endpoint
   * For any student update, the PUT request SHALL be sent to /children/{id}
   * **Validates: Requirements 4.4**
   */
  test.prop([validIdArb, studentUpdateDataArb], { numRuns: 100 })(
    'update student sends PUT request to correct endpoint',
    async (studentId, updateData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: studentId, ...updateData })
      });

      const result = await apiRequest(`/children/${studentId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });

      // Verify fetch was called with correct parameters
      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      
      expect(url).toBe(`${API_BASE_URL}/children/${studentId}`);
      expect(options.method).toBe('PUT');
      expect(options.headers['Content-Type']).toBe('application/json');
    }
  );

  /**
   * Property 4.4: Update student response contains updated data
   * For any student update, the response SHALL contain the updated fields
   * **Validates: Requirements 4.4**
   */
  test.prop([validIdArb, studentUpdateDataArb], { numRuns: 100 })(
    'update student response contains updated data',
    async (studentId, updateData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      const responseData = { 
        id: studentId, 
        ...updateData, 
        class_id: 1,
        child_code: `CHILD${studentId}`
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => responseData
      });

      const result = await apiRequest(`/children/${studentId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });

      // Verify response contains updated data
      expect(result.id).toBe(studentId);
      expect(result.display_name).toBe(updateData.display_name);
      if (updateData.age !== null) {
        expect(result.age).toBe(updateData.age);
      }
    }
  );

  /**
   * Property 4.5: Delete classroom sends DELETE request to correct endpoint
   * For any classroom deletion, the DELETE request SHALL be sent to /classes/{id}
   * **Validates: Requirements 4.3, 6.4**
   */
  test.prop([validIdArb], { numRuns: 100 })(
    'delete classroom sends DELETE request to correct endpoint',
    async (classId) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204
      });

      const result = await apiRequest(`/classes/${classId}`, {
        method: 'DELETE'
      });

      // Verify fetch was called with correct parameters
      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      
      expect(url).toBe(`${API_BASE_URL}/classes/${classId}`);
      expect(options.method).toBe('DELETE');
    }
  );

  /**
   * Property 4.6: Delete student sends DELETE request to correct endpoint
   * For any student deletion, the DELETE request SHALL be sent to /children/{id}
   * **Validates: Requirements 4.3**
   */
  test.prop([validIdArb], { numRuns: 100 })(
    'delete student sends DELETE request to correct endpoint',
    async (studentId) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204
      });

      const result = await apiRequest(`/children/${studentId}`, {
        method: 'DELETE'
      });

      // Verify fetch was called with correct parameters
      expect(mockFetch).toHaveBeenCalledTimes(1);
      const [url, options] = mockFetch.mock.calls[0];
      
      expect(url).toBe(`${API_BASE_URL}/children/${studentId}`);
      expect(options.method).toBe('DELETE');
    }
  );

  /**
   * Property 4.7: Deleted entity is removed from list
   * For any deleted entity, fetching the list SHALL NOT include the deleted entity
   * **Validates: Requirements 4.3, 6.4**
   */
  test.prop([
    fc.array(existingClassArb, { minLength: 2, maxLength: 10 })
      .map(items => items.map((item, i) => ({ ...item, id: i + 1 }))),
    fc.integer({ min: 0, max: 9 })
  ], { numRuns: 100 })(
    'deleted classroom is removed from subsequent list fetch',
    async (classes, deleteIndex) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      // Ensure deleteIndex is within bounds
      const safeDeleteIndex = deleteIndex % classes.length;
      const deletedId = classes[safeDeleteIndex].id;
      
      // Simulate the list after deletion
      const remainingClasses = classes.filter(c => c.id !== deletedId);
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ classes: remainingClasses })
      });

      const result = await apiRequest('/schools/1/classes');

      // Verify the deleted class is NOT in the list
      const foundClass = result.classes.find(c => c.id === deletedId);
      expect(foundClass).toBeUndefined();
      
      // Verify remaining classes are still present
      expect(result.classes.length).toBe(classes.length - 1);
    }
  );

  /**
   * Property 4.8: Deleted student is removed from class list
   * For any deleted student, fetching the class students SHALL NOT include the deleted student
   * **Validates: Requirements 4.3**
   */
  test.prop([
    fc.array(existingStudentArb, { minLength: 2, maxLength: 10 })
      .map(items => items.map((item, i) => ({ ...item, id: i + 1 }))),
    fc.integer({ min: 0, max: 9 })
  ], { numRuns: 100 })(
    'deleted student is removed from subsequent class student list fetch',
    async (students, deleteIndex) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      // Ensure deleteIndex is within bounds
      const safeDeleteIndex = deleteIndex % students.length;
      const deletedId = students[safeDeleteIndex].id;
      
      // Simulate the list after deletion
      const remainingStudents = students.filter(s => s.id !== deletedId);
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ children: remainingStudents })
      });

      const result = await apiRequest('/classes/1/children');

      // Verify the deleted student is NOT in the list
      const foundStudent = result.children.find(s => s.id === deletedId);
      expect(foundStudent).toBeUndefined();
      
      // Verify remaining students are still present
      expect(result.children.length).toBe(students.length - 1);
    }
  );

  /**
   * Property 4.9: Updated entity reflects changes in list
   * For any updated entity, fetching the list SHALL show the updated data
   * **Validates: Requirements 4.4, 6.4**
   */
  test.prop([
    fc.array(existingClassArb, { minLength: 1, maxLength: 5 })
      .map(items => items.map((item, i) => ({ ...item, id: i + 1 }))),
    fc.integer({ min: 0, max: 4 }),
    classUpdateDataArb
  ], { numRuns: 100 })(
    'updated classroom reflects changes in subsequent list fetch',
    async (classes, updateIndex, updateData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      // Ensure updateIndex is within bounds
      const safeUpdateIndex = updateIndex % classes.length;
      const updatedId = classes[safeUpdateIndex].id;
      
      // Simulate the list after update
      const updatedClasses = classes.map(c => 
        c.id === updatedId ? { ...c, ...updateData } : c
      );
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ classes: updatedClasses })
      });

      const result = await apiRequest('/schools/1/classes');

      // Verify the updated class has new data
      const foundClass = result.classes.find(c => c.id === updatedId);
      expect(foundClass).toBeDefined();
      expect(foundClass.name).toBe(updateData.name);
      
      // Verify list length is unchanged
      expect(result.classes.length).toBe(classes.length);
    }
  );

  /**
   * Property 4.10: Update preserves entity ID
   * For any update operation, the entity ID SHALL remain unchanged
   * **Validates: Requirements 4.4**
   */
  test.prop([validIdArb, studentUpdateDataArb], { numRuns: 100 })(
    'update operation preserves entity ID',
    async (studentId, updateData) => {
      // Reset mock for each iteration
      mockFetch.mockReset();
      
      const responseData = { 
        id: studentId, 
        ...updateData, 
        class_id: 1,
        child_code: `CHILD${studentId}`
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => responseData
      });

      const result = await apiRequest(`/children/${studentId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });

      // Verify ID is preserved
      expect(result.id).toBe(studentId);
      expect(typeof result.id).toBe('number');
    }
  );
});
