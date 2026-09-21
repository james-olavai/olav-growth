---
name: marketing-analytics
description: "Fetch and aggregate marketing performance metrics (GitHub Stars, Forks, community post engagement, traffic telemetry) for OLAV. Saves output to olav-post/marketing-metrics.json. Use when the user says 'fetch marketing data', 'check marketing metrics', '更新营销指标', or before running marketing-strategist."
argument-hint: "Optional: --repo james-olavai/olav | --history-days 7"
---

# Marketing Analytics Skill

Fetch telemetry and engagement metrics for OLAV repositories and published community posts, outputting structured performance data to `olav-post/marketing-metrics.json`.

---

## Scope

This skill **only collects and aggregates data**. It does NOT make strategic decisions or write marketing copy. Hand off output to `marketing-strategist` when metrics are ready.

---

## Step-by-Step Procedure

### Step 1 — Run Data Collector Script

Run the python metrics collection script:

```bash
uv run python .agent/skills/marketing-analytics/scripts/fetch_metrics.py
```

This script automatically:
1. Queries the GitHub API for current repo metrics (Stars, Forks, Open Issues, Watchers, Recent Stargazer Velocity).
2. Reads published post URLs from the latest `olav-post/archive/YYYY-MM-DD/_meta.md`.
3. Formats and writes the aggregated metrics into `olav-post/marketing-metrics.json`.

### Step 2 — Verify Output

Verify that `olav-post/marketing-metrics.json` has been updated and contains valid metrics.

Read: [metrics-schema.md](./references/metrics-schema.md) to understand the structure of the generated metrics JSON.

### Step 3 — Report Summary

Output a short summary table to the user:

```
Marketing Metrics Updated: olav-post/marketing-metrics.json

Metric                Value        Change (7d)
────────────────────────────────────────────────
GitHub Stars          1,240        +45
GitHub Forks          88           +6
Recent Release        v0.22.0      (2026-08-01)
Tracked Archives      3            -
```

Suggest running `marketing-strategist` to analyze metrics and plan the next campaign.
