# Trend-to-Feature Mapping Registry

This registry maps high-growth search terms (captured by `marketing-analytics` via Google Trends / Search Intent) directly to OLAV's core technical differentiators and blog post templates.

---

## 1. Feature Mapping Matrix

| Search Keyword / Trend Topic | Matched OLAV Feature | Technical Differentiator | Recommended Blog Title Pattern |
| :--- | :--- | :--- | :--- |
| **`MCP / Model Context Protocol`** | **Beyond MCP (API-as-Service)** | Single-command REST API registration (`olav registry register`). Zero MCP server processes or stdio/HTTP overhead. | *"Beyond MCP: Why We Built Single-Command API Registration for Infrastructure AI"* |
| **`NetBox / IPAM / DCIM`** | **NetBox Schema-Aware Integration** | Natural language queries for NetBox devices (`olav "how many devices in NetBox?"`). Cross-DB state verification. | *"Query Your NetBox Infrastructure in 60 Seconds with OLAV Natural Language CLI"* |
| **`AI Safety / Network Misconfiguration`** | **7-Layer Write Security** | Read-only by default (`--enable-api-write` lock). Mandatory dry-run simulation pass before execution. | *"Safety-First AIOps: How OLAV Prevents AI Agents from Nuking Production Switches"* |
| **`Ansible / Network Automation`** | **Ops Agent & Script Gen** | Generates real, environment-aware automation scripts with strict tool isolation across Core, Ops, and Audit Agents. | *"Autonomous Network Ops: Generating Environment-Aware Automation Scripts safely with OLAV"* |
| **`AIOps / Autonomous Infrastructure`** | **Agentic Architecture** | Subagent harness with principle of least authority. Only 5 orchestrator tools. | *"Inside OLAV: Designing a Least-Authority Agent Architecture for Infrastructure Operations"* |

---

## 2. Demand-Led Campaign Selection Rules

When `marketing-analytics` reports a keyword in `trending_keywords` with high growth (>50% YoY or >100% WoW):
1. **Prioritize the matched angle** over default release notes.
2. **Inject the trending keyword** into the first 100 words and H1/H2 headers of the post (for GEO & SEO Answer Snippets).
3. **Target communities** where that specific keyword is actively discussed (e.g. NetBox Slack for `NetBox`, `r/networkautomation` for `Ansible/Automation`, HackerNews for `MCP`).
