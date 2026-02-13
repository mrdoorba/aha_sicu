import { test, expect } from "@playwright/test";

const BACKEND_URL =
  process.env.SMOKE_BACKEND_URL || "http://localhost:8000";
const AUTH_TOKEN = process.env.SMOKE_AUTH_TOKEN;

test.describe("GCS Signed URL (AC5)", { tag: "@smoke" }, () => {
  // Also tested in auth-enforcement.spec.ts (AC2) — duplicated here for AC5 completeness
  test("POST /api/v1/upload/signed-url without auth returns 401 or 403", async ({
    request,
  }) => {
    const response = await request.post(
      `${BACKEND_URL}/api/v1/upload/signed-url`,
      {
        data: {
          filename: "smoke-test.csv",
          content_type: "text/csv",
          file_type: "cpc_ad_report",
          brand_id: 1,
        },
      }
    );

    expect([401, 403]).toContain(response.status());
  });

  test.describe("Authenticated", () => {
    test.skip(!AUTH_TOKEN, "Skipped: SMOKE_AUTH_TOKEN not set");

    test("POST /api/v1/upload/signed-url returns upload_url, upload_id, expires_at", async ({
      request,
    }) => {
      const response = await request.post(
        `${BACKEND_URL}/api/v1/upload/signed-url`,
        {
          headers: { Authorization: `Bearer ${AUTH_TOKEN}` },
          data: {
            filename: "smoke-test.csv",
            content_type: "text/csv",
            file_type: "cpc_ad_report",
            brand_id: 1,
          },
        }
      );

      expect(response.status()).toBe(200);

      const body = await response.json();
      expect(body).toHaveProperty("upload_url");
      expect(body).toHaveProperty("upload_id");
      expect(body).toHaveProperty("expires_at");
    });

    test("upload_url points to storage.googleapis.com", async ({ request }) => {
      const response = await request.post(
        `${BACKEND_URL}/api/v1/upload/signed-url`,
        {
          headers: { Authorization: `Bearer ${AUTH_TOKEN}` },
          data: {
            filename: "smoke-test.csv",
            content_type: "text/csv",
            file_type: "cpc_ad_report",
            brand_id: 1,
          },
        }
      );

      expect(response.status()).toBe(200);

      const body = await response.json();
      expect(body.upload_url).toContain("storage.googleapis.com");
    });
  });
});
