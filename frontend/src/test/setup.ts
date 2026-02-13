import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Firebase to prevent auth/invalid-api-key errors in tests
class MockFirebaseError extends Error {
  code: string;
  customData?: Record<string, unknown>;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
    this.name = 'FirebaseError';
  }
}
vi.mock('firebase/app', () => ({
  initializeApp: vi.fn(() => ({})),
  FirebaseError: MockFirebaseError,
}));
vi.mock('firebase/auth', () => ({
  getAuth: vi.fn(() => ({})),
  signInWithEmailAndPassword: vi.fn(),
  signOut: vi.fn(),
  onAuthStateChanged: vi.fn(),
  reauthenticateWithCredential: vi.fn(),
  EmailAuthProvider: { credential: vi.fn() },
}));

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

// Mock pointer and scroll APIs for jsdom (used by Radix UI Select)
if (!Element.prototype.hasPointerCapture) {
  Element.prototype.hasPointerCapture = () => false;
}
if (!Element.prototype.setPointerCapture) {
  Element.prototype.setPointerCapture = () => {};
}
if (!Element.prototype.releasePointerCapture) {
  Element.prototype.releasePointerCapture = () => {};
}
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => {};
}
