import subprocess
import os
from datetime import datetime
from pathlib import Path


def compress_pdf(input_file, output_file, target_size_kb):
    # Select quality levels based on target size (highest quality first)
    if target_size_kb <= 200:
        # Very small - try only screen
        qualities = ["/screen"]
    elif target_size_kb <= 500:
        # Small - try ebook and screen
        qualities = ["/ebook", "/screen"]
    elif target_size_kb <= 1000:
        # Medium - try printer, ebook, and screen
        qualities = ["/printer", "/ebook", "/screen"]
    else:
        # Large - try all quality levels from highest to lowest
        qualities = ["/prepress", "/printer", "/ebook", "/screen"]

    print(f"Target size: {target_size_kb} KB")
    print(f"Will try quality levels (highest to lowest): {qualities}\n")

    temp_output = output_file + ".tmp"

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
            # This quality fits! Use it and we're done
            os.rename(temp_output, output_file)
            print(f"\n✓ Compression successful! Using {quality} quality")
            print(f"Final size: {size_kb:.2f} KB")
            return True

    # None of the qualities fit under target
    if os.path.exists(temp_output):
        os.rename(temp_output, output_file)

    print(f"\n✗ Could not compress below {target_size_kb} KB with available settings.")
    print(f"Final size: {size_kb:.2f} KB (using lowest quality)")
    return False


if __name__ == "__main__":
    input_pdf = input("Enter input PDF path: ")

    target_size = input("Enter target size in KB (default 1000): ").strip()
    target_size_kb = int(target_size) if target_size else 1000

    # Generate output filename: inputname_COMPRESSED_timestamp.pdf
    input_path = Path(input_pdf)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf = f"{input_path.stem}_COMPRESSED_{timestamp}.pdf"

    compress_pdf(input_pdf, output_pdf, target_size_kb)
    print(f"\nOutput saved to: {output_pdf}")
