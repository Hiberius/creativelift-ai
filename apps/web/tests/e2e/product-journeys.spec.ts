import { expect, test } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const apiBaseUrl = process.env.E2E_API_BASE_URL ?? "http://localhost:8000";
const screenshotDir = process.env.E2E_SCREENSHOT_DIR;

if (screenshotDir) {
  mkdirSync(screenshotDir, { recursive: true });
}

async function capture(page: import("@playwright/test").Page, name: string) {
  if (!screenshotDir) return;
  await page.screenshot({ path: join(screenshotDir, `${name}.png`), fullPage: false });
}

test.beforeAll(async ({ request }) => {
  const ready = await request.get(`${apiBaseUrl}/readyz`);
  expect(ready.ok(), "API must be up before running E2E").toBeTruthy();
  // Seed a fully measured demo scenario so every screen has real data.
  const scenario = await request.post(`${apiBaseUrl}/v1/demo/scenario`);
  expect(scenario.ok()).toBeTruthy();
  // Seed one treatment awaiting review so the approvals queue is populated.
  const pending = await request.post(`${apiBaseUrl}/v1/creative-treatments`, {
    data: {
      name: "Pending review: contrarian ROAS hook",
      objective: "Increase demo requests",
      target_audience: "B2B growth teams",
      channel: "paid_social",
      hook: "Your ROAS is lying to you.",
      cta: "Run a lift test",
    },
  });
  expect(pending.ok()).toBeTruthy();
});

test("landing page renders the product story", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("h1").first()).toBeVisible();
  await capture(page, "01-landing");
});

test("dashboard renders hero metrics and API-fed panels", async ({ page }) => {
  await page.goto("/app/dashboard");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText(/Prompt-to-profit lift/i).first()).toBeVisible({ timeout: 15_000 });
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);
  await capture(page, "02-dashboard");
});

test("approvals queue lists creative treatments loaded from the API", async ({ page }) => {
  await page.goto("/app/approvals");
  await expect(page.getByRole("heading", { name: /creative review queue/i })).toBeVisible();
  // The seeded scenario persists real treatments; the page must not show the fetch-failure fallback.
  await page.waitForLoadState("networkidle");
  await expect(page.getByText(/Failed to fetch/i)).toHaveCount(0);
  await expect(page.getByText("Pending review: contrarian ROAS hook").first()).toBeVisible({
    timeout: 15_000,
  });
  await capture(page, "03-approvals");
});

test("experiments list shows the measured demo experiment", async ({ page }) => {
  await page.goto("/app/experiments");
  await expect(page.getByText(/Proof-led creative vs control/i).first()).toBeVisible({
    timeout: 15_000,
  });
  await capture(page, "04-experiments");
});

test("experiment results page reports lift and a recommendation", async ({ page, request }) => {
  const experiments = await request.get(`${apiBaseUrl}/v1/experiments`);
  expect(experiments.ok()).toBeTruthy();
  const list = await experiments.json();
  expect(list.length).toBeGreaterThan(0);
  const experimentId = list[0].id;

  await page.goto(`/app/experiments/${experimentId}/results`);
  await expect(page.getByText(/lift|recommendation/i).first()).toBeVisible({ timeout: 15_000 });
  await page.waitForTimeout(1500);
  await capture(page, "05-experiment-results");
});

test("events page reports ingestion health from the API", async ({ page }) => {
  await page.goto("/app/events");
  await expect(page.getByText(/quality|events/i).first()).toBeVisible({ timeout: 15_000 });
  await page.waitForTimeout(1500);
  await capture(page, "06-events-health");
});

test("api ingestion, health history, and measurement summary respond end to end", async ({
  request,
}) => {
  const history = await request.get(`${apiBaseUrl}/v1/events/health/history`);
  expect(history.ok()).toBeTruthy();
  const snapshots = await history.json();
  expect(snapshots.length).toBeGreaterThan(0);
  expect(snapshots[0].total_events).toBeGreaterThan(0);

  const summary = await request.get(`${apiBaseUrl}/v1/measurement/summary`, {
    headers: { "X-API-Key": "dev-api-key" },
  });
  expect(summary.ok()).toBeTruthy();
  const cards = (await summary.json()).data.cards;
  const impressions = cards.find((card: { metric: string }) => card.metric === "impressions");
  expect(impressions.value).toBeGreaterThan(0);
  expect(impressions.value).not.toBe(128_420);
});
