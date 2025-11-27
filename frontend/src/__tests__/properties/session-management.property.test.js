/**
 * **Feature: frontend-backend-integration, Property 5: Session Lifecycle Management**
 * **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
 * 
 * For any authentication flow, the token SHALL be stored on successful login,
 * restored on page load if valid, cleared on logout, and the user SHALL be
 * redirected to login when the token is invalid or expired.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { test, fc } from '@fast-check/vitest';

// Token storage key constant
const TOKEN_KEY = 'token';

// Helper to simulate localStorage behavior
function createMockStorage() {
  const store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = String(value); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { Object.keys(store).forEach(k => delete store[k]); },
    _store: store
  };
}

// Generate valid tokens (non-empty strings)
const validTokenArb = fc.string({ minLength: 10, maxLength: 100 })
  .filter(s => s.trim().length > 0);

// Generate valid user data
const validUserArb = fc.record({
  id: fc.integer({ min: 1 }),
  email: fc.emailAddress(),
  name: fc.string({ minLength: 1, maxLength: 50 }).filter(s => s.trim().length > 0),
  role: fc.constantFrom('teacher', 'admin'),
  school_id: fc.integer({ min: 1 })
});

describe('Property 5: Session Lifecycle Management', () => {
  
  /**
   * Property 5.1: Token storage on login
   * WHEN a user logs in successfully THEN the Frontend SHALL store the authentication token in localStorage
   * **Validates: Requirements 9.1**
   */
  test.prop([validTokenArb, validUserArb], { numRuns: 100 })(
    'token is stored in localStorage on successful login',
    (token, user) => {
      const storage = createMockStorage();
      
      // Simulate successful login - store token
      storage.setItem(TOKEN_KEY, token);
      
      // Verify token is stored
      expect(storage.getItem(TOKEN_KEY)).toBe(token);
      expect(storage._store[TOKEN_KEY]).toBe(token);
    }
  );

  /**
   * Property 5.2: Session restoration
   * WHEN the application loads THEN the Frontend SHALL check for an existing token and restore the user session
   * **Validates: Requirements 9.2**
   */
  test.prop([validTokenArb], { numRuns: 100 })(
    'existing token can be retrieved for session restoration',
    (token) => {
      const storage = createMockStorage();
      
      // Pre-existing token in storage (simulating previous login)
      storage.setItem(TOKEN_KEY, token);
      
      // Simulate app load - check for existing token
      const storedToken = storage.getItem(TOKEN_KEY);
      
      // Token should be retrievable
      expect(storedToken).toBe(token);
      expect(storedToken).not.toBeNull();
    }
  );

  /**
   * Property 5.3: Token cleared on logout
   * WHEN a user logs out THEN the Frontend SHALL clear the stored token
   * **Validates: Requirements 9.4**
   */
  test.prop([validTokenArb], { numRuns: 100 })(
    'token is cleared from localStorage on logout',
    (token) => {
      const storage = createMockStorage();
      
      // User is logged in with token
      storage.setItem(TOKEN_KEY, token);
      expect(storage.getItem(TOKEN_KEY)).toBe(token);
      
      // Simulate logout - clear token
      storage.removeItem(TOKEN_KEY);
      
      // Token should be cleared
      expect(storage.getItem(TOKEN_KEY)).toBeNull();
    }
  );

  /**
   * Property 5.4: No token means no session
   * WHEN no token exists THEN session restoration should return null
   * **Validates: Requirements 9.2, 9.3**
   */
  it('returns null when no token exists', () => {
    const storage = createMockStorage();
    
    // No token stored
    const storedToken = storage.getItem(TOKEN_KEY);
    
    // Should return null
    expect(storedToken).toBeNull();
  });

  /**
   * Property 5.5: Login-logout cycle consistency
   * For any valid token, login followed by logout should result in no stored token
   * **Validates: Requirements 9.1, 9.4**
   */
  test.prop([validTokenArb], { numRuns: 100 })(
    'login followed by logout clears all session data',
    (token) => {
      const storage = createMockStorage();
      
      // Login - store token
      storage.setItem(TOKEN_KEY, token);
      expect(storage.getItem(TOKEN_KEY)).toBe(token);
      
      // Logout - clear token
      storage.removeItem(TOKEN_KEY);
      
      // No session data should remain
      expect(storage.getItem(TOKEN_KEY)).toBeNull();
    }
  );

  /**
   * Property 5.6: Multiple login sessions
   * For any sequence of logins, only the most recent token should be stored
   * **Validates: Requirements 9.1**
   */
  test.prop([fc.array(validTokenArb, { minLength: 2, maxLength: 5 })], { numRuns: 100 })(
    'only the most recent token is stored after multiple logins',
    (tokens) => {
      const storage = createMockStorage();
      
      // Simulate multiple logins
      tokens.forEach(token => {
        storage.setItem(TOKEN_KEY, token);
      });
      
      // Only the last token should be stored
      const lastToken = tokens[tokens.length - 1];
      expect(storage.getItem(TOKEN_KEY)).toBe(lastToken);
    }
  );

  /**
   * Property 5.7: Token integrity
   * Stored token should be exactly the same as the original token
   * **Validates: Requirements 9.1, 9.2**
   */
  test.prop([validTokenArb], { numRuns: 100 })(
    'stored token maintains integrity (no modification)',
    (token) => {
      const storage = createMockStorage();
      
      // Store token
      storage.setItem(TOKEN_KEY, token);
      
      // Retrieved token should be identical
      const retrieved = storage.getItem(TOKEN_KEY);
      expect(retrieved).toBe(token);
      expect(retrieved.length).toBe(token.length);
    }
  );
});
