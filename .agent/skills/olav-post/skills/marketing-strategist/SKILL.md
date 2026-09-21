---
name: marketing-strategist
description: "Analyze project telemetry, evaluate marketing performance (Reflection), and formulate the next Campaign Plan for OLAV. Generates olav-post/campaign-plan.md and dispatches angles to content-writer. Use when the user says 'plan marketing', '制定营销策略', '复盘营销效果', 'marketing strategy', or after running marketing-analytics."
argument-hint: "Optional: --phase launch | --phase ecosystem | --phase case-study"
---

# Marketing Strategist Skill

The strategic brain of the OLAV marketing loop. Reads `olav-post/marketing-metrics.json`, analyzes conversion angles, evaluates current project status, and formulates a targeted campaign plan (`olav-post/campaign-plan.md`).

---

## Scope

This skill **formulates strategy, evaluates angles, and dispatches tasks**.
- Reads telemetry from `marketing-analytics`.
- Instructs `content-writer` on what angles and channels to target.
- Instructs `social-poster` on launch windows and compliance rules.

---

## Execution Flow

```
┌───────────────────────────┐
│ marketing-analytics       │
│ olav-post/metrics.json    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ marketing-strategist      │
│ 1. Evaluate Metrics       │
│ 2. Analyze Campaign Phase │
│ 3. Select Primary Angle   │
│ 4. Output campaign-plan   │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ Dispatch to content-writer│
│ (Angle + Target Channels) │
└───────────────────────────┘
```

---

## Autonomous Marketing Workflow Automation

The marketing controller script (`marketing_workflow.py`) integrates all 5 marketing skills into an automated scheduled workflow:

```bash
# Daily Task (Run 9:00 UTC daily): Telemetry + Google Trends + GEO llms.txt update
uv run python .agent/skills/marketing-strategist/scripts/marketing_workflow.py --mode daily

# Publishing Task (Run Mon/Thu 10:00 UTC): Gate scoring + Campaign Plan + HITL Preview
uv run python .agent/skills/marketing-strategist/scripts/marketing_workflow.py --mode publish

# Weekly Review Task (Run Sun 20:00 UTC): 14-day sliding reflection + Weekly Report
uv run python .agent/skills/marketing-strategist/scripts/marketing_workflow.py --mode review
```

---

## Step-by-Step Procedure

### Step 1 — Load Data & Code Context

1. Ensure `olav-post/marketing-metrics.json` exists. If not, trigger `marketing-analytics` first.
2. Read `olav-post/marketing-metrics.json`.
3. Check recent git log and release tags:
   ```bash
   git log --oneline -10
   cat CHANGELOG.md | head -50
   ```

### Step 2 — Determine Campaign Phase & Primary Angle

Read: [campaign-framework.md](./references/campaign-framework.md)
Read: [feature-mapping.md](./references/feature-mapping.md) for Trend-to-Feature matching.

1. **Check Search Trends**: Inspect `trending_keywords` in `olav-post/marketing-metrics.json`.
2. **Match Keyword to Feature**: If a high-growth keyword is detected (e.g. *"NetBox MCP"* or *"AI Agent safety"*), match it against `feature-mapping.md` to select the highest-leverage OLAV feature and blog title pattern.
3. **Match Scenario & Channel Mix**:

| Phase / Scenario | Trigger / Trend Keyword | Primary Angle Focus | Target Channels |
| :--- | :--- | :--- | :--- |
| **Demand-Led (Trend Spike)** | High growth in *"NetBox MCP"* or *"AI Safety"* | Beyond MCP / Zero Overhead OR 7-Layer Write Security | NetBox Slack #show-and-tell, Show HN, V2EX, r/netbox |
| **Launch Spike (Major Version Release)** | Version ReleaseTag | Single-command setup + GitHub Trending launch window | Show HN, Reddit r/netbox, NetBox Slack, V2EX, LinkedIn |
| **Troubleshooting (Case Study)** | System Post-Mortem | 7-Layer Write Security & Dry-run simulation | 知乎, 掘金, 微信公众号, Reddit r/sysadmin |

### Step 3 — Generate Campaign Plan Artifact

Write `olav-post/campaign-plan.md`:

```markdown
# Campaign Plan — YYYY-MM-DD

## Executive Summary
[1-2 sentences: Objective of this campaign, target phase, and expected outcomes]

## Current Telemetry Reflection
- **Current GitHub Stars**: X
- **Top Converting Angle**: [e.g., NetBox Zero-MCP Overhead]
- **Key Observation**: [What worked well in previous post / what to improve]

## Target Angle & Hook
- **Primary Angle**: [Selected Angle]
- **Open-Source Card Statement**: [Selected Open-Source Opening Line]
- **Core Proof Points**:
  1. `pip install olav` (60s setup)
  2. `olav registry register` (No MCP server overhead)
  3. 7-Layer Write Security (`--enable-api-write` & dry-run)

## Channel Mix & Priority
- [x] NetBox Community Slack (`#show-and-tell`) — High Priority
- [x] HackerNews (`Show HN`) — Launch Window
- [x] V2EX (`/go/create`) — High Priority
- [x] Reddit (`r/netbox`, `r/networkautomation`) — Medium Priority
- [ ] Vendor Forums — SKIPPED (Rule Compliance)

## Launch Window & Coordination
- **Target Launch Date/Time**: YYYY-MM-DD HH:MM UTC
- **GitHub Trending Spike Strategy**: Simultaneous cross-channel release within 24 hours.

## Hand-off Instructions
1. Run `content-writer` with primary angle: "[Primary Angle Name]".
2. Hand off drafts to `social-poster` for compliance check & post staging.
```

### Step 4 — Dispatch & Hand Off

Report the generated Campaign Plan to the user and ask:
> *"Campaign Plan is ready in `olav-post/campaign-plan.md`. Shall I trigger `content-writer` with the selected Primary Angle?"*
