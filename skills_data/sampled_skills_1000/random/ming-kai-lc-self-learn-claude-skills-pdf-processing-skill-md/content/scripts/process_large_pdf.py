#!/usr/bin/env python3
"""
Large PDF Processing Orchestration Script

Automatically handles large PDFs that exceed Claude Code's reading capabilities.
Provides end-to-end workflow for processing PDFs of any size.

Workflow:
1. Analyze PDF (size, pages, type)
2. Determine optimal processing strategy
3. Execute strategy (chunk, extract text, extract tables)
4. Generate summary report

Usage:
    python process_large_pdf.py input.pdf --strategy auto --output processed/
    python process_large_pdf.py input.pdf --strategy chunk --output processed/
    python process_large_pdf.py input.pdf --strategy text --output processed/
    python process_large_pdf.py input.pdf --strategy tables --output processed/
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime


def check_dependencies():
    """Check if required libraries are installed."""
    available = {}

    try:
        import fitz
        available['pymupdf'] = True
    except ImportError:
        available['pymupdf'] = False

    try:
        from pypdf import PdfReader
        available['pypdf'] = True
    except ImportError:
        available['pypdf'] = False

    try:
        import pdfplumber
        available['pdfplumber'] = True
    except ImportError:
        available['pdfplumber'] = False

    return available


def analyze_pdf(pdf_path):
    """
    Comprehensive PDF analysis.

    Returns dict with:
    - size_mb
    - page_count
    - is_scanned
    - avg_text_per_page
    - has_tables
    - is_safe_for_direct_read
    - recommended_strategy
    """
    analysis = {
        'file': pdf_path,
        'timestamp': datetime.now().isoformat()
    }

    # File size
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    analysis['size_mb'] = round(size_mb, 2)

    try:
        import fitz

        doc = fitz.open(pdf_path)
        page_count = len(doc)
        analysis['page_count'] = page_count

        # Sample first few pages to determine type
        sample_pages = min(3, page_count)
        total_text_length = 0

        for i in range(sample_pages):
            page = doc[i]
            text = page.get_text()
            total_text_length += len(text.strip())

        avg_text = total_text_length / sample_pages
        analysis['avg_text_per_page'] = round(avg_text, 1)

        # Determine if scanned
        is_scanned = avg_text < 50
        analysis['is_scanned'] = is_scanned

        # Check metadata
        metadata = doc.metadata
        analysis['metadata'] = {
            'title': metadata.get('title', 'N/A'),
            'author': metadata.get('author', 'N/A'),
            'creator': metadata.get('creator', 'N/A')
        }

        doc.close()

    except Exception as e:
        analysis['error'] = str(e)
        return analysis

    # Determine if safe for direct reading
    is_safe = size_mb < 10 and page_count < 50
    analysis['is_safe_for_direct_read'] = is_safe

    # Check for tables (quick heuristic)
    has_tables = False
    if not is_scanned:
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                # Check first few pages for tables
                for page in pdf.pages[:3]:
                    if page.extract_tables():
                        has_tables = True
                        break
        except:
            pass

    analysis['likely_has_tables'] = has_tables

    # Recommend strategy
    if is_safe:
        strategy = "direct"
        reason = "PDF is small enough for direct reading in Claude Code"
    elif is_scanned:
        strategy = "text-ocr"
        reason = "PDF appears to be scanned - OCR extraction recommended"
    elif has_tables:
        strategy = "tables"
        reason = "PDF contains tables - specialized table extraction recommended"
    elif size_mb > 15 or page_count > 100:
        strategy = "chunk"
        reason = "PDF is large - chunking recommended to prevent crashes"
    else:
        strategy = "text"
        reason = "Extract text first, then process as text file"

    analysis['recommended_strategy'] = strategy
    analysis['recommendation_reason'] = reason

    return analysis


def execute_chunk_strategy(pdf_path, output_dir, pages_per_chunk=25, overlap=2):
    """Execute chunking strategy."""
    print(f"\nExecuting CHUNK strategy...")
    print(f"  Pages per chunk: {pages_per_chunk}")
    print(f"  Overlap: {overlap} pages")

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return False, "pypdf not installed"

    try:
        chunk_dir = os.path.join(output_dir, "chunks")
        os.makedirs(chunk_dir, exist_ok=True)

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        chunk_num = 0
        start = 0
        chunks_created = []

        while start < total_pages:
            writer = PdfWriter()
            end = min(start + pages_per_chunk, total_pages)

            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])

            input_name = Path(pdf_path).stem
            output_file = os.path.join(
                chunk_dir,
                f"{input_name}_chunk_{chunk_num:03d}_pages_{start+1}-{end}.pdf"
            )

            with open(output_file, "wb") as f:
                writer.write(f)

            chunks_created.append({
                'file': output_file,
                'pages': f"{start+1}-{end}",
                'page_count': end - start
            })

            print(f"  Created: {os.path.basename(output_file)}")

            chunk_num += 1
            start = end - overlap

        return True, {
            'chunks_created': len(chunks_created),
            'chunks': chunks_created,
            'directory': chunk_dir
        }

    except Exception as e:
        return False, str(e)


def execute_text_strategy(pdf_path, output_dir, use_ocr=False):
    """Execute text extraction strategy."""
    print(f"\nExecuting TEXT extraction strategy...")

    if use_ocr:
        print("  Using OCR (this may take a while)...")

    try:
        import fitz
    except ImportError:
        return False, "PyMuPDF not installed"

    try:
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, Path(pdf_path).stem + "_text.txt")

        # Extract text
        if use_ocr:
            try:
                from pdf2image import convert_from_path
                import pytesseract

                images = convert_from_path(pdf_path, dpi=300)
                text = ""

                for i, image in enumerate(images, 1):
                    print(f"  OCR processing page {i}/{len(images)}...")
                    page_text = pytesseract.image_to_string(image)
                    text += f"\n{'='*70}\nPage {i}\n{'='*70}\n\n{page_text}"

            except ImportError:
                return False, "OCR dependencies not installed (pdf2image, pytesseract)"

        else:
            doc = fitz.open(pdf_path)
            text = ""

            for page_num, page in enumerate(doc, 1):
                print(f"  Extracting page {page_num}/{len(doc)}...")
                page_text = page.get_text()
                text += f"\n{'='*70}\nPage {page_num}\n{'='*70}\n\n{page_text}"

            doc.close()

        # Save text
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        text_size_kb = len(text.encode('utf-8')) / 1024
        word_count = len(text.split())

        return True, {
            'output_file': output_file,
            'size_kb': round(text_size_kb, 2),
            'word_count': word_count
        }

    except Exception as e:
        return False, str(e)


def execute_tables_strategy(pdf_path, output_dir, output_format='csv'):
    """Execute table extraction strategy."""
    print(f"\nExecuting TABLE extraction strategy...")
    print(f"  Output format: {output_format}")

    try:
        import pdfplumber
    except ImportError:
        return False, "pdfplumber not installed"

    try:
        tables_dir = os.path.join(output_dir, "tables")
        os.makedirs(tables_dir, exist_ok=True)

        tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"  Processing page {page_num}/{len(pdf.pages)}...")

                page_tables = page.extract_tables()

                if page_tables:
                    print(f"    Found {len(page_tables)} table(s)")

                for table_num, table in enumerate(page_tables, 1):
                    if table:
                        tables.append({
                            'page': page_num,
                            'table_num': table_num,
                            'data': table
                        })

        if not tables:
            return True, {'tables_found': 0, 'message': 'No tables found'}

        # Save tables
        saved_files = []

        if output_format == 'csv':
            import csv

            for table in tables:
                filename = f"{Path(pdf_path).stem}_page{table['page']}_table{table['table_num']}.csv"
                filepath = os.path.join(tables_dir, filename)

                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(table['data'])

                saved_files.append(filepath)

        elif output_format == 'json':
            output_file = os.path.join(tables_dir, f"{Path(pdf_path).stem}_tables.json")

            output_data = {'tables': []}
            for table in tables:
                headers = table['data'][0] if table['data'] else []
                rows = table['data'][1:] if len(table['data']) > 1 else []

                table_records = []
                for row in rows:
                    record = {str(headers[i] if i < len(headers) else f"Col_{i}"): value
                              for i, value in enumerate(row)}
                    table_records.append(record)

                output_data['tables'].append({
                    'page': table['page'],
                    'table_num': table['table_num'],
                    'data': table_records
                })

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            saved_files.append(output_file)

        return True, {
            'tables_found': len(tables),
            'files_created': len(saved_files),
            'directory': tables_dir
        }

    except Exception as e:
        return False, str(e)


def generate_report(pdf_path, analysis, strategy_used, result, output_dir):
    """Generate comprehensive processing report."""
    report = []

    report.append("=" * 80)
    report.append("PDF PROCESSING REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nInput File: {pdf_path}")

    report.append("\n" + "-" * 80)
    report.append("PDF ANALYSIS")
    report.append("-" * 80)
    report.append(f"Size: {analysis['size_mb']}MB")
    report.append(f"Pages: {analysis['page_count']}")
    report.append(f"Type: {'Scanned (image-based)' if analysis.get('is_scanned') else 'Text-based'}")
    report.append(f"Average text per page: {analysis.get('avg_text_per_page', 'N/A')} characters")
    report.append(f"Likely has tables: {'Yes' if analysis.get('likely_has_tables') else 'No'}")
    report.append(f"Safe for direct read: {'Yes' if analysis.get('is_safe_for_direct_read') else 'No'}")

    if 'metadata' in analysis:
        report.append("\nMetadata:")
        for key, value in analysis['metadata'].items():
            report.append(f"  {key.capitalize()}: {value}")

    report.append("\n" + "-" * 80)
    report.append("PROCESSING STRATEGY")
    report.append("-" * 80)
    report.append(f"Recommended: {analysis.get('recommended_strategy', 'N/A')}")
    report.append(f"Reason: {analysis.get('recommendation_reason', 'N/A')}")
    report.append(f"Strategy used: {strategy_used}")

    report.append("\n" + "-" * 80)
    report.append("RESULTS")
    report.append("-" * 80)

    if strategy_used == "chunk":
        report.append(f"Chunks created: {result['chunks_created']}")
        report.append(f"Output directory: {result['directory']}")
        report.append("\nChunks:")
        for chunk in result['chunks']:
            report.append(f"  - {os.path.basename(chunk['file'])} (pages {chunk['pages']})")

    elif strategy_used == "text" or strategy_used == "text-ocr":
        report.append(f"Text file: {result['output_file']}")
        report.append(f"Size: {result['size_kb']}KB")
        report.append(f"Word count: {result['word_count']:,}")

    elif strategy_used == "tables":
        report.append(f"Tables found: {result['tables_found']}")
        if result['tables_found'] > 0:
            report.append(f"Files created: {result['files_created']}")
            report.append(f"Output directory: {result['directory']}")

    report.append("\n" + "-" * 80)
    report.append("NEXT STEPS FOR CLAUDE CODE")
    report.append("-" * 80)

    if strategy_used == "chunk":
        report.append("\n1. Process chunks sequentially:")
        for i, chunk in enumerate(result['chunks'], 1):
            report.append(f"   {i}. Read {os.path.basename(chunk['file'])}")
        report.append("\n2. Combine insights from all chunks")

    elif strategy_used == "text" or strategy_used == "text-ocr":
        report.append(f"\n1. Read {os.path.basename(result['output_file'])} in Claude Code")
        report.append("2. This is much safer than reading the original PDF")
        report.append("3. Process the text as needed")

    elif strategy_used == "tables":
        if result['tables_found'] > 0:
            report.append(f"\n1. Review extracted tables in {result['directory']}")
            report.append("2. Read individual CSV/JSON files in Claude Code")
            report.append("3. Analyze table data as needed")
        else:
            report.append("\nNo tables found in the PDF")

    report.append("\n" + "=" * 80)

    report_text = "\n".join(report)

    # Save report
    report_file = os.path.join(output_dir, "processing_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text, report_file


def main():
    parser = argparse.ArgumentParser(
        description="Automatically process large PDFs with optimal strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Processing Strategies:
  auto      - Automatically select best strategy based on PDF analysis (default)
  chunk     - Split PDF into smaller chunks for sequential processing
  text      - Extract all text to a single text file
  text-ocr  - Extract text using OCR (for scanned PDFs)
  tables    - Extract all tables to CSV/JSON format
  direct    - Recommend direct reading in Claude Code (if safe)

Examples:
  # Automatic strategy selection
  python process_large_pdf.py large_doc.pdf --strategy auto --output processed/

  # Force chunking
  python process_large_pdf.py huge_doc.pdf --strategy chunk --output processed/

  # Extract text only
  python process_large_pdf.py report.pdf --strategy text --output processed/

  # Extract tables
  python process_large_pdf.py data.pdf --strategy tables --output processed/
        """
    )

    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("--strategy", choices=["auto", "chunk", "text", "text-ocr", "tables", "direct"],
                        default="auto", help="Processing strategy (default: auto)")
    parser.add_argument("--output", "-o", required=True,
                        help="Output directory for processed files")
    parser.add_argument("--pages-per-chunk", type=int, default=25,
                        help="Pages per chunk (for chunk strategy, default: 25)")
    parser.add_argument("--overlap", type=int, default=2,
                        help="Page overlap for chunks (default: 2)")
    parser.add_argument("--table-format", choices=["csv", "json"],
                        default="csv", help="Table output format (default: csv)")

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    # Check dependencies
    deps = check_dependencies()
    print("Checking dependencies...")
    for dep, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")

    if not any(deps.values()):
        print("\nError: No PDF processing libraries installed")
        print("Install with: pip install pypdf PyMuPDF pdfplumber")
        sys.exit(1)

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Analyze PDF
    print(f"\n{'='*80}")
    print("ANALYZING PDF")
    print('='*80)

    analysis = analyze_pdf(args.input)

    if 'error' in analysis:
        print(f"Error analyzing PDF: {analysis['error']}")
        sys.exit(1)

    print(f"\nFile: {args.input}")
    print(f"Size: {analysis['size_mb']}MB")
    print(f"Pages: {analysis['page_count']}")
    print(f"Type: {'Scanned' if analysis.get('is_scanned') else 'Text-based'}")
    print(f"\nRecommended strategy: {analysis['recommended_strategy']}")
    print(f"Reason: {analysis['recommendation_reason']}")

    # Determine strategy
    if args.strategy == "auto":
        strategy = analysis['recommended_strategy']
        print(f"\nUsing recommended strategy: {strategy}")
    else:
        strategy = args.strategy
        print(f"\nUsing specified strategy: {strategy}")

    # Execute strategy
    print(f"\n{'='*80}")
    print("PROCESSING")
    print('='*80)

    success = False
    result = None

    if strategy == "direct":
        print("\nThis PDF appears safe for direct reading in Claude Code.")
        print("No processing needed - just use the Read tool on the original PDF.")
        sys.exit(0)

    elif strategy == "chunk":
        success, result = execute_chunk_strategy(
            args.input, args.output,
            pages_per_chunk=args.pages_per_chunk,
            overlap=args.overlap
        )

    elif strategy == "text":
        success, result = execute_text_strategy(args.input, args.output, use_ocr=False)

    elif strategy == "text-ocr":
        success, result = execute_text_strategy(args.input, args.output, use_ocr=True)

    elif strategy == "tables":
        success, result = execute_tables_strategy(
            args.input, args.output,
            output_format=args.table_format
        )

    # Check result
    if not success:
        print(f"\n✗ Processing failed: {result}")
        sys.exit(1)

    print(f"\n✓ Processing completed successfully")

    # Generate report
    print(f"\n{'='*80}")
    print("GENERATING REPORT")
    print('='*80)

    report_text, report_file = generate_report(
        args.input, analysis, strategy, result, args.output
    )

    print(report_text)

    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
