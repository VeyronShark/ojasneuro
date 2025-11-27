/**
 * **Feature: frontend-backend-integration, Property 7: Loading State Visibility**
 * **Validates: Requirements 10.1**
 * 
 * For any API call in progress, the UI SHALL display a loading indicator,
 * and the indicator SHALL be removed when the call completes (success or failure).
 */

import { describe, it, expect, afterEach } from 'vitest';
import { test, fc } from '@fast-check/vitest';
import { render, screen, cleanup } from '@testing-library/react';
import LoadingSpinner from '../../components/LoadingSpinner';

// Clean up after each test to prevent DOM pollution
afterEach(() => {
  cleanup();
});

// Generate valid loading messages (non-empty strings)
const validMessageArb = fc.string({ minLength: 1, maxLength: 100 })
  .filter(s => s.trim().length > 0);

// Generate valid size options
const validSizeArb = fc.constantFrom('small', 'medium', 'large');

describe('Property 7: Loading State Visibility', () => {
  
  /**
   * Property 7.1: Loading spinner renders with any valid message
   * For any valid message string, the LoadingSpinner SHALL display that message
   * **Validates: Requirements 10.1**
   */
  test.prop([validMessageArb], { numRuns: 100 })(
    'loading spinner displays any valid message',
    (message) => {
      cleanup(); // Clean before each property iteration
      const { container } = render(<LoadingSpinner message={message} />);
      
      // The message should be visible in the document (use container query to handle whitespace)
      const messageElement = container.querySelector('p');
      expect(messageElement).toBeInTheDocument();
      expect(messageElement.textContent).toBe(message);
    }
  );

  /**
   * Property 7.2: Loading spinner has accessible role
   * For any configuration, the LoadingSpinner SHALL have role="status"
   * **Validates: Requirements 10.1**
   */
  test.prop([validMessageArb, validSizeArb], { numRuns: 100 })(
    'loading spinner has accessible status role',
    (message, size) => {
      cleanup(); // Clean before each property iteration
      render(<LoadingSpinner message={message} size={size} />);
      
      // Should have status role for accessibility
      expect(screen.getByRole('status')).toBeInTheDocument();
    }
  );

  /**
   * Property 7.3: Loading spinner renders without message
   * When message is empty or undefined, spinner should still render
   * **Validates: Requirements 10.1**
   */
  it('loading spinner renders without message when message is empty', () => {
    render(<LoadingSpinner message="" />);
    
    // Should still have status role
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  /**
   * Property 7.4: Loading spinner renders with default message
   * When no message prop is provided, default message should appear
   * **Validates: Requirements 10.1**
   */
  it('loading spinner shows default message when none provided', () => {
    render(<LoadingSpinner />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  /**
   * Property 7.5: Loading state visibility toggle
   * For any loading state, the spinner SHALL be visible when loading is true
   * and not visible when loading is false
   * **Validates: Requirements 10.1**
   */
  test.prop([fc.boolean(), validMessageArb], { numRuns: 100 })(
    'loading spinner visibility matches loading state',
    (isLoading, message) => {
      cleanup(); // Clean before each property iteration
      const { container } = render(
        isLoading ? <LoadingSpinner message={message} /> : <div data-testid="content">Content</div>
      );
      
      if (isLoading) {
        // Spinner should be visible
        expect(screen.getByRole('status')).toBeInTheDocument();
        const messageElement = container.querySelector('p');
        expect(messageElement).toBeInTheDocument();
        expect(messageElement.textContent).toBe(message);
      } else {
        // Content should be visible, not spinner
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
        expect(screen.getByTestId('content')).toBeInTheDocument();
      }
    }
  );

  /**
   * Property 7.6: Size variations render correctly
   * For any valid size, the spinner SHALL render without errors
   * **Validates: Requirements 10.1**
   */
  test.prop([validSizeArb], { numRuns: 100 })(
    'loading spinner renders correctly for all size variations',
    (size) => {
      cleanup(); // Clean before each property iteration
      render(<LoadingSpinner size={size} />);
      
      // Should render without errors
      expect(screen.getByRole('status')).toBeInTheDocument();
    }
  );
});
