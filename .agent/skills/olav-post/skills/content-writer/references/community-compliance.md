# Community Self-Promotion & Compliance Guidelines

This guide defines the rules for publishing open-source release announcements and technical articles in technical communities (NetBox Slack, NTC Slack, Reddit, HackerNews, V2EX, etc.).

---

## Core Philosophy: Open-Source Card & Value-First

Developers and network engineers have a high threshold of skepticism for promotional content. To maintain community trust and prevent posts from being removed or flagged as spam, follow these mandatory rules:

### 1. The Open-Source Card (开源身份第一句)
Every social post or community draft MUST begin by establishing the author's status as an open-source creator/maintainer.

**Approved English Formats:**
- *"Hi everyone, I'm the author of OLAV (an open-source CLI for AI-native infrastructure ops). I wanted to share..."*
- *"We just released an open-source tool for NetBox natural language querying called OLAV..."*

**Approved Chinese Formats (V2EX / 掘金等):**
- *“大家好，我是开源项目 OLAV（面向网络基础设施与 NetBox 的 AI Agent CLI）的开发者。今天想和大家分享...”*

### 2. The 10:1 Rule (Self-Promotion Ratio)
On platforms like Reddit (`r/netbox`, `r/networkautomation`) and technical Slack communities, self-promotion posts must be balanced with genuine community engagement.
- Always answer user questions in comments promptly.
- Never cross-post identical content across multiple subreddits on the same day.

### 3. Value-First & Proof-Based (讲技术与踩坑，不讲 PPT)
- **Do NOT** write generic marketing claims like *"Revolutionary AI platform for your network"*.
- **DO** write concrete technical problem-solving stories, e.g., *"How we eliminated MCP server overhead by parsing REST OpenAPI schemas into markdown references for schema-aware querying"*.
- Include concrete numbers (e.g. *"reduced setup time from 20 mins to a single `pip install olav` command"*).
- Include safety guarantees: Highlight OLAV's **7-Layer Write Security** (`--enable-api-write` lock, dry-run mandatory pass) to address SRE fear of AI misconfiguration.

---

## Approved Green-Light Channels

| Community / Platform | Approved Channel / Section | Posting Rules |
| :--- | :--- | :--- |
| **NetBox Community Slack** | `#show-and-tell`, `#integrations` | Focus on NetBox integration (`olav registry register`). Mandatory Open-Source Card. |
| **NetBox Discourse** | `Community Projects` | Full technical breakdown of how OLAV interacts with NetBox API. |
| **Network to Code (NTC) Slack** | `#tooling`, `#showcase` | Focus on Network Automation workflow, PyPI installation, CLI demo. |
| **HackerNews** | Frontpage via `Show HN:` | Title: `Show HN: OLAV – Single-command CLI to query & control infrastructure`. Code/demo first. |
| **Reddit** | `r/netbox`, `r/networkautomation`, `r/selfhosted` | Educational breakdown of problem + solution. No hype adjectives. |
| **V2EX** | `/go/create` (分享创造) | 详细写明开发背景、解决的 NetBox 排障痛点、开源地址与安装步骤。 |

---

## Strictly Forbidden Actions (Red Lines)

1. **Vendor Forums (Cisco / Juniper / Arista)**: NEVER create standalone promotional threads. (Only allowed as inline answers to existing technical help threads when relevant).
2. **Reddit `r/networking`**: NEVER create standalone promotional posts on the main feed. (Only allowed in weekly vendor/promotion threads).
3. **Identical Cross-Posting**: NEVER post the exact same text to multiple platforms. Every platform gets a unique angle and format.
