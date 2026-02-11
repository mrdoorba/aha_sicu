import createClient, { type Middleware } from 'openapi-fetch';
import { getCurrentUserToken } from '../firebase/auth';
import { API_BASE_URL } from '../config';

const baseUrl = API_BASE_URL;

// Define paths type (can be replaced with generated OpenAPI types).
// Keep response shapes in sync with hook types in useBrands.ts and useSync.ts.
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
  // SSE endpoint — consumed via native EventSource in useSSE.ts, not openapi-fetch
  '/api/v1/events': {
    get: {
      parameters: {
        query: {
          token: string;
        };
      };
      responses: {
        200: {
          content: {
            'text/event-stream': unknown;
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
  '/api/v1/brands/{brand_id}': {
    get: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              id: number;
              brand_name: string;
              raw_data: Record<string, unknown>;
              updated_at: string;
              meeting_raw_data: Record<string, unknown> | null;
            };
          };
        };
      };
    };
  };
  '/api/v1/upload/signed-url': {
    post: {
      requestBody: {
        content: {
          'application/json': {
            filename: string;
            content_type: string;
            file_type: string;
            brand_id: number;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              upload_url: string;
              upload_id: string;
              expires_at: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/upload/process': {
    post: {
      requestBody: {
        content: {
          'application/json': {
            upload_id: string;
            brand_id: number;
            file_type: string;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              id: number;
              brand_id: number;
              file_type: string;
              filename: string;
              file_size: number;
              row_count: number;
              uploaded_at: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/upload/brands/{brand_id}': {
    get: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              brand_id: number;
              uploads: Array<{
                id: number;
                file_type: string;
                filename: string;
                file_size: number;
                row_count: number;
                uploaded_at: string;
              }>;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/brands/{brand_id}': {
    get: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              brand_id: number;
              category_type: string | null;
              manual_data: Record<string, unknown> | null;
              updated_at: string | null;
            };
          };
        };
      };
    };
    put: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      requestBody: {
        content: {
          'application/json': {
            category_type?: string | null;
            manual_data?: Record<string, unknown> | null;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              brand_id: number;
              category_type: string | null;
              manual_data: Record<string, unknown> | null;
              updated_at: string | null;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/brands/{brand_id}/calculators/ads_keyword': {
    post: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              calculator_type: string;
              output_text: string;
              details: Record<string, unknown>;
              calculated_at: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/brands/{brand_id}/calculators/discount': {
    post: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              calculator_type: string;
              output_text: string;
              details: Record<string, unknown>;
              calculated_at: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/brands/{brand_id}/calculators/top_sku': {
    post: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              calculator_type: string;
              output_text: string;
              details: Record<string, unknown>;
              calculated_at: string;
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
