# Productivity Hacks

A collection of Claude skills for everyday productivity tasks.

## Skills

### compress-pdf

Compress PDF files to a target size using Ghostscript while maintaining the best possible quality.

**How to Use:**

Ask Claude to compress a PDF:

```
Compress my-document.pdf to under 500KB
```

```
Make this PDF smaller for email: /path/to/large-file.pdf
```

**What It Does:**

- Intelligently selects compression quality based on target size
- Tries highest quality first, stops when target is met
- Generates timestamped output: `{input_name}_COMPRESSED_{timestamp}.pdf`

**Requirements:**

- Ghostscript: `brew install ghostscript`

---

### linkedin-link-extractor

Extract and verify links from LinkedIn posts. Resolves shortened `lnkd.in` URLs to their actual destinations, fetches page titles, and generates one-line summaries.

**How to Use:**

Paste a LinkedIn post with links and ask Claude to extract them:

```
Extract and verify the links from this LinkedIn post:

VIDEOS
1. LLM Introduction: https://lnkd.in/difutThA
2. Building Agents: https://lnkd.in/dbQGbG8K

REPOS
1. GenAI Agents: https://lnkd.in/d8eHCvcQ
```

**What It Does:**

- Extracts all `lnkd.in` shortened URLs
- Resolves them to actual destination URLs
- Fetches page titles and descriptions
- Generates one-line summaries
- Outputs organized markdown table by category

**Output Example:**

| # | Status | Title | Resolved URL | Summary |
|---|--------|-------|--------------|---------|
| 1 | ✅ | Intro to Large Language Models | https://youtube.com/... | 1 hour introduction to LLMs |
| 2 | ✅ | Building Agents with MCP | https://youtube.com/... | Tutorial on creating AI agents |

**Status indicators:**
- ✅ Successfully resolved and verified
- ⚠️ URL resolved but content couldn't be fetched (e.g., PDFs)
- ❌ Failed to resolve

**Requirements:**

- Python 3.12+ with `requests`, `beautifulsoup4`, `certifi`
- `curl` command-line tool

## Installation

1. Clone this repository
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (For PDF compression) Install Ghostscript:
   ```bash
   brew install ghostscript
   ```

## License

This project is provided as-is for educational and productivity purposes. Feel free to use, modify, and share these scripts and skills in your own projects. A link back to this repository is appreciated but not required.
