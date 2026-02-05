# Story 1.3: Frontend Login Flow

Status: done

## Story

As a **BD team member**,
I want **to log in using my credentials**,
So that **I can access the Store ICU application securely**.

## Acceptance Criteria

1. **Given** I am not logged in **When** I navigate to any protected page (e.g., `/dashboard`) **Then** I am redirected to `/login`

2. **Given** I am on the login page **When** I enter valid email/password and click "Login" **Then**:
   - Firebase Auth authenticates me
   - The app stores the auth token
   - I am redirected to `/dashboard`
   - The header shows my email and a logout button

3. **Given** I am logged in and refresh the page **When** the page loads **Then**:
   - My auth state persists (I remain logged in)
   - I see the dashboard, not the login page

4. **Given** I am logged in **When** I click "Logout" **Then**:
   - Firebase Auth signs me out
   - I am redirected to `/login`
   - Protected routes are no longer accessible

5. **Given** I enter invalid credentials **When** I click "Login" **Then**:
   - I see a user-friendly error message (e.g., "Invalid email or password")
   - I remain on the login page

## Tasks / Subtasks

- [x] Task 1: Install Firebase Dependencies (AC: #1-5)
  - [x] Add `firebase` SDK to package.json
  - [x] Run `npm install` to install dependencies

- [x] Task 2: Configure Firebase Client SDK (AC: #1-5)
  - [x] Create `frontend/src/firebase/config.ts` with Firebase initialization
  - [x] Create `frontend/src/firebase/auth.ts` with auth helper functions
  - [x] Add Firebase config to `.env.example` and `.env.local`

- [x] Task 3: Implement AuthContext for State Management (AC: #1-5)
  - [x] Create `frontend/src/context/AuthContext.tsx`
  - [x] Implement `AuthProvider` component with Firebase `onAuthStateChanged`
  - [x] Implement `useAuth` hook returning user, loading, login, logout
  - [x] Handle auth persistence across page refreshes

- [x] Task 4: Create Protected Route Component (AC: #1, #4)
  - [x] Create `frontend/src/components/auth/ProtectedRoute.tsx`
  - [x] Redirect unauthenticated users to `/login`
  - [x] Show loading state while checking auth
  - [x] Preserve intended destination for redirect after login

- [x] Task 5: Create Login Page (AC: #2, #5)
  - [x] Create `frontend/src/pages/LoginPage.tsx`
  - [x] Implement email/password form with React Hook Form
  - [x] Style with Tailwind CSS (light mode, professional appearance)
  - [x] Handle form validation (required fields, email format)
  - [x] Display loading state during authentication
  - [x] Display error messages for failed login attempts

- [x] Task 6: Create Dashboard Page (AC: #2, #3)
  - [x] Create `frontend/src/pages/DashboardPage.tsx`
  - [x] Display placeholder content with welcome message
  - [x] Show current user's email
  - [x] Protect route with `ProtectedRoute` component

- [x] Task 7: Create Header Component with Logout (AC: #2, #4)
  - [x] Create `frontend/src/components/layout/Header.tsx`
  - [x] Display user email when logged in
  - [x] Implement logout button with confirmation
  - [x] Style with dark sidebar theme per UX spec

- [x] Task 8: Configure React Router (AC: #1-5)
  - [x] Install `react-router-dom`
  - [x] Set up routes in `App.tsx`: `/login`, `/dashboard`
  - [x] Configure default redirect from `/` to `/dashboard`
  - [x] Wrap app with `AuthProvider` and `BrowserRouter`

- [x] Task 9: Wire API Client with Auth Token (AC: #2, #3)
  - [x] Create `frontend/src/services/apiClient.ts`
  - [x] Configure to include `Authorization: Bearer <token>` header
  - [x] Get token from Firebase current user
  - [x] Test integration with `/api/v1/me` endpoint

- [x] Task 10: Write Tests (AC: #1-5)
  - [x] Test: Login page renders form correctly
  - [x] Test: Successful login redirects to dashboard
  - [x] Test: Failed login shows error message
  - [x] Test: Protected route redirects unauthenticated users
  - [x] Test: Logout clears auth state

## Dev Notes

### Technical Stack Requirements

| Component | Technology | Version | Notes |
|-----------|------------|---------|-------|
| Firebase Client SDK | firebase | 10.x | Auth with email/password |
| Routing | react-router-dom | 6.x | Latest with data loading |
| Forms | react-hook-form | 7.x | Already installed |
| State (Auth only) | React Context | - | Per architecture spec |
| Styling | Tailwind CSS | 4.x | Already configured |
| API Client | openapi-fetch | - | Already installed |

### Firebase Client SDK Setup

**Firebase Config (firebase/config.ts):**
```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

export const firebaseApp = initializeApp(firebaseConfig);
export const firebaseAuth = getAuth(firebaseApp);
```

**Auth Helpers (firebase/auth.ts):**
```typescript
import {
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User
} from 'firebase/auth';
import { firebaseAuth } from './config';

export const loginWithEmail = async (email: string, password: string) => {
  return signInWithEmailAndPassword(firebaseAuth, email, password);
};

export const logout = async () => {
  return signOut(firebaseAuth);
};

export const subscribeToAuthChanges = (callback: (user: User | null) => void) => {
  return onAuthStateChanged(firebaseAuth, callback);
};

export const getCurrentUserToken = async (): Promise<string | null> => {
  const user = firebaseAuth.currentUser;
  if (!user) return null;
  return user.getIdToken();
};
```

### AuthContext Pattern

**AuthContext.tsx:**
```typescript
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from 'firebase/auth';
import { subscribeToAuthChanges, loginWithEmail, logout as firebaseLogout } from '../firebase/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = subscribeToAuthChanges((user) => {
      setUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const login = async (email: string, password: string) => {
    await loginWithEmail(email, password);
  };

  const logout = async () => {
    await firebaseLogout();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Protected Route Pattern

**ProtectedRoute.tsx:**
```typescript
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!user) {
    // Save intended destination for redirect after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
```

### Login Page Pattern

**LoginPage.tsx:**
```typescript
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FirebaseError } from 'firebase/app';

interface LoginForm {
  email: string;
  password: string;
}

export const LoginPage = () => {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

  // Redirect if already logged in
  const from = (location.state as { from?: Location })?.from?.pathname || '/dashboard';

  if (user) {
    navigate(from, { replace: true });
    return null;
  }

  const onSubmit = async (data: LoginForm) => {
    setError(null);
    setIsSubmitting(true);
    try {
      await login(data.email, data.password);
      navigate(from, { replace: true });
    } catch (err) {
      if (err instanceof FirebaseError) {
        setError(getFirebaseErrorMessage(err.code));
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F4F4F5]">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-semibold text-[#18181B] mb-6 text-center">
          Store ICU Login
        </h1>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Form fields here */}
        </form>
      </div>
    </div>
  );
};

const getFirebaseErrorMessage = (code: string): string => {
  switch (code) {
    case 'auth/user-not-found':
    case 'auth/wrong-password':
    case 'auth/invalid-credential':
      return 'Invalid email or password';
    case 'auth/too-many-requests':
      return 'Too many failed attempts. Please try again later.';
    case 'auth/user-disabled':
      return 'This account has been disabled';
    default:
      return 'Login failed. Please try again.';
  }
};
```

### API Client with Auth Token

**apiClient.ts:**
```typescript
import createClient from 'openapi-fetch';
import type { paths } from './api-schema'; // Generated from OpenAPI spec
import { getCurrentUserToken } from '../firebase/auth';

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = createClient<paths>({ baseUrl });

// Add auth token to all requests
client.use({
  async onRequest({ request }) {
    const token = await getCurrentUserToken();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
});

export default client;
```

### Router Configuration

**App.tsx:**
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

### UX Design Requirements

**Visual Design (from ux-design-specification.md):**

| Element | Specification |
|---------|---------------|
| Background | Page: `#F4F4F5` (Light Gray) |
| Login card | White (`#FFFFFF`), 8px radius, shadow |
| Primary button | Blue `#4361EE`, white text, 8px radius |
| Text primary | `#18181B` (Near Black) |
| Text muted | `#71717A` (Gray) |
| Error text | `#EF4444` (Red) |
| Focus ring | 2px `#4361EE` (Blue) |
| Font | Inter (system default from shadcn/ui) |

**Layout Structure:**
- Centered login card on light gray background
- Card width: max-w-md (448px)
- Card padding: 32px (p-8)
- Form spacing: 16px between fields (space-y-4)

**Header Component (Dark Sidebar Theme):**
```
┌─────────────────────────────────────────────────────────────┐
│  Store ICU                    user@email.com    [Logout]    │
│  ─────────────────────────────────────────────────────────  │
│  (Dark background #18181B, white text)                      │
└─────────────────────────────────────────────────────────────┘
```

### Environment Variables

**Add to `.env.example`:**
```env
# Firebase Client SDK
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id

# API
VITE_API_BASE_URL=http://localhost:8000
```

### File Structure

**Files to Create:**

| File | Purpose |
|------|---------|
| `frontend/src/firebase/config.ts` | Firebase initialization |
| `frontend/src/firebase/auth.ts` | Auth helper functions |
| `frontend/src/context/AuthContext.tsx` | Auth state management |
| `frontend/src/components/auth/ProtectedRoute.tsx` | Route protection |
| `frontend/src/components/layout/Header.tsx` | App header with logout |
| `frontend/src/pages/LoginPage.tsx` | Login form page |
| `frontend/src/pages/DashboardPage.tsx` | Dashboard placeholder |
| `frontend/src/services/apiClient.ts` | API client with auth |
| `frontend/.env.example` | Environment template |

**Files to Modify:**

| File | Changes |
|------|---------|
| `frontend/package.json` | Add firebase, react-router-dom |
| `frontend/src/App.tsx` | Add routing and AuthProvider |

### Naming Conventions (MUST FOLLOW)

| Element | Pattern | Example |
|---------|---------|---------|
| Component files | `PascalCase.tsx` | `LoginPage.tsx` |
| Component exports | `PascalCase` | `export const LoginPage` |
| Hooks | `useCamelCase` | `useAuth` |
| Context files | `PascalCase.tsx` | `AuthContext.tsx` |
| Utility files | `camelCase.ts` | `apiClient.ts` |
| TypeScript interfaces | `PascalCase` | `AuthContextType` |

### Testing Strategy

**Component Tests (Vitest + React Testing Library):**
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';

// Mock AuthContext
const mockLogin = vi.fn();
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    loading: false,
    login: mockLogin,
    logout: vi.fn(),
  }),
}));

describe('LoginPage', () => {
  it('renders login form', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('shows error on invalid credentials', async () => {
    mockLogin.mockRejectedValueOnce({ code: 'auth/invalid-credential' });
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    await userEvent.type(screen.getByLabelText(/email/i), 'test@test.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'wrong');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });
});
```

### Anti-Patterns to Avoid

1. **DO NOT** store Firebase auth state in localStorage manually — Firebase SDK handles persistence
2. **DO NOT** use Redux or Zustand for auth state — use React Context per architecture spec
3. **DO NOT** call backend without auth token — always include `Authorization` header
4. **DO NOT** expose Firebase Admin credentials to frontend — use client SDK only
5. **DO NOT** implement custom token refresh — Firebase SDK handles this automatically
6. **DO NOT** create dark mode styles — light mode only per UX spec
7. **DO NOT** use class components — use functional components with hooks
8. **DO NOT** skip loading states — show spinner while auth state is initializing

### Previous Story Intelligence

**From Story 1.2 (Firebase Auth Backend Integration):**
- Backend `/api/v1/me` endpoint exists for testing auth
- Token validation returns `AUTH_TOKEN_MISSING` (no header) or `AUTH_TOKEN_INVALID` (bad token)
- User is auto-created on first login with role `member`
- Backend expects `Authorization: Bearer <token>` header
- Error response format: `{ "code": "...", "detail": "...", "timestamp": "..." }`

**From Story 1.1 (Project Structure):**
- Frontend uses Tailwind CSS v4 with `@tailwindcss/postcss` plugin
- TanStack Query, React Hook Form, openapi-fetch already installed
- TypeScript strict mode enabled
- Directory structure: `components/`, `pages/`, `hooks/`, `services/`, `firebase/`, `context/`

### Git Intelligence Summary

Recent commits show:
- Story 1.1: Project structure with React + Vite + Tailwind v4
- Story 1.2: Firebase Admin SDK on backend with `/api/v1/me` endpoint
- Code review fixes applied: Pydantic config pattern, type declarations

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3: Frontend Login Flow]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication Flow]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design System Foundation]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual Design Foundation]
- [Source: _bmad-output/implementation-artifacts/1-2-firebase-auth-backend-integration.md#Dev Notes]
- [Source: _bmad-output/implementation-artifacts/1-1-initialize-project-structure.md#Dev Notes]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None

### Completion Notes List

- Installed Firebase SDK v12.8.0 and React Router DOM v7.13.0
- Created Firebase configuration with environment variable support for secure credential handling
- Implemented AuthContext with onAuthStateChanged for automatic auth state persistence
- Created ProtectedRoute component that redirects unauthenticated users and preserves intended destination
- Built LoginPage with React Hook Form validation, loading states, and user-friendly error messages
- Created DashboardPage with Header showing user email and logout functionality
- Header includes logout confirmation modal with dark theme styling per UX spec
- Configured React Router with `/login`, `/dashboard`, and root redirect
- Created API client with middleware that automatically injects Firebase auth token
- Added comprehensive test suite with Vitest + React Testing Library (27 tests passing)
- All code follows TypeScript strict mode with proper type imports

### Change Log

- 2026-02-05: Implemented complete frontend login flow (Story 1.3)
- 2026-02-05: Code Review fixes applied:
  - Fixed test warnings by wrapping async state updates in act()
  - Added missing API client tests (6 tests for auth middleware)
  - Added modal accessibility: focus trapping, Escape key, aria-modal, role="dialog", backdrop click-to-close
  - Added form accessibility: aria-describedby, aria-invalid, role="alert" for error messages
  - Improved redirect handling in LoginPage (shows "Redirecting..." instead of blank)
  - Added ESLint disable comment explanation in AuthContext
  - Fixed vite.config.ts import to use 'vite' instead of 'vitest/config'

### File List

**New Files:**
- frontend/src/firebase/config.ts
- frontend/src/firebase/auth.ts
- frontend/src/context/AuthContext.tsx
- frontend/src/components/auth/ProtectedRoute.tsx
- frontend/src/components/auth/ProtectedRoute.test.tsx
- frontend/src/components/layout/Header.tsx
- frontend/src/components/layout/Header.test.tsx
- frontend/src/pages/LoginPage.tsx
- frontend/src/pages/LoginPage.test.tsx
- frontend/src/pages/DashboardPage.tsx
- frontend/src/services/apiClient.ts
- frontend/src/services/apiClient.test.ts
- frontend/src/test/setup.ts
- frontend/.env.example

**Modified Files:**
- frontend/package.json (added firebase, react-router-dom, vitest, testing-library dependencies)
- frontend/package-lock.json (dependency lock file updated)
- frontend/src/App.tsx (added routing and AuthProvider)
- frontend/vite.config.ts (added Vitest configuration)
- frontend/tsconfig.node.json (added vitest types)
