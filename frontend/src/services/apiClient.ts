import createClient, { type Middleware } from 'openapi-fetch';
import type { AuthService } from './authService';
import { firebaseAuthService } from './firebaseAuthService';
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
              language: string;
              created_at: string;
              last_login: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/me/language': {
    patch: {
      requestBody: {
        content: {
          'application/json': {
            language: 'id' | 'en' | 'th';
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              id: string;
              email: string;
              role: string;
              language: string;
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
              upload: {
                id: number;
                brand_id: number;
                file_type: string;
                filename: string;
                file_size: number;
                row_count: number;
                uploaded_at: string;
              };
              auto_calculated: Array<{
                calculator_type: string;
                status: string;
                result?: Record<string, unknown>;
                reason?: string;
              }>;
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
  '/api/v1/upload/brands/{brand_id}/download/{file_type}': {
    get: {
      parameters: {
        path: {
          brand_id: number;
          file_type: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              download_url: string;
              filename: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/grouped': {
    get: {
      parameters: {
        query?: {
          page?: number;
          limit?: number;
          search?: string;
          date_from?: string;
          date_to?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              items: Array<{
                brand_id: number;
                brand_name: string;
                evaluation_count: number;
                top_score: number;
                top_verdict: string;
                latest_date: string;
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
  '/api/v1/evaluations/grouped/{brand_id}': {
    get: {
      parameters: {
        path: {
          brand_id: number;
        };
        query?: {
          limit?: number;
          date_from?: string;
          date_to?: string;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              items: Array<{
                id: number;
                final_score: number;
                verdict: string;
                template: string;
                evaluator_email: string;
                created_at: string;
              }>;
              total: number;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/{evaluation_id}': {
    get: {
      parameters: {
        path: {
          evaluation_id: number;
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              id: number;
              brand_id: number;
              brand_name: string;
              final_score: number;
              verdict: string;
              template: string;
              score_breakdown: Array<Record<string, unknown>>;
              calculator_results: Record<string, unknown>;
              manual_inputs: Record<string, unknown>;
              email_output: string | null;
              evaluator_email: string;
              created_at: string;
              rule_version: number;
              period: string;
              brand_raw_data: {
                email: string | null;
                pic_name: string | null;
                store_link: string | null;
                kategori: string | null;
              };
            };
          };
        };
      };
    };
    delete: {
      parameters: {
        path: {
          evaluation_id: number;
        };
      };
      responses: {
        204: {
          content: never;
        };
      };
    };
  };
  '/api/v1/evaluations': {
    get: {
      parameters: {
        query?: {
          page?: number;
          limit?: number;
          sort_by?: 'created_at' | 'final_score';
          sort_order?: 'asc' | 'desc';
          search?: string;
          date_from?: string;
          date_to?: string;

        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              items: Array<{
                id: number;
                brand_name: string;
                final_score: number;
                verdict: string;
                template: string;
                evaluator_email: string;
                created_at: string;
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
  '/api/v1/evaluations/brands/{brand_id}/calculators/results': {
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
              results: Array<{
                calculator_type: string;
                output_text: string;
                details: Record<string, unknown>;
                calculated_at: string;
              }>;
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
  '/api/v1/evaluations/brands/{brand_id}/calculators/run-all': {
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
              results: Array<{
                calculator_type: string;
                status: string;
                result?: Record<string, unknown>;
                reason?: string;
              }>;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/brands/{brand_id}/score': {
    post: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      requestBody: {
        content: {
          'application/json': {
            template: 'fashion' | 'non_fashion';
            verdict: string;
            store_name: string;
            period: string;
            brand_name: string;
            email?: string | null;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              total_score: number;
              category_scores: Array<{
                category: string;
                score: number;
                max_score: number;
                rows: Array<{
                  row: number;
                  metric: string;
                  value: unknown;
                  benchmark: string;
                  verdict: string;
                  message: string;
                  score: number;
                }>;
                available: boolean;
              }>;
              verdict: string;
              conclusion: string;
              conclusion_i18n?: Array<{
                key: string;
                vars: Record<string, string>;
              }>;
              marketing_estimation: string;
              marketing_percentage: string;
              marketing_budget: string;
              marketing_budget_i18n?: {
                key: string;
                vars: Record<string, string>;
              };
              closing_message: string;
              closing_message_i18n?: {
                key: string;
                vars: Record<string, string>;
              };
              email_subject: string;
              email_body: string;
              template: string;
              rule_version: number;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/brands/{brand_id}/save': {
    post: {
      parameters: {
        path: {
          brand_id: number;
        };
      };
      requestBody: {
        content: {
          'application/json': {
            template: 'fashion' | 'non_fashion';
            final_score: number;
            verdict: string;
            score_breakdown: Array<Record<string, unknown>>;
            calculator_results: Record<string, unknown>;
            manual_inputs: Record<string, unknown>;
            rule_version?: number;
            email_output?: string | null;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              id: number;
              brand_id: number;
              final_score: number;
              verdict: string;
              template: string;
              created_at: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/rules': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': Array<{
              id: number;
              template: string;
              rules: Record<string, unknown>;
              version: number;
              updated_by: number | null;
              updated_at: string;
            }>;
          };
        };
      };
    };
  };
  '/api/v1/rules/{template}': {
    put: {
      parameters: {
        path: {
          template: 'fashion' | 'non_fashion' | 'default';
        };
      };
      requestBody: {
        content: {
          'application/json': {
            rules: Record<string, unknown>;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              id: number;
              template: string;
              rules: Record<string, unknown>;
              version: number;
              updated_by: number | null;
              updated_at: string;
            };
          };
        };
      };
    };
  };
  '/api/v1/evaluations/brands/{brand_id}/calculators/status': {
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
              calculators: Record<string, {
                status: string;
                has_result: boolean;
                required_files: string[];
                required_manual: string[];
                available_files: string[];
                missing_files: string[];
                missing_manual: string[];
                calculated_at: string | null;
              }>;
            };
          };
        };
      };
    };
  };
  '/api/v1/accounts': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': Array<{
              id: number;
              email: string;
              role: string;
              created_at: string;
              last_login: string | null;
            }>;
          };
        };
      };
    };
    post: {
      requestBody: {
        content: {
          'application/json': {
            email: string;
            password: string;
            role: 'member' | 'leader' | 'admin';
          };
        };
      };
      responses: {
        201: {
          content: {
            'application/json': {
              id: number;
              email: string;
              role: string;
              created_at: string;
              last_login: string | null;
            };
          };
        };
      };
    };
  };
  '/api/v1/accounts/{user_id}/role': {
    patch: {
      parameters: {
        path: {
          user_id: number;
        };
      };
      requestBody: {
        content: {
          'application/json': {
            role: 'member' | 'leader' | 'admin';
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              id: number;
              email: string;
              role: string;
              created_at: string;
              last_login: string | null;
            };
          };
        };
      };
    };
  };
  '/api/v1/accounts/{user_id}/reset-password': {
    post: {
      parameters: {
        path: {
          user_id: number;
        };
      };
      requestBody: {
        content: {
          'application/json': {
            password: string;
          };
        };
      };
      responses: {
        204: {
          content: never;
        };
      };
    };
  };
  '/api/v1/accounts/{user_id}': {
    delete: {
      parameters: {
        path: {
          user_id: number;
        };
      };
      responses: {
        204: {
          content: never;
        };
      };
    };
  };
  '/api/v1/config/features': {
    get: {
      responses: {
        200: {
          content: {
            'application/json': {
              email_enabled: boolean;
            };
          };
        };
      };
    };
  };
  '/api/v1/email/send': {
    post: {
      requestBody: {
        content: {
          'application/json': {
            evaluation_id: number;
            recipients: string[];
            chart_image: string;
            subject?: string | null;
            cc?: string[];
            bcc?: string[];
            note?: string | null;
          };
        };
      };
      responses: {
        200: {
          content: {
            'application/json': {
              success: boolean;
              message_id: string;
              recipients: string[];
            };
          };
        };
      };
    };
  };
}

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
    if (response.status === 500) {
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

export const updateLanguage = async (language: 'id' | 'en' | 'th') => {
  const { data, error } = await client.PATCH('/api/v1/me/language', {
    body: { language },
  });
  if (error) {
    throw error;
  }
  return data;
};
