---
name: compress-pdf
description: Compress PDF files to a target size using Ghostscript while maintaining the best possible quality. Use this skill when the user wants to compress a PDF, reduce PDF file size, make a PDF smaller for email attachments, or shrink a PDF to meet upload size limits.
---

# PDF Compressor

Compress PDF files to meet size requirements (like email attachments or document uploads) while maintaining the best possible quality.

## What This Skill Does

1. Takes an input PDF file path
2. Accepts a target size in KB (default: 1000 KB)
3. Tries compression levels from highest to lowest quality
4. Stops at the first quality level that fits under the target size
5. Outputs the compressed PDF as `{input_name}_COMPRESSED_{timestamp}.pdf`

## How to Use

Run the `compress_pdf.py` script in this skill's directory:

```bash
python .claude/skills/compress-pdf/compress_pdf.py
```

The script will prompt for:
- Input PDF file path
- Target size in KB (press Enter for default 1000 KB)

### Example Session

```
Enter input PDF path: /path/to/large-document.pdf
Enter target size in KB (default 1000): 500

Target size: 500 KB
Will try quality levels (highest to lowest): ['/ebook', '/screen']

Quality /ebook -> 623.45 KB
Quality /screen -> 412.33 KB

✓ Compression successful! Using /screen quality
Final size: 412.33 KB

Output saved to: large-document_COMPRESSED_20260319_150423.pdf
```

## Requirements

- **Ghostscript** must be installed:
  ```bash
  # macOS
  brew install ghostscript
  
  # Ubuntu/Debian
  sudo apt-get install ghostscript
  
  # Windows (via Chocolatey)
  choco install ghostscript
  ```
- Python 3.x

## Quality Levels

The skill intelligently selects which compression levels to try based on your target:

| Target Size | Quality Levels Tried (highest to lowest) |
|-------------|------------------------------------------|
| ≤200 KB | `/screen` only |
| ≤500 KB | `/ebook`, `/screen` |
| ≤1000 KB | `/printer`, `/ebook`, `/screen` |
| >1000 KB | `/prepress`, `/printer`, `/ebook`, `/screen` |

### Quality Level Details

- **`/prepress`** - High quality, suitable for print (300 dpi images)
- **`/printer`** - Good quality for printing (300 dpi images, some downsampling)
- **`/ebook`** - Medium quality for on-screen viewing (150 dpi images)
- **`/screen`** - Low quality, smallest file size (72 dpi images)

## Output

- Compressed file is saved in the current directory
- Filename format: `{original_name}_COMPRESSED_{YYYYMMDD_HHMMSS}.pdf`
- Original file is never modified

## Troubleshooting

### "gs: command not found"
Ghostscript is not installed. Install it using the commands in the Requirements section.

### Output still too large
The PDF may contain content that can't be compressed further (e.g., vector graphics, text-heavy documents). Consider:
- Removing unnecessary pages
- Converting to grayscale if color isn't needed
- Reducing the target size to force lower quality settings
