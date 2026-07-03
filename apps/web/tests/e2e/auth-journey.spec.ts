import { expect, test } from "@playwright/test";

const apiBaseUrl = process.env.E2E_API_BASE_URL ?? "http://localhost:8000";

test.beforeAll(async ({ request }) => {
  const ready = await request.get(`${apiBaseUrl}/readyz`);
  expect(ready.ok(), "API must be up before running E2E").toBeTruthy();
});

test("a new user can register, land on the dashboard, and log out", async ({ page }) => {
  const stamp = Date.now();
  const email = `e2e-user-${stamp}@creativelift.test`;
  const password = "correct-horse-battery-staple";
  const name = "E2E Test User";
  const organizationName = `E2E Org ${stamp}`;

  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();

  // Toggle to registration mode.
  await page.getByRole("button", { name: /new here\? create account/i }).click();
  await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();

  await page.getByLabel("Your name").fill(name);
  await page.getByLabel("Organization name").fill(organizationName);
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);

  await page.getByRole("button", { name: "Create account" }).click();

  // Successful registration lands on the dashboard.
  await expect(page).toHaveURL(/\/app\/dashboard$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

  // The header now shows the registered organization instead of the demo chip.
  await expect(page.getByText(organizationName)).toBeVisible({ timeout: 15_000 });

  // Logging out clears the session and returns to /login.
  await page.getByRole("button", { name: "Logout" }).click();
  await expect(page).toHaveURL(/\/login$/, { timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
});
