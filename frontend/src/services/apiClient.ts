import createClient, { type Middleware } from 'openapi-fetch';
import type { paths } from '../types/api.generated';
import type { AuthService } from './authService';
import { firebaseAuthService } from './firebaseAuthService';
import { API_BASE_URL } from '../config';
import type { LanguageCode } from '../lib/languages';

const baseUrl = API_BASE_URL;

let _authService: AuthService = firebaseAuthService;

export function setAuthService(service: AuthService): void {
  _authService = service;
}

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    const token = await _authService.getToken();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
};

const serverErrorMiddleware: Middleware = {
  async onResponse({ response }) {
    if (response.status === 500 || response.status === 503) {
      window.dispatchEvent(new CustomEvent('api-server-error'));
    }
    return response;
  },
};

const client = createClient<paths>({ baseUrl });
client.use(authMiddleware);
client.use(serverErrorMiddleware);

export default client;

// Convenience function to test auth with /api/v1/me endpoint
export const getCurrentUser = async () => {
  const { data, error } = await client.GET('/api/v1/me');
  if (error) {
    throw error;
  }
  return data;
};

export const updateLanguage = async (language: LanguageCode) => {
  const { data, error } = await client.PATCH('/api/v1/me/language', {
    body: { language },
  });
  if (error) {
    throw error;
  }
  return data;
};
