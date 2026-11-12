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

---

### goldfish-review

Fresh-context review of a finished draft before it ships. Two reviewers that have never seen your drafting conversation attack it: a fact-checker that sees only the draft and the raw sources, and a cold reader that sees only the text.

**How to Use:**

```
Fact-check this blog post draft against the sources in ./sources before I publish it
```

```
Red-team my design doc with a cold reader and a fact-checker
```

**What It Does:**

- Builds a clean review folder (draft, extracted image text, source list) with `goldfish_prep.py`
- Produces two ready-to-paste reviewer prompts and explains how to run them in fresh contexts
- Walks through verifying findings, fixing the draft and re-running once
- Includes a checklist of the errors this review keeps finding (a source's claim stated as fact, an inference presented as sourced, a dropped condition)

**Requirements:** Python 3 (standard library only). Idea borrowed from Google's open-source `elephant-goldfish-model`; this is an independent, much smaller implementation.

---

### paper-revision-evidence-hardening

A method for turning reviewer criticism of a paper into verified, honestly scoped evidence.

**How to Use:**

```
Reviewers rejected my paper for weak evaluation. Plan the revision and harden the evidence.
```

**What It Does:**

- Triage rules for reviewer points, checked against code and recorded results before agreeing
- Rules for new files and branches, numbers generated from raw result files, and counts that agree everywhere
- A step-by-step procedure from smoke tests to a fresh-context adversarial review
- A pitfall list from real revision work (tuned-on-test parameters, deterministic reruns, superseded result files)

---

### deep-research-methodology

Deep research for claims that will be cited as evidence: audit source independence, run an adversarial critic pass, verify every citation against its source text.

**How to Use:**

```
Do a deep research pass on whether this claim holds up, with sources that are actually independent
```

**What It Does:**

- Decomposes the question, sweeps sources in parallel with subagents, and clusters derivative copies as one source
- Runs a separate adversarial critic on the draft synthesis
- Checks each citation against the source text and checks papers for retraction

Adapted from the methodology of `jordan-gibbs/hyperresearch` (MIT). No code from that project is used.

---

### jetson-model-ops

Install, benchmark and troubleshoot local LLMs and related services on an NVIDIA Jetson Orin Nano 8 GB.

**How to Use:**

```
Will this 9B GGUF model run on my Jetson Orin Nano? Check the size first and benchmark it.
```

**What It Does:**

- Fit checks against the real file size and the 7.3 GiB unified-memory budget
- A headless load test script that restores the desktop and containers even if the test fails
- A small checkable benchmark (`scripts/ollama_bench.py`) for tokens per second and lowest free memory
- Measured results for several 2B to 9B models, CUDA toolkit install notes, and GPU builds of speech and image runtimes

**Requirements:** a Jetson Orin Nano reachable over SSH, Ollama, optionally Docker.

## Using a Skill

- **Claude Code:** copy a folder from `.claude/skills/` into `~/.claude/skills/` (all projects) or into your project's `.claude/skills/`.
- **Claude.ai:** zip a skill folder and upload it in the skills settings (availability depends on your plan).
- **Other agents:** each skill is a plain `SKILL.md` with optional reference files and scripts, so any agent that reads Agent Skills can use them.

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
