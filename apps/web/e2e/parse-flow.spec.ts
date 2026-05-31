import { test, expect } from "@playwright/test";
import path from "path";

test.describe("Parse flow", () => {
  test("parse sample PDF end-to-end", async ({ page, request }) => {
    const health = await request.get("http://127.0.0.1:8080/health");
    test.skip(!health.ok(), "Worker not running");

    await page.goto("/");
    const samplePath = path.join(__dirname, "../../../samples/minimal.pdf");
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(samplePath);
    await page.getByRole("button", { name: /Parse PDF/i }).click();
    await expect(page.getByText("Pages").first()).toBeVisible({ timeout: 90000 });
    await expect(page.getByRole("button", { name: /chunks\.jsonl/i })).toBeVisible();
  });
});
