---
name: linkedin-link-extractor
description: Extract and verify links from LinkedIn posts. Resolves shortened lnkd.in URLs to their actual destinations, fetches page titles, and generates one-line summaries. Use this skill when the user shares LinkedIn content with lnkd.in links, wants to extract real URLs from LinkedIn posts, needs to verify LinkedIn shared links, or asks about resolving/expanding shortened LinkedIn URLs.
---

# LinkedIn Link Extractor

Extract, verify, and summarize links from LinkedIn posts. LinkedIn uses shortened URLs (lnkd.in) that redirect to the actual content. This skill resolves those URLs and provides helpful metadata.

## What This Skill Does

1. **Extracts** all shortened LinkedIn URLs (lnkd.in/xxx) from the input text
2. **Resolves** each URL by following redirects to find the actual destination
3. **Fetches** the page title and content preview
4. **Generates** a one-line summary describing what the linked content is about
5. **Outputs** a clean, organized list with status indicators

## How to Use

Run the `resolve_linkedin_links.py` script in this skill's directory:

```bash
python .claude/skills/linkedin-link-extractor/resolve_linkedin_links.py
```

The script will prompt for input text (paste the LinkedIn post content), then process all links.

### Input Format

Paste text containing LinkedIn shortened URLs. The script handles multiple formats:
- Bare URLs: `https://lnkd.in/xyz123`
- Numbered lists: `1. Resource Name: https://lnkd.in/xyz123`
- Inline text: `Check out this article https://lnkd.in/xyz123`

### Output Format

The script outputs a markdown table with:

| # | Status | Title | Resolved URL | Summary |
|---|--------|-------|--------------|---------|

Status indicators:
- ✅ Successfully resolved and verified
- ⚠️ URL resolved but content couldn't be fetched
- ❌ Failed to resolve

## Example

**Input:**
```
VIDEOS
1. LLM Introduction: https://lnkd.in/difutThA
2. Building Agents: https://lnkd.in/dbQGbG8K
```

**Output:**
```
| # | Status | Title | Resolved URL | Summary |
|---|--------|-------|--------------|---------|
| 1 | ✅ | Intro to Large Language Models | https://youtube.com/... | Comprehensive video introduction to how LLMs work and their applications |
| 2 | ✅ | Building AI Agents with MCP | https://youtube.com/... | Tutorial on creating AI agents using the Model Context Protocol |
```

## Requirements

- Python 3.12+
- `requests` library (for URL resolution)
- `beautifulsoup4` library (for HTML parsing)
- `certifi` library (for SSL certificates)
- `curl` command-line tool (used for reliable URL resolution in corporate environments)

Install dependencies:
```bash
pip install requests beautifulsoup4 certifi
```

## Handling Large Lists

For posts with many links, the script processes them in batches with rate limiting to avoid being blocked. Progress is shown during execution.

## Error Handling

- **Timeout**: Some URLs may take too long to resolve. The script has a 10-second timeout per URL.
- **Blocked**: Some sites block automated requests. These will show as ⚠️ with partial information.
- **Invalid**: Expired or invalid LinkedIn links show as ❌.
- **LinkedIn Interstitial**: Some external links show a LinkedIn warning page instead of redirecting directly. The script automatically extracts the actual destination URL from these pages.
- **PDF Links**: PDF files can be resolved but their content can't be summarized (shows as ⚠️).

## Tips

- The script deduplicates URLs automatically
- Categories from the original post are preserved when possible
- Use `--json` flag to get output as JSON for further processing
