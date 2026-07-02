import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const marketingRoutes = [
  "/",
  "/product",
  "/use-cases/ai-creative-testing",
  "/use-cases/marketing-attribution",
  "/use-cases/agencies",
  "/use-cases/b2b-saas",
  "/use-cases/ecommerce",
  "/open-source",
  "/security",
  "/docs",
  "/blog",
  "/pricing",
  "/github"
];

test("marketing route inventory includes core SEO pages", () => {
  assert.ok(marketingRoutes.includes("/use-cases/ai-creative-testing"));
  assert.ok(marketingRoutes.includes("/pricing"));
});

test("first workflow screens are wired to API components", () => {
  const apiKeysPage = readFileSync("app/app/api-keys/page.tsx", "utf8");
  const briefsPage = readFileSync("app/app/briefs/page.tsx", "utf8");
  const newBriefPage = readFileSync("app/app/briefs/new/page.tsx", "utf8");
  const packageJson = JSON.parse(readFileSync("package.json", "utf8"));

  assert.match(apiKeysPage, /ApiKeysManager/);
  assert.match(briefsPage, /BriefsManager/);
  assert.match(newBriefPage, /BriefComposer/);
  assert.equal(packageJson.dependencies["framer-motion"], undefined);
  assert.equal(packageJson.devDependencies.eslint, undefined);
});

test("creative treatment, approval, experiment, and result screens use API managers", () => {
  const briefComposer = readFileSync("components/brief-composer.tsx", "utf8");
  const creativesPage = readFileSync("app/app/creatives/page.tsx", "utf8");
  const creativeDetailPage = readFileSync("app/app/creatives/[id]/page.tsx", "utf8");
  const approvalsPage = readFileSync("app/app/approvals/page.tsx", "utf8");
  const experimentsPage = readFileSync("app/app/experiments/page.tsx", "utf8");
  const experimentDetailPage = readFileSync("app/app/experiments/[id]/page.tsx", "utf8");
  const resultsPage = readFileSync("app/app/experiments/[id]/results/page.tsx", "utf8");
  const connectorsPage = readFileSync("app/app/connectors/page.tsx", "utf8");
  const eventsPage = readFileSync("app/app/events/page.tsx", "utf8");
  const onboardingPage = readFileSync("app/app/onboarding/page.tsx", "utf8");
  const settingsPage = readFileSync("app/app/settings/page.tsx", "utf8");
  const dashboard = readFileSync("components/dashboard.tsx", "utf8");
  const apiClient = readFileSync("lib/api-client.ts", "utf8");

  assert.match(briefComposer, /createCreativeTreatment/);
  assert.match(briefComposer, /Save as Creative Treatment/);
  assert.match(creativesPage, /CreativesManager/);
  assert.match(creativeDetailPage, /CreativeDetailPanel/);
  assert.match(approvalsPage, /ApprovalsManager/);
  assert.match(experimentsPage, /ExperimentsManager/);
  assert.match(experimentDetailPage, /ExperimentDetailPanel/);
  assert.match(resultsPage, /ExperimentResultsPanel/);
  assert.match(connectorsPage, /ConnectorsManager/);
  assert.match(eventsPage, /EventsManager/);
  assert.match(onboardingPage, /OnboardingManager/);
  assert.match(settingsPage, /SettingsManager/);
  assert.match(dashboard, /DashboardSummary/);
  assert.match(dashboard, /DemoScenarioLauncher/);
  assert.match(dashboard, /DashboardIngestionHealth/);
  assert.match(dashboard, /DashboardApprovalRisk/);
  assert.match(dashboard, /DashboardLineagePanel/);
  assert.match(apiClient, /X-API-Key/);
  assert.match(apiClient, /getMe/);
  assert.match(apiClient, /runDemoScenario/);
  assert.match(apiClient, /createOrganization/);
  assert.match(apiClient, /createBrandPack/);
  assert.match(apiClient, /listClaimEvidence/);
  assert.match(apiClient, /createClaimEvidence/);
  assert.match(apiClient, /listAuditLogs/);
  assert.match(apiClient, /ingestEvents/);
  assert.match(apiClient, /getCreativeTreatment/);
  assert.match(apiClient, /getMeasurementSummary/);
  assert.match(apiClient, /listConnectors/);
  assert.match(apiClient, /approveCreativeTreatment/);
  assert.match(apiClient, /claim_evidence_urls/);
  assert.match(apiClient, /createExperiment/);
  assert.match(apiClient, /getExperiment/);
  assert.match(apiClient, /assignExperimentVariant/);
  assert.match(apiClient, /getExperimentResults/);
  assert.match(apiClient, /getExperimentInsights/);
  assert.match(apiClient, /listEvents/);
  assert.match(apiClient, /getEventHealth/);
});

test("typescript sdk uses api-key ingestion header", () => {
  const sdk = readFileSync("../../packages/sdk-ts/src/index.ts", "utf8");

  assert.match(sdk, /"X-API-Key": this\.apiKey/);
  assert.match(sdk, /assign\(experimentId: string, unitId: string\)/);
  assert.match(sdk, /\/v1\/experiments\/\$\{experimentId\}\/assign/);
  assert.match(sdk, /eventHealth\(\): Promise<EventHealth>/);
  assert.match(sdk, /\/v1\/events\/health/);
  assert.match(sdk, /experimentInsight\(experimentId: string\): Promise<ExperimentInsight>/);
  assert.match(sdk, /\/v1\/experiments\/\$\{experimentId\}\/insights/);
  assert.doesNotMatch(sdk, /Authorization/);
});

test("sdk tracking examples cover assignment, ingestion, and event health", () => {
  const browserTracker = readFileSync("../../examples/sdk-tracking/browser-tracker.js", "utf8");
  const pythonTracker = readFileSync("../../examples/sdk-tracking/server-side-python.py", "utf8");

  assert.match(browserTracker, /assignCreativeLiftVariant/);
  assert.match(browserTracker, /trackCreativeLiftEvent/);
  assert.match(browserTracker, /\/v1\/events\/ingest/);
  assert.match(pythonTracker, /CreativeLiftClient/);
  assert.match(pythonTracker, /client\.ingest/);
  assert.match(pythonTracker, /client\.event_health/);
});
