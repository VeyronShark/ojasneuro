/**
 * useStudents - Hook for student management with CRUD operations
 * Requirements: 3.3, 3.4, 4.3, 4.4 - Student CRUD with auto-refresh
 */
import { useState, useCallback, useEffect } from 'react';
import { classesAPI, studentsAPI } from '../api/config';

/**
 * Custom hook for managing students with CRUD operations
 * @param {number|string} classId - The class ID to fetch students for
 * @returns {Object} - { students, loading, error, addStudent, updateStudent, deleteStudent, refresh }
 */
export function useStudents(classId) {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStudents = useCallback(async () => {
    if (!classId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await classesAPI.getStudents(classId);
      setStudents(response.children || response || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch students');
    } finally {
      setLoading(false);
    }
  }, [classId]);

  // Fetch students on mount and when classId changes
  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  const addStudent = useCallback(async (studentData) => {
    setLoading(true);
    setError(null);
    
    try {
      const newStudent = await studentsAPI.create({
        ...studentData,
        class_id: classId,
      });
      // Auto-refresh list after mutation
      await fetchStudents();
      return newStudent;
    } catch (err) {
      setError(err.message || 'Failed to create student');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [classId, fetchStudents]);

  const updateStudent = useCallback(async (studentId, studentData) => {
    setLoading(true);
    setError(null);
    
    try {
      const updatedStudent = await studentsAPI.update(studentId, studentData);
      // Auto-refresh list after mutation
      await fetchStudents();
      return updatedStudent;
    } catch (err) {
      setError(err.message || 'Failed to update student');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchStudents]);

  const deleteStudent = useCallback(async (studentId) => {
    setLoading(true);
    setError(null);
    
    try {
      await studentsAPI.delete(studentId);
      // Auto-refresh list after mutation
      await fetchStudents();
    } catch (err) {
      setError(err.message || 'Failed to delete student');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchStudents]);

  const refresh = useCallback(() => {
    return fetchStudents();
  }, [fetchStudents]);

  return {
    students,
    loading,
    error,
    addStudent,
    updateStudent,
    deleteStudent,
    refresh,
  };
}

export default useStudents;
