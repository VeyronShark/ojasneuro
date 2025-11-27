/**
 * useClasses - Hook for class management with CRUD operations
 * Requirements: 2.2, 2.3, 4.3, 4.4 - Class CRUD with auto-refresh
 */
import { useState, useCallback, useEffect } from 'react';
import { schoolsAPI, classesAPI } from '../api/config';

/**
 * Custom hook for managing classes with CRUD operations
 * @param {number|string} schoolId - The school ID to fetch classes for
 * @returns {Object} - { classes, loading, error, addClass, updateClass, deleteClass, refresh }
 */
export function useClasses(schoolId) {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchClasses = useCallback(async () => {
    if (!schoolId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await schoolsAPI.getClasses(schoolId);
      setClasses(response.classes || response || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch classes');
    } finally {
      setLoading(false);
    }
  }, [schoolId]);

  // Fetch classes on mount and when schoolId changes
  useEffect(() => {
    fetchClasses();
  }, [fetchClasses]);

  const addClass = useCallback(async (classData) => {
    setLoading(true);
    setError(null);
    
    try {
      const newClass = await classesAPI.create({
        ...classData,
        school_id: schoolId,
      });
      // Auto-refresh list after mutation
      await fetchClasses();
      return newClass;
    } catch (err) {
      setError(err.message || 'Failed to create class');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [schoolId, fetchClasses]);

  const updateClass = useCallback(async (classId, classData) => {
    setLoading(true);
    setError(null);
    
    try {
      const updatedClass = await classesAPI.update(classId, classData);
      // Auto-refresh list after mutation
      await fetchClasses();
      return updatedClass;
    } catch (err) {
      setError(err.message || 'Failed to update class');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchClasses]);

  const deleteClass = useCallback(async (classId) => {
    setLoading(true);
    setError(null);
    
    try {
      await classesAPI.delete(classId);
      // Auto-refresh list after mutation
      await fetchClasses();
    } catch (err) {
      setError(err.message || 'Failed to delete class');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchClasses]);

  const refresh = useCallback(() => {
    return fetchClasses();
  }, [fetchClasses]);

  return {
    classes,
    loading,
    error,
    addClass,
    updateClass,
    deleteClass,
    refresh,
  };
}

export default useClasses;
