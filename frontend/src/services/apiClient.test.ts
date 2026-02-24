import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { getCurrentUserToken } from '../firebase/auth';

// Mock the firebase auth module
vi.mock('../firebase/auth', () => ({
  getCurrentUserToken: vi.fn(),
}));

const mockedGetCurrentUserToken = vi.mocked(getCurrentUserToken);

describe('apiClient', () => {
  let originalFetch: typeof global.fetch;

  beforeEach(() => {
    vi.clearAllMocks();
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    vi.resetModules();
  });

  describe('auth middleware', () => {
    it('adds Authorization header when user has a token', async () => {
      // Capture the fetch call to verify headers
      let capturedRequest: Request | undefined;

      global.fetch = vi.fn().mockImplementation((input: Request) => {
        capturedRequest = input;
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: '123',
              email: 'test@example.com',
              role: 'member',
              created_at: '2026-02-05T00:00:00Z',
              last_login: '2026-02-05T00:00:00Z',
            }),
            {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            }
          )
        );
      });

      mockedGetCurrentUserToken.mockResolvedValue('test-firebase-token');

      // Re-import to get fresh module with mocked fetch
      const { getCurrentUser } = await import('./apiClient');
      await getCurrentUser();

      expect(capturedRequest).toBeDefined();
      expect(capturedRequest?.headers.get('Authorization')).toBe(
        'Bearer test-firebase-token'
      );
    });

    it('does not add Authorization header when user has no token', async () => {
      let capturedRequest: Request | undefined;

      global.fetch = vi.fn().mockImplementation((input: Request) => {
        capturedRequest = input;
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: '123',
              email: 'test@example.com',
              role: 'member',
              created_at: '2026-02-05T00:00:00Z',
              last_login: '2026-02-05T00:00:00Z',
            }),
            {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            }
          )
        );
      });

      mockedGetCurrentUserToken.mockResolvedValue(null);

      const { getCurrentUser } = await import('./apiClient');
      await getCurrentUser();

      expect(capturedRequest).toBeDefined();
      expect(capturedRequest?.headers.get('Authorization')).toBeNull();
    });

    it('calls getCurrentUserToken for each request', async () => {
      global.fetch = vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            id: '123',
            email: 'test@example.com',
            role: 'member',
            created_at: '2026-02-05T00:00:00Z',
            last_login: '2026-02-05T00:00:00Z',
          }),
          {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          }
        )
      );

      mockedGetCurrentUserToken.mockResolvedValue('token-1');

      const { getCurrentUser } = await import('./apiClient');
      await getCurrentUser();

      expect(mockedGetCurrentUserToken).toHaveBeenCalledTimes(1);
    });
  });

  describe('server error middleware', () => {
    it('dispatches api-server-error event on HTTP 500', async () => {
      const eventHandler = vi.fn();
      window.addEventListener('api-server-error', eventHandler);

      global.fetch = vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Internal Server Error' }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' },
        })
      );

      mockedGetCurrentUserToken.mockResolvedValue('test-token');

      const { getCurrentUser } = await import('./apiClient');
      try { await getCurrentUser(); } catch { /* expected to throw */ }

      expect(eventHandler).toHaveBeenCalledTimes(1);
      window.removeEventListener('api-server-error', eventHandler);
    });

    it('does not dispatch event on HTTP 401', async () => {
      const eventHandler = vi.fn();
      window.addEventListener('api-server-error', eventHandler);

      global.fetch = vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Unauthorized' }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        })
      );

      mockedGetCurrentUserToken.mockResolvedValue('test-token');

      const { getCurrentUser } = await import('./apiClient');
      try { await getCurrentUser(); } catch { /* expected to throw */ }

      expect(eventHandler).not.toHaveBeenCalled();
      window.removeEventListener('api-server-error', eventHandler);
    });

    it('does not dispatch event on HTTP 404', async () => {
      const eventHandler = vi.fn();
      window.addEventListener('api-server-error', eventHandler);

      global.fetch = vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Not found' }), {
          status: 404,
          headers: { 'Content-Type': 'application/json' },
        })
      );

      mockedGetCurrentUserToken.mockResolvedValue('test-token');

      const { getCurrentUser } = await import('./apiClient');
      try { await getCurrentUser(); } catch { /* expected to throw */ }

      expect(eventHandler).not.toHaveBeenCalled();
      window.removeEventListener('api-server-error', eventHandler);
    });
  });

  describe('getCurrentUser', () => {
    it('makes request to /api/v1/me endpoint', async () => {
      let capturedUrl: string | undefined;

      global.fetch = vi.fn().mockImplementation((input: Request) => {
        capturedUrl = input.url;
        return Promise.resolve(
          new Response(
            JSON.stringify({
              id: '123',
              email: 'test@example.com',
              role: 'member',
              created_at: '2026-02-05T00:00:00Z',
              last_login: '2026-02-05T00:00:00Z',
            }),
            {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            }
          )
        );
      });

      mockedGetCurrentUserToken.mockResolvedValue('test-token');

      const { getCurrentUser } = await import('./apiClient');
      await getCurrentUser();

      expect(capturedUrl).toContain('/api/v1/me');
    });

    it('returns user data on success', async () => {
      const userData = {
        id: '123',
        email: 'test@example.com',
        role: 'member',
        created_at: '2026-02-05T00:00:00Z',
        last_login: '2026-02-05T00:00:00Z',
      };

      global.fetch = vi.fn().mockResolvedValue(
        new Response(JSON.stringify(userData), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        })
      );

      mockedGetCurrentUserToken.mockResolvedValue('test-token');

      const { getCurrentUser } = await import('./apiClient');
      const result = await getCurrentUser();

      expect(result).toEqual(userData);
    });

    it('throws error on API error response', async () => {
      const errorResponse = {
        code: 'AUTH_TOKEN_INVALID',
        detail: 'Token validation failed',
      };

      global.fetch = vi.fn().mockResolvedValue(
        new Response(JSON.stringify(errorResponse), {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        })
      );

      mockedGetCurrentUserToken.mockResolvedValue('invalid-token');

      const { getCurrentUser } = await import('./apiClient');

      await expect(getCurrentUser()).rejects.toMatchObject(errorResponse);
    });
  });
});
