import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  retries: 1,
  fullyParallel: true,
  reporter: [["list"], ["json", { outputFile: "smoke-results.json" }]],
  use: {
    baseURL: process.env.SMOKE_BACKEND_URL || "http://localhost:8000",
    extraHTTPHeaders: {
      Accept: "application/json",
    },
  },
  projects: [
    {
      name: "smoke",
      testMatch: /.*\.spec\.ts/,
    },
  ],
});
