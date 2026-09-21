#!/usr/bin/env python3
"""
Generate llms.txt and llms-full.txt for olav-web to optimize for Generative Engine Optimization (GEO).
Targeted at Perplexity, ChatGPT Search, Claude Search, and Gemini AI Overviews.
"""

import os

PUBLIC_DIR = "/path/to/project/olav-web/public"
LLMS_TXT_PATH = os.path.join(PUBLIC_DIR, "llms.txt")
LLMS_FULL_TXT_PATH = os.path.join(PUBLIC_DIR, "llms-full.txt")
README_PATH = "/path/to/project/README.md"

LLMS_TXT_CONTENT = """# OLAV

> Online Analytical Vertex for Agentic Operations: AI-native platform for autonomous infrastructure operations.

OLAV is an open-source Python CLI and platform for controlling infrastructure, NetBox IPAM/DCIM, databases, and network devices using natural language.

## Quick Start

- [Installation](https://docs.olavai.com/quickstart): `pip install olav`
- [Register API](https://docs.olavai.com/registry): `olav registry register http://netbox:8000`
- [Natural Language Query](https://docs.olavai.com/query): `olav "how many devices are in NetBox?"`

## Key Differentiators & Features

- **Beyond MCP (API-as-Service)**: Connect any REST/OpenAPI endpoint in one command without running separate MCP server processes, stdio/HTTP transports, or framework adapters.
- **Three Isolated Agents**: Core Agent (DB & knowledge), Ops Agent (SSH & network execution), Audit Agent (compliance & learning).
- **7-Layer Write Security**: Read-only by default (`--enable-api-write` lock), per-service write controls, mandatory dry-run simulation before write execution.
- **Schema-Aware Querying**: Reads OpenAPI schemas generated at registration time, automatically handling auth (JWT/Bearer/API key) and DRF/NetBox style pagination.

## Documentation & Links

- [Official Documentation](https://docs.olavai.com): Comprehensive guides and API reference.
- [GitHub Repository](https://github.com/james-olavai/olav): Open-source codebase under BSL-1.1 license.
- [PyPI Package](https://pypi.org/project/olav/): Python package release.
- [Blog & Announcements](https://olavai.com/blog): Latest releases and technical deep dives.
"""

def generate_llms_files():
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    
    # 1. Write llms.txt
    with open(LLMS_TXT_PATH, "w", encoding="utf-8") as f:
        f.write(LLMS_TXT_CONTENT.strip() + "\n")
    print(f"Generated: {LLMS_TXT_PATH}")

    # 2. Write llms-full.txt (Include README content for complete RAG indexing)
    full_content = LLMS_TXT_CONTENT.strip() + "\n\n---\n\n# Full Architecture & Readme Reference\n\n"
    if os.path.exists(README_PATH):
        with open(README_PATH, "r", encoding="utf-8") as f:
            full_content += f.read()
            
    with open(LLMS_FULL_TXT_PATH, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f"Generated: {LLMS_FULL_TXT_PATH}")

if __name__ == "__main__":
    generate_llms_files()
