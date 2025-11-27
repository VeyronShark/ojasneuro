// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://ojasneuro-backend.onrender.com';

// Helper function for API calls
export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.error?.message || error.message || 'Request failed');
  }
  
  return response.json();
}

// Auth API
export const authAPI = {
  login: (email, password) => 
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  
  logout: () => 
    apiRequest('/auth/logout', { method: 'POST' }),
  
  getProfile: () => 
    apiRequest('/auth/me'),
};

// Schools API
export const schoolsAPI = {
  getAll: () => apiRequest('/schools'),
  getById: (id) => apiRequest(`/schools/${id}`),
  getClasses: (schoolId) => apiRequest(`/schools/${schoolId}/classes`),
};

// Classes API
export const classesAPI = {
  getById: (id) => apiRequest(`/classes/${id}`),
  getStudents: (classId) => apiRequest(`/classes/${classId}/children`),
};

// Analytics API
export const analyticsAPI = {
  getSchoolMetrics: (schoolId) => apiRequest(`/analytics/school/${schoolId}`),
  getClassMetrics: (classId) => apiRequest(`/analytics/class/${classId}`),
  getChildMetrics: (childId) => apiRequest(`/analytics/child/${childId}`),
};

// Events API
export const eventsAPI = {
  getByChild: (childId) => apiRequest(`/events/child/${childId}`),
};

// Insights API
export const insightsAPI = {
  getByChild: (childId) => apiRequest(`/insights/child/${childId}`),
  getByClass: (classId) => apiRequest(`/insights/class/${classId}`),
};

// Consent API
export const consentAPI = {
  getByChild: (childId) => apiRequest(`/consent/child/${childId}`),
  update: (childId, data) => 
    apiRequest(`/consent/child/${childId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

// Reports API
export const reportsAPI = {
  getChildReport: (childId) => apiRequest(`/reports/child/${childId}`),
  downloadChildPDF: (childId) => 
    fetch(`${API_BASE_URL}/reports/child/${childId}/pdf`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    }),
};

// Templates API
export const templatesAPI = {
  getAll: () => apiRequest('/templates'),
  getById: (id) => apiRequest(`/templates/${id}`),
};
