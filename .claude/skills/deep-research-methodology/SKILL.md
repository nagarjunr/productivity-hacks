---
name: deep-research-methodology
description: Deep-research method for claims that will be cited as evidence - audit source independence, run an adversarial critic pass, and verify every citation against its source text. Use when the user asks for a "deep research pass", to "verify this claim properly", or to research material that will go into a paper's related-work section, a grant or regulatory filing, a due-diligence memo or a published article. Not for quick fact checks.
---

# Deep Research Methodology

A scaled-down research method built on two principles that change the quality of the output more than anything else: **independence auditing** and **adversarial review before a claim ships**.

Credit: the methodology is adapted from `jordan-gibbs/hyperresearch` (MIT licence), a deep-research harness for Claude Code. None of that repository's code is used here; this skill re-implements only its core method with plain subagents, scaled down from a 16-step pipeline to what is proportionate for occasional, high-stakes research.

## When to Use

- Evidence gathering where a claim needs several genuinely independent sources.
- Literature review or related-work research for a paper.
- Fact-checking a claim that will go into a permanent or public record.
- Any request like "do a deep research pass" or "verify this claim properly".

Do not use it for ordinary lookups. Use normal search and fetch for those.

## The Two Load-Bearing Principles

1. **Independence auditing, not just source counting.** Five reprints of one press release are ONE vote, not five. Before treating several sources as consensus, check whether they are derivative (the same announcement, the same underlying study, one citing another) or genuinely independent investigations.
2. **Adversarial review before shipping a claim.** Do not let your own synthesis go unchallenged. After drafting, run a dedicated adversarial pass whose only job is to attack the claims: what source would overturn this, what is the counter-evidence, is any cited claim actually unsupported by its source when re-checked?

## Pipeline

### 1. Decompose the query
Break the research question into atomic sub-claims before searching. For each, note what kind of evidence would settle it (a measurement, a primary document, an independent replication) and what the comparator baseline is.

### 2. Width sweep (parallel subagents)
Run one independent subagent per sub-question rather than one agent reading everything sequentially. Go to academic APIs first for anything with a research literature (arXiv, Semantic Scholar, OpenAlex, IEEE Xplore) before general web search; web search tends to return derivative commentary, not primary sources. Public endpoints: `https://api.openalex.org/works?search=<query>`, `https://api.semanticscholar.org/graph/v1/paper/search?query=<query>`, `http://export.arxiv.org/api/query?search_query=all:<query>`.

### 3. Independence audit
Before treating multiple hits as corroboration, check whether they trace back to the same press release, paper or announcement. Cluster derivative copies and count each cluster as ONE source. State it explicitly: "3 sources, but 2 are reprints of the same article, so 1 independent source."

### 4. Adversarial critic pass
After drafting the synthesis, dispatch a SEPARATE subagent with an explicitly adversarial brief: "Attack this draft. What is the strongest counter-evidence, which claim is weakest, what source would overturn the conclusion if it existed?" Do not let the context that wrote the synthesis grade it; a fresh context with no attachment to the draft is the point of this step. (See the `goldfish-review` skill for the same pattern applied to finished drafts.)

### 5. Citation verification
For every claim attributed to a source, verify that the source text supports the specific sentence citing it, not merely that the source exists and is on topic. Quote the supporting text. Treat a citation that does not hold up as a hard block: fix or drop the claim before it ships.

### 6. Retraction and currency check
For academic sources, check whether a cited paper has been retracted or superseded (search "<paper title> retraction", or use the retraction flags in OpenAlex or Semantic Scholar) before it goes into any permanent record.

## How to Run It

- **Claude Code**: use subagents (the Task tool) for the width sweep and for the critic. Give each subagent only its sub-question and the instruction to use primary sources.
- **Chat tools without subagents**: run the critic pass in a separate, fresh chat that has only the draft and the source list.
- Keep the source list and every fetched excerpt in a durable file (one markdown file per research task) so the work is reusable. A plain file is enough; no database is needed.

## What This Deliberately Drops from the Source Methodology

- The full 16-step pipeline, four parallel adversarial critics, tool-locked patch-only editing and a SQLite vault: real engineering for a tool that produces dissertation-scale reports on a recurring basis.
- Semantic embedding search, note lifecycle management, an MCP server and a web UI: infrastructure, not method.
- Keep only the two things that change output quality: independence auditing and adversarial review before a claim ships.
