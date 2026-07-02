from __future__ import annotations

from fastapi.responses import HTMLResponse


DEMO_CONSOLE_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CreativeLift AI Measurement Lab</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #07090c;
      --panel: #11161c;
      --panel-2: #151c23;
      --line: #28323d;
      --text: #f4f7fb;
      --muted: #9aa8b7;
      --soft: #c7d2df;
      --cyan: #1fd4e6;
      --mint: #55d987;
      --amber: #f2b84b;
      --red: #ff6678;
      --ink: #061014;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    main {
      width: min(1280px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 11px;
      min-width: 0;
    }
    .mark {
      display: grid;
      place-items: center;
      width: 34px;
      height: 34px;
      border: 1px solid #315966;
      border-radius: 8px;
      color: var(--cyan);
      font-size: 13px;
      font-weight: 800;
      flex: 0 0 auto;
    }
    h1 {
      margin: 0;
      font-size: 22px;
      line-height: 1.15;
    }
    .subhead {
      margin: 3px 0 0;
      color: var(--muted);
      font-size: 13px;
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: flex-end;
    }
    button, a.button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      border: 1px solid transparent;
      border-radius: 8px;
      padding: 9px 13px;
      background: var(--cyan);
      color: var(--ink);
      font: inherit;
      font-size: 13px;
      font-weight: 750;
      cursor: pointer;
      text-decoration: none;
      white-space: nowrap;
    }
    button.secondary, a.button.secondary {
      border-color: var(--line);
      background: transparent;
      color: var(--text);
    }
    button.ghost {
      border-color: transparent;
      background: transparent;
      color: var(--soft);
    }
    button[disabled] { cursor: wait; opacity: 0.65; }
    .shell {
      display: grid;
      grid-template-columns: minmax(360px, 0.86fr) minmax(520px, 1.14fr);
      gap: 14px;
      margin-top: 18px;
      align-items: start;
    }
    .left-stack {
      display: grid;
      gap: 14px;
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 56px;
      padding: 16px;
      border-bottom: 1px solid var(--line);
    }
    h2 {
      margin: 0;
      font-size: 16px;
      line-height: 1.2;
    }
    .panel-body { padding: 16px; }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .full { grid-column: 1 / -1; }
    label {
      display: grid;
      gap: 6px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }
    input, textarea {
      width: 100%;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #090d12;
      color: var(--text);
      padding: 9px 10px;
      font: inherit;
      font-size: 14px;
      outline: none;
    }
    textarea {
      min-height: 150px;
      resize: vertical;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      line-height: 1.5;
    }
    input:focus, textarea:focus { border-color: var(--cyan); }
    fieldset {
      display: grid;
      gap: 12px;
      margin: 14px 0 0;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0c1117;
    }
    legend {
      padding: 0 7px;
      color: var(--soft);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .status {
      min-height: 22px;
      margin: 12px 0 0;
      color: var(--muted);
      font-size: 13px;
    }
    .status.error { color: var(--red); }
    .scoreboard {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
    }
    .metric {
      min-height: 96px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
    }
    .metric-label {
      margin: 0;
      color: var(--muted);
      font-size: 11px;
      font-weight: 750;
      text-transform: uppercase;
    }
    .metric-value {
      margin: 10px 0 0;
      font-size: 27px;
      font-weight: 800;
      line-height: 1.05;
    }
    .metric-value.good { color: var(--mint); }
    .metric-value.warn { color: var(--amber); }
    .metric-value.bad { color: var(--red); }
    .decision {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 14px;
    }
    .block {
      min-height: 150px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0c1117;
    }
    .block p {
      margin: 10px 0 0;
      color: var(--soft);
      font-size: 14px;
      line-height: 1.55;
    }
    .rows {
      display: grid;
      gap: 0;
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    .row {
      display: grid;
      grid-template-columns: minmax(160px, 1fr) minmax(110px, 0.7fr) minmax(110px, 0.7fr);
      gap: 12px;
      align-items: center;
      padding: 11px 13px;
      background: #0c1117;
      border-top: 1px solid var(--line);
      font-size: 13px;
    }
    .row:first-child {
      border-top: 0;
      background: #121922;
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .list {
      display: grid;
      gap: 9px;
      margin: 12px 0 0;
      padding: 0;
      list-style: none;
    }
    .list li {
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--soft);
      font-size: 13px;
      line-height: 1.45;
    }
    .history {
      display: grid;
      gap: 9px;
      margin-top: 12px;
    }
    .report-item {
      display: grid;
      gap: 6px;
      width: 100%;
      min-height: 0;
      padding: 11px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0c1117;
      color: var(--text);
      font: inherit;
      font-size: 13px;
      font-weight: 500;
      text-align: left;
      white-space: normal;
    }
    .report-item:hover { border-color: #3b5361; }
    .report-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .report-title {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 750;
    }
    .report-tag {
      color: var(--mint);
      font-size: 12px;
      font-weight: 800;
      flex: 0 0 auto;
    }
    .report-meta {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }
    .import-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
      gap: 9px;
      margin-top: 12px;
    }
    .import-stat {
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0c1117;
    }
    .import-stat strong {
      display: block;
      margin-top: 4px;
      font-size: 20px;
    }
    details {
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0c1117;
    }
    summary {
      cursor: pointer;
      padding: 12px 14px;
      color: var(--soft);
      font-size: 13px;
      font-weight: 750;
    }
    pre {
      overflow: auto;
      max-height: 340px;
      margin: 0;
      padding: 0 14px 14px;
      color: #d8e5ef;
      font-size: 12px;
      line-height: 1.5;
    }
    @media (max-width: 980px) {
      header { align-items: flex-start; flex-direction: column; }
      .actions { justify-content: flex-start; }
      .shell, .decision, .scoreboard { grid-template-columns: 1fr; }
    }
    @media (max-width: 620px) {
      main { width: min(100vw - 20px, 1280px); padding-top: 18px; }
      .form-grid, .import-stats { grid-template-columns: 1fr; }
      .row { grid-template-columns: 1fr; }
      h1 { font-size: 20px; }
      button, a.button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">
        <span class="mark">CL</span>
        <div>
          <h1>CreativeLift AI Measurement Lab</h1>
          <p class="subhead">Local experiment calculator and demo scenario runner.</p>
        </div>
      </div>
      <div class="actions">
        <a class="button secondary" href="/docs">API docs</a>
        <a class="button secondary" href="/healthz">Health</a>
      </div>
    </header>

    <section class="shell">
      <div class="left-stack">
        <form id="analysis-form" class="panel">
          <div class="panel-header">
            <h2>Experiment Inputs</h2>
            <button id="seed-button" class="ghost" type="button">Load demo numbers</button>
          </div>
          <div class="panel-body">
            <div class="form-grid">
              <label class="full">
                Experiment name
                <input id="experiment-name" name="name" value="Signup page proof test" autocomplete="off" />
              </label>
              <label>
                Minimum detectable lift (pp)
                <input id="mde" name="mde" type="number" min="0.1" max="100" step="0.1" value="2.0" />
              </label>
              <label>
                Primary metric
                <input id="metric" name="metric" value="conversion_rate" autocomplete="off" />
              </label>
            </div>

            <fieldset>
              <legend>Control</legend>
              <div class="form-grid">
                <label class="full">
                  Label
                  <input id="control-label" value="Current page" autocomplete="off" />
                </label>
                <label>
                  Visitors
                  <input id="control-visitors" type="number" min="0" step="1" value="1000" />
                </label>
                <label>
                  Conversions
                  <input id="control-conversions" type="number" min="0" step="1" value="70" />
                </label>
                <label>
                  Revenue
                  <input id="control-revenue" type="number" min="0" step="1" value="9000" />
                </label>
                <label>
                  Allocation
                  <input id="control-allocation" type="number" min="0.01" max="1" step="0.01" value="0.5" />
                </label>
              </div>
            </fieldset>

            <fieldset>
              <legend>Treatment</legend>
              <div class="form-grid">
                <label class="full">
                  Label
                  <input id="treatment-label" value="Proof-led page" autocomplete="off" />
                </label>
                <label>
                  Visitors
                  <input id="treatment-visitors" type="number" min="0" step="1" value="1000" />
                </label>
                <label>
                  Conversions
                  <input id="treatment-conversions" type="number" min="0" step="1" value="120" />
                </label>
                <label>
                  Revenue
                  <input id="treatment-revenue" type="number" min="0" step="1" value="18000" />
                </label>
                <label>
                  Allocation
                  <input id="treatment-allocation" type="number" min="0.01" max="1" step="0.01" value="0.5" />
                </label>
              </div>
            </fieldset>

            <div class="actions" style="margin-top:14px">
              <button id="analyze-button" type="submit">Analyze numbers</button>
              <button id="scenario-button" class="secondary" type="button">Run full scenario</button>
              <a id="results-link" class="button secondary" href="#" style="display:none">Open generated result</a>
            </div>
            <p id="status" class="status">Ready.</p>
          </div>
        </form>

        <section class="panel" aria-label="CSV import">
          <div class="panel-header">
            <h2>CSV Import</h2>
            <button id="csv-sample-button" class="ghost" type="button">Load sample CSV</button>
          </div>
          <div class="panel-body">
            <div class="form-grid">
              <label class="full">
                CSV file
                <input id="csv-file" type="file" accept=".csv,text/csv" />
              </label>
              <label class="full">
                CSV rows
                <textarea id="csv-text" spellcheck="false"></textarea>
              </label>
            </div>
            <div class="actions" style="margin-top:14px">
              <button id="csv-import-button" type="button">Import CSV</button>
            </div>
            <p id="csv-status" class="status">No CSV imported.</p>
            <div id="csv-import-stats" class="import-stats" style="display:none"></div>
            <div id="csv-import-results" class="history"></div>
          </div>
        </section>
      </div>

      <section class="panel" aria-label="Measurement result">
        <div class="panel-header">
          <h2>Decision</h2>
          <div class="actions">
            <button id="save-report-button" class="secondary" type="button">Save report</button>
            <button id="copy-report-button" class="secondary" type="button">Copy JSON</button>
          </div>
        </div>
        <div class="panel-body">
          <p id="scenario-count" class="subhead" style="margin:0 0 12px">Manual analysis</p>
          <div class="scoreboard">
            <article class="metric">
              <p class="metric-label">Recommendation</p>
              <p id="recommendation" class="metric-value">-</p>
            </article>
            <article class="metric">
              <p class="metric-label">Control CVR</p>
              <p id="control-cvr" class="metric-value">-</p>
            </article>
            <article class="metric">
              <p class="metric-label">Treatment CVR</p>
              <p id="treatment-cvr" class="metric-value good">-</p>
            </article>
            <article class="metric">
              <p class="metric-label">Confidence</p>
              <p id="confidence" class="metric-value">-</p>
            </article>
          </div>

          <div class="decision">
            <article class="block">
              <h2>Readout</h2>
              <p id="summary">Submit the form to calculate a decision.</p>
              <p id="action"></p>
            </article>
            <article class="block">
              <h2>Sample Plan</h2>
              <p id="sample-plan">-</p>
            </article>
          </div>

          <div class="rows" aria-label="Variant table">
            <div class="row"><span>Variant</span><span>Visitors</span><span>Conversions</span></div>
            <div class="row"><span id="control-row-label">Control</span><span id="control-row-visitors">-</span><span id="control-row-conversions">-</span></div>
            <div class="row"><span id="treatment-row-label">Treatment</span><span id="treatment-row-visitors">-</span><span id="treatment-row-conversions">-</span></div>
          </div>

          <ul id="next-steps" class="list"></ul>

          <details>
            <summary>API payload</summary>
            <pre id="payload">{}</pre>
          </details>

          <section class="block" style="margin-top:14px">
            <div class="report-top">
              <h2>Decision Log</h2>
              <div class="actions">
                <a class="button secondary" href="/v1/demo/reports/export?format=csv">CSV</a>
                <a class="button secondary" href="/v1/demo/reports/export?format=json">JSON</a>
                <a class="button secondary" href="/v1/demo/reports/export?format=markdown">MD</a>
                <button id="clear-reports-button" class="secondary" type="button">Clear</button>
              </div>
            </div>
            <div id="report-summary" class="import-stats"></div>
            <div id="report-history" class="history">
              <p class="subhead">No saved reports yet.</p>
            </div>
          </section>
        </div>
      </section>
    </section>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);
    const numberValue = (id) => Number($(id).value || 0);
    const pct = (value, digits = 1) => Number.isFinite(value) ? `${(value * 100).toFixed(digits)}%` : "-";
    const pp = (value) => Number.isFinite(value) ? `${(value * 100).toFixed(2)} pp` : "-";
    const fmt = (value) => Number.isFinite(value) ? new Intl.NumberFormat("en-US").format(value) : "-";
    const csvSample = [
      "name,control_visitors,control_conversions,treatment_visitors,treatment_conversions,control_revenue,treatment_revenue,mde,notes",
      "Homepage proof,1000,70,1000,120,9000,18000,2,Winner candidate",
      "Email subject,900,90,900,72,4000,3100,1.5,Loser candidate"
    ].join("\\n");
    let currentRequest = null;
    let currentAnalysis = null;
    let currentReport = null;
    let currentSource = "manual";

    function setStatus(message, isError = false) {
      $("status").textContent = message;
      $("status").className = isError ? "status error" : "status";
    }

    function setCsvStatus(message, isError = false) {
      $("csv-status").textContent = message;
      $("csv-status").className = isError ? "status error" : "status";
    }

    function payloadFromForm() {
      return {
        name: $("experiment-name").value.trim() || "Untitled experiment",
        primary_metric: $("metric").value.trim() || "conversion_rate",
        minimum_detectable_effect: numberValue("mde") / 100,
        control: {
          key: "control",
          label: $("control-label").value.trim() || "Control",
          visitors: numberValue("control-visitors"),
          conversions: numberValue("control-conversions"),
          revenue: numberValue("control-revenue"),
          allocation: numberValue("control-allocation")
        },
        treatment: {
          key: "treatment",
          label: $("treatment-label").value.trim() || "Treatment",
          visitors: numberValue("treatment-visitors"),
          conversions: numberValue("treatment-conversions"),
          revenue: numberValue("treatment-revenue"),
          allocation: numberValue("treatment-allocation")
        }
      };
    }

    function setField(id, value) {
      $(id).value = String(value);
    }

    function seedNumbers() {
      setField("experiment-name", "Signup page proof test");
      setField("mde", "2.0");
      setField("metric", "conversion_rate");
      setField("control-label", "Current page");
      setField("control-visitors", "1000");
      setField("control-conversions", "70");
      setField("control-revenue", "9000");
      setField("control-allocation", "0.5");
      setField("treatment-label", "Proof-led page");
      setField("treatment-visitors", "1000");
      setField("treatment-conversions", "120");
      setField("treatment-revenue", "18000");
      setField("treatment-allocation", "0.5");
    }

    function loadCsvSample() {
      $("csv-text").value = csvSample;
      setCsvStatus("Sample CSV loaded.");
    }

    function applyRequestToForm(request) {
      setField("experiment-name", request.name);
      setField("mde", (Number(request.minimum_detectable_effect || 0) * 100).toFixed(1));
      setField("metric", request.primary_metric || "conversion_rate");
      setField("control-label", request.control.label || "Control");
      setField("control-visitors", request.control.visitors);
      setField("control-conversions", request.control.conversions);
      setField("control-revenue", request.control.revenue || 0);
      setField("control-allocation", request.control.allocation || 0.5);
      setField("treatment-label", request.treatment.label || "Treatment");
      setField("treatment-visitors", request.treatment.visitors);
      setField("treatment-conversions", request.treatment.conversions);
      setField("treatment-revenue", request.treatment.revenue || 0);
      setField("treatment-allocation", request.treatment.allocation || 0.5);
    }

    function styleRecommendation(value) {
      const el = $("recommendation");
      el.textContent = value || "-";
      el.className = "metric-value";
      if (value === "winner") el.classList.add("good");
      if (value === "inconclusive" || value === "needs_more_data" || value === "invalid_srm") el.classList.add("warn");
      if (value === "loser") el.classList.add("bad");
    }

    function renderAnalysis(analysis, sourceLabel = "Manual analysis") {
      const variantKeys = Object.keys(analysis.variants);
      const control = analysis.variants[variantKeys[0]];
      const treatment = analysis.variants[variantKeys[1]];
      const pValue = analysis.comparison.p_value;
      const confidence = typeof pValue === "number" ? Math.max(0, Math.min(1, 1 - pValue)) : NaN;
      currentAnalysis = analysis;
      currentSource = sourceLabel;

      styleRecommendation(analysis.recommendation);
      $("control-cvr").textContent = pct(control.conversion_rate);
      $("treatment-cvr").textContent = pct(treatment.conversion_rate);
      $("confidence").textContent = pct(confidence);
      $("summary").textContent = analysis.decision_summary;
      $("action").textContent = analysis.recommended_action;
      $("scenario-count").textContent = sourceLabel;

      const sample = analysis.sample_size;
      $("sample-plan").textContent = sample.per_variant
        ? `Target ${fmt(sample.per_variant)} visitors per variant for ${pp(sample.minimum_detectable_effect)} minimum detectable lift. Remaining: ${fmt(sample.remaining_control)} control, ${fmt(sample.remaining_treatment)} treatment.`
        : sample.note;

      $("control-row-label").textContent = control.label;
      $("control-row-visitors").textContent = fmt(control.visitors);
      $("control-row-conversions").textContent = fmt(control.conversions);
      $("treatment-row-label").textContent = treatment.label;
      $("treatment-row-visitors").textContent = fmt(treatment.visitors);
      $("treatment-row-conversions").textContent = fmt(treatment.conversions);

      const list = $("next-steps");
      list.innerHTML = "";
      analysis.next_steps.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
      });
      $("payload").textContent = JSON.stringify(analysis, null, 2);
    }

    function renderReportHistory(reports) {
      const container = $("report-history");
      container.innerHTML = "";
      if (!reports.length) {
        const empty = document.createElement("p");
        empty.className = "subhead";
        empty.textContent = "No saved reports yet.";
        container.appendChild(empty);
        return;
      }
      reports.forEach((report) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "report-item";
        const created = new Date(report.created_at).toLocaleString();
        const top = document.createElement("span");
        top.className = "report-top";
        const title = document.createElement("span");
        title.className = "report-title";
        title.textContent = report.analysis.name;
        const tag = document.createElement("span");
        tag.className = "report-tag";
        tag.textContent = report.analysis.recommendation;
        top.append(title, tag);
        const meta = document.createElement("span");
        meta.className = "report-meta";
        meta.textContent = `${created} · ${report.source}`;
        button.append(top, meta);
        button.addEventListener("click", () => {
          currentReport = report;
          currentRequest = report.request;
          applyRequestToForm(report.request);
          renderAnalysis(report.analysis, `Saved report · ${created}`);
          $("payload").textContent = JSON.stringify(report, null, 2);
          setStatus("Saved report loaded.");
        });
        container.appendChild(button);
      });
    }

    function renderReportSummary(summary) {
      const container = $("report-summary");
      container.innerHTML = "";
      const avgLift = typeof summary.average_relative_lift === "number" ? pct(summary.average_relative_lift) : "-";
      const best = summary.best_report_name || "-";
      [
        ["Reports", summary.total],
        ["Winners", summary.winners],
        ["Avg lift", avgLift],
        ["Best", best]
      ].forEach(([label, value]) => {
        const item = document.createElement("div");
        item.className = "import-stat";
        const caption = document.createElement("span");
        caption.className = "metric-label";
        caption.textContent = label;
        const strong = document.createElement("strong");
        strong.textContent = String(value);
        item.append(caption, strong);
        container.appendChild(item);
      });
    }

    async function loadReportSummary() {
      try {
        const response = await fetch("/v1/demo/reports/summary");
        if (!response.ok) throw new Error(await response.text());
        renderReportSummary(await response.json());
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Could not load report summary.", true);
      }
    }

    async function loadReports() {
      try {
        const response = await fetch("/v1/demo/reports?limit=8");
        if (!response.ok) throw new Error(await response.text());
        renderReportHistory(await response.json());
        await loadReportSummary();
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Could not load reports.", true);
      }
    }

    async function clearReports() {
      if (!confirm("Clear saved local reports?")) return;
      $("clear-reports-button").disabled = true;
      try {
        const response = await fetch("/v1/demo/reports", { method: "DELETE" });
        if (!response.ok && response.status !== 204) throw new Error(await response.text());
        currentReport = null;
        await loadReports();
        setStatus("Decision log cleared.");
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Could not clear reports.", true);
      } finally {
        $("clear-reports-button").disabled = false;
      }
    }

    function renderImportStats(importResult) {
      const stats = $("csv-import-stats");
      stats.style.display = "grid";
      stats.innerHTML = "";
      [
        ["Accepted", importResult.accepted],
        ["Rejected", importResult.rejected],
        ["Saved reports", importResult.reports.length]
      ].forEach(([label, value]) => {
        const item = document.createElement("div");
        item.className = "import-stat";
        const caption = document.createElement("span");
        caption.className = "metric-label";
        caption.textContent = label;
        const strong = document.createElement("strong");
        strong.textContent = String(value);
        item.append(caption, strong);
        stats.appendChild(item);
      });
    }

    function renderImportResults(importResult) {
      const container = $("csv-import-results");
      container.innerHTML = "";
      importResult.reports.slice(0, 5).forEach((report) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "report-item";
        const top = document.createElement("span");
        top.className = "report-top";
        const title = document.createElement("span");
        title.className = "report-title";
        title.textContent = report.analysis.name;
        const tag = document.createElement("span");
        tag.className = "report-tag";
        tag.textContent = report.analysis.recommendation;
        top.append(title, tag);
        const meta = document.createElement("span");
        meta.className = "report-meta";
        meta.textContent = report.analysis.decision_summary;
        button.append(top, meta);
        button.addEventListener("click", () => {
          currentReport = report;
          currentRequest = report.request;
          applyRequestToForm(report.request);
          renderAnalysis(report.analysis, "CSV import");
          $("payload").textContent = JSON.stringify(report, null, 2);
          setCsvStatus("Imported report loaded.");
        });
        container.appendChild(button);
      });
      importResult.errors.slice(0, 5).forEach((error) => {
        const row = document.createElement("div");
        row.className = "report-item";
        const top = document.createElement("span");
        top.className = "report-top";
        const title = document.createElement("span");
        title.className = "report-title";
        title.textContent = `Row ${error.row_number}`;
        const tag = document.createElement("span");
        tag.className = "report-tag";
        tag.style.color = "var(--red)";
        tag.textContent = "rejected";
        top.append(title, tag);
        const meta = document.createElement("span");
        meta.className = "report-meta";
        meta.textContent = error.message;
        row.append(top, meta);
        container.appendChild(row);
      });
    }

    async function importCsvReports() {
      const csvText = $("csv-text").value.trim();
      if (!csvText) {
        setCsvStatus("CSV is empty.", true);
        return;
      }
      $("csv-import-button").disabled = true;
      setCsvStatus("Importing CSV...");
      try {
        const response = await fetch("/v1/demo/reports/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            csv_text: csvText,
            source: "csv",
            save_reports: true,
            default_minimum_detectable_effect: numberValue("mde") / 100 || 0.02
          })
        });
        if (!response.ok) throw new Error(await response.text());
        const importResult = await response.json();
        renderImportStats(importResult);
        renderImportResults(importResult);
        await loadReports();
        if (importResult.reports.length) {
          const report = importResult.reports[0];
          currentReport = report;
          currentRequest = report.request;
          applyRequestToForm(report.request);
          renderAnalysis(report.analysis, "CSV import");
          $("payload").textContent = JSON.stringify(report, null, 2);
        }
        setCsvStatus(`Imported ${importResult.accepted} report(s), rejected ${importResult.rejected}.`, Boolean(importResult.rejected && !importResult.accepted));
      } catch (error) {
        setCsvStatus(error instanceof Error ? error.message : "CSV import failed.", true);
      } finally {
        $("csv-import-button").disabled = false;
      }
    }

    async function analyzeCurrentForm(sourceLabel) {
      const payload = payloadFromForm();
      $("analyze-button").disabled = true;
      setStatus("Analyzing...");
      try {
        const response = await fetch("/v1/demo/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(await response.text());
        const analysis = await response.json();
        currentRequest = payload;
        currentReport = null;
        renderAnalysis(analysis, sourceLabel);
        setStatus("Analysis complete.");
        return analysis;
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Analysis failed.", true);
      } finally {
        $("analyze-button").disabled = false;
      }
    }

    async function saveCurrentReport() {
      if (!currentRequest) {
        await analyzeCurrentForm("Manual analysis");
      }
      if (!currentRequest || !currentAnalysis) return;
      $("save-report-button").disabled = true;
      setStatus("Saving report...");
      try {
        const response = await fetch("/v1/demo/reports", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            source: currentSource.slice(0, 80),
            notes: currentAnalysis.recommended_action,
            request: currentRequest
          })
        });
        if (!response.ok) throw new Error(await response.text());
        currentReport = await response.json();
        $("payload").textContent = JSON.stringify(currentReport, null, 2);
        await loadReports();
        setStatus("Report saved.");
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Report save failed.", true);
      } finally {
        $("save-report-button").disabled = false;
      }
    }

    async function copyPayload() {
      const text = $("payload").textContent || "{}";
      try {
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(text);
        } else {
          const area = document.createElement("textarea");
          area.value = text;
          document.body.appendChild(area);
          area.select();
          document.execCommand("copy");
          area.remove();
        }
        setStatus("JSON copied.");
      } catch (error) {
        setStatus("Copy failed.", true);
      }
    }

    function applyScenarioToForm(scenario) {
      const control = scenario.result.variants.control;
      const treatment = scenario.result.variants.ai_proof;
      setField("experiment-name", scenario.experiment.name);
      setField("mde", "2.0");
      setField("metric", scenario.experiment.primary_metric);
      setField("control-label", "Control");
      setField("control-visitors", control.visitors);
      setField("control-conversions", control.conversions);
      setField("control-revenue", control.revenue || 0);
      setField("control-allocation", "0.5");
      setField("treatment-label", "AI proof");
      setField("treatment-visitors", treatment.visitors);
      setField("treatment-conversions", treatment.conversions);
      setField("treatment-revenue", treatment.revenue || 0);
      setField("treatment-allocation", "0.5");
    }

    $("analysis-form").addEventListener("submit", (event) => {
      event.preventDefault();
      analyzeCurrentForm("Manual analysis");
    });

    $("seed-button").addEventListener("click", () => {
      seedNumbers();
      analyzeCurrentForm("Seeded analysis");
    });

    $("save-report-button").addEventListener("click", saveCurrentReport);
    $("copy-report-button").addEventListener("click", copyPayload);
    $("clear-reports-button").addEventListener("click", clearReports);
    $("csv-sample-button").addEventListener("click", loadCsvSample);
    $("csv-import-button").addEventListener("click", importCsvReports);
    $("csv-file").addEventListener("change", async (event) => {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      try {
        $("csv-text").value = await file.text();
        setCsvStatus(`${file.name} loaded.`);
      } catch (error) {
        setCsvStatus("Could not read CSV file.", true);
      }
    });

    $("scenario-button").addEventListener("click", async () => {
      $("scenario-button").disabled = true;
      setStatus("Creating scenario...");
      try {
        const response = await fetch("/v1/demo/scenario", { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        const scenario = await response.json();
        applyScenarioToForm(scenario);
        const analysis = await analyzeCurrentForm(`${scenario.ingestion.accepted} scenario events`);
        $("payload").textContent = JSON.stringify({ scenario, analysis }, null, 2);
        const link = $("results-link");
        link.href = scenario.results_url;
        link.style.display = "inline-flex";
        setStatus("Scenario created and analyzed.");
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Scenario failed.", true);
      } finally {
        $("scenario-button").disabled = false;
      }
    });

    seedNumbers();
    loadCsvSample();
    loadReports();
    analyzeCurrentForm("Seeded analysis");
  </script>
</body>
</html>
"""


def demo_console() -> HTMLResponse:
    return HTMLResponse(DEMO_CONSOLE_HTML)
