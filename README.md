# Productivity Hacks

A collection of useful scripts and Claude skills for everyday productivity tasks.

## Scripts

### compress_pdf.py

Compress PDF files to a target size while maintaining the best possible quality.

**Usage:**
```bash
python compress_pdf.py
```

**Requirements:**
- Ghostscript: `brew install ghostscript`
- Python 3.x

**Features:**
- Intelligent quality selection based on target size
- Tries highest quality first, stops when target is met
- Supports custom target sizes (default 1000 KB)
- Shows compression progress and results
- Generates timestamped output files: `{input_name}_COMPRESSED_{timestamp}.pdf`

## Claude Skills

### /compress-pdf

Use this skill in Claude Code to compress PDFs interactively.

**Usage:**
```
/compress-pdf
```

The skill will guide you through selecting a PDF file and target size, then compress it using the optimal quality settings.

## Installation

1. Clone this repository
2. Install Ghostscript:
   ```bash
   brew install ghostscript
   ```
3. (Optional) Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

## License

MIT
