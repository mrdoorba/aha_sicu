import { test, expect } from "@playwright/test";

const BACKEND_URL =
  process.env.SMOKE_BACKEND_URL || "http://localhost:8000";
const AUTH_TOKEN = process.env.SMOKE_AUTH_TOKEN;

test.describe("Database Connectivity (AC4)", { tag: "@smoke" }, () => {
  // Authenticated tests — skip when no token is available
  test.skip(!AUTH_TOKEN, "Skipped: SMOKE_AUTH_TOKEN not set");

  test("GET /api/v1/brands?page=1&limit=1 returns 200 with items array", async ({
    request,
  }) => {
    const response = await request.get(
      `${BACKEND_URL}/api/v1/brands?page=1&limit=1`,
      {
        headers: { Authorization: `Bearer ${AUTH_TOKEN}` },
      }
    );

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty("items");
    expect(Array.isArray(body.items)).toBe(true);
  });

  test("GET /api/v1/sync/status returns 200 with sync status", async ({
    request,
  }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/sync/status`, {
      headers: { Authorization: `Bearer ${AUTH_TOKEN}` },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty("status");
    expect(body).toHaveProperty("last_sync");
  });
});
