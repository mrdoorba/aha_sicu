import { test, expect } from "@playwright/test";

const FRONTEND_URL =
  process.env.SMOKE_FRONTEND_URL || "http://localhost:5173";

test.describe("Frontend SPA (AC3)", { tag: "@smoke" }, () => {
  test("Root URL returns 200 with text/html", async ({ request }) => {
    const response = await request.get(`${FRONTEND_URL}/`);

    expect(response.status()).toBe(200);

    const contentType = response.headers()["content-type"];
    expect(contentType).toContain("text/html");
  });

  test("HTML body contains script tags and root div", async ({ request }) => {
    const response = await request.get(`${FRONTEND_URL}/`);
    const body = await response.text();

    expect(body).toContain("<script");
    expect(body).toContain('<div id="root"');
  });

  test("Deep link /brands returns 200 (SPA rewrite)", async ({ request }) => {
    const response = await request.get(`${FRONTEND_URL}/brands`);
    expect(response.status()).toBe(200);
  });

  test("Deep link /history returns 200 (SPA rewrite)", async ({ request }) => {
    const response = await request.get(`${FRONTEND_URL}/history`);
    expect(response.status()).toBe(200);
  });
});
