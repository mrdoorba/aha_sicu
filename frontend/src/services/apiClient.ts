import createClient, { type Middleware } from 'openapi-fetch';
import { getCurrentUserToken } from '../firebase/auth';

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Define minimal paths type for now (can be replaced with generated OpenAPI types)
interface paths {
  '/api/v1/me': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              id: string;
              email: string;
              role: string;
              created_at: string;
              last_login: string;
            };
          };
        };
      };
    };
  };
}

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    const token = await getCurrentUserToken();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
};

const client = createClient<paths>({ baseUrl });
client.use(authMiddleware);

export default client;

// Convenience function to test auth with /api/v1/me endpoint
export const getCurrentUser = async () => {
  const { data, error } = await client.GET('/api/v1/me');
  if (error) {
    throw error;
  }
  return data;
};
