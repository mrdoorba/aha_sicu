import { test, expect } from "@playwright/test";

const BACKEND_URL =
  process.env.SMOKE_BACKEND_URL || "http://localhost:8000";

test.describe("Auth Enforcement (AC2)", { tag: "@smoke" }, () => {
  test("GET /api/v1/brands without auth returns 401 or 403", async ({
    request,
  }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/brands`);
    expect([401, 403]).toContain(response.status());
  });

  test("GET /api/v1/evaluations without auth returns 401 or 403", async ({
    request,
  }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/evaluations`);
    expect([401, 403]).toContain(response.status());
  });

  test("POST /api/v1/sync without auth returns 401 or 403", async ({
    request,
  }) => {
    const response = await request.post(`${BACKEND_URL}/api/v1/sync`);
    expect([401, 403]).toContain(response.status());
  });

  test("POST /api/v1/upload/signed-url without auth returns 401 or 403", async ({
    request,
  }) => {
    const response = await request.post(
      `${BACKEND_URL}/api/v1/upload/signed-url`
    );
    expect([401, 403]).toContain(response.status());
  });
});
