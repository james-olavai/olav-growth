# Campaign Strategy Framework

Strategic guidelines for selecting angles, timing, and channels for OLAV marketing.

---

## 1. The Three Primary Campaign Angles

### Angle A: "Beyond MCP — Zero Overhead Infrastructure AI"
* **Target Audience**: SREs, DevOps, Engineers tired of running dozens of local MCP server processes.
* **Core Value Prop**:
  - `olav registry register http://endpoint:8000` — Registers OpenAPI/REST APIs in 1 command.
  - Zero MCP server background processes, no stdio/HTTP adapter overhead.
  - Schema-aware Markdown reference generation.
* **Best Platforms**: HackerNews (`Show HN`), V2EX, Reddit (`r/devops`, `r/selfhosted`).

### Angle B: "Natural Language for NetBox"
* **Target Audience**: Network Engineers, NetBox users, DCIM/IPAM admins.
* **Core Value Prop**:
  - Query NetBox IPAM/DCIM via natural language (`olav "how many switches in NetBox?"`).
  - Cross-check local database vs NetBox state.
  - Instant installation: `pip install olav`.
* **Best Platforms**: NetBox Community Slack (`#show-and-tell`), NetBox Discourse (`Community Projects`), Reddit (`r/netbox`, `r/networkautomation`), Network to Code (NTC) Slack (`#tooling`).

### Angle C: "Safety-First AIOps — 7-Layer Write Protection"
* **Target Audience**: IT Directors, Senior Network Architects, Security Auditors.
* **Core Value Prop**:
  - Prevent AI from executing destructive CLI commands on production switches.
  - Mandatory `--enable-api-write` lock, dry-run simulation pass before execution.
  - Least-privilege tool isolation across Core, Ops, and Audit Agents.
* **Best Platforms**: 知乎, 掘金, 微信公众号, LinkedIn, Packet Pushers.

---

## 2. Launch Window & Spike Coordination (GitHub Trending)

To maximize conversion and trigger GitHub Daily Trending:
1. **Never stagger posts over a week**. Concentrate cross-channel announcements within a single 24-hour UTC window.
2. **Optimal Timing**: Wednesday 13:00 UTC (09:00 EST / 21:00 SGT/CST).
3. **Sequence**:
   - T+00:00 — Release GitHub Version & update README.
   - T+00:30 — Post `Show HN` on HackerNews.
   - T+01:00 — Post on NetBox Community Slack & NTC Slack.
   - T+02:00 — Post on Reddit (`r/netbox`).
   - T+08:00 — Post on V2EX (`/go/create`).
