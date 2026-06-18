import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 120_000,
  workers: 1,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: "http://localhost:8000",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run dev -- --hostname 127.0.0.1 --port 3000",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: true,
    timeout: 120_000,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
