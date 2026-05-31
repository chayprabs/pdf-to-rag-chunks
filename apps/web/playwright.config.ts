import { defineConfig, devices } from "@playwright/test";
import path from "path";

const webDir = path.dirname(new URL(import.meta.url).pathname);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  timeout: 120_000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: process.env.CI
    ? {
        command: "bash ../../scripts/start-web-production.sh",
        cwd: webDir,
        url: "http://127.0.0.1:3000",
        reuseExistingServer: false,
        timeout: 120_000,
        env: {
          PORT: "3000",
          HOSTNAME: "127.0.0.1",
        },
      }
    : undefined,
});
