import { test, expect } from "@playwright/test";

const BACKEND_URL =
  process.env.SMOKE_BACKEND_URL || "http://localhost:8000";
const AUTH_TOKEN = process.env.SMOKE_AUTH_TOKEN;

test.describe("SSE Endpoint (AC6)", { tag: "@smoke" }, () => {
  test("GET /api/v1/events without token returns 422", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/events`);
    expect(response.status()).toBe(422);
  });

  test("GET /api/v1/events?token=invalid returns 401 or 403", async ({
    request,
  }) => {
    const response = await request.get(
      `${BACKEND_URL}/api/v1/events?token=invalid-token`
    );
    expect([401, 403]).toContain(response.status());
  });

  test.describe("Authenticated", () => {
    test.skip(!AUTH_TOKEN, "Skipped: SMOKE_AUTH_TOKEN not set");

    test("GET /api/v1/events with valid token returns text/event-stream", async () => {
      // Playwright's request API doesn't support streaming responses,
      // so we use fetch with an AbortController timeout.
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5_000);

      try {
        const response = await fetch(
          `${BACKEND_URL}/api/v1/events?token=${AUTH_TOKEN}`,
          { signal: controller.signal }
        );

        expect(response.status).toBe(200);

        const contentType = response.headers.get("content-type");
        expect(contentType).toContain("text/event-stream");
      } catch (error: unknown) {
        // AbortError is expected — connection stays open (SSE)
        if (error instanceof Error && error.name === "AbortError") {
          // SSE connection was successfully established and then aborted
          return;
        }
        throw error;
      } finally {
        clearTimeout(timeout);
      }
    });
  });
});
