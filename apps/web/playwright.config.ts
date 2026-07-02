import { defineConfig, devices } from "@playwright/test";

// E2E runs against a live stack: API (RESOURCE_REPOSITORY_BACKEND=sqlalchemy)
// plus the production web build. See docs/self-hosting.md and `make e2e`.
export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    viewport: { width: 1440, height: 900 },
    colorScheme: "dark",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
