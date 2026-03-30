#!/usr/bin/env python3
"""
PDF Chunking Script

Splits large PDF files into smaller chunks using various strategies.
Prevents Claude Code crashes when processing large PDFs.

Usage:
    python chunk_pdf.py input.pdf --strategy pages --pages 25 --output chunks/
    python chunk_pdf.py input.pdf --strategy size --max-mb 8 --output chunks/
    python chunk_pdf.py input.pdf --strategy overlap --pages 30 --overlap 2 --output chunks/
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Error: pypdf not installed. Install with: pip install pypdf")
    sys.exit(1)


def check_pdf_size(pdf_path):
    """Get PDF size and page count."""
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    try:
        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)
        return size_mb, page_count, None
    except Exception as e:
        return size_mb, 0, str(e)


def chunk_by_pages(input_path, pages_per_chunk, output_dir):
    """Split PDF into fixed page chunks."""
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    os.makedirs(output_dir, exist_ok=True)

    chunk_num = 0
    chunks_created = []

    for i in range(0, total_pages, pages_per_chunk):
        writer = PdfWriter()
        end = min(i + pages_per_chunk, total_pages)

        for page_num in range(i, end):
            writer.add_page(reader.pages[page_num])

        # Create descriptive filename
        input_name = Path(input_path).stem
        output_file = os.path.join(
            output_dir,
            f"{input_name}_chunk_{chunk_num:03d}_pages_{i+1}-{end}.pdf"
        )

        with open(output_file, "wb") as f:
            writer.write(f)

        # Get chunk size
        chunk_size_mb = os.path.getsize(output_file) / (1024 * 1024)

        chunks_created.append({
            'file': output_file,
            'pages': f"{i+1}-{end}",
            'page_count': end - i,
            'size_mb': chunk_size_mb
        })

        print(f"Created: {output_file} ({end - i} pages, {chunk_size_mb:.2f}MB)")
        chunk_num += 1

    return chunks_created


def chunk_by_size(input_path, max_mb, output_dir):
    """Split PDF keeping chunks under size limit."""
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    os.makedirs(output_dir, exist_ok=True)

    writer = PdfWriter()
    chunk_num = 0
    start_page = 0
    chunks_created = []

    for page_num in range(total_pages):
        writer.add_page(reader.pages[page_num])

        # Check current size
        from io import BytesIO
        buffer = BytesIO()
        writer.write(buffer)
        size_mb = buffer.tell() / (1024 * 1024)

        # If size limit reached or last page, save chunk
        if size_mb >= max_mb or page_num == total_pages - 1:
            input_name = Path(input_path).stem
            output_file = os.path.join(
                output_dir,
                f"{input_name}_chunk_{chunk_num:03d}_pages_{start_page+1}-{page_num+1}.pdf"
            )

            with open(output_file, "wb") as f:
                writer.write(f)

            actual_size_mb = os.path.getsize(output_file) / (1024 * 1024)

            chunks_created.append({
                'file': output_file,
                'pages': f"{start_page+1}-{page_num+1}",
                'page_count': page_num - start_page + 1,
                'size_mb': actual_size_mb
            })

            print(f"Created: {output_file} ({page_num - start_page + 1} pages, {actual_size_mb:.2f}MB)")

            chunk_num += 1
            start_page = page_num + 1
            writer = PdfWriter()  # Start new chunk

    return chunks_created


def chunk_with_overlap(input_path, pages_per_chunk, overlap, output_dir):
    """Split PDF with overlapping pages for context preservation."""
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    os.makedirs(output_dir, exist_ok=True)

    chunk_num = 0
    start = 0
    chunks_created = []

    while start < total_pages:
        writer = PdfWriter()
        end = min(start + pages_per_chunk, total_pages)

        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        input_name = Path(input_path).stem
        output_file = os.path.join(
            output_dir,
            f"{input_name}_chunk_{chunk_num:03d}_pages_{start+1}-{end}.pdf"
        )

        with open(output_file, "wb") as f:
            writer.write(f)

        chunk_size_mb = os.path.getsize(output_file) / (1024 * 1024)

        chunks_created.append({
            'file': output_file,
            'pages': f"{start+1}-{end}",
            'page_count': end - start,
            'size_mb': chunk_size_mb,
            'overlap': overlap if chunk_num > 0 else 0
        })

        print(f"Created: {output_file} ({end - start} pages, {chunk_size_mb:.2f}MB, overlap: {overlap if chunk_num > 0 else 0})")

        chunk_num += 1
        start = end - overlap  # Move forward with overlap

    return chunks_created


def generate_summary(input_path, chunks, strategy):
    """Generate summary file documenting the chunking process."""
    size_mb, page_count, error = check_pdf_size(input_path)

    summary = []
    summary.append("=" * 70)
    summary.append("PDF CHUNKING SUMMARY")
    summary.append("=" * 70)
    summary.append(f"\nInput File: {input_path}")
    summary.append(f"Original Size: {size_mb:.2f}MB")
    summary.append(f"Total Pages: {page_count}")
    summary.append(f"Strategy: {strategy}")
    summary.append(f"Chunks Created: {len(chunks)}")
    summary.append("\n" + "-" * 70)
    summary.append("CHUNK DETAILS")
    summary.append("-" * 70)

    for i, chunk in enumerate(chunks, 1):
        summary.append(f"\nChunk {i}:")
        summary.append(f"  File: {chunk['file']}")
        summary.append(f"  Pages: {chunk['pages']} ({chunk['page_count']} pages)")
        summary.append(f"  Size: {chunk['size_mb']:.2f}MB")
        if 'overlap' in chunk:
            summary.append(f"  Overlap: {chunk['overlap']} pages")

    summary.append("\n" + "=" * 70)
    summary.append("RECOMMENDATION")
    summary.append("=" * 70)
    summary.append("\nProcess chunks sequentially in Claude Code:")
    for i, chunk in enumerate(chunks, 1):
        summary.append(f"  {i}. Read {os.path.basename(chunk['file'])}")

    summary_text = "\n".join(summary)
    return summary_text


def main():
    parser = argparse.ArgumentParser(
        description="Split large PDF files into manageable chunks for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split into 25-page chunks
  python chunk_pdf.py document.pdf --strategy pages --pages 25

  # Split keeping chunks under 8MB
  python chunk_pdf.py document.pdf --strategy size --max-mb 8

  # Split with 2-page overlap for context
  python chunk_pdf.py document.pdf --strategy overlap --pages 30 --overlap 2

  # Custom output directory
  python chunk_pdf.py document.pdf --strategy pages --pages 20 --output my_chunks/
        """
    )

    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("--strategy", choices=["pages", "size", "overlap"],
                        default="pages", help="Chunking strategy (default: pages)")
    parser.add_argument("--pages", type=int, default=25,
                        help="Pages per chunk (default: 25)")
    parser.add_argument("--max-mb", type=float, default=8.0,
                        help="Max size per chunk in MB (default: 8.0)")
    parser.add_argument("--overlap", type=int, default=2,
                        help="Pages to overlap between chunks (default: 2)")
    parser.add_argument("--output", default="chunks",
                        help="Output directory (default: chunks)")
    parser.add_argument("--summary", action="store_true",
                        help="Generate summary file")

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    # Check PDF info
    print(f"\nAnalyzing PDF: {args.input}")
    size_mb, page_count, error = check_pdf_size(args.input)

    if error:
        print(f"Error reading PDF: {error}")
        sys.exit(1)

    print(f"Size: {size_mb:.2f}MB")
    print(f"Pages: {page_count}")

    # Warn if file is small enough for direct reading
    if size_mb < 10 and page_count < 50:
        print("\nWARNING: This PDF may be small enough for Claude Code to read directly.")
        print("Consider trying direct reading first before chunking.")
        response = input("Continue with chunking? (y/n): ")
        if response.lower() != 'y':
            print("Chunking cancelled.")
            sys.exit(0)

    # Execute chunking strategy
    print(f"\nChunking strategy: {args.strategy}")
    print("-" * 70)

    chunks = []

    if args.strategy == "pages":
        chunks = chunk_by_pages(args.input, args.pages, args.output)

    elif args.strategy == "size":
        chunks = chunk_by_size(args.input, args.max_mb, args.output)

    elif args.strategy == "overlap":
        chunks = chunk_with_overlap(args.input, args.pages, args.overlap, args.output)

    # Print summary
    print("\n" + "=" * 70)
    print(f"SUCCESS: Created {len(chunks)} chunks in {args.output}/")
    print("=" * 70)

    total_size = sum(c['size_mb'] for c in chunks)
    print(f"\nTotal output size: {total_size:.2f}MB")
    print(f"Average chunk size: {total_size/len(chunks):.2f}MB")
    print(f"Average pages per chunk: {page_count/len(chunks):.1f}")

    # Generate summary file if requested
    if args.summary:
        summary_file = os.path.join(args.output, "chunking_summary.txt")
        summary_text = generate_summary(args.input, chunks, args.strategy)

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_text)

        print(f"\nSummary saved to: {summary_file}")

    print(f"\nNext steps:")
    print(f"1. Read chunks sequentially in Claude Code")
    print(f"2. Process each chunk independently or maintain context across chunks")
    print(f"3. Combine results if needed")


if __name__ == "__main__":
    main()
