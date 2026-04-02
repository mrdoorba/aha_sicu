import { test, expect } from "@playwright/test";

const BACKEND_URL =
  process.env.SMOKE_BACKEND_URL || "http://localhost:8000";

test.describe("Backend Health (AC1)", { tag: "@smoke" }, () => {
  test("GET /health returns 200 with healthy status", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/health`);

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toMatchObject({
      status: "healthy",
      checks: {
        database: "ok",
      },
    });
  });

  test("GET /docs returns 200 (FastAPI Swagger UI)", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/docs`);

    expect(response.status()).toBe(200);
  });
});
