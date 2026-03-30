#!/usr/bin/env python3
"""
PDF Table Extraction Script

Extracts tables from PDF files and saves them in various formats (CSV, JSON, Excel).
Uses pdfplumber for high-accuracy table detection.

Usage:
    python extract_tables.py input.pdf --output tables/
    python extract_tables.py input.pdf --format csv --output tables/
    python extract_tables.py input.pdf --format excel --output report_tables.xlsx
    python extract_tables.py input.pdf --pages 1,3,5 --output selected_tables/
"""

import argparse
import os
import sys
import json
from pathlib import Path


def check_dependencies():
    """Check if required libraries are installed."""
    missing = []

    try:
        import pdfplumber
    except ImportError:
        missing.append("pdfplumber")

    return missing


def extract_tables(pdf_path, pages=None, table_settings=None):
    """
    Extract all tables from PDF.

    Args:
        pdf_path: Path to PDF file
        pages: List of page numbers to process (1-indexed), or None for all pages
        table_settings: Custom table detection settings

    Returns:
        List of table dictionaries with metadata
    """
    try:
        import pdfplumber
    except ImportError:
        return None, "pdfplumber not installed"

    # Default table settings
    if table_settings is None:
        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "edge_min_length": 3,
            "intersection_tolerance": 3,
        }

    try:
        tables = []

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            # Determine which pages to process
            if pages:
                pages_to_process = [p - 1 for p in pages if 0 < p <= total_pages]
            else:
                pages_to_process = range(total_pages)

            for page_idx in pages_to_process:
                page = pdf.pages[page_idx]
                page_num = page_idx + 1

                print(f"Processing page {page_num}...")

                # Extract tables
                page_tables = page.extract_tables(table_settings)

                if page_tables:
                    print(f"  Found {len(page_tables)} table(s) on page {page_num}")

                for table_num, table in enumerate(page_tables, 1):
                    if table and len(table) > 0:
                        # Get table bounding box if possible
                        bbox = None
                        try:
                            table_objects = page.find_tables(table_settings)
                            if table_num <= len(table_objects):
                                bbox = table_objects[table_num - 1].bbox
                        except:
                            pass

                        tables.append({
                            'page': page_num,
                            'table_num': table_num,
                            'data': table,
                            'row_count': len(table),
                            'col_count': len(table[0]) if table else 0,
                            'bbox': bbox
                        })

        if not tables:
            return [], "No tables found in PDF"

        return tables, None

    except Exception as e:
        return None, str(e)


def save_tables_csv(tables, output_dir, base_name):
    """Save each table as a separate CSV file."""
    import csv

    os.makedirs(output_dir, exist_ok=True)

    saved_files = []

    for table in tables:
        filename = f"{base_name}_page{table['page']}_table{table['table_num']}.csv"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(table['data'])

        saved_files.append(filepath)
        print(f"  Saved: {filepath}")

    return saved_files


def save_tables_json(tables, output_path, base_name):
    """Save all tables to a single JSON file."""
    # Convert tables to JSON-serializable format
    output_data = {
        'source': base_name,
        'table_count': len(tables),
        'tables': []
    }

    for table in tables:
        # Try to use first row as headers
        headers = table['data'][0] if table['data'] else []
        rows = table['data'][1:] if len(table['data']) > 1 else []

        # Convert to list of dictionaries
        table_records = []
        for row in rows:
            record = {}
            for i, value in enumerate(row):
                header = headers[i] if i < len(headers) else f"Column_{i}"
                record[str(header).strip() if header else f"Column_{i}"] = value
            table_records.append(record)

        output_data['tables'].append({
            'page': table['page'],
            'table_num': table['table_num'],
            'row_count': table['row_count'],
            'col_count': table['col_count'],
            'bbox': table['bbox'],
            'data': table_records
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {output_path}")
    return [output_path]


def save_tables_excel(tables, output_path, base_name):
    """Save all tables to a single Excel file with multiple sheets."""
    try:
        import pandas as pd
    except ImportError:
        return None, "pandas not installed (required for Excel export)"

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for table in tables:
                # Convert to DataFrame
                if table['data'] and len(table['data']) > 1:
                    # Use first row as headers
                    headers = table['data'][0]
                    rows = table['data'][1:]

                    df = pd.DataFrame(rows, columns=headers)

                    # Clean column names
                    df.columns = [str(col).strip() if col else f"Column_{i}"
                                  for i, col in enumerate(df.columns)]

                    # Create sheet name
                    sheet_name = f"P{table['page']}_T{table['table_num']}"

                    # Save to sheet
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                    print(f"  Added sheet: {sheet_name}")

        print(f"  Saved: {output_path}")
        return [output_path], None

    except Exception as e:
        return None, str(e)


def save_tables_markdown(tables, output_path, base_name):
    """Save all tables to a single Markdown file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Tables extracted from {base_name}\n\n")
        f.write(f"Total tables: {len(tables)}\n\n")

        for table in tables:
            f.write(f"## Page {table['page']}, Table {table['table_num']}\n\n")
            f.write(f"Dimensions: {table['row_count']} rows × {table['col_count']} columns\n\n")

            # Write table in markdown format
            if table['data']:
                # Headers
                if table['data'][0]:
                    f.write("| " + " | ".join(str(cell) if cell else "" for cell in table['data'][0]) + " |\n")
                    f.write("| " + " | ".join("---" for _ in table['data'][0]) + " |\n")

                # Rows
                for row in table['data'][1:]:
                    f.write("| " + " | ".join(str(cell) if cell else "" for cell in row) + " |\n")

            f.write("\n---\n\n")

    print(f"  Saved: {output_path}")
    return [output_path]


def parse_page_range(page_string):
    """
    Parse page range string into list of page numbers.

    Examples:
        "1,3,5" -> [1, 3, 5]
        "1-5" -> [1, 2, 3, 4, 5]
        "1-3,7,9-11" -> [1, 2, 3, 7, 9, 10, 11]
    """
    pages = []

    for part in page_string.split(','):
        part = part.strip()

        if '-' in part:
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))

    return sorted(set(pages))


def main():
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF files with high accuracy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Formats:
  csv       - Each table saved as separate CSV file (default)
  json      - All tables in single JSON file with metadata
  excel     - All tables in single Excel file with multiple sheets
  markdown  - All tables in single Markdown file

Examples:
  # Extract all tables to CSV files
  python extract_tables.py report.pdf --output tables/

  # Extract tables from specific pages
  python extract_tables.py report.pdf --pages 1,3,5 --output tables/

  # Extract page range
  python extract_tables.py report.pdf --pages 1-10 --output tables/

  # Save as Excel file
  python extract_tables.py report.pdf --format excel --output report_tables.xlsx

  # Save as JSON
  python extract_tables.py report.pdf --format json --output tables.json

  # Save as Markdown
  python extract_tables.py report.pdf --format markdown --output tables.md
        """
    )

    parser.add_argument("input", help="Input PDF file path")
    parser.add_argument("--output", "-o", required=True,
                        help="Output path (directory for CSV, file for other formats)")
    parser.add_argument("--format", choices=["csv", "json", "excel", "markdown"],
                        default="csv", help="Output format (default: csv)")
    parser.add_argument("--pages", help="Pages to process (e.g., '1,3,5' or '1-10' or '1-5,8,10-15')")
    parser.add_argument("--preview", action="store_true",
                        help="Show preview of tables without saving")

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print("Error: Missing dependencies:", ", ".join(missing_deps))
        print("Install with: pip install " + " ".join(missing_deps))
        sys.exit(1)

    # Parse page range if specified
    pages = None
    if args.pages:
        try:
            pages = parse_page_range(args.pages)
            print(f"Processing pages: {pages}")
        except Exception as e:
            print(f"Error parsing page range: {e}")
            sys.exit(1)

    # Extract tables
    print(f"\nExtracting tables from: {args.input}")
    print("-" * 70)

    tables, error = extract_tables(args.input, pages=pages)

    if error:
        print(f"\nError: {error}")
        sys.exit(1)

    if not tables:
        print("\nNo tables found in PDF")
        sys.exit(0)

    print(f"\nFound {len(tables)} table(s)")

    # Preview mode
    if args.preview:
        print("\n" + "=" * 70)
        print("TABLE PREVIEW")
        print("=" * 70)

        for table in tables:
            print(f"\nPage {table['page']}, Table {table['table_num']}")
            print(f"Dimensions: {table['row_count']} rows × {table['col_count']} columns")

            # Show first few rows
            print("\nFirst 5 rows:")
            for i, row in enumerate(table['data'][:5]):
                print(f"  Row {i}: {row}")

            print()

        sys.exit(0)

    # Save tables
    base_name = Path(args.input).stem

    print(f"\nSaving tables as {args.format.upper()}...")
    print("-" * 70)

    saved_files = []

    if args.format == "csv":
        saved_files = save_tables_csv(tables, args.output, base_name)

    elif args.format == "json":
        saved_files = save_tables_json(tables, args.output, base_name)

    elif args.format == "excel":
        result = save_tables_excel(tables, args.output, base_name)
        if isinstance(result, tuple):
            saved_files, error = result
            if error:
                print(f"\nError: {error}")
                print("Note: Excel export requires pandas. Install with: pip install pandas openpyxl")
                sys.exit(1)
        else:
            saved_files = result

    elif args.format == "markdown":
        saved_files = save_tables_markdown(tables, args.output, base_name)

    # Summary
    print("\n" + "=" * 70)
    print("SUCCESS")
    print("=" * 70)
    print(f"\nTables extracted: {len(tables)}")
    print(f"Files created: {len(saved_files)}")

    if args.format == "csv":
        print(f"Output directory: {args.output}")
    else:
        print(f"Output file: {args.output}")

    # Table summary
    print("\nTable Summary:")
    for table in tables:
        print(f"  Page {table['page']}, Table {table['table_num']}: "
              f"{table['row_count']} rows × {table['col_count']} columns")


if __name__ == "__main__":
    main()
