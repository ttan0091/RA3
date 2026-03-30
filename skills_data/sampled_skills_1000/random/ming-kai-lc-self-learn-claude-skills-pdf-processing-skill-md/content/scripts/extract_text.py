#!/usr/bin/env python3
"""
PDF Text Extraction Script

Extracts text from PDF files with automatic detection of text-based vs scanned PDFs.
Supports multiple extraction methods with fallback strategies.

Usage:
    python extract_text.py input.pdf --output text.txt
    python extract_text.py input.pdf --method pymupdf --output text.txt
    python extract_text.py scanned.pdf --method ocr --output text.txt
    python extract_text.py input.pdf --method auto --output text.txt
"""

import argparse
import os
import sys
from pathlib import Path


def check_dependencies():
    """Check if required libraries are installed."""
    missing = []

    try:
        import fitz  # PyMuPDF
    except ImportError:
        missing.append("PyMuPDF")

    try:
        import pdfplumber
    except ImportError:
        missing.append("pdfplumber")

    return missing


def extract_with_pymupdf(pdf_path):
    """Extract text using PyMuPDF (fastest method)."""
    try:
        import fitz
    except ImportError:
        return None, "PyMuPDF not installed"

    try:
        doc = fitz.open(pdf_path)
        text = ""

        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            text += f"\n{'='*70}\nPage {page_num}\n{'='*70}\n\n{page_text}"

        doc.close()
        return text, None

    except Exception as e:
        return None, str(e)


def extract_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber (more reliable for complex layouts)."""
    try:
        import pdfplumber
    except ImportError:
        return None, "pdfplumber not installed"

    try:
        text = ""

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                text += f"\n{'='*70}\nPage {page_num}\n{'='*70}\n\n{page_text}"

        return text, None

    except Exception as e:
        return None, str(e)


def extract_with_ocr(pdf_path, dpi=300, preprocess=False):
    """Extract text using OCR (for scanned PDFs)."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as e:
        return None, f"OCR dependencies not installed: {e}"

    try:
        # Convert PDF to images
        print(f"Converting PDF to images (DPI: {dpi})...")
        images = convert_from_path(pdf_path, dpi=dpi)

        text = ""

        for i, image in enumerate(images, 1):
            print(f"Processing page {i}/{len(images)} with OCR...")

            if preprocess:
                # Apply preprocessing for better accuracy
                import cv2
                import numpy as np

                img_array = np.array(image)
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

                # Convert back to PIL Image
                from PIL import Image
                image = Image.fromarray(denoised)

            # OCR
            page_text = pytesseract.image_to_string(image)
            text += f"\n{'='*70}\nPage {i} (OCR)\n{'='*70}\n\n{page_text}"

        return text, None

    except Exception as e:
        return None, str(e)


def detect_scanned_pdf(pdf_path, sample_pages=3, threshold=50):
    """
    Detect if PDF is scanned (requires OCR) or text-based.

    Returns: (is_scanned, avg_text_length_per_page)
    """
    try:
        import fitz
    except ImportError:
        return None, "PyMuPDF not installed for detection"

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_to_check = min(sample_pages, total_pages)

        total_text_length = 0

        for page_num in range(pages_to_check):
            page = doc[page_num]
            text = page.get_text()
            total_text_length += len(text.strip())

        doc.close()

        avg_text_length = total_text_length / pages_to_check

        # If average text length is below threshold, likely scanned
        is_scanned = avg_text_length < threshold

        return is_scanned, avg_text_length

    except Exception as e:
        return None, str(e)


def extract_auto(pdf_path):
    """
    Automatically detect best extraction method and apply it.

    Tries:
    1. Detection: Is it scanned or text-based?
    2. For text-based: Try PyMuPDF -> pdfplumber
    3. For scanned: Use OCR
    """
    print("Auto-detecting PDF type...")

    is_scanned, info = detect_scanned_pdf(pdf_path)

    if is_scanned is None:
        print(f"Detection failed: {info}")
        print("Falling back to PyMuPDF...")
        return extract_with_pymupdf(pdf_path)

    if is_scanned:
        print(f"Detected: Scanned PDF (avg text per page: {info:.1f} chars)")
        print("Using OCR extraction...")
        return extract_with_ocr(pdf_path)
    else:
        print(f"Detected: Text-based PDF (avg text per page: {info:.1f} chars)")
        print("Using PyMuPDF extraction...")

        text, error = extract_with_pymupdf(pdf_path)

        if text and text.strip():
            return text, None
        else:
            print("PyMuPDF failed or returned empty. Trying pdfplumber...")
            return extract_with_pdfplumber(pdf_path)


def extract_with_fallback(pdf_path):
    """
    Try multiple extraction methods with fallback.

    Order: PyMuPDF -> pdfplumber -> OCR
    """
    # Try 1: PyMuPDF (fastest)
    print("Trying PyMuPDF...")
    text, error = extract_with_pymupdf(pdf_path)

    if text and text.strip():
        print("Success with PyMuPDF")
        return text, "pymupdf"

    if error:
        print(f"PyMuPDF failed: {error}")

    # Try 2: pdfplumber (more reliable)
    print("Trying pdfplumber...")
    text, error = extract_with_pdfplumber(pdf_path)

    if text and text.strip():
        print("Success with pdfplumber")
        return text, "pdfplumber"

    if error:
        print(f"pdfplumber failed: {error}")

    # Try 3: OCR (last resort)
    print("Trying OCR (this may take a while)...")
    text, error = extract_with_ocr(pdf_path)

    if text:
        print("Success with OCR")
        return text, "ocr"

    if error:
        print(f"OCR failed: {error}")

    return None, "all_methods_failed"


def get_pdf_info(pdf_path):
    """Get basic PDF information."""
    try:
        import fitz

        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)

        doc = fitz.open(pdf_path)
        page_count = len(doc)

        # Get metadata
        metadata = doc.metadata

        doc.close()

        return {
            'size_mb': size_mb,
            'page_count': page_count,
            'title': metadata.get('title', 'N/A'),
            'author': metadata.get('author', 'N/A'),
            'creation_date': metadata.get('creationDate', 'N/A')
        }

    except Exception as e:
        return {'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files with automatic format detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Extraction Methods:
  auto      - Automatically detect and use best method (default)
  pymupdf   - Fast extraction using PyMuPDF (best for text-based PDFs)
  pdfplumber- Reliable extraction with complex layout support
  ocr       - OCR extraction for scanned PDFs (slow but handles image-based PDFs)
  fallback  - Try all methods until one succeeds

Examples:
  # Auto-detect and extract
  python extract_text.py document.pdf --output text.txt

  # Force OCR for scanned document
  python extract_text.py scanned.pdf --method ocr --output text.txt

  # Use specific method
  python extract_text.py document.pdf --method pymupdf --output text.txt

  # Try all methods with fallback
  python extract_text.py problematic.pdf --method fallback --output text.txt
        """
    )

    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("--output", "-o", help="Output text file path (default: input_name.txt)")
    parser.add_argument("--method", choices=["auto", "pymupdf", "pdfplumber", "ocr", "fallback"],
                        default="auto", help="Extraction method (default: auto)")
    parser.add_argument("--dpi", type=int, default=300,
                        help="DPI for OCR (default: 300, lower=faster but less accurate)")
    parser.add_argument("--preprocess", action="store_true",
                        help="Apply image preprocessing for better OCR accuracy (slower)")
    parser.add_argument("--info", action="store_true",
                        help="Show PDF information and exit")

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print("Warning: Missing dependencies:", ", ".join(missing_deps))
        print("Install with: pip install " + " ".join(missing_deps))

    # Show PDF info if requested
    print(f"\nPDF: {args.input}")
    info = get_pdf_info(args.input)

    if 'error' in info:
        print(f"Error getting PDF info: {info['error']}")
    else:
        print(f"Size: {info['size_mb']:.2f}MB")
        print(f"Pages: {info['page_count']}")
        print(f"Title: {info['title']}")
        print(f"Author: {info['author']}")

    if args.info:
        sys.exit(0)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = Path(args.input).stem + ".txt"

    print(f"\nExtraction method: {args.method}")
    print("-" * 70)

    # Extract text based on method
    text = None
    method_used = args.method

    if args.method == "auto":
        text, error = extract_auto(args.input)
        if error:
            print(f"Error: {error}")
            sys.exit(1)

    elif args.method == "pymupdf":
        text, error = extract_with_pymupdf(args.input)
        if error:
            print(f"Error: {error}")
            sys.exit(1)

    elif args.method == "pdfplumber":
        text, error = extract_with_pdfplumber(args.input)
        if error:
            print(f"Error: {error}")
            sys.exit(1)

    elif args.method == "ocr":
        text, error = extract_with_ocr(args.input, dpi=args.dpi, preprocess=args.preprocess)
        if error:
            print(f"Error: {error}")
            sys.exit(1)

    elif args.method == "fallback":
        text, method_used = extract_with_fallback(args.input)
        if text is None:
            print("Error: All extraction methods failed")
            sys.exit(1)

    # Save extracted text
    if text:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        text_size_kb = len(text.encode('utf-8')) / 1024
        word_count = len(text.split())

        print("\n" + "=" * 70)
        print("SUCCESS: Text extracted")
        print("=" * 70)
        print(f"\nOutput file: {output_path}")
        print(f"Text size: {text_size_kb:.2f}KB")
        print(f"Word count: {word_count:,}")
        print(f"Method used: {method_used}")

        print(f"\nNext steps:")
        print(f"1. Read {output_path} in Claude Code (much safer than reading PDF)")
        print(f"2. Process text as needed")
    else:
        print("\nError: No text extracted")
        sys.exit(1)


if __name__ == "__main__":
    main()
