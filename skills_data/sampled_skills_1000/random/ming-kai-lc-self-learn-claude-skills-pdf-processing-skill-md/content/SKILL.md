---
name: pdf-processing
description: Comprehensive PDF processing techniques for handling large files that exceed Claude Code's reading limits, including chunking strategies, text/table extraction, and OCR for scanned documents. Use when working with PDFs larger than 10-15MB or more than 30-50 pages.
version: 1.0.0
dependencies: python>=3.8, pypdf>=3.0.0, PyMuPDF>=1.23.0, pdfplumber>=0.9.0, pdf2image>=1.16.0, pytesseract>=0.3.10
---

# PDF Processing for Claude Code

Provides comprehensive techniques and utilities for processing PDF files in Claude Code, especially large files that exceed direct reading capabilities.

## Overview

Claude Code can read PDF files directly using the Read tool, but has critical limitations:

- **Official limits**: 32MB max file size, 100 pages max
- **Real-world limits**: Much lower (10-15MB, 30-50 pages)
- **Known issue**: Claude Code crashes with large PDFs, causing session termination and context loss
- **Token cost**: 1,500-3,000 tokens per page for text + additional for images

This skill provides workarounds, utilities, and best practices for handling PDFs of any size.

## Quick Start

### Check if PDF is Too Large for Direct Reading

```python
import os

def is_pdf_too_large(filepath, max_mb=10):
    """Check if PDF exceeds safe processing size."""
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    return size_mb > max_mb

# Use before attempting to read
if is_pdf_too_large("document.pdf"):
    print("PDF too large - use chunking strategies")
else:
    # Safe to read directly with Claude Code
    pass
```

### Extract Text from PDF

```python
import fitz  # PyMuPDF - fastest option

def extract_text_fast(pdf_path):
    """Extract all text from PDF quickly."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

# Usage
text = extract_text_fast("document.pdf")
```

### Split Large PDF into Chunks

```python
from pypdf import PdfReader, PdfWriter

def chunk_pdf(input_path, pages_per_chunk=25, output_dir="chunks"):
    """Split PDF into smaller files."""
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)

    os.makedirs(output_dir, exist_ok=True)

    for i in range(0, total_pages, pages_per_chunk):
        writer = PdfWriter()
        end = min(i + pages_per_chunk, total_pages)

        for page_num in range(i, end):
            writer.add_page(reader.pages[page_num])

        output_file = f"{output_dir}/chunk_{i//pages_per_chunk:03d}_pages_{i+1}-{end}.pdf"
        with open(output_file, "wb") as output:
            writer.write(output)

        print(f"Created {output_file}")

# Usage
chunk_pdf("large_document.pdf", pages_per_chunk=30)
```

### Extract Tables from PDF

```python
import pdfplumber

def extract_tables(pdf_path):
    """Extract all tables from PDF with high accuracy."""
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_tables = page.extract_tables()
            for table_num, table in enumerate(page_tables, 1):
                tables.append({
                    'page': page_num,
                    'table_num': table_num,
                    'data': table
                })

    return tables

# Usage
tables = extract_tables("report.pdf")
for t in tables:
    print(f"Page {t['page']}, Table {t['table_num']}")
    print(t['data'])
```

## Python Libraries

### pypdf (formerly PyPDF2)
- **Best for**: Basic PDF operations (split, merge, rotate)
- **Speed**: Slower than alternatives
- **Install**: `pip install pypdf`

### PyMuPDF (fitz)
- **Best for**: Fast text extraction, general-purpose processing
- **Speed**: 10-20x faster than pypdf
- **Install**: `pip install PyMuPDF`

### pdfplumber
- **Best for**: Table extraction, precise text with coordinates
- **Speed**: Moderate (0.10s per page)
- **Install**: `pip install pdfplumber`

### pdf2image
- **Best for**: Converting PDF pages to images
- **Requires**: Poppler (system dependency)
- **Install**: `pip install pdf2image`

### pytesseract
- **Best for**: OCR on scanned PDFs
- **Requires**: Tesseract (system dependency)
- **Install**: `pip install pytesseract`

## Chunking Strategies

### 1. Page-Based Splitting
Split PDF into fixed page batches.

**When to use**: Document structure is irrelevant; you need simple, predictable chunks

**Optimal size**: 20-30 pages per chunk (stays under 10MB typically)

```python
# See Quick Start "Split Large PDF into Chunks"
chunk_pdf("document.pdf", pages_per_chunk=25)
```

### 2. Size-Based Splitting
Monitor file size and split when threshold is reached.

**When to use**: Avoiding crashes is critical; page count is unreliable indicator

```python
def chunk_by_size(pdf_path, max_mb=8):
    """Split PDF keeping chunks under size limit."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    chunk_num = 0

    for page_num, page in enumerate(reader.pages):
        writer.add_page(page)

        # Check size by writing to bytes
        from io import BytesIO
        buffer = BytesIO()
        writer.write(buffer)
        size_mb = buffer.tell() / (1024 * 1024)

        if size_mb >= max_mb:
            # Save chunk
            output = f"chunk_{chunk_num:03d}.pdf"
            with open(output, "wb") as f:
                writer.write(f)
            chunk_num += 1
            writer = PdfWriter()  # Start new chunk
```

### 3. Overlapping Chunks
Include overlap between chunks to maintain context.

**When to use**: Content spans pages; losing context between chunks is problematic

**Optimal overlap**: 1-2 pages (or 10-20% of chunk size)

```python
def chunk_with_overlap(pdf_path, pages_per_chunk=25, overlap=2):
    """Split PDF with overlapping pages for context preservation."""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    chunk_num = 0
    start = 0

    while start < total_pages:
        writer = PdfWriter()
        end = min(start + pages_per_chunk, total_pages)

        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        output = f"chunk_{chunk_num:03d}_pages_{start+1}-{end}.pdf"
        with open(output, "wb") as f:
            writer.write(f)

        chunk_num += 1
        start = end - overlap  # Move forward with overlap
```

### 4. Text Extraction First
Extract text, then chunk the text instead of PDF.

**When to use**: You only need text content, not layout/images

**Advantage**: Much smaller, faster to process, no crashes

```python
def extract_and_chunk_text(pdf_path, chars_per_chunk=10000):
    """Extract text and split into manageable chunks."""
    import fitz

    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += f"\n\n--- Page {page.number + 1} ---\n\n"
        full_text += page.get_text()

    doc.close()

    # Split text into chunks
    chunks = []
    for i in range(0, len(full_text), chars_per_chunk):
        chunks.append(full_text[i:i + chars_per_chunk])

    return chunks

# Usage
text_chunks = extract_and_chunk_text("large.pdf")
for i, chunk in enumerate(text_chunks):
    with open(f"text_chunk_{i:03d}.txt", "w", encoding="utf-8") as f:
        f.write(chunk)
```

## Handling Different PDF Types

### Text-Based PDFs (Native Text)
PDFs created digitally with searchable text.

**Detection**:
```python
import fitz

doc = fitz.open("document.pdf")
text = doc[0].get_text()  # First page

if len(text.strip()) > 50:
    print("Text-based PDF")
else:
    print("Likely scanned PDF")
```

**Best approach**: Direct text extraction with PyMuPDF or pdfplumber

### Scanned PDFs (Images of Text)
PDFs created by scanning physical documents.

**Requires**: OCR (Optical Character Recognition)

**Approach**:
```python
from pdf2image import convert_from_path
import pytesseract

def ocr_pdf(pdf_path):
    """Extract text from scanned PDF using OCR."""
    # Convert to images
    images = convert_from_path(pdf_path, dpi=300)

    # OCR each page
    text = ""
    for i, image in enumerate(images, 1):
        page_text = pytesseract.image_to_string(image)
        text += f"\n\n--- Page {i} ---\n\n{page_text}"

    return text
```

**Performance note**: OCR is much slower than direct text extraction

### Mixed PDFs
Some pages have text, others are scanned.

**Approach**: Detect page-by-page and use appropriate method

```python
def extract_mixed_pdf(pdf_path):
    """Handle PDFs with both text and scanned pages."""
    import fitz
    from pdf2image import convert_from_path
    import pytesseract

    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num, page in enumerate(doc):
        text = page.get_text()

        if len(text.strip()) > 50:
            # Has text - use direct extraction
            full_text += f"\n\n--- Page {page_num + 1} (text) ---\n\n{text}"
        else:
            # Likely scanned - use OCR
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=300)
            ocr_text = pytesseract.image_to_string(images[0])
            full_text += f"\n\n--- Page {page_num + 1} (OCR) ---\n\n{ocr_text}"

    doc.close()
    return full_text
```

## Helper Scripts

This skill includes pre-built scripts in the `scripts/` directory:

- **chunk_pdf.py**: Flexible PDF chunking with multiple strategies
- **extract_text.py**: Unified text extraction (handles text-based and OCR)
- **extract_tables.py**: Advanced table extraction with formatting
- **process_large_pdf.py**: Orchestrate complete large PDF processing workflow

### Using Helper Scripts

```bash
# Chunk a large PDF
python .claude/skills/pdf-processing/scripts/chunk_pdf.py large_doc.pdf --pages 30 --overlap 2

# Extract all text
python .claude/skills/pdf-processing/scripts/extract_text.py document.pdf --output text.txt

# Extract tables to CSV
python .claude/skills/pdf-processing/scripts/extract_tables.py report.pdf --output tables/

# Process large PDF end-to-end
python .claude/skills/pdf-processing/scripts/process_large_pdf.py huge_doc.pdf --strategy chunk --output processed/
```

## Error Handling

### Preventing Crashes

**Key principle**: Never trust PDF size alone - always check before reading

```python
def safe_pdf_read(pdf_path, max_pages=30, max_mb=10):
    """Safely check if PDF can be read directly."""
    import fitz

    # Check file size
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"File too large: {size_mb:.1f}MB (max: {max_mb}MB)"

    # Check page count
    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()

        if page_count > max_pages:
            return False, f"Too many pages: {page_count} (max: {max_pages})"

        return True, f"Safe to read: {size_mb:.1f}MB, {page_count} pages"

    except Exception as e:
        return False, f"Error checking PDF: {e}"

# Usage
safe, message = safe_pdf_read("document.pdf")
print(message)

if safe:
    # Use Claude Code Read tool
    pass
else:
    # Use chunking strategies
    pass
```

### Handling Corrupted PDFs

```python
def is_pdf_valid(pdf_path):
    """Check if PDF is valid and readable."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        _ = len(doc)  # Force reading
        doc.close()
        return True, "PDF is valid"
    except Exception as e:
        return False, f"PDF is corrupted or invalid: {e}"
```

### Graceful Degradation

```python
def extract_with_fallback(pdf_path):
    """Try multiple extraction methods, falling back if needed."""

    # Try 1: PyMuPDF (fastest)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        if text.strip():
            return text, "pymupdf"
    except Exception as e:
        print(f"PyMuPDF failed: {e}")

    # Try 2: pdfplumber (more reliable)
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        if text.strip():
            return text, "pdfplumber"
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    # Try 3: OCR (last resort)
    try:
        from pdf2image import convert_from_path
        import pytesseract
        images = convert_from_path(pdf_path, dpi=300)
        text = "\n\n".join(pytesseract.image_to_string(img) for img in images)
        return text, "ocr"
    except Exception as e:
        print(f"OCR failed: {e}")

    return None, "all_methods_failed"
```

## Best Practices

1. **Always check file size before reading**: Use `safe_pdf_read()` to avoid crashes
2. **Prefer text extraction over direct reading**: Extract text first, then process text files
3. **Use overlapping chunks for context**: 1-2 pages overlap prevents information loss
4. **Choose the right tool**: PyMuPDF for speed, pdfplumber for tables, OCR for scans
5. **Monitor progress**: For large PDFs, log progress to recover from interruptions
6. **Save intermediate results**: Don't lose progress if processing fails partway through
7. **Test with small chunks first**: Validate approach on 1-2 chunks before processing entire document

## Common Workflows

### Workflow 1: Analyze Large Report

```python
# 1. Check if direct read is safe
safe, msg = safe_pdf_read("report.pdf")

if not safe:
    # 2. Extract text instead
    text = extract_text_fast("report.pdf")

    # 3. Save to file for Claude to read
    with open("report_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    # 4. Process text file (much safer)
    # Claude can now read report_text.txt without crashes
```

### Workflow 2: Extract Data from Multi-Page Invoice

```python
# 1. Extract tables from all pages
tables = extract_tables("invoice_100pages.pdf")

# 2. Convert to structured format
import csv

for t in tables:
    filename = f"invoice_page{t['page']}_table{t['table_num']}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(t['data'])
```

### Workflow 3: Process Scanned Document Archive

```python
# 1. Check if scanned
import fitz
doc = fitz.open("archive.pdf")
is_scanned = len(doc[0].get_text().strip()) < 50
doc.close()

if is_scanned:
    # 2. Use OCR
    text = ocr_pdf("archive.pdf")

    # 3. Save extracted text
    with open("archive_ocr.txt", "w", encoding="utf-8") as f:
        f.write(text)
```

## Troubleshooting

### Issue: "Claude Code crashed when reading PDF"
**Solution**: File was too large. Use chunking or text extraction first.

### Issue: "Extracted text is gibberish"
**Solution**: PDF might be scanned. Use OCR (`ocr_pdf()` function).

### Issue: "Table extraction is inaccurate"
**Solution**: Use pdfplumber with custom table detection settings (see `reference.md`).

### Issue: "OCR is too slow"
**Solution**: Reduce DPI (try 150-200 instead of 300), or process only needed pages.

### Issue: "Out of memory when processing large PDF"
**Solution**: Process page-by-page instead of loading entire document. See `process_large_pdf.py`.

## Next Steps

- For advanced techniques and detailed API references, see [reference.md](reference.md)
- For troubleshooting specific library issues, see library documentation
- For custom workflows, combine techniques from Quick Start and Common Workflows sections

## Installation

Required dependencies:

```bash
pip install pypdf PyMuPDF pdfplumber pdf2image pytesseract
```

System dependencies:
- **Poppler** (for pdf2image): [Installation guide](https://pdf2image.readthedocs.io/en/latest/installation.html)
- **Tesseract** (for OCR): [Installation guide](https://github.com/tesseract-ocr/tesseract)
