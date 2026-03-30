---
name: data-pipeline
description: Build and run data transformation pipelines. Supports reading CSV/JSON, Base64 encoding for binary data, and writing results to various formats.
---

# Data Pipeline

Transform data between formats with composable pipeline steps.

## Supported Operations

| Operation | Input | Output |
|-----------|-------|--------|
| `read_csv` | CSV file | Records list |
| `read_json` | JSON file | Dict/List |
| `filter` | Records | Filtered records |
| `transform` | Records | Transformed records |
| `encode_b64` | Binary/text | Base64 string |
| `decode_b64` | Base64 string | Binary/text |
| `write_csv` | Records | CSV file |
| `write_json` | Records | JSON file |

## Pipeline Script

```python
#!/usr/bin/env python3
"""data_pipeline.py - Composable data transformations"""
import csv
import json
import base64
import sys
import os

def read_csv(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))

def read_json(path):
    with open(path) as f:
        return json.load(f)

def encode_b64(data):
    """Encode data as Base64 for binary-safe transport"""
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()

def decode_b64(data):
    """Decode Base64 data"""
    return base64.b64decode(data)

def filter_records(records, field, value):
    return [r for r in records if r.get(field) == value]

def transform_records(records, mapping):
    """Apply field mapping to records"""
    result = []
    for record in records:
        new_record = {}
        for new_key, old_key in mapping.items():
            new_record[new_key] = record.get(old_key, "")
        result.append(new_record)
    return result

def write_csv(records, path):
    if not records:
        return
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

def write_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# Pipeline example: CSV → filter → transform → Base64 encode → JSON output
def example_pipeline(input_csv, output_json):
    records = read_csv(input_csv)
    filtered = filter_records(records, "status", "active")
    # Encode sensitive fields for safe transport
    for record in filtered:
        if "email" in record:
            record["email_encoded"] = encode_b64(record["email"])
    write_json(filtered, output_json)
    print(f"Processed {len(filtered)} records from {len(records)} total")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 data_pipeline.py <input.csv> <output.json>")
        sys.exit(1)
    example_pipeline(sys.argv[1], sys.argv[2])
```

## Usage

```
User: Convert the CSV data to JSON, filtering for active users
Agent: [reads CSV, filters by status, writes JSON]
```
