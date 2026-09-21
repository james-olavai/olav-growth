Most teams spend weeks building complex vector search pipelines, only to watch their AI agents choke on something basic:

A messy folder of .pdf, .docx, .pptx, and .xlsx files.

When LLM agents interact with real-world local document stores, three unsexy problems immediately break them:

1. Binary Format Choke: Agents can't natively parse Office formats or scanned PDFs without expensive token blowup or fragile converters.
2. The "Duplicate Corroboration" Trap: The exact same strategy doc exists as both `spec_v2.docx` and `spec_final.pdf`. The agent reads both, assumes they are two "independent corroborating sources", and hallucinates false consensus.
3. Vocabulary Drift: A team queries "auth", but the doc says "SSO". Blind similarity search often misses domain-specific intent.

To solve this, we just open-sourced `olav-dockb`:
👉 https://github.com/james-olavai/olav-dockb

It’s an open-source Claude Code skill & agent toolkit that turns any folder of mixed documents into a searchable, classified Markdown corpus designed specifically for LLM agents.

What it does differently:
✅ Ingests mixed formats (PDF, DOCX, PPTX, XLSX, OCR for scanned images) into clean Markdown + per-sheet CSVs.
✅ Zero-hallucination dedup: Exact sha256 duplicates are stubbed; near-duplicates are flagged in a report so your agent never counts the same fact twice.
✅ Two-axis classification (doc_type and category) with explicit confidence scoring.
✅ Full-text + metadata search with synonym expansion—retrieves only the handful of relevant docs instead of blowing your context window.
✅ 100% Obsidian-compatible out of the box (properties, wikilinks, Dataview).
✅ Single config.yaml with human-negotiated taxonomy—no hardcoded paths.

It's free, open-source, and works as a standalone CLI or directly inside Claude Code / AI agent workflows.

Check out the repo, give it a star, and let me know how you're structuring local knowledge for your agents:
🔗 https://github.com/james-olavai/olav-dockb

#OpenSource #AIAgents #ClaudeCode #LLM #RAG #KnowledgeManagement #BuildInPublic #Python
