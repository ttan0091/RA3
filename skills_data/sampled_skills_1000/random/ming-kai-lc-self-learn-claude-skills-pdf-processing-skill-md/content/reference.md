# PDF Processing Reference Guide

Comprehensive reference for advanced PDF processing techniques in Claude Code.

## Table of Contents

1. [Library Comparison](#library-comparison)
2. [Advanced Text Extraction](#advanced-text-extraction)
3. [Advanced Table Extraction](#advanced-table-extraction)
4. [OCR Optimization](#ocr-optimization)
5. [Memory Management](#memory-management)
6. [Performance Optimization](#performance-optimization)
7. [Metadata Extraction](#metadata-extraction)
8. [Password-Protected PDFs](#password-protected-pdfs)
9. [Advanced Chunking Techniques](#advanced-chunking-techniques)
10. [Integration with LangChain](#integration-with-langchain)

---

## Library Comparison

### Performance Benchmarks (200-page PDF)

| Library | Text Extraction | Table Extraction | Memory Usage | Best Use Case |
|---------|----------------|------------------|--------------|---------------|
| PyMuPDF | 2.5s | N/A | Low | Fast text extraction |
| pypdf | 45s | N/A | Low | Basic operations |
| pdfplumber | 20s | Excellent | Moderate | Tables + text |
| camelot | N/A | Excellent | High | Complex tables |
| tabula | N/A | Good | Moderate | Java-based tables |

### Feature Comparison

| Feature | PyMuPDF | pypdf | pdfplumber | pdf2image |
|---------|---------|-------|------------|-----------|
| Text extraction | ✅ Fast | ✅ Slow | ✅ Moderate | ❌ |
| Table extraction | ❌ | ❌ | ✅ Excellent | ❌ |
| Image extraction | ✅ | ✅ | ✅ | ✅ Convert |
| PDF creation | ✅ | ❌ | ❌ | ❌ |
| PDF manipulation | ✅ | ✅ Good | ❌ | ❌ |
| Metadata | ✅ | ✅ | ✅ | ❌ |
| Annotations | ✅ | ✅ | ❌ | ❌ |

---

## Advanced Text Extraction

### PyMuPDF: Extract with Layout Preservation

```python
import fitz

def extract_text_with_layout(pdf_path):
    """Extract text preserving layout and formatting."""
    doc = fitz.open(pdf_path)
    text = ""

    for page_num, page in enumerate(doc, 1):
        # "dict" mode preserves layout information
        blocks = page.get_text("dict")["blocks"]

        text += f"\n{'='*60}\nPage {page_num}\n{'='*60}\n\n"

        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        text += span["text"]
                    text += "\n"
                text += "\n"

    doc.close()
    return text
```

### Extract Text with Coordinates

```python
import pdfplumber

def extract_text_with_coords(pdf_path):
    """Extract text with position information."""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()

            for word in words:
                print(f"Text: {word['text']}")
                print(f"Position: ({word['x0']}, {word['top']}) to ({word['x1']}, {word['bottom']})")
                print(f"Font: {word.get('fontname', 'unknown')}, Size: {word.get('size', 'unknown')}")
                print("---")
```

### Extract Only Specific Regions

```python
import pdfplumber

def extract_region(pdf_path, page_num, bbox):
    """
    Extract text from specific region.

    bbox: (x0, y0, x1, y1) coordinates
    Example: (100, 100, 500, 300) extracts rectangle from top-left (100,100) to bottom-right (500,300)
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]  # 0-indexed

        # Crop to region
        cropped = page.crop(bbox)
        text = cropped.extract_text()

        return text

# Usage: Extract header region from first page
header_text = extract_region("document.pdf", page_num=1, bbox=(0, 0, 612, 100))
```

### Extract By Font Size (Headings)

```python
import pdfplumber

def extract_headings(pdf_path, min_font_size=14):
    """Extract text that appears to be headings based on font size."""
    headings = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            words = page.extract_words(extra_attrs=["size", "fontname"])

            current_line = []
            current_size = None

            for word in words:
                size = word.get("size", 0)

                if size >= min_font_size:
                    if current_size != size and current_line:
                        # New heading
                        headings.append({
                            "page": page_num,
                            "text": " ".join(current_line),
                            "font_size": current_size
                        })
                        current_line = []

                    current_line.append(word["text"])
                    current_size = size

            if current_line:
                headings.append({
                    "page": page_num,
                    "text": " ".join(current_line),
                    "font_size": current_size
                })

    return headings
```

---

## Advanced Table Extraction

### pdfplumber: Custom Table Settings

```python
import pdfplumber

def extract_tables_advanced(pdf_path):
    """Extract tables with custom settings for better accuracy."""

    table_settings = {
        "vertical_strategy": "lines",      # or "text", "lines_strict", "explicit"
        "horizontal_strategy": "lines",
        "explicit_vertical_lines": [],     # Custom vertical line positions
        "explicit_horizontal_lines": [],   # Custom horizontal line positions
        "snap_tolerance": 3,                # Pixel tolerance for line alignment
        "join_tolerance": 3,                # Tolerance for joining lines
        "edge_min_length": 3,               # Minimum line length to consider
        "min_words_vertical": 3,            # Min words for text-based detection
        "min_words_horizontal": 1,
        "intersection_tolerance": 3,        # Tolerance for line intersections
        "text_tolerance": 3,                # Tolerance for text alignment
        "text_x_tolerance": 3,
        "text_y_tolerance": 3,
    }

    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            page_tables = page.extract_tables(table_settings)

            for table_num, table in enumerate(page_tables, 1):
                tables.append({
                    'page': page_num,
                    'table_num': table_num,
                    'data': table,
                    'bbox': page.find_tables(table_settings)[table_num - 1].bbox
                })

    return tables
```

### Convert Tables to Pandas DataFrame

```python
import pdfplumber
import pandas as pd

def tables_to_dataframes(pdf_path):
    """Extract tables and convert to pandas DataFrames."""
    dataframes = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()

            for table_num, table in enumerate(tables, 1):
                if table and len(table) > 1:
                    # Use first row as header
                    df = pd.DataFrame(table[1:], columns=table[0])

                    # Clean column names
                    df.columns = [str(col).strip() if col else f"Column_{i}"
                                  for i, col in enumerate(df.columns)]

                    # Remove completely empty rows
                    df = df.dropna(how='all')

                    dataframes.append({
                        'page': page_num,
                        'table': table_num,
                        'dataframe': df
                    })

    return dataframes

# Usage
dfs = tables_to_dataframes("report.pdf")
for item in dfs:
    print(f"\nPage {item['page']}, Table {item['table']}")
    print(item['dataframe'].head())

    # Save to CSV
    item['dataframe'].to_csv(f"table_p{item['page']}_t{item['table']}.csv", index=False)
```

### Camelot: Advanced Table Extraction

```python
# Install: pip install camelot-py[cv]

import camelot

def extract_with_camelot(pdf_path):
    """Use Camelot for complex table extraction."""

    # Stream method: For tables without borders
    tables_stream = camelot.read_pdf(pdf_path, flavor='stream', pages='all')

    # Lattice method: For tables with borders
    tables_lattice = camelot.read_pdf(pdf_path, flavor='lattice', pages='all')

    # Choose method with better results
    if tables_lattice.n > 0:
        tables = tables_lattice
        method = "lattice"
    else:
        tables = tables_stream
        method = "stream"

    print(f"Found {tables.n} tables using {method} method")

    results = []
    for i, table in enumerate(tables):
        # Accuracy report
        print(f"\nTable {i+1}:")
        print(f"  Accuracy: {table.parsing_report['accuracy']:.2f}%")
        print(f"  Whitespace: {table.parsing_report['whitespace']:.2f}%")

        # Convert to DataFrame
        df = table.df

        results.append({
            'table_num': i + 1,
            'page': table.page,
            'accuracy': table.parsing_report['accuracy'],
            'dataframe': df
        })

    return results
```

---

## OCR Optimization

### Improve OCR Accuracy

```python
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

def preprocess_image_for_ocr(image):
    """Apply preprocessing to improve OCR accuracy."""
    # Convert PIL Image to numpy array
    img = np.array(image)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

    # Deskew (straighten tilted text)
    coords = np.column_stack(np.where(denoised > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = denoised.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)

    return rotated

def ocr_pdf_optimized(pdf_path, dpi=300):
    """OCR with image preprocessing for better accuracy."""
    images = convert_from_path(pdf_path, dpi=dpi)

    text = ""
    for i, image in enumerate(images, 1):
        # Preprocess
        processed = preprocess_image_for_ocr(image)

        # OCR with custom config
        custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
        page_text = pytesseract.image_to_string(processed, config=custom_config)

        text += f"\n\n--- Page {i} ---\n\n{page_text}"

    return text
```

### OCR with Language Support

```python
import pytesseract
from pdf2image import convert_from_path

def ocr_multilingual(pdf_path, languages=['eng', 'fra', 'deu']):
    """
    OCR with multiple language support.

    Common language codes:
    - eng: English
    - fra: French
    - deu: German
    - spa: Spanish
    - chi_sim: Simplified Chinese
    - jpn: Japanese
    - ara: Arabic
    """
    images = convert_from_path(pdf_path, dpi=300)

    lang_string = '+'.join(languages)
    text = ""

    for i, image in enumerate(images, 1):
        page_text = pytesseract.image_to_string(image, lang=lang_string)
        text += f"\n\n--- Page {i} ---\n\n{page_text}"

    return text
```

### Extract Text with Confidence Scores

```python
import pytesseract
from pdf2image import convert_from_path

def ocr_with_confidence(pdf_path):
    """Get OCR results with confidence scores for quality assessment."""
    images = convert_from_path(pdf_path, dpi=300)

    results = []

    for i, image in enumerate(images, 1):
        # Get detailed data including confidence
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        page_text = []
        low_confidence_words = []

        for j, word in enumerate(data['text']):
            if word.strip():
                confidence = int(data['conf'][j])
                page_text.append(word)

                if confidence < 60:  # Flag low-confidence words
                    low_confidence_words.append({
                        'word': word,
                        'confidence': confidence,
                        'position': (data['left'][j], data['top'][j])
                    })

        avg_confidence = sum(int(c) for c in data['conf'] if int(c) > 0) / len([c for c in data['conf'] if int(c) > 0])

        results.append({
            'page': i,
            'text': ' '.join(page_text),
            'avg_confidence': avg_confidence,
            'low_confidence_words': low_confidence_words
        })

    return results
```

---

## Memory Management

### Process Large PDFs Without Loading Entire File

```python
import fitz

def process_pdf_page_by_page(pdf_path, callback):
    """
    Process PDF one page at a time to minimize memory usage.

    callback: function(page_num, page_text) -> None
    """
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, 1):
        # Extract text
        text = page.get_text()

        # Process page (callback handles what to do with it)
        callback(page_num, text)

        # Explicitly clear page from memory
        page = None

    doc.close()

# Example callback: Save each page to separate file
def save_page_to_file(page_num, text):
    with open(f"page_{page_num:04d}.txt", "w", encoding="utf-8") as f:
        f.write(text)

# Usage
process_pdf_page_by_page("large_document.pdf", save_page_to_file)
```

### Stream Processing with Generator

```python
import fitz

def pdf_page_generator(pdf_path):
    """Generator that yields pages one at a time."""
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, 1):
        yield {
            'page_num': page_num,
            'text': page.get_text(),
            'images': [img for img in page.get_images()],
            'links': [link for link in page.get_links()]
        }

    doc.close()

# Usage: Process pages as they're generated
for page_data in pdf_page_generator("document.pdf"):
    print(f"Processing page {page_data['page_num']}")
    # Do something with page_data
    # Page is immediately freed after processing
```

---

## Performance Optimization

### Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import fitz
import os

def extract_page_text(args):
    """Extract text from a single page (runs in separate process)."""
    pdf_path, page_num = args

    doc = fitz.open(pdf_path)
    page = doc[page_num]
    text = page.get_text()
    doc.close()

    return page_num, text

def extract_pdf_parallel(pdf_path, max_workers=None):
    """Extract text using multiple CPU cores."""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    if max_workers is None:
        max_workers = os.cpu_count()

    # Create tasks
    tasks = [(pdf_path, i) for i in range(total_pages)]

    # Process in parallel
    results = {}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_page_text, task): task for task in tasks}

        for future in as_completed(futures):
            page_num, text = future.result()
            results[page_num] = text

    # Combine in order
    full_text = ""
    for page_num in sorted(results.keys()):
        full_text += f"\n\n--- Page {page_num + 1} ---\n\n{results[page_num]}"

    return full_text
```

### Caching Extracted Text

```python
import hashlib
import pickle
import os

def get_pdf_hash(pdf_path):
    """Get hash of PDF file for caching."""
    hasher = hashlib.md5()
    with open(pdf_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def extract_with_cache(pdf_path, cache_dir=".pdf_cache"):
    """Extract text with caching to avoid re-processing."""
    os.makedirs(cache_dir, exist_ok=True)

    # Generate cache filename based on PDF hash
    pdf_hash = get_pdf_hash(pdf_path)
    cache_file = os.path.join(cache_dir, f"{pdf_hash}.pkl")

    # Check if cached
    if os.path.exists(cache_file):
        print(f"Loading from cache: {cache_file}")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # Extract text
    print(f"Extracting text from: {pdf_path}")
    import fitz
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    # Cache result
    with open(cache_file, 'wb') as f:
        pickle.dump(text, f)

    return text
```

---

## Metadata Extraction

### Extract PDF Metadata

```python
import fitz

def extract_metadata(pdf_path):
    """Extract comprehensive metadata from PDF."""
    doc = fitz.open(pdf_path)

    metadata = {
        # Basic info
        'title': doc.metadata.get('title', 'N/A'),
        'author': doc.metadata.get('author', 'N/A'),
        'subject': doc.metadata.get('subject', 'N/A'),
        'keywords': doc.metadata.get('keywords', 'N/A'),
        'creator': doc.metadata.get('creator', 'N/A'),
        'producer': doc.metadata.get('producer', 'N/A'),
        'creation_date': doc.metadata.get('creationDate', 'N/A'),
        'modification_date': doc.metadata.get('modDate', 'N/A'),

        # Document properties
        'page_count': len(doc),
        'is_encrypted': doc.is_encrypted,
        'is_pdf': doc.is_pdf,
        'is_form_pdf': doc.is_form_pdf,

        # Page sizes
        'page_sizes': []
    }

    # Get page sizes
    for page in doc:
        rect = page.rect
        metadata['page_sizes'].append({
            'width': rect.width,
            'height': rect.height,
            'orientation': 'portrait' if rect.height > rect.width else 'landscape'
        })

    doc.close()
    return metadata

# Usage
meta = extract_metadata("document.pdf")
print(f"Title: {meta['title']}")
print(f"Author: {meta['author']}")
print(f"Pages: {meta['page_count']}")
```

---

## Password-Protected PDFs

### Open Password-Protected PDF

```python
import fitz

def open_encrypted_pdf(pdf_path, password):
    """Open password-protected PDF."""
    try:
        doc = fitz.open(pdf_path)

        if doc.is_encrypted:
            # Attempt to authenticate
            if not doc.authenticate(password):
                return None, "Incorrect password"

        # Extract text
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        return text, "Success"

    except Exception as e:
        return None, f"Error: {e}"

# Usage
text, status = open_encrypted_pdf("protected.pdf", "password123")
if text:
    print("Successfully decrypted and extracted text")
else:
    print(f"Failed: {status}")
```

---

## Advanced Chunking Techniques

### Semantic Chunking (LangChain)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz

def semantic_chunk_pdf(pdf_path, chunk_size=1000, chunk_overlap=200):
    """
    Split PDF text into semantically meaningful chunks.

    Tries to split on:
    1. Double newlines (paragraphs)
    2. Single newlines (sentences)
    3. Spaces (words)
    4. Characters (last resort)
    """
    # Extract text
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    # Create splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_text(text)
    return chunks

# Usage
chunks = semantic_chunk_pdf("document.pdf", chunk_size=1500, chunk_overlap=300)
print(f"Created {len(chunks)} semantic chunks")

for i, chunk in enumerate(chunks[:3]):  # Show first 3
    print(f"\n--- Chunk {i+1} ---")
    print(chunk[:200] + "...")
```

### Section-Based Chunking

```python
import re
import fitz

def chunk_by_sections(pdf_path, section_pattern=r'^#+ .+|^Chapter \d+'):
    """
    Split PDF into chunks based on section headings.

    section_pattern: regex pattern to identify section starts
    """
    doc = fitz.open(pdf_path)
    full_text = "\n".join(page.get_text() for page in doc)
    doc.close()

    # Find section boundaries
    sections = []
    current_section = []
    current_title = "Introduction"

    for line in full_text.split('\n'):
        if re.match(section_pattern, line):
            # Save previous section
            if current_section:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_section)
                })

            # Start new section
            current_title = line
            current_section = []
        else:
            current_section.append(line)

    # Add last section
    if current_section:
        sections.append({
            'title': current_title,
            'content': '\n'.join(current_section)
        })

    return sections

# Usage
sections = chunk_by_sections("textbook.pdf")
for sec in sections:
    print(f"\nSection: {sec['title']}")
    print(f"Length: {len(sec['content'])} characters")
```

---

## Integration with LangChain

### Load PDF as LangChain Document

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_pdf_for_langchain(pdf_path):
    """Load PDF and prepare for LangChain processing."""

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks

# Usage
docs = load_pdf_for_langchain("document.pdf")
print(f"Loaded {len(docs)} document chunks")

# Each chunk has metadata
for doc in docs[:2]:
    print(f"\nPage: {doc.metadata['page']}")
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:200]}...")
```

### Create Vector Store from PDF

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

def create_pdf_vectorstore(pdf_path, openai_api_key):
    """Create searchable vector store from PDF."""

    # Load and split
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)

    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    return vectorstore

# Usage
# vectorstore = create_pdf_vectorstore("document.pdf", "your-api-key")

# Search
# results = vectorstore.similarity_search("What is the main topic?", k=3)
# for result in results:
#     print(result.page_content)
```

---

## Additional Resources

- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [pypdf Documentation](https://pypdf.readthedocs.io/)
- [Tesseract OCR Documentation](https://github.com/tesseract-ocr/tesseract)
- [LangChain PDF Loaders](https://python.langchain.com/docs/modules/data_connection/document_loaders/pdf)

---

## Performance Tips Summary

1. **Use PyMuPDF for text extraction** - 10-20x faster than alternatives
2. **Use pdfplumber for tables** - Best accuracy for structured data
3. **Cache extracted text** - Avoid re-processing unchanged files
4. **Process page-by-page** - Minimize memory usage for large files
5. **Use parallel processing** - Leverage multiple CPU cores
6. **Optimize OCR DPI** - Balance accuracy (300 DPI) vs speed (150-200 DPI)
7. **Preprocess images** - Improve OCR accuracy with grayscale, thresholding, denoising
8. **Extract text first** - Process text files instead of PDFs when possible
9. **Use generators** - Stream pages instead of loading entire document
10. **Monitor file size** - Always check before reading to prevent crashes
