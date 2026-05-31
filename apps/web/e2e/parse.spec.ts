import { test, expect } from "@playwright/test";

test.describe("DoclingRAG playground", () => {
  test("homepage loads with parser UI", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: /DoclingRAG/i }).first()).toBeVisible();
    await expect(page.getByRole("button", { name: /Parse PDF/i })).toBeVisible();
    await expect(page.getByText(/Drag and drop a PDF/i)).toBeVisible();
  });

  test("privacy and terms links work", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: /Privacy Policy/i }).click();
    await expect(page.getByRole("heading", { name: /Privacy Policy/i })).toBeVisible();
    await page.goto("/terms");
    await expect(page.getByRole("heading", { name: /Terms/i })).toBeVisible();
  });

  test("SEO sub-route returns 200", async ({ page }) => {
    const res = await page.goto("/pdf-to-markdown");
    expect(res?.status()).toBe(200);
    await expect(page.getByRole("heading", { name: /PDF to Markdown/i, level: 1 })).toHaveCount(1);
    await expect(page.getByRole("button", { name: /Parse PDF/i })).toBeVisible();
  });
});
