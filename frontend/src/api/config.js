// API Configuration
// VITE_API_URL must be set in .env file - no hardcoded fallback
export const API_BASE_URL = import.meta.env.VITE_API_URL;

if (!API_BASE_URL) {
  console.error('VITE_API_URL environment variable is not set. Please configure your .env file.');
}

// Custom API Error class for structured error handling
export class ApiError extends Error {
  constructor(message, status, details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

// Event emitter for auth events (401 handling)
const authEventListeners = new Set();

export const authEvents = {
  subscribe: (callback) => {
    authEventListeners.add(callback);
    return () => authEventListeners.delete(callback);
  },
  emit: (event) => {
    authEventListeners.forEach(callback => callback(event));
  }
};

// Request interceptor - adds auth token to requests
function applyRequestInterceptor(options = {}) {
  const token = localStorage.getItem('token');
  
  return {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };
}

// Response interceptor - handles errors including 401
async function handleResponse(response) {
  if (response.ok) {
    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return null;
    }
    return response.json();
  }

  // Parse error response
  let errorData;
  try {
    errorData = await response.json();
  } catch {
    errorData = { message: 'Request failed' };
  }

  const errorMessage = errorData.error?.message || errorData.message || 'Request failed';
  const errorDetails = errorData.error?.details || errorData.details || null;

  // Handle 401 Unauthorized - emit event for auth context to handle
  if (response.status === 401) {
    authEvents.emit({ type: 'unauthorized', message: errorMessage });
  }

  throw new ApiError(errorMessage, response.status, errorDetails);
}

// Helper function for API calls with centralized error handling
export async function apiRequest(endpoint, options = {}) {
  const config = applyRequestInterceptor(options);
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    return await handleResponse(response);
  } catch (error) {
    // Re-throw ApiError as-is
    if (error instanceof ApiError) {
      throw error;
    }
    // Wrap network errors
    throw new ApiError(
      error.message || 'Network error. Please check your connection.',
      0,
      null
    );
  }
}

// Auth API
export const authAPI = {
  login: (email, password) => 
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  
  signup: (data) =>
    apiRequest('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  logout: () => 
    apiRequest('/auth/logout', { method: 'POST' }),
  
  getProfile: () => 
    apiRequest('/auth/me'),
  
  getSchools: () =>
    apiRequest('/auth/schools'),
};

// Schools API
export const schoolsAPI = {
  getAll: () => apiRequest('/schools'),
  getById: (id) => apiRequest(`/schools/${id}`),
  getClasses: (schoolId) => apiRequest(`/schools/${schoolId}/classes`),
  getTeachers: (schoolId) => apiRequest(`/schools/${schoolId}/teachers`),
  getAllStudents: (schoolId) => apiRequest(`/schools/${schoolId}/students`),
  getSummary: (schoolId) => apiRequest(`/schools/${schoolId}/summary`),
  getMetrics: (schoolId) => apiRequest(`/schools/${schoolId}/metrics`),
};

// Classes API
export const classesAPI = {
  getById: (id) => apiRequest(`/classes/${id}`),
  getStudents: (classId) => apiRequest(`/classes/${classId}/children`),
  getMetrics: (classId) => apiRequest(`/analytics/class/${classId}`),
  create: (data) => apiRequest('/classes', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => apiRequest(`/classes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => apiRequest(`/classes/${id}`, {
    method: 'DELETE',
  }),
};

// Students/Children API
export const studentsAPI = {
  getById: (id) => apiRequest(`/children/${id}`),
  getMetrics: (childId) => apiRequest(`/analytics/child/${childId}`),
  getSkillProfile: (childId) => apiRequest(`/children/${childId}/skill-profile`),
  getInsights: (childId) => apiRequest(`/insights/child/${childId}`),
  create: (data) => apiRequest('/children', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  update: (id, data) => apiRequest(`/children/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  delete: (id) => apiRequest(`/children/${id}`, {
    method: 'DELETE',
  }),
};

// Teachers API (Admin only)
export const teachersAPI = {
  getAll: (schoolId) => apiRequest(`/schools/${schoolId}/teachers`),
  getById: (id) => apiRequest(`/teachers/${id}`),
  getClasses: (teacherId) => apiRequest(`/teachers/${teacherId}/classes`),
};

// Analytics API
export const analyticsAPI = {
  getSchoolMetrics: (schoolId) => apiRequest(`/analytics/school/${schoolId}`),
  getClassMetrics: (classId) => apiRequest(`/analytics/classes/${classId}/metrics`),
  getChildMetrics: (childId) => apiRequest(`/analytics/children/${childId}/metrics`),
  getClassSkillOverview: (classId) => apiRequest(`/analytics/classes/${classId}/skill-overview`),
  getChildSkillProfile: (childId) => apiRequest(`/analytics/children/${childId}/skill-profile`),
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
