import createClient, { type Middleware } from 'openapi-fetch';
import { getCurrentUserToken } from '../firebase/auth';

const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Define paths type (can be replaced with generated OpenAPI types)
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
  '/api/v1/brands': {
    get: {
      parameters: {
        query?: {
          page?: number;
          limit?: number;
          search?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              items: Array<{
                id: number;
                brand_name: string;
                raw_data: Record<string, unknown>;
                updated_at: string;
                meeting_raw_data: Record<string, unknown> | null;
              }>;
              total: number;
              page: number;
              limit: number;
              pages: number;
            };
          };
        };
      };
    };
  };
  '/api/v1/sync/status': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              id: number;
              last_sync: string;
              status: 'success' | 'failed' | 'in_progress';
              started_at: string;
              completed_at: string | null;
              brands_synced: number;
              error_message: string | null;
              sync_details: Record<string, {
                rows_synced: number;
                rows_skipped: number;
                status: string;
              }> | null;
            };
          };
        };
      };
    };
  };
  '/api/v1/sync': {
    post: {
      responses: {
        202: {
          content: {
            'application/json': {
              status: string;
              sync_id: number;
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
