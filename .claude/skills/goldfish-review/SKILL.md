---
name: goldfish-review
description: Fresh-context review of a finished written draft before it ships (social post, spec, design doc, README, paper section). Runs two reviewers that have never seen the drafting conversation - a fact-checker that sees only the draft and the raw sources, and a cold reader that sees only the text. Use when the user asks to fact-check, red-team, stress-test or "cold read" a draft, or before publishing anything that makes claims about someone else's work, a standard, a regulation or a benchmark.
---

# Goldfish Review

"Design with an elephant, review with a goldfish." The agent that drafted the text (the elephant) remembers everything: the notes, the earlier discussion, what each source "really meant". That memory hides mistakes, because the author already knows what the sentence is supposed to say. A goldfish reviewer remembers none of it and sees only what a real reader, or the original sources, would show.

The idea is borrowed from Google's open-source `elephant-goldfish-model` (Apache-2.0), a design-spec workflow. This skill is an independent, much smaller implementation of the review idea for finished drafts. Nothing from that repository is copied.

## What This Skill Does

1. Builds a clean review folder containing only what a reviewer may see.
2. Produces two ready-to-paste reviewer prompts:
   - **Fact-checker**: reads the draft and the raw source files, quotes the supporting passage for every claim, and flags anything the sources do not carry.
   - **Cold reader**: reads only the text, as a skeptical senior colleague would, and reports unstated assumptions, contradictions, overclaims and whether the takeaway follows.
3. Guides you through verifying the findings, fixing the draft, and re-running once.

## When to Use

- An article, blog post, spec or README that makes factual claims (numbers, dates, who did what, what a standard says, what a benchmark measured).
- A draft built on someone else's work: a regulation, a vendor announcement, a paper.
- A text that has an accompanying image or slide deck: the visible text of the image is reviewed too.

Do not use it for brainstorming, for style polishing (length, voice and lint checks stay with your normal tools), or for deciding whether a topic is worth writing about.

## The Rule That Makes It Work: Input Hygiene

Reviewers get: the draft text, the extracted visible text of any accompanying image, and the raw source files.

Reviewers must NOT get: your outline, research notes, a summary of the sources, the brief you wrote from them, or any earlier discussion. Those are the elephant's memory. A reviewer that reads your notes inherits your blind spots and reports that everything checks out.

Extract the image text from the file that actually ships (for HTML posters or slides, strip the tags from the final HTML). A text dump saved earlier can belong to an older variant.

## Procedure

1. **Prepare.** Run the helper from this skill's own folder, or give its full path (Python 3, standard library only; use `python3` on macOS and Linux):

   ```
   python3 ~/.claude/skills/goldfish-review/goldfish_prep.py --draft draft.txt --sources ./sources --extra image_text.txt --out ./goldfish
   ```

   It copies the draft and image text into `./goldfish/`, lists the source files, and writes `fact_checker_prompt.md` and `cold_reader_prompt.md`. If your tool cannot run code (for example a plain chat), skip the helper: copy `prompts/fact-checker.md` and `prompts/cold-reader.md`, fill the `<<...>>` placeholders by hand, and paste the source texts into the fact-checker chat.

2. **Dispatch both reviewers in fresh contexts, in parallel.**
   - Claude Code: start two subagents (the Task tool). Give each the matching prompt file as its task. The fact-checker needs file reading and shell search (`grep -n`); the cold reader needs no tools.
   - Claude.ai or any chat tool: open two new chats and paste one prompt into each. Do not continue in the drafting conversation.

3. **Verify every major finding yourself** against the source before acting. Reviewers sometimes misread a paraphrase or overstate a quote.

4. **Fix what is supported.** Removing or attributing a claim is always safe. Adding a new fact means going back to the source. Then re-run your normal checks (length, style, lint) and run the review once more on the fixed text. Stop after two rounds and list what remains.

5. **Report** what was found, what was fixed, what was left and why. If a finding touches the author's own opinion or conclusion line, propose the change and say so; never rewrite it silently.

## Reviewer Prompts

- `prompts/fact-checker.md`: template for the fact-checker (placeholders are filled in by the helper).
- `prompts/cold-reader.md`: template for the cold reader.

## Recurring Findings

`references/recurring-findings.md` lists the classes of error this review keeps finding (a source's claim stated as fact, an inference presented as sourced, text and image disagreeing, a dropped condition, a falsifier that tests a position nobody holds). Read it while drafting to avoid them in the first place.

## Limits

- It does not replace a human read of the final text.
- It is only as good as the sources you give it. Claims of absence ("the notice does not mention X") need a search of the source, which the fact-checker is told to do.
- A reviewer verdict is advice. If a finding conflicts with a constraint you set (for example a "do not claim" list), the constraint wins.
- Cost: two short reviewer runs, typically well under a minute.
