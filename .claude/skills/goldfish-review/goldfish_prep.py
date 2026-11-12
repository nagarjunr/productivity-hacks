#!/usr/bin/env python3
"""Prepare a goldfish review: a clean folder plus two reviewer prompts.

Usage:
  python goldfish_prep.py --draft draft.txt --sources ./sources [--extra image_text.txt]
                          [--audience "senior engineers and managers"] [--out ./goldfish]

Writes into --out:
  draft.txt, extra.txt           copies of the only texts the reviewers may see
  fact_checker_prompt.md         prompt for the reviewer that reads draft + raw sources
  cold_reader_prompt.md          prompt for the reviewer that sees the text only (inline)
Standard library only. Nothing is sent anywhere; you dispatch the prompts to fresh reviewer contexts.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT_EXT = {".txt", ".md", ".html", ".htm", ".json", ".csv", ".xml", ".rst", ".tex"}


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def fill(template, mapping):
    for key, value in mapping.items():
        template = template.replace("<<" + key + ">>", value)
    return template


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draft", required=True, help="the text to review")
    ap.add_argument("--sources", required=True, help="directory of raw source files (text)")
    ap.add_argument("--extra", help="visible text of an accompanying image or slides")
    ap.add_argument("--audience", default="experienced professionals in the field the text is about")
    ap.add_argument("--out", default="./goldfish")
    args = ap.parse_args()

    if not os.path.isfile(args.draft):
        sys.exit("draft not found: " + args.draft)
    if not os.path.isdir(args.sources):
        sys.exit("sources directory not found: " + args.sources)

    os.makedirs(args.out, exist_ok=True)
    out = os.path.abspath(args.out)
    draft_text = read(args.draft)
    extra_text = read(args.extra) if args.extra else ""
    with open(os.path.join(out, "draft.txt"), "w", encoding="utf-8") as f:
        f.write(draft_text)
    with open(os.path.join(out, "extra.txt"), "w", encoding="utf-8") as f:
        f.write(extra_text)

    src_dir = os.path.abspath(args.sources)
    sources = []
    for name in sorted(os.listdir(src_dir)):
        p = os.path.join(src_dir, name)
        if os.path.isfile(p) and os.path.splitext(name)[1].lower() in TEXT_EXT:
            sources.append("- %s (%d characters)" % (name, os.path.getsize(p)))
    if not sources:
        sys.exit("no text source files found in " + src_dir + " (convert PDFs to .txt first)")

    base = os.path.join(HERE, "prompts")
    fact = fill(read(os.path.join(base, "fact-checker.md")), {
        "DRAFT_PATH": os.path.join(out, "draft.txt"),
        "EXTRA_PATH": os.path.join(out, "extra.txt"),
        "SOURCES_DIR": src_dir,
        "SOURCE_LIST": "\n".join(sources),
    })
    cold = fill(read(os.path.join(base, "cold-reader.md")), {
        "AUDIENCE": args.audience,
        "DRAFT_TEXT": draft_text.strip(),
        "EXTRA_TEXT": extra_text.strip() or "(none)",
    })
    with open(os.path.join(out, "fact_checker_prompt.md"), "w", encoding="utf-8") as f:
        f.write(fact)
    with open(os.path.join(out, "cold_reader_prompt.md"), "w", encoding="utf-8") as f:
        f.write(cold)

    print("Review folder: " + out)
    print("  draft: %d words | image text: %d words | sources: %d files" % (len(draft_text.split()), len(extra_text.split()), len(sources)))
    print("Next: start two fresh reviewer contexts in parallel.")
    print("  1) fact checker  <- " + os.path.join(out, "fact_checker_prompt.md") + "  (needs file read + grep)")
    print("  2) cold reader   <- " + os.path.join(out, "cold_reader_prompt.md") + "  (no tools)")
    print("Do not give either reviewer your notes, outline or earlier discussion.")


if __name__ == "__main__":
    main()
