import '@testing-library/jest-dom';

// Mock IntersectionObserver for jsdom (used by EvaluationSections scroll tracking)
class MockIntersectionObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
});
