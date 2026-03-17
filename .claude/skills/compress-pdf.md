# compress-pdf

Compress PDF files to a target size using Ghostscript with the best quality possible.

## Usage

```
/compress-pdf
```

## Description

This skill helps you compress PDF files to meet size requirements (like email attachments or document uploads) while maintaining the best possible quality. It:

1. Prompts for the input PDF file path
2. Asks for target size in KB (default 1000 KB)
3. Tries different compression levels from highest to lowest quality
4. Stops at the first quality level that fits under the target size
5. Outputs the compressed PDF as `{input_name}_COMPRESSED_{timestamp}.pdf`

## Requirements

- Ghostscript must be installed: `brew install ghostscript`
- Python 3.x

## Quality Levels

The skill intelligently selects which compression levels to try based on your target:

- **≤200 KB**: `/screen` only
- **≤500 KB**: `/ebook`, `/screen`
- **≤1000 KB**: `/printer`, `/ebook`, `/screen`
- **>1000 KB**: `/prepress`, `/printer`, `/ebook`, `/screen`

Higher quality levels are tried first to give you the best possible output.

## Instructions

Run the compress_pdf.py script in the productivity-hacks directory with user-provided inputs.
