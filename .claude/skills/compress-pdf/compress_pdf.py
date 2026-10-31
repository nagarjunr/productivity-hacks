#!/usr/bin/env python3
"""
PDF Compressor

Compress PDF files to a target size using Ghostscript while maintaining
the best possible quality. Tries compression levels from highest to lowest
quality and stops at the first one that meets the target size.
"""

import subprocess
import os
from datetime import datetime
from pathlib import Path


def compress_pdf(input_file, output_file, target_size_kb):
    """
    Compress a PDF file to meet a target size.
    
    Args:
        input_file: Path to the input PDF
        output_file: Path for the output PDF
        target_size_kb: Target size in kilobytes
        
    Returns:
        bool: True if compression succeeded within target, False otherwise
    """
    # Select quality levels based on target size (highest quality first)
    if target_size_kb <= 200:
        qualities = ["/screen"]
    elif target_size_kb <= 500:
        qualities = ["/ebook", "/screen"]
    elif target_size_kb <= 1000:
        qualities = ["/printer", "/ebook", "/screen"]
    else:
        qualities = ["/prepress", "/printer", "/ebook", "/screen"]

    print(f"Target size: {target_size_kb} KB")
    print(f"Will try quality levels (highest to lowest): {qualities}\n")

    temp_output = output_file + ".tmp"
    size_kb = 0

    for quality in qualities:
        subprocess.run([
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={temp_output}",
            input_file
        ])

        size_kb = os.path.getsize(temp_output) / 1024
        print(f"Quality {quality} -> {size_kb:.2f} KB")

        if size_kb <= target_size_kb:
            os.rename(temp_output, output_file)
            print(f"\n✓ Compression successful! Using {quality} quality")
            print(f"Final size: {size_kb:.2f} KB")
            return True

    if os.path.exists(temp_output):
        os.rename(temp_output, output_file)

    print(f"\n✗ Could not compress below {target_size_kb} KB with available settings.")
    print(f"Final size: {size_kb:.2f} KB (using lowest quality)")
    return False


def main():
    input_pdf = input("Enter input PDF path: ").strip()
    
    if not os.path.exists(input_pdf):
        print(f"Error: File not found: {input_pdf}")
        return

    target_size = input("Enter target size in KB (default 1000): ").strip()
    try:
        target_size_kb = int(target_size) if target_size else 1000
    except ValueError:
        print(f"Error: Invalid size '{target_size}'. Please enter a number.")
        return

    input_path = Path(input_pdf)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf = f"{input_path.stem}_COMPRESSED_{timestamp}.pdf"

    compress_pdf(input_pdf, output_pdf, target_size_kb)
    print(f"\nOutput saved to: {output_pdf}")


if __name__ == "__main__":
    main()
