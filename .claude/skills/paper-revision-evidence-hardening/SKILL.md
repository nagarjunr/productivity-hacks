---
name: paper-revision-evidence-hardening
description: Turn reviewer criticism of a rejected or revised paper into verified, honestly scoped evidence. Use when revising a manuscript after peer review, hardening the evaluation behind a technical paper, planning new experiments to answer reviewers, or checking that every claim, number and table in a paper is backed by raw result files.
---

# Paper Revision and Evidence Hardening

A working method for turning reviewer criticism (or the author's own doubts) into verified, honestly scoped evidence. Honesty outranks a stronger-looking result: report what the data show, including defects in your own earlier design.

## What This Skill Does

1. Triages each reviewer point and checks it against the code and the recorded evidence before agreeing or disagreeing.
2. Designs the revised study so it answers the reviewers' exact questions.
3. Rebuilds every number in the paper from raw result files, then has a fresh-context checker read the paper against those files.

## Always-On Rules

- Revisions are NEW files or a new branch. The submitted version, its code and its results stay untouched, so the reviewers' copy matches the archive.
- Before agreeing with any reviewer point, check it against the code and the recorded run evidence. Reviewers are often right about defects the original pass criteria could not see; read the raw record, not the summary.
- Never write a claim the evidence does not carry, and never imply a stronger kind of evidence than you have. If the new evidence comes from simulation or a replay rather than the original setup, say so in the abstract and narrow the claims to what was actually exercised.
- Every number in tables and results prose is generated from raw result files by a builder script with assertions. No hand transcription. A fresh checker reads the paper against the JSON.
- Counts and descriptions must agree across abstract, tables, text and conclusion. Recount rows from the source table before quoting a total.
- Plain wording. Never restate a limit as a strength.

## Procedure

1. **Triage** the reviewer points: error, defect, closable gap, unclosable gap, framing. Verify each against the source. Report the surprises to the authors first.
2. **Design the study** to answer the reviewers' exact questions: trial counts, pass criteria, distributions, and overhead against a stated baseline.
3. **Fix the code defects** the study exposes in a separate variant. Keep the old variant runnable so both are measured by one harness (v1 versus v2).
4. **Smoke-test** every study with tiny counts before the long run. Fix harness bugs there.
5. **Run the full study in the background.** Do only light edits meanwhile, because timing studies are perturbed by compile or CPU bursts.
6. **Rebuild the paper from the JSON.** Compile. Check the page limit, undefined references and overfull boxes. Render figures to an image and inspect them.
7. **Dispatch a fresh-context adversarial reviewer** with the manuscript, the raw results, the code paths and the list of prior findings. Ask for numbers versus JSON, code versus claim, overclaims and counts (see the `goldfish-review` skill for the pattern). Apply every must-fix and re-run the affected studies on the FINAL code, not a mix of commits.
8. **Review again** if the code changed after the first review. Stop when the remaining findings are minor.
9. **Commit** results, harness, builder and paper to a branch. Run a key and secret scan before every push. Verify that the remote commit hash equals the local one.

## Pitfalls

- Score results by the outcome that matters, not by a proxy the system reports about itself (a tool's own success message cannot tell a deliberate refusal from an error). Check an independent record of what actually happened.
- Report results stratified by the variable they depend on (for example input size or load level). A single aggregate rate depends on the distribution you chose.
- Record the raw inputs and traces of every experiment so a real effect can be told apart from a harness artefact such as a scheduler stall.
- When you claim a mechanism for a failure, test the mechanism directly and record the raw observations; do not assert it.
- Repeated runs of a deterministic code path are executions, not independent samples. Say so, and keep statistical language for the stochastic parts.
- A parameter chosen after seeing test data is tuned on the test set. State it and present a trade-off curve.
- If a new run contradicts an earlier one, move the old file to a `superseded/` folder with a README that maps files to tables. Never leave a stale block inside a live results file.
