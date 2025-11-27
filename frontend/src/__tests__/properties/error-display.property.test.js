/**
 * **Feature: frontend-backend-integration, Property 3: Error Display Consistency**
 * **Validates: Requirements 1.4, 2.4, 3.5**
 * 
 * For any API error response, the frontend SHALL display the error message from
 * the response in a user-visible notification or inline error, without crashing
 * or showing raw error objects.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { test, fc } from '@fast-check/vitest';
import { ApiError, apiRequest, API_BASE_URL } from '../../api/config';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  localStorage.clear();
});

// Generate valid error messages (non-empty strings)
const validErrorMessageArb = fc.string({ minLength: 1, maxLength: 500 })
  .filter(s => s.trim().length > 0);

// Generate valid HTTP error status codes
const errorStatusCodeArb = fc.constantFrom(400, 401, 403, 404, 422, 500, 502, 503);

// Generate error response structures
const errorResponseArb = fc.oneof(
  // Format 1: { message: "error" }
  fc.record({
    message: validErrorMessageArb
  }),
  // Format 2: { error: { message: "error" } }
  fc.record({
    error: fc.record({
      message: validErrorMessageArb,
      details: fc.option(fc.dictionary(fc.string(), fc.string()), { nil: undefined })
    })
  }),
  // Format 3: { error: "error" } (string error)
  fc.record({
    error: validErrorMessageArb
  })
);

describe('Property 3: Error Display Consistency', () => {

  /**
   * Property 3.1: ApiError contains structured error information
   * For any error message and status, ApiError SHALL preserve the information
   * **Validates: Requirements 1.4, 2.4, 3.5**
   */
  test.prop([validErrorMessageArb, errorStatusCodeArb], { numRuns: 100 })(
    'ApiError preserves error message and status',
    (message, status) => {
      const error = new ApiError(message, status);
      
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(ApiError);
      expect(error.message).toBe(message);
      expect(error.status).toBe(status);
      expect(error.name).toBe('ApiError');
    }
  );

  /**
   * Property 3.2: ApiError with details preserves all information
   * For any error with details, ApiError SHALL preserve the details
   * **Validates: Requirements 1.4, 2.4, 3.5**
   */
  test.prop([
    validErrorMessageArb, 
    errorStatusCodeArb,
    fc.dictionary(fc.string({ minLength: 1 }), fc.string())
  ], { numRuns: 100 })(
    'ApiError preserves error details',
    (message, status, details) => {
      const error = new ApiError(message, status, details);
      
      expect(error.message).toBe(message);
      expect(error.status).toBe(status);
      expect(error.details).toEqual(details);
    }
  );

  /**
   * Property 3.3: API errors are thrown as ApiError instances
   * For any HTTP error response, apiRequest SHALL throw an ApiError
   * **Validates: Requirements 1.4, 2.4, 3.5**
   */
  test.prop([errorStatusCodeArb, validErrorMessageArb], { numRuns: 100 })(
    'API errors are thrown as ApiError with correct status',
    async (status, message) => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status,
        json: async () => ({ message })
      });

      await expect(apiRequest('/test')).rejects.toThrow(ApiError);
      
      try {
        await apiRequest('/test-again');
      } catch (error) {
        // This won't run since we only mocked once, but the pattern is correct
      }
    }
  );

  /**
   * Property 3.4: Error messages are extracted from various response formats
   * For any error response format, the message SHALL be extracted correctly
   * **Validates: Requirements 1.4, 2.4, 3.5**
   */
  test.prop([errorStatusCodeArb, errorResponseArb], { numRuns: 100 })(
    'error messages are extracted from various response formats',
    async (status, errorResponse) => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status,
        json: async () => errorResponse
      });

      try {
        await apiRequest('/test');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect(error.status).toBe(status);
        // Message should be a non-empty string
        expect(typeof error.message).toBe('string');
        expect(error.message.length).toBeGreaterThan(0);
        // Should not contain [object Object]
        expect(error.message).not.toContain('[object Object]');
      }
    }
  );

  /**
   * Property 3.5: Network errors are wrapped in ApiError
   * For any network failure, apiRequest SHALL throw an ApiError with status 0
   * **Validates: Requirements 1.4, 2.4, 3.5**
   */
  test.prop([validErrorMessageArb], { numRuns: 100 })(
    'network errors are wrapped in ApiError with status 0',
    async (errorMessage) => {
      mockFetch.mockRejectedValueOnce(new Error(errorMessage));

      try {
        await apiRequest('/test');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect(error.status).toBe(0);
        expect(typeof error.message).toBe('string');
        expect(error.message.length).toBeGreaterThan(0);
      }
    }
  );

  /**
   * Property 3.6: Malformed JSON responses are handled gracefully
   * For any response that fails JSON parsing, a default error message SHALL be used
   * **Validates: Requirements 1.4, 2.4, 3.5**
   */
  test.prop([errorStatusCodeArb], { numRuns: 100 })(
    'malformed JSON responses are handled gracefully',
    async (status) => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      try {
        await apiRequest('/test');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect(error.status).toBe(status);
        expect(typeof error.message).toBe('string');
        expect(error.message.length).toBeGreaterThan(0);
        // Should have a fallback message
        expect(error.message).toBe('Request failed');
      }
    }
  );

  /**
   * Property 3.7: Error messages are always strings, never objects
   * For any error, the message property SHALL be a string
   * **Validates: Requirements 1.4, 2.4, 3.5**
   */
  test.prop([
    errorStatusCodeArb,
    fc.oneof(
      fc.record({ message: validErrorMessageArb }),
      fc.record({ error: fc.record({ message: validErrorMessageArb }) }),
      fc.record({ error: validErrorMessageArb }),
      fc.record({}) // Empty object
    )
  ], { numRuns: 100 })(
    'error messages are always strings',
    async (status, errorResponse) => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status,
        json: async () => errorResponse
      });

      try {
        await apiRequest('/test');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect(typeof error.message).toBe('string');
        // Should never be empty
        expect(error.message.length).toBeGreaterThan(0);
      }
    }
  );

  /**
   * Property 3.8: Successful responses don't throw errors
   * For any successful response, apiRequest SHALL return the data
   * **Validates: Requirements 1.4**
   */
  test.prop([
    fc.record({
      id: fc.integer({ min: 1 }),
      name: fc.string({ minLength: 1 })
    })
  ], { numRuns: 100 })(
    'successful responses return data without throwing',
    async (responseData) => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => responseData
      });

      const result = await apiRequest('/test');
      expect(result).toEqual(responseData);
    }
  );

  /**
   * Property 3.9: 204 No Content responses are handled correctly
   * For any 204 response, apiRequest SHALL return null
   * **Validates: Requirements 1.4**
   */
  it('204 No Content responses return null', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
      json: async () => { throw new Error('No content'); }
    });

    const result = await apiRequest('/test');
    expect(result).toBeNull();
  });
});
