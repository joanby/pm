import { defineConfig, devices } from "@playwright/test";

process.env.PM_E2E_DOCKER ??= "1";

export default defineConfig({
  testDir: "./tests",
  globalSetup: "./tests/docker-global-setup.ts",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: "http://127.0.0.1:8000",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
